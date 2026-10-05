"""No live client, Frida attachment, or firewall changes in this suite."""
import json
from pathlib import Path
import sys
import threading

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import frida_client_trial as trial


class FakeOwner:
    def __init__(self, fail=False, exited=False):
        self.fail = fail
        self.is_exited = exited
        self.process = None
        self.closed = False

    def claim(self, pid, exe):
        if self.fail:
            raise PermissionError("denied")
        self.process = object()
        return 123456789

    def exited(self):
        return self.is_exited

    def close(self):
        self.closed = True


class FakeScript:
    def __init__(self, name, guard_fail=False, upstream_logs=()):
        self.name = name
        self.guard_fail = guard_fail
        self.upstream_logs = upstream_logs
        self.callback = None

    def on(self, signal, callback):
        assert signal == "message"
        self.callback = callback

    def load(self):
        if self.name == "bounded-trial-observer":
            payload = {"type": "observer-status", "ok": not self.guard_fail,
                       "event": "admitted_and_attached"}
        else:
            for upstream_text in self.upstream_logs:
                self.callback({"type": "send", "payload": {"type": "log", "text": upstream_text}}, None)
            payload = {"type": "status", "ok": True}
        self.callback({"type": "send", "payload": payload}, None)


class FakeSession:
    def __init__(self, guard_fail=False, upstream_logs=()):
        self.guard_fail = guard_fail
        self.upstream_logs = upstream_logs
        self.gated = False
        self.detached = False
        self.detached_callback = None

    def on(self, signal, callback):
        assert signal == "detached"
        self.detached_callback = callback

    def enable_child_gating(self):
        self.gated = True

    def create_script(self, source, name):
        assert self.gated
        return FakeScript(name, self.guard_fail, self.upstream_logs)

    def detach(self):
        self.detached = True


class FakeDevice:
    def __init__(self, *, attach_fail=False, guard_fail=False, emit_child=False,
                 detach_after_resume=False, upstream_logs=()):
        self.attach_fail = attach_fail
        self.emit_child = emit_child
        self.detach_after_resume = detach_after_resume
        self.session = FakeSession(guard_fail, upstream_logs)
        self.resumed = []
        self.killed = []
        self.callback = None
        self.spawned = False

    def on(self, signal, callback):
        assert signal == "child-added"
        self.callback = callback

    def off(self, signal, callback):
        assert callback is self.callback

    def spawn(self, path, **options):
        self.spawned = True
        assert options["cwd"] == str(Path(path).parent)
        assert options["env"]["SteamAppId"] == "1063730"
        assert options["env"]["SteamGameId"] == "1063730"
        return 41

    def attach(self, pid):
        if self.attach_fail:
            raise PermissionError("Frida attach denied")
        return self.session

    def resume(self, pid):
        if self.emit_child:
            self.callback(type("Child", (), {"pid": 42, "parent_pid": pid})())
        self.resumed.append(pid)
        if self.detach_after_resume:
            self.session.detached_callback("connection-terminated", None)

    def kill(self, pid):
        self.killed.append(pid)


def run_fake(tmp_path, device, owner, record=None, *, context_gate_observer=False):
    exe = tmp_path / "client" / "Bin64" / "NewWorld.exe"
    if record is None:
        record = lambda *args, **kwargs: None
    admission = {"path": str(exe), "bytes": [0] * 16, "hex": "00" * 16}
    if context_gate_observer:
        admission["context_gate_targets"] = []  # FakeScript bypasses runtime entry guards.
    trial.execute(device, owner, tmp_path, exe, admission, 1, record)


def test_attach_denied_never_resumes_and_owned_job_closes(tmp_path):
    device, owner = FakeDevice(attach_fail=True), FakeOwner()
    with pytest.raises(PermissionError):
        run_fake(tmp_path, device, owner)
    assert device.resumed == [] and owner.closed


def test_observer_guard_failure_never_loads_upstream_or_resumes(tmp_path):
    device, owner = FakeDevice(guard_fail=True), FakeOwner()
    with pytest.raises(RuntimeError, match="observer"):
        run_fake(tmp_path, device, owner)
    assert device.resumed == [] and owner.closed and device.session.detached


def test_strict_logger_records_observer_and_sanitizes_only_known_trust_logs(tmp_path):
    logs = (
        "module=NewWorld.exe base=0x1234 secret-sentinel",
        "[trust-bypass] zeroed verifyField ctx=0x111 was=0x222",
        "[trust-bypass] FAILED to null verifyField ctx=0x333: secret-sentinel",
        "arbitrary secret-sentinel",
    )
    device, owner = FakeDevice(upstream_logs=logs), FakeOwner()
    events = []

    def strict_record(event, **fields):
        events.append({"event": event, **fields})

    run_fake(tmp_path, device, owner, strict_record)
    assert {"event": "observer_status", "ok": True,
            "observer_event": "admitted_and_attached", "error": None} in events
    assert [item for item in events if item["event"] == "trust_write_result"] == [
        {"event": "trust_write_result", "success": True},
        {"event": "trust_write_result", "success": False},
    ]
    assert "secret-sentinel" not in json.dumps(events)


def test_failed_log_publication_still_cleans_new_spawn(tmp_path):
    device, owner = FakeDevice(), FakeOwner()

    def broken(*_args, **_kwargs):
        raise OSError("disk full")

    with pytest.raises(OSError, match="disk full"):
        run_fake(tmp_path, device, owner, broken)
    assert owner.closed and device.killed == [41] and device.resumed == []


def test_child_is_killed_during_gating(tmp_path):
    device, owner = FakeDevice(emit_child=True), FakeOwner()
    run_fake(tmp_path, device, owner)
    assert device.killed == [42] and owner.closed


def test_session_loss_after_resume_closes_job(tmp_path):
    device, owner = FakeDevice(detach_after_resume=True), FakeOwner()
    with pytest.raises(RuntimeError, match="session detached"):
        run_fake(tmp_path, device, owner)
    assert device.resumed == [41] and owner.closed


def test_unrelated_device_child_is_ignored(tmp_path):
    device, owner = FakeDevice(), FakeOwner(exited=True)
    def record(*_args, **_kwargs):
        pass
    # Own process exits before attach; event is still registered for cleanup.
    with pytest.raises(RuntimeError, match="before attach"):
        run_fake(tmp_path, device, owner, record)
    device.callback(type("Child", (), {"pid": 99, "parent_pid": 500})())
    assert 99 not in device.killed


def test_unclaimed_spawn_is_killed_and_never_resumed(tmp_path):
    device, owner = FakeDevice(), FakeOwner(fail=True)
    with pytest.raises(PermissionError):
        run_fake(tmp_path, device, owner)
    assert device.killed == [41] and not device.resumed and owner.closed


def test_job_assignment_failure_cleanup_terminates_process_handle():
    calls = []

    class Api:
        def WaitForSingleObject(self, _handle, _timeout):
            return 258 if not calls else 0

        def TerminateProcess(self, handle, code):
            calls.append(("terminate", handle, code))
            return True

        def CloseHandle(self, handle):
            calls.append(("close", handle))
            return True

    owner = trial.WindowsOwner.__new__(trial.WindowsOwner)
    owner.api = Api()
    owner.process = 10
    owner.job = 20
    owner.assigned = False
    owner._lock = threading.RLock()
    owner.close()
    assert calls == [("terminate", 10, 1), ("close", 20), ("close", 10)]


def test_stop_before_spawn_has_no_spawn_call(tmp_path):
    (tmp_path / "stop.request").write_text("stop", encoding="utf-8")
    device, owner = FakeDevice(), FakeOwner()
    with pytest.raises(RuntimeError, match="before spawn"):
        run_fake(tmp_path, device, owner)
    assert not device.spawned and device.resumed == [] and owner.closed


@pytest.fixture
def admission_case(tmp_path, monkeypatch):
    private = tmp_path / "private" / "frida-trials"
    run = private / "run-abc"
    exe = run / "client" / "Bin64" / "NewWorld.exe"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(bytes(range(64)))
    hook = tmp_path / "hook.js"
    hook.write_text("pinned", encoding="utf-8")
    metadata = run / "admission.json"
    metadata.write_text(json.dumps({"exe_sha256": trial.EXE_SHA256, "rva": trial.RVA,
                                    "expected_entry_hex": bytes(range(16)).hex()}), encoding="utf-8")
    monkeypatch.setattr(trial, "PRIVATE", private)
    monkeypatch.setattr(trial, "HOOK", hook)
    monkeypatch.setattr(trial, "file_offset_for_rva", lambda _data, _rva: 0)
    monkeypatch.setattr(trial, "sha256", lambda path: trial.HOOK_SHA256 if path == hook else trial.EXE_SHA256)
    return run, exe, metadata


def test_admission_rejects_wrong_path_hash_rva_or_bytes(admission_case, monkeypatch):
    run, exe, metadata = admission_case
    assert trial.admit(run, exe, metadata)["hex"] == bytes(range(16)).hex()
    other = run / "wrong.exe"
    other.write_bytes(exe.read_bytes())
    with pytest.raises(ValueError, match="path"):
        trial.admit(run, other, metadata)
    monkeypatch.setattr(trial, "sha256", lambda _path: "0" * 64)
    with pytest.raises(ValueError, match="hash"):
        trial.admit(run, exe, metadata)
    monkeypatch.setattr(trial, "sha256", lambda path: trial.HOOK_SHA256 if path == trial.HOOK else trial.EXE_SHA256)
    data = json.loads(metadata.read_text(encoding="utf-8"))
    data["rva"] += 1
    metadata.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="RVA"):
        trial.admit(run, exe, metadata)
    data["rva"] = trial.RVA
    data["expected_entry_hex"] = "ff" * 16
    metadata.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="entry bytes"):
        trial.admit(run, exe, metadata)


def test_context_gate_admission_is_opt_in_and_uses_only_fixed_image_sites(admission_case):
    run, exe, metadata = admission_case
    assert "context_gate_targets" not in trial.admit(run, exe, metadata)
    targets = trial.admit(run, exe, metadata, context_gate_observer=True)["context_gate_targets"]
    assert [(item["site"], item["rva"], item["adjustment"]) for item in targets] == list(trial.CONTEXT_GATE_TARGETS)
    assert all(item["bytes"] == list(range(16)) and item["hex"] == bytes(range(16)).hex()
               for item in targets)


def gate_payload(**updates):
    payload = {"type": "context-gate", "site": "self_identification", "phase": "entry",
               "port_tag": 1, **{key: False for key in trial.CONTEXT_GATE_FLAGS}}
    payload.update(updates)
    return payload


@pytest.mark.parametrize("updates", [
    {"address": "secret-sentinel"}, {"site": "arbitrary"}, {"site": []},
    {"phase": "elsewhere"}, {"port_tag": True}, {"port_tag": 0}, {"port_tag": 17},
    {"self_identified": 1}, {"client_sdk_present": "secret-sentinel"},
])
def test_context_gate_logger_rejects_non_allowlisted_metadata(updates):
    assert trial.context_gate_metadata(gate_payload(**updates)) is None


def test_context_gate_logger_accepts_boolean_and_unknown_values():
    payload = gate_payload(client_sdk_present=None, self_identified=True, phase="return")
    assert trial.context_gate_metadata(payload) == {key: value for key, value in payload.items()
                                                    if key != "type"}


@pytest.mark.parametrize("enabled,expected", [(False, 0), (True, 96)])
def test_context_gate_events_require_opt_in_and_respect_budget(tmp_path, enabled, expected):
    device, owner = FakeDevice(), FakeOwner()
    original_create = device.session.create_script

    def create(source, name):
        script = original_create(source, name)
        original_load = script.load

        def load():
            original_load()
            if name == "bounded-trial-observer":
                script.callback({"type": "send", "payload": gate_payload(address="secret-sentinel")}, None)
                for _ in range(110):
                    script.callback({"type": "send", "payload": gate_payload()}, None)
        script.load = load
        return script

    device.session.create_script = create
    events = []
    run_fake(tmp_path, device, owner, lambda event, **fields: events.append({"event": event, **fields}),
             context_gate_observer=enabled)
    assert len([item for item in events if item["event"] == "context_gate"]) == expected
    assert "secret-sentinel" not in json.dumps(events)
    assert owner.closed


@pytest.fixture
def reused_admission_case(tmp_path, monkeypatch):
    private = tmp_path / "private" / "frida-trials"
    source = private / "run-original"
    run = private / "run-fresh"
    exe = source / "client" / "Bin64" / "NewWorld.exe"
    exe.parent.mkdir(parents=True)
    run.mkdir(parents=True)
    exe.write_bytes(bytes(range(64)))
    (source / "stop.request").write_text("stop", encoding="utf-8")
    cleanup = source / "cleanup-reconciled.json"
    cleanup.write_text(json.dumps({"game_absent": True, "ports_closed": True,
                                   "firewall_rules_absent": True, "hosts_byte_exact": True}),
                       encoding="utf-8")
    metadata = run / "admission.json"
    metadata.write_text(json.dumps({"exe_sha256": trial.EXE_SHA256, "rva": trial.RVA,
                                    "expected_entry_hex": bytes(range(16)).hex(),
                                    "staged_copy_run": source.name}), encoding="utf-8")
    hook = tmp_path / "hook.js"
    hook.write_text("pinned", encoding="utf-8")
    monkeypatch.setattr(trial, "PRIVATE", private)
    monkeypatch.setattr(trial, "HOOK", hook)
    monkeypatch.setattr(trial, "file_offset_for_rva", lambda _data, _rva: 0)
    monkeypatch.setattr(trial, "sha256", lambda path: trial.HOOK_SHA256 if path == hook else trial.EXE_SHA256)
    return run, source, exe, metadata, cleanup


def test_reused_copy_admits_only_named_closed_physical_source(reused_admission_case):
    run, source, exe, metadata, _cleanup = reused_admission_case
    selected, owner = trial.selected_copy(run, exe, metadata)
    assert selected == exe and owner == source
    assert trial.admit(run, exe, metadata)["path"] == str(exe)
    outsider = run / "NewWorld.exe"
    outsider.write_bytes(exe.read_bytes())
    with pytest.raises(ValueError, match="path mismatch"):
        trial.admit(run, outsider, metadata)


def test_reused_copy_rejects_source_name_outside_private_runs(reused_admission_case):
    run, _source, exe, metadata, _cleanup = reused_admission_case
    contents = json.loads(metadata.read_text(encoding="utf-8"))
    contents["staged_copy_run"] = "../outside"
    metadata.write_text(json.dumps(contents), encoding="utf-8")
    with pytest.raises(ValueError, match="direct private run"):
        trial.admit(run, exe, metadata)


def test_reused_copy_rejects_live_or_unreconciled_source(reused_admission_case):
    run, source, exe, metadata, cleanup = reused_admission_case
    (source / "stop.request").unlink()
    with pytest.raises(ValueError, match="still live"):
        trial.admit(run, exe, metadata)
    (source / "stop.request").write_text("stop", encoding="utf-8")
    cleanup.write_text(json.dumps({"game_absent": False, "ports_closed": True,
                                   "firewall_rules_absent": True, "hosts_byte_exact": True}),
                       encoding="utf-8")
    with pytest.raises(ValueError, match="not reconciled"):
        trial.admit(run, exe, metadata)


def test_reused_copy_rejects_changed_executable_hash(reused_admission_case, monkeypatch):
    run, _source, exe, metadata, _cleanup = reused_admission_case
    monkeypatch.setattr(trial, "sha256", lambda path: trial.HOOK_SHA256 if path == trial.HOOK else "0" * 64)
    with pytest.raises(ValueError, match="hash mismatch"):
        trial.admit(run, exe, metadata)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows byte-range lock")
def test_copy_use_lock_rejects_concurrent_trial(reused_admission_case):
    _run, source, _exe, _metadata, _cleanup = reused_admission_case
    with trial.hold_copy_use(source):
        with pytest.raises(RuntimeError, match="already in use"):
            with trial.hold_copy_use(source):
                pass
