"""Synthetic PE controls only; these tests never import PyGhidra or read a client."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile

import pytest

spec = importlib.util.spec_from_file_location("ghidra_function_slice", Path(__file__).parents[1] / "scripts/ghidra_function_slice.py")
slice_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(slice_tool)
BASE = 0x140000000


@pytest.fixture
def slice_workspace():
    # The offline runner's pytest basetemp contains .scratch; production rejects
    # such database paths. Own and clean a separate non-dot synthetic workspace.
    with tempfile.TemporaryDirectory(prefix="nw-ghidra-slice-test-") as directory:
        yield Path(directory)


def synthetic_pe():
    data = bytearray(0xC00)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HH", data, 0x84, 0x8664, 4)
    struct.pack_into("<H", data, 0x94, 0xF0)
    struct.pack_into("<H", data, 0x98, 0x20B)
    struct.pack_into("<Q", data, 0xB0, BASE)
    struct.pack_into("<I", data, 0x104, 16)
    struct.pack_into("<II", data, 0x120, 0x2000, 36)
    for index, name in enumerate((b".text", b".pdata", b".xdata", b".rdata")):
        position = 0x188 + index * 40
        data[position:position + len(name)] = name
        struct.pack_into("<IIII", data, position + 8, 0x200, (index + 1) * 0x1000, 0x200, 0x400 + index * 0x200)
        struct.pack_into("<I", data, position + 36, 0x60000020 if index == 0 else 0x40000040)
    data[0x400:0x600] = b"\x90" * 0x200
    data[0x400:0x406] = b"\xB8\x2A\x00\x00\x00\xC3"
    for index, record in enumerate(((0x1000, 0x1006, 0x3000), (0x1010, 0x1014, 0x3010), (0x1020, 0x1026, 0x3020))):
        struct.pack_into("<III", data, 0x600 + index * 12, *record)
    data[0x800] = data[0x820] = 1
    data[0x810] = 0x21  # version 1 plus UNW_FLAG_CHAININFO
    struct.pack_into("<III", data, 0x814, 0x1000, 0x1006, 0x3000)
    return data


def test_split_function_keeps_chained_body_and_excludes_other_code():
    selected = slice_tool.Image(bytes(synthetic_pe())).select([BASE + 0x1000])
    assert selected == [{"entry": BASE + 0x1000, "ranges": [(BASE + 0x1000, BASE + 0x1006), (BASE + 0x1010, BASE + 0x1014)]}]


@pytest.mark.parametrize("entries", [[], [BASE + 0x1001], [BASE + 0x1010], [BASE + 0x1000] * 2, list(range(9))])
def test_no_guessed_body_or_unbounded_selection(entries):
    with pytest.raises(slice_tool.SliceError):
        slice_tool.Image(bytes(synthetic_pe())).select(entries)


def test_chained_unwind_cycle_rejected():
    data = synthetic_pe()
    struct.pack_into("<III", data, 0x814, 0x1010, 0x1014, 0x3010)
    with pytest.raises(slice_tool.SliceError, match="Cyclic"):
        slice_tool.Image(bytes(data)).select([BASE + 0x1000])


def test_overlapping_function_ownership_rejected():
    data = synthetic_pe()
    struct.pack_into("<III", data, 0x618, 0x1002, 0x1005, 0x3020)
    with pytest.raises(slice_tool.SliceError, match="overlap"):
        slice_tool.Image(bytes(data)).select([BASE + 0x1000, BASE + 0x1002])


def test_code_budget_rejected_before_backend(monkeypatch):
    monkeypatch.setattr(slice_tool, "MAX_CODE_BYTES", 5)
    with pytest.raises(slice_tool.SliceError, match="one MiB"):
        slice_tool.Image(bytes(synthetic_pe())).select([BASE + 0x1000])


@pytest.mark.parametrize("fault", ["file_extent", "bad_pdata_size", "nonexecutable", "wrong_machine", "unbacked_code"])
def test_malformed_or_noncode_ranges_rejected(fault):
    data = synthetic_pe()
    if fault == "file_extent":
        struct.pack_into("<I", data, 0x188 + 20, len(data))
    elif fault == "bad_pdata_size":
        struct.pack_into("<I", data, 0x124, 35)
    elif fault == "nonexecutable":
        struct.pack_into("<I", data, 0x188 + 36, 0x40000040)
    elif fault == "wrong_machine":
        struct.pack_into("<H", data, 0x84, 0x14C)
    else:
        struct.pack_into("<I", data, 0x604, 0x1300)
    with pytest.raises(slice_tool.SliceError):
        slice_tool.Image(bytes(data)).select([BASE + 0x1000])


def paths(tmp_path, monkeypatch):
    monkeypatch.setattr(slice_tool, "ROOT", tmp_path)
    image = tmp_path / "synthetic.exe"
    image.write_bytes(synthetic_pe())
    return image, tmp_path / ".scratch/query", tmp_path / "private/ghidra/query"


def test_bad_hash_refuses_backend_and_creates_no_destinations(slice_workspace, monkeypatch):
    image, output, project = paths(slice_workspace, monkeypatch)
    with pytest.raises(slice_tool.SliceError, match="hash mismatch"):
        slice_tool.run(image, "0" * 64, [BASE + 0x1000], output, project, 30,
                       backend=lambda *unused: pytest.fail("Backend started"))
    assert not output.exists() and not project.exists()


@pytest.mark.parametrize("fault", ["outside_output", "outside_project", "dot_database", "existing", "nested"])
def test_private_output_identity_guard(slice_workspace, monkeypatch, fault):
    image, output, project = paths(slice_workspace, monkeypatch)
    if fault == "outside_output":
        output = slice_workspace / "tracked"
    elif fault == "outside_project":
        project = slice_workspace / "database"
    elif fault == "dot_database":
        project = slice_workspace / "private/ghidra/.hidden/database"
    elif fault == "existing":
        output.mkdir(parents=True)
        (output / "keep").write_text("preserve", encoding="utf-8")
    else:
        output = project / "output"
    with pytest.raises(slice_tool.SliceError):
        slice_tool.run(image, slice_tool.sha256(image.read_bytes()), [BASE + 0x1000], output, project, 30,
                       backend=lambda *unused: pytest.fail("Backend started"))
    if fault == "existing":
        assert (output / "keep").read_text(encoding="utf-8") == "preserve"
    assert not project.exists()


def test_output_symlink_cannot_escape_private_root(slice_workspace, monkeypatch):
    image, output, project = paths(slice_workspace, monkeypatch)
    outside = slice_workspace / "outside"
    outside.mkdir()
    output.parent.mkdir()
    alias = output.parent / "alias"
    alias.symlink_to(outside, target_is_directory=True)
    with pytest.raises(slice_tool.SliceError, match="private root"):
        slice_tool.run(image, slice_tool.sha256(image.read_bytes()), [BASE + 0x1000], alias / "new", project, 30,
                       backend=lambda *unused: pytest.fail("Backend started"))
    assert not (outside / "new").exists() and not project.exists()


def test_failed_query_leaves_partial_receipt_without_success_claim(slice_workspace, monkeypatch):
    image, output, project = paths(slice_workspace, monkeypatch)

    def fail(*unused):
        raise RuntimeError("Backend failure")

    monkeypatch.setattr(slice_tool.subprocess, "check_output", lambda *a, **kw: "fixture\n")
    with pytest.raises(RuntimeError):
        slice_tool.run(image, slice_tool.sha256(image.read_bytes()), [BASE + 0x1000], output, project, 30, backend=fail)
    receipt = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "failed" and receipt["errorType"] == "RuntimeError"
    assert receipt["automaticAnalysis"] is False and receipt["clientExecuted"] is False
    assert image.read_bytes() == synthetic_pe()


def test_decompile_timeout_is_partial_not_success(slice_workspace, monkeypatch):
    image, output, project = paths(slice_workspace, monkeypatch)

    def partial(image, selected, output, project, timeout, results):
        results.append({"completed": False})
        return {"fixture": True}

    monkeypatch.setattr(slice_tool.subprocess, "check_output", lambda *a, **kw: "fixture\n")
    receipt = slice_tool.run(image, slice_tool.sha256(image.read_bytes()), [BASE + 0x1000], output, project, 1, backend=partial)
    assert receipt["status"] == "partial" and receipt["sourceStable"] is True


def test_image_drift_rejects_completed_backend(slice_workspace, monkeypatch):
    image, output, project = paths(slice_workspace, monkeypatch)

    def change_source(parsed, selected, output, project, timeout, results):
        results.append({"completed": True})
        image.write_bytes(b"changed")
        return {"fixture": True}

    monkeypatch.setattr(slice_tool.subprocess, "check_output", lambda *a, **kw: "fixture\n")
    with pytest.raises(slice_tool.SliceError, match="changed during"):
        slice_tool.run(image, slice_tool.sha256(image.read_bytes()), [BASE + 0x1000], output, project, 30, backend=change_source)
    assert json.loads((output / "receipt.json").read_text(encoding="utf-8"))["status"] == "failed"
