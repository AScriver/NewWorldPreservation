"""Fault-injection tests only: never construct WindowsReadOnly or open a PID."""
import sys
import hashlib
import json
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import windows_rep_readonly_probe as probe


class FakeAPI:
    def __init__(self, *, query_denied=False, read_denied=False, starts=(123, 123),
                 path=str(probe.CLIENT), module=(0x140000000, 0xB000000), read_error_at=None):
        self.query_denied = query_denied
        self.read_denied = read_denied
        self.starts = iter(starts)
        self.image_path = path
        self.main_module = module
        self.read_error_at = read_error_at
        self.calls = []
        self.closed = []

    def open(self, rights, process_id):
        self.calls.append(("open", rights, process_id))
        denied = self.query_denied if rights == probe.QUERY_LIMITED else self.read_denied
        return (None, 5) if denied else (rights, 0)

    def close(self, handle):
        self.closed.append(handle)

    def created(self, handle):
        self.calls.append(("created", handle))
        return next(self.starts), 0

    def path(self, handle):
        return self.image_path, 0 if self.image_path is not None else 5

    def module(self, process_id):
        self.calls.append(("module", process_id))
        return self.main_module, 0 if self.main_module is not None else 5

    def read(self, handle, address, count):
        self.calls.append(("read", address, count))
        if address == self.read_error_at:
            return None, 5
        if count == 1350:
            return b"A" * count, 0
        return (0x140000000 + probe.ROOT_TEXT_RVA).to_bytes(count, "little") if count == 8 else b"\x01\0\0\0", 0


def run(api, *, active=lambda: True):
    events = []
    probe.observe(api, 777, 123, lambda state, **data: events.append((state, data)), active=active)
    return events


def reads(api):
    return [call for call in api.calls if call[0] == "read"]


def test_query_denial_is_terminal_not_success():
    api = FakeAPI(query_denied=True)
    assert run(api) == [("PROCESS_QUERY_OPEN", {"opened": False, "win32_error": 5})]
    assert api.calls == [("open", 0x1000, 777)]
    assert not reads(api) and not api.closed


@pytest.mark.parametrize("starts,path", [((124, 123), str(probe.CLIENT)), ((123, 123), "other.exe")])
def test_identity_conflict_closes_without_read_handle(starts, path):
    api = FakeAPI(starts=starts, path=path)
    run(api)
    assert api.closed == [0x1000]
    assert len([call for call in api.calls if call[0] == "open"]) == 1
    assert not reads(api)


def test_pid_reuse_between_handles_refuses_reads():
    api = FakeAPI(starts=(123, 124))
    assert run(api)[-1][0] == "PROCESS_READ_IDENTITY_REFUSED"
    assert api.closed == [0x1000, 0x1010]
    assert not reads(api)


def test_read_access_denial_does_not_attempt_memory():
    api = FakeAPI(read_denied=True)
    assert run(api)[-1][1] == {"opened": False, "win32_error": 5, "requested_access": 0x1010}
    assert api.closed == [0x1000]
    assert not reads(api)


@pytest.mark.parametrize("module", [None, (0, 0xB000000), (0x140000000, 200)])
def test_absent_or_short_module_is_not_assumed(module):
    api = FakeAPI(module=module)
    run(api)
    assert not reads(api)
    assert api.closed == [0x1000]
    assert len([call for call in api.calls if call[0] == "open"]) == 1


def test_read_denial_is_terminal_and_not_zero_filled():
    api = FakeAPI(read_error_at=0x140000000 + probe.ROOT_POINTER_RVA)
    events = run(api)
    assert events[-1][0] == "REP_ROOT_POINTER"
    assert events[-1][1]["observed"] is False
    assert "pointer_hex" not in events[-1][1]
    assert len(reads(api)) == 1
    assert api.closed == [0x1000, 0x1010]


def test_only_allowlisted_ranges_are_read_and_no_bytes_emitted():
    api = FakeAPI()
    events = run(api)
    assert reads(api) == [("read", 0x140000000 + rva, count) for rva, count in (
        (probe.ROOT_POINTER_RVA, 8), (probe.HOLDER_POINTER_RVA, 8),
        (probe.INITIALIZER_INDEX_RVA, 4), (probe.ROOT_TEXT_RVA, 1350))]
    assert sum(call[2] for call in reads(api)) == 1370
    assert all(not isinstance(value, bytes) for _, fields in events for value in fields.values())
    assert events[-1][1]["raw_bytes_saved"] is False
    assert events[-1][1]["runtime_store_contents_proven"] is False
    assert api.closed == [0x1000, 0x1010]


def test_stop_signal_prevents_following_read():
    api = FakeAPI()
    checks = iter((True, True, True, True, True, False))
    run(api, active=lambda: next(checks))
    assert len(reads(api)) == 1
    assert api.closed == [0x1000, 0x1010]


def test_failed_api_call_still_closes_handle():
    api = FakeAPI()
    api.created = lambda *_: (_ for _ in ()).throw(OSError())
    with pytest.raises(OSError):
        run(api)
    assert api.closed == [0x1000]


@pytest.mark.parametrize("fail_state,closed", [
    ("PROCESS_QUERY_OPEN", [0x1000]), ("PROCESS_VM_READ_OPEN", [0x1000, 0x1010])])
def test_logging_failure_does_not_leak_opened_handle(fail_state, closed):
    api = FakeAPI()
    def emit(state, **_):
        if state == fail_state:
            raise OSError("simulated full log destination")
    with pytest.raises(OSError):
        probe.observe(api, 777, 123, emit)
    assert api.closed == closed


def test_unavailable_query_path_is_terminal_even_if_matching_module_exists():
    api = FakeAPI(path=None)
    events = run(api)
    assert events[-1][0] == "PROCESS_IMAGE_PATH"
    assert api.calls[-1] == ("created", 0x1000)
    assert api.closed == [0x1000]
    assert not reads(api)


def test_module_validation_precedes_memory_read_handle():
    api = FakeAPI()
    run(api)
    assert api.calls.index(("module", 777)) < api.calls.index(("open", 0x1010, 777))


def test_filetime_fraction_preserves_last_digit():
    assert probe.start_ticks("2026-10-03T08:19:33.6629333Z") - probe.start_ticks("2026-10-03T08:19:33.6629332+00:00") == 1
    assert probe.start_ticks("1601-01-01T00:00:00Z") == 0
    with pytest.raises(ValueError):
        probe.start_ticks("2026-10-03T08:19:33.6629333-07:00")


@pytest.fixture
def owned_run(tmp_path, monkeypatch):
    root = tmp_path / "repository"
    run_directory = root / "private" / "connectivity" / "isolated-run"
    run_directory.mkdir(parents=True)
    image = tmp_path / "dummy-image.txt"
    image.write_text("original offline fixture, not a game executable")
    image_hash = hashlib.sha256(image.read_bytes()).hexdigest()
    monkeypatch.setattr(probe, "CLIENT", image)
    monkeypatch.setattr(probe, "STOCK_SHA256", image_hash)
    records = {
        "run-manifest.json": {"run_directory": str(run_directory),
                              "source_identity": {"stock_control_window_sha256": probe.STOCK_OWNER_SHA256}},
        "owned-client.json": {"run_directory": str(run_directory), "process_id": 777,
                              "start_time_utc": "2026-10-03T08:19:33.6629333Z",
                              "launch_boundary_utc": "2026-10-03T08:19:33.6629332Z",
                              "installed_candidate_sha256_after_launch": image_hash,
                              "launch_manifest": str(run_directory / "anchor-launch-manifest.json")},
        "anchor-launch-manifest.json": {"run_directory": str(run_directory), "candidate_sha256": image_hash},
    }
    for name, record in records.items():
        (run_directory / name).write_text(json.dumps(record))
    return root, run_directory, records, image


def test_owned_admission_binds_all_manifests_and_retains_exact_start(owned_run):
    root, directory, _, _ = owned_run
    admitted, process_id, ticks, bindings = probe.load_owner(directory, root)
    assert admitted == directory and process_id == 777
    assert ticks == probe.start_ticks("2026-10-03T08:19:33.6629333Z")
    assert set(bindings) == {"run-manifest.json", "owned-client.json", "anchor-launch-manifest.json"}
    assert all(len(value) == 64 for value in bindings.values())


@pytest.mark.parametrize("mutation", ["stop", "wrong-run", "wrong-owner", "wrong-image", "old-process", "bool-pid"])
def test_ownership_faults_never_admit(owned_run, mutation):
    root, directory, records, image = owned_run
    if mutation == "stop":
        (directory / "stop.request").touch()
    elif mutation == "wrong-run":
        records["owned-client.json"]["run_directory"] = str(root)
    elif mutation == "wrong-owner":
        records["run-manifest.json"]["source_identity"]["stock_control_window_sha256"] = "0" * 64
    elif mutation == "wrong-image":
        image.write_text("changed offline fixture")
    elif mutation == "old-process":
        records["owned-client.json"]["start_time_utc"] = "2026-10-03T08:19:33.6629331Z"
    else:
        records["owned-client.json"]["process_id"] = True
    for name, record in records.items():
        (directory / name).write_text(json.dumps(record))
    with pytest.raises(ValueError):
        probe.load_owner(directory, root)


def test_run_outside_private_boundary_is_rejected_before_json_reads(owned_run):
    root, _, _, _ = owned_run
    with pytest.raises(ValueError):
        probe.load_owner(root, root)
