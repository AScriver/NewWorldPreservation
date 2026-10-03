"""Preflight must report uncertain/stale inputs without touching private or live resources."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import project_preflight as preflight


@pytest.fixture
def workspace(tmp_path):
    root = tmp_path / "workspace"
    for name in ("scripts", "tests/fixtures", "docs", "research/evidence"):
        (root / name).mkdir(parents=True)
    (root / "scripts/control.py").write_text("original synthetic control\n")
    (root / "docs/EVIDENCE_LEDGER.md").write_text("| K01 | known claim | source-supported | evidence |\n")
    (root / "docs/ROADMAP.md").write_text("| M1-00 | bounded task |\n")
    fixture = root / "tests/fixtures/control.json"
    fixture.write_text('{"synthetic": true}\n')
    index = {"boundaries": [{"id": "control", "claimIds": ["K01"], "roadmapTasks": ["M1-00"],
                             "docs": ["docs/ROADMAP.md"], "scripts": ["scripts/control.py"], "tests": [], "evidence": []}],
             "fixtures": [{"path": "tests/fixtures/control.json", "classification": "synthetic", "sha256": preflight.file_hash(fixture)}],
             "receipts": []}
    (root / preflight.INDEX).write_text(json.dumps(index))
    return root


def receipt(root, value):
    (root / "research/evidence/control.json").write_text(json.dumps(value))
    return "research/evidence/control.json"


def test_matching_receipt_does_not_upgrade_historical_gameplay(workspace):
    name = receipt(workspace, {"status": "passed", "sources_sha256": {
        "scripts/control.py": preflight.file_hash(workspace / "scripts/control.py")}})
    result = preflight.receipt_report(workspace, name)
    assert result["freshness"] == "local-bindings-match"
    assert "real client unverified" in result["scope"]


def test_changed_and_missing_bindings_are_stale_despite_green_status(workspace):
    name = receipt(workspace, {"status": "passed", "tested_source_sha256": {
        "scripts/control.py": "0" * 64, "tests/missing.py": "1" * 64}})
    result = preflight.receipt_report(workspace, name)
    assert result["freshness"] == "stale-local-inputs"
    assert result["recordedStatus"] == "passed"
    assert result["mismatches"] == ["scripts/control.py"]
    assert result["missing"] == ["tests/missing.py"]


def test_mixed_private_external_and_traversal_hashes_are_never_opened(workspace, monkeypatch):
    name = receipt(workspace, {"source_and_private_sha256": {
        "private/raw.json": "0" * 64, ".scratch/capture.txt": "0" * 64,
        "C:\\game\\NewWorld.exe": "0" * 64, "\\\\server\\share\\secret": "0" * 64,
        "scripts/../../secret.txt": "0" * 64, "/secret.txt": "0" * 64,
        "research/upstream/first-light/raw.txt": "0" * 64}})
    monkeypatch.setattr(preflight, "file_hash", lambda _: pytest.fail("out-of-scope file opened"))
    result = preflight.receipt_report(workspace, name)
    assert result["uncheckedBindings"] == 7
    assert result["checkedBindings"] == 0
    assert result["freshness"] == "unknown"


def test_public_symlink_to_private_is_rejected(workspace):
    private = workspace / "private"
    private.mkdir()
    target = private / "capture.txt"
    target.write_text("synthetic private sentinel")
    link = workspace / "scripts/linked.txt"
    try:
        link.symlink_to(target)
    except OSError:
        # Windows may not permit creating symlinks; execute equivalent resolve-path control.
        original_resolve = Path.resolve
        from unittest.mock import patch
        def fake_resolve(path, *arguments, **keywords):
            return target if path == link else original_resolve(path, *arguments, **keywords)
        with patch.object(Path, "resolve", fake_resolve):
            assert preflight.public_path(workspace, "scripts/linked.txt") is None
    else:
        assert preflight.public_path(workspace, "scripts/linked.txt") is None


def test_receipt_without_identity_remains_unknown(workspace):
    name = receipt(workspace, {"status": "passed", "tests": 999})
    assert preflight.receipt_report(workspace, name)["freshness"] == "unknown"


def test_malformed_public_binding_cannot_hide_behind_one_matching_hash(workspace):
    name = receipt(workspace, {"sourceSha256": {"scripts/control.py": preflight.file_hash(workspace / "scripts/control.py"),
                                              "scripts/missing.py": "not-a-hash"}})
    result = preflight.receipt_report(workspace, name)
    assert result["freshness"] == "unknown"
    assert result["malformedBindings"] == ["scripts/missing.py"]
    assert result["malformedCount"] == 1


def test_malformed_or_incomplete_receipt_is_unknown(workspace):
    name = receipt(workspace, {"runtime": {"packages": []}})
    result = preflight.receipt_report(workspace, name, runtime={"packages": {}})
    assert result["freshness"] == "unknown"
    assert "malformed" in result["reason"]


def test_list_style_and_nested_legacy_bindings_are_checked(workspace):
    name = receipt(workspace, {"sources": [{"path": "scripts/control.py", "sha256": "0" * 64}],
                               "tests": {"sourceSha256": {"scripts/control.py": "0" * 64}}})
    result = preflight.receipt_report(workspace, name)
    assert result["checkedBindings"] == 2
    assert result["mismatchCount"] == 1


def test_root_document_binding_is_checked_without_directory_separator(workspace):
    (workspace / "README.md").write_text("new navigation\n")
    name = receipt(workspace, {"sourceSha256": {"README.md": "0" * 64,
                                               "scripts/control.py": preflight.file_hash(workspace / "scripts/control.py")}})
    result = preflight.receipt_report(workspace, name)
    assert result["freshness"] == "stale-local-inputs"
    assert result["checkedBindings"] == 2
    assert result["mismatches"] == ["README.md"]


def test_runtime_lock_or_package_drift_is_stale(workspace):
    name = receipt(workspace, {"runtime": {"python": "3.11.9", "lockSha256": "0" * 64,
                                          "packages": {"pytest": "9.1.1"}}})
    current = {"python": "3.12.0", "lockSha256": "1" * 64, "packages": {"pytest": {"installed": "9.2.0"}}}
    result = preflight.receipt_report(workspace, name, runtime=current)
    assert result["freshness"] == "stale-local-inputs"
    assert set(result["mismatches"]) == {"runtime:python", "runtime:package:pytest", "requirements-dev.lock"}


@pytest.mark.parametrize("fault", ["malformed", "duplicate", "missing-hash", "bad-hash"])
def test_dependency_lock_cannot_ignore_malformed_or_unhashed_requirements(workspace, monkeypatch, fault):
    content = "".join(f"{name}==1.0 \\\n+    --hash=sha256:{'0' * 64}\n" for name in ("pytest", "pyopenssl", "cryptography"))
    if fault == "malformed":
        content += "broken-dependency >= 999\n"
    elif fault == "duplicate":
        content += "pytest==1.0\n"
    elif fault == "missing-hash":
        content += "extra==1.0\n"
    else:
        content += "extra==1.0 \\\n+    --hash=sha256:not-a-hash\n"
    (workspace / "requirements-dev.lock").write_text(content)
    monkeypatch.setattr(preflight.metadata, "version", lambda _name: "1.0")
    monkeypatch.setattr(preflight.sys, "prefix", str(workspace / ".venv"))
    result = preflight.environment_report(workspace)
    assert not result["ready"]
    assert "dependency lock unavailable or malformed" in result["problems"]


def test_fixture_drift_new_fixture_unknown_claim_and_task_are_actionable(workspace):
    assert preflight.index_report(workspace)["ready"]
    (workspace / "tests/fixtures/control.json").write_text('{"changed": true}\n')
    (workspace / "tests/fixtures/new.json").write_text('{}\n')
    (workspace / "docs/EVIDENCE_LEDGER.md").write_text("no material claims\n")
    (workspace / "docs/ROADMAP.md").write_text("| M1-99 | new task |\n")
    result = preflight.index_report(workspace)
    assert not result["ready"]
    assert any("fixture hash mismatch" in error for error in result["errors"])
    assert any("fixture not indexed" in error for error in result["errors"])
    assert "unknown claim: K01" in result["errors"]
    assert "roadmap task not indexed: M1-99" in result["errors"]


def test_git_timeout_is_unavailable_instead_of_clean(workspace, monkeypatch):
    def timeout(*arguments, **keywords):
        raise subprocess.TimeoutExpired("git", 20)
    monkeypatch.setattr(preflight.subprocess, "run", timeout)
    assert preflight.git_state(workspace) == {"status": "unavailable"}


def test_git_rename_and_untracked_spaces_keep_exact_path_identity(workspace, monkeypatch):
    output = "R  scripts/new name.py\0scripts/old name.py\0?? tests/new test.py\0"
    monkeypatch.setattr(preflight.subprocess, "run", lambda *a, **kw: subprocess.CompletedProcess(a, 0, stdout=output))
    monkeypatch.setattr(preflight, "git_read", lambda _root, *a: "head" if a[0] == "rev-parse" else "main")
    state = preflight.git_state(workspace)
    assert state["totalChanges"] == 2
    assert state["changes"][0]["originalPath"] == "scripts/old name.py"
    assert state["changes"][1]["path"] == "tests/new test.py"


def test_collect_and_hash_checks_do_not_write_files(workspace, monkeypatch):
    monkeypatch.setattr(preflight, "environment_report", lambda _root: {"ready": True, "packages": {}, "python": "3.11.9"})
    monkeypatch.setattr(preflight, "git_state", lambda _root: {"status": "observed", "changes": []})
    monkeypatch.setattr(preflight, "upstream_report", lambda _root: [{"name": "firstLight", "status": "missing"}])
    def refused(*arguments, **keywords):
        pytest.fail("preflight attempted a filesystem mutation")
    for method in ("write_text", "write_bytes", "mkdir", "unlink", "rename"):
        monkeypatch.setattr(Path, method, refused)
    result = preflight.collect(workspace, powershell={"ready": True})
    assert result["workspaceReady"]
    assert not result["newWorldClientTested"]
    assert result["upstreams"][0]["status"] == "missing"


def test_repo_index_covers_current_public_fixtures_and_roadmap():
    result = preflight.index_report(Path(__file__).resolve().parents[1])
    assert result["ready"], result["errors"]
