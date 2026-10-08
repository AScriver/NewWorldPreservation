"""Failure controls for the offline runner's selection, receipts, and lifecycle."""
from __future__ import annotations

import json
import io
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_offline as runner


@pytest.mark.parametrize("omit_test_module", [False, True])
def test_upstream_allows_pinned_helper_but_rejects_unexpected_empty_module(tmp_path, monkeypatch, omit_test_module):
    import validate_first_light as reference_runner
    reference = tmp_path / "research/upstream/reference"
    reference.mkdir(parents=True)
    (tmp_path / "research/upstreams.json").write_text(json.dumps({"firstLight": {"directory": "research/upstream/reference"}}))
    files = ("server/test_loopback.py", "server/test_wire.py")
    calls = []
    monkeypatch.setattr(reference_runner, "TEST_FILES", files)
    monkeypatch.setattr(reference_runner, "EXPECTED_TESTS", 2)
    monkeypatch.setattr(reference_runner, "EXPECTED_SKIPS", {"expected": "deliberate"})
    monkeypatch.setattr(reference_runner, "verify_reference", lambda *a: calls.append("verified") or {"commit": "pinned"})
    monkeypatch.setattr(reference_runner, "verify_environment", lambda *a: {})
    monkeypatch.setattr(reference_runner, "probe_dtls_context", lambda *a: {"constructed": True})
    monkeypatch.setattr(reference_runner, "parse_junit", lambda *a: {"total": 2, "passed": 1, "skipped": 1,
                                                                  "failed": 0, "errors": 0, "unexpectedSkips": []})
    def command(arguments, cwd, log, timeout, **keywords):
        module = "server/test_loopback.py" if omit_test_module else "server/test_wire.py"
        log.write_text(f"{module}::test_one\n{module}::test_two\n")
    monkeypatch.setattr(runner, "run_command", command)
    manifest = {"upstream": {"expectedTests": 2, "expectedSkips": 1, "zeroCaseModules": ["server/test_loopback.py"]}}
    if omit_test_module:
        with pytest.raises(ValueError, match="unexpected empty"):
            runner.upstream_validation(tmp_path, tmp_path, manifest)
    else:
        result = runner.upstream_validation(tmp_path, tmp_path, manifest)
        assert result["zeroCaseModules"] == ["server/test_loopback.py"]
        assert calls == ["verified", "verified"]


def workspace_tree(tmp_path: Path) -> tuple[Path, dict]:
    manifest = runner.load_manifest()
    for group in manifest["groups"].values():
        for name in group:
            target = tmp_path / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# reviewed synthetic test\n", encoding="utf-8")
    return tmp_path, manifest


def runner_inputs(root: Path, manifest: dict) -> None:
    for name, content in {
        "scripts/offline-test-profiles.json": json.dumps(manifest),
        "research/agent-evidence-index.json": json.dumps({"receipts": ["research/evidence/control.json"],
                                                       "boundaries": [{"evidence": [{"path": "research/evidence/control.json"}]}]}),
        "research/evidence/control.json": "{}",
        "scripts/validate_offline.py": "synthetic",
        "scripts/Test-Offline.ps1": "synthetic",
        "scripts/project_preflight.py": "synthetic",
        "requirements-dev.lock": "synthetic",
        "research/upstreams.json": "{}",
        "docs/ROADMAP.md": "synthetic",
        "docs/EVIDENCE_LEDGER.md": "synthetic",
    }.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def test_full_selection_rejects_missing_and_unreviewed_modules(tmp_path):
    root, manifest = workspace_tree(tmp_path)
    chosen = runner.selection(root, manifest, "workspace")
    assert len(chosen["python"]) == 51
    assert len(chosen["powershell"]) == 5
    assert chosen["cli"] is True
    (root / "tests/test_queue_contract_probe.py").unlink()
    with pytest.raises(ValueError, match="Missing selected test"):
        runner.selection(root, manifest, "workspace")
    (root / "tests/test_queue_contract_probe.py").write_text("# restored\n")
    (root / "tests/test_unreviewed.py").write_text("# new\n")
    with pytest.raises(ValueError, match="Unreviewed test"):
        runner.selection(root, manifest, "workspace")
    assert "tests/test_windows_rep_readonly_probe.py" in chosen["python"]
    assert runner.selection(root, manifest, "rep-readonly")["python"] == manifest["groups"]["rep-readonly"]
    assert runner.selection(root, manifest, "frida-trial")["python"] == ["tests/test_frida_client_trial.py"]


def test_manifest_rejects_baseline_omission(tmp_path):
    _, manifest = workspace_tree(tmp_path)
    manifest["groups"]["protocol-loopback"].pop()
    path = tmp_path / "offline-test-profiles.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="Reviewed group inventory"):
        runner.load_manifest(path)


def test_same_size_rep_reclassification_cannot_omit_baseline(tmp_path):
    _, manifest = workspace_tree(tmp_path)
    baseline = manifest["groups"]["fixtures-static"][0]
    rep = manifest["groups"]["rep-readonly"][0]
    manifest["groups"]["fixtures-static"][0] = rep
    manifest["groups"]["rep-readonly"][0] = baseline
    path = tmp_path / "offline-test-profiles.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="REP readonly test was reclassified"):
        runner.load_manifest(path)


def test_public_input_guard_rejects_traversal_and_symlink(tmp_path):
    root, manifest = workspace_tree(tmp_path)
    runner_inputs(root, manifest)
    chosen = runner.selection(root, manifest, "tooling")
    assert "research/evidence/control.json" in runner.input_files(root, chosen)
    index = root / "research/agent-evidence-index.json"
    for unsafe in ("../private.json", "research/evidence/../../private.json"):
        index.write_text(json.dumps({"receipts": [unsafe], "boundaries": []}))
        with pytest.raises(ValueError, match="unsafe receipt path"):
            runner.input_files(root, chosen)
    external = tmp_path.parent / "external-receipt.json"
    external.write_text("{}")
    alias = root / "research/evidence/alias.json"
    alias.symlink_to(external)
    index.write_text(json.dumps({"receipts": ["research/evidence/alias.json"], "boundaries": []}))
    with pytest.raises(ValueError, match="unsafe receipt path"):
        runner.input_files(root, chosen)


def test_subprocess_environment_discards_inherited_pytest_addopts(monkeypatch):
    monkeypatch.setenv("PYTEST_ADDOPTS", "--ignore=tests/test_offline_runner.py")
    environment = runner.subprocess_env()
    assert "PYTEST_ADDOPTS" not in environment
    assert environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"


@pytest.mark.parametrize("fault", ["zero", "changed", "missing_module", "skip", "failure", "timeout", "exit"])
def test_pytest_gate_rejects_bad_collection_or_execution(tmp_path, monkeypatch, fault):
    root, _ = workspace_tree(tmp_path)
    run = tmp_path / "run"
    run.mkdir()

    def fake_command(arguments, cwd, log, timeout, **kwargs):
        if fault == "timeout":
            raise subprocess.TimeoutExpired(arguments, timeout)
        if fault == "exit":
            raise RuntimeError("Child exited 1")
        if "--collect-only" in arguments:
            selected = "tests/test_other.py::test_one\n" if fault == "missing_module" else "tests/test_a.py::test_one\n"
            log.write_text("" if fault == "zero" else selected, encoding="utf-8")
        else:
            cases = [] if fault == "changed" else [ET.Element("testcase", classname="a", name="test_one")]
            if cases and fault in ("skip", "failure"):
                ET.SubElement(cases[0], "skipped" if fault == "skip" else "failure")
            suite = ET.Element("testsuite")
            suite.extend(cases)
            ET.ElementTree(suite).write(run / "workspace-junit.xml")
        return 0

    monkeypatch.setattr(runner, "run_command", fake_command)
    with pytest.raises((ValueError, RuntimeError, subprocess.TimeoutExpired)):
        runner.run_pytest(root, ["tests/test_a.py"], run)


def test_independent_receipts_and_source_drift_fail_closed(tmp_path, monkeypatch):
    root, manifest = workspace_tree(tmp_path)
    runner_inputs(root, manifest)
    source = root / "scripts/validate_offline.py"
    source.write_text("original", encoding="utf-8")
    monkeypatch.setattr(runner, "environment_report", lambda _: {"ready": True})
    monkeypatch.setattr(runner, "git_state", lambda _: {"status": "synthetic"})
    def passing_test(root_arg, files_arg, run_arg):
        assert json.loads((run_arg / "receipt.json").read_text())["status"] == "running"
        return {"collected": 1, "executed": 1}

    monkeypatch.setattr(runner, "run_pytest", passing_test)
    code, first = runner.validate(root, "tooling")
    assert code == 0
    assert json.loads(first.read_text())["status"] == "passed"

    def changing_test(*args, **kwargs):
        source.write_text("changed", encoding="utf-8")
        return {"collected": 1, "executed": 1}

    monkeypatch.setattr(runner, "run_pytest", changing_test)
    code, second = runner.validate(root, "tooling")
    assert code == 1 and second != first
    failed = json.loads(second.read_text())
    assert failed["status"] == "failed"
    assert failed["errorType"] == "InputChangedDuringRun"
    assert "scripts/validate_offline.py" in failed["changedInputs"]
    assert json.loads(first.read_text())["status"] == "passed"

    receipt_input = root / "research/evidence/control.json"

    def changing_evidence(*args, **kwargs):
        receipt_input.write_text('{"changed":true}', encoding="utf-8")
        return {"collected": 1, "executed": 1}

    monkeypatch.setattr(runner, "run_pytest", changing_evidence)
    code, third = runner.validate(root, "tooling")
    assert code == 1
    assert "research/evidence/control.json" in json.loads(third.read_text())["changedInputs"]


def test_failed_child_still_writes_fresh_failed_receipt(tmp_path, monkeypatch):
    root, manifest = workspace_tree(tmp_path)
    runner_inputs(root, manifest)
    monkeypatch.setattr(runner, "environment_report", lambda _: {"ready": True})
    monkeypatch.setattr(runner, "git_state", lambda _: {"status": "synthetic"})
    monkeypatch.setattr(runner, "run_pytest", lambda *args, **kwargs: (_ for _ in ()).throw(subprocess.TimeoutExpired("pytest", 1)))
    code, receipt = runner.validate(root, "tooling")
    assert code == 1
    assert json.loads(receipt.read_text())["errorType"] == "TimeoutExpired"
    assert (receipt.parent / "error.txt").is_file()


def test_cli_failure_terminates_only_owned_child(tmp_path, monkeypatch):
    class FakeChild:
        def __init__(self):
            self.stdout = io.StringIO('{"bind":"unexpected","port":42}\n')
            self.terminated = False

        def poll(self):
            return None if not self.terminated else 1

        def terminate(self):
            self.terminated = True

        def wait(self, timeout):
            return 1

    child = FakeChild()
    monkeypatch.setattr(runner, "run_command", lambda *args, **kwargs: 0)
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: child)
    with pytest.raises(ValueError, match="listener identity"):
        runner.cli_lifecycle(tmp_path, tmp_path)
    assert child.terminated
    assert child.stdout.closed
