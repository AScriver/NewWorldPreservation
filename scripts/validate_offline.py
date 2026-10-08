"""Explicit, isolated offline validation of reviewed workspace and opt-in reference tests."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import queue
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import xml.etree.ElementTree as ET

from project_preflight import environment_report, file_hash, git_state, public_path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "scripts/offline-test-profiles.json"
RUN_ROOT = ROOT / ".scratch/offline-validation"
PS_VALIDATOR = Path(r"C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1")
PYTHON_TIMEOUT = 180
PS_TIMEOUT = 120
CLI_TIMEOUT = 20
REVIEWED_GROUP_SIZES = {"fixtures-static": 25, "protocol-loopback": 12, "windows-native": 4,
                        "tooling": 9, "powershell": 5, "rep-readonly": 1, "frida-trial": 1}
WORKSPACE_MEMBERS = ["fixtures-static", "protocol-loopback", "windows-native",
                     "tooling", "powershell", "rep-readonly", "frida-trial", "cli-lifecycle"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_manifest(path: Path = MANIFEST) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("version") != 1:
        raise ValueError("Unsupported offline profile manifest version")
    groups = manifest["groups"]
    if {name: len(files) for name, files in groups.items()} != REVIEWED_GROUP_SIZES:
        raise ValueError("Reviewed group inventory differs from expected offline baseline")
    if manifest["profiles"].get("workspace") != WORKSPACE_MEMBERS:
        raise ValueError("Workspace profile omits or changes reviewed controls")
    if manifest["profiles"].get("all") != [*WORKSPACE_MEMBERS, "upstream"]:
        raise ValueError("All profile omits or changes reviewed controls")
    for name, files in groups.items():
        if not isinstance(files, list) or not files or len(files) != len(set(files)):
            raise ValueError(f"Invalid group: {name}")
        for file in files:
            if (not isinstance(file, str) or not file.startswith("tests/test_")
                    or not file.endswith((".py", ".ps1")) or ".." in Path(file).parts):
                raise ValueError(f"Unsafe test selection: {file}")
    for name, members in manifest["profiles"].items():
        if not isinstance(members, list) or not members or any(member not in groups and member not in ("cli-lifecycle", "upstream") for member in members):
            raise ValueError(f"Invalid profile: {name}")
    reviewed = [file for files in groups.values() for file in files]
    if len(reviewed) != len(set(reviewed)):
        raise ValueError("Test module appears in multiple groups")
    if groups["rep-readonly"] != ["tests/test_windows_rep_readonly_probe.py"]:
        raise ValueError("REP readonly test was reclassified")
    if manifest["upstream"].get("zeroCaseModules") != ["server/test_loopback.py"]:
        raise ValueError("Pinned upstream helper coverage exception changed")
    return manifest


def selection(root: Path, manifest: dict, profile: str) -> dict:
    if profile not in manifest["profiles"]:
        raise ValueError(f"Unknown profile: {profile}")
    members = manifest["profiles"][profile]
    files = [file for member in members if member in manifest["groups"] for file in manifest["groups"][member]]
    if len(files) != len(set(files)):
        raise ValueError("Duplicate selected test")
    missing = [file for file in files if not (root / file).is_file()]
    if missing:
        raise ValueError("Missing selected test: " + ", ".join(missing))
    if profile in ("workspace", "all"):
        required = {file for group in manifest["groups"].values() for file in group}
        if set(files) != required:
            raise ValueError("Full workspace profile omits a reviewed baseline test")
        discovered = {path.relative_to(root).as_posix() for suffix in ("*.py", "*.ps1")
                      for path in (root / "tests").glob("test_" + suffix)}
        unexpected = discovered - required
        if unexpected:
            raise ValueError("Unreviewed test module(s): " + ", ".join(sorted(unexpected)))
    return {"python": [file for file in files if file.endswith(".py")],
            "powershell": [file for file in files if file.endswith(".ps1")],
            "cli": "cli-lifecycle" in members, "upstream": "upstream" in members}


def input_files(root: Path, chosen: dict) -> list[str]:
    names = {"scripts/offline-test-profiles.json", "scripts/validate_offline.py",
             "scripts/Test-Offline.ps1", "scripts/project_preflight.py", "requirements-dev.lock",
             "research/upstreams.json", "research/agent-evidence-index.json",
             "docs/ROADMAP.md", "docs/EVIDENCE_LEDGER.md",
             *chosen["python"], *chosen["powershell"]}
    index = json.loads((root / "research/agent-evidence-index.json").read_text(encoding="utf-8"))
    evidence = list(index["receipts"])
    evidence.extend(item["path"] for boundary in index["boundaries"] for item in boundary["evidence"])
    for name in evidence:
        if (not isinstance(name, str) or not name.startswith("research/evidence/")
                or public_path(root, name) is None):
            raise ValueError("Evidence index contains an unsafe receipt path")
        names.add(name)
    # Bound the result to source and public redacted fixtures that selected tests can read.
    names.update(path.relative_to(root).as_posix() for path in (root / "scripts").glob("*.py")
                 if path.name not in {"windows_rep_readonly_probe.py", "validate_first_light.py"})
    names.update(path.relative_to(root).as_posix() for path in (root / "scripts").glob("*.ps1"))
    names.update(path.relative_to(root).as_posix() for path in (root / "scripts").glob("*.psm1"))
    names.update(path.relative_to(root).as_posix() for path in (root / "scripts").glob("*.js"))
    names.update(path.relative_to(root).as_posix() for path in (root / "tests/fixtures").rglob("*.json"))
    if chosen["cli"]:
        names.add("scripts/connectivity_probe.py")
    if chosen["upstream"]:
        names.add("scripts/validate_first_light.py")
    if "tests/test_windows_rep_readonly_probe.py" in chosen["python"]:
        names.add("scripts/windows_rep_readonly_probe.py")
    for name in names:
        candidate = public_path(root, name)
        if candidate is None or not candidate.is_file():
            raise ValueError(f"Missing or unsafe public input: {name}")
    return sorted(names)


def snapshot(root: Path, names: list[str]) -> dict[str, str]:
    return {name: file_hash(root / name) for name in names}


def subprocess_env() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
                       PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    return environment


def run_command(arguments: list[str], cwd: Path, log: Path, timeout: int, *, env: dict | None = None) -> int:
    with log.open("w", encoding="utf-8") as output:
        result = subprocess.run(arguments, cwd=cwd, env=env, stdout=output,
                                stderr=subprocess.STDOUT, timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError(f"Child exited {result.returncode}; see {log.name}")
    return result.returncode


def junit_counts(path: Path) -> dict[str, int]:
    cases = list(ET.parse(path).getroot().iter("testcase"))
    return {"total": len(cases),
            "failed": sum(case.find("failure") is not None for case in cases),
            "errors": sum(case.find("error") is not None for case in cases),
            "skipped": sum(case.find("skipped") is not None for case in cases)}


def run_pytest(root: Path, files: list[str], run: Path, *, name: str = "workspace", timeout: int = PYTHON_TIMEOUT) -> dict:
    if not files:
        return {"selectedFiles": 0, "collected": 0, "executed": 0}
    base = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
            "--basetemp", str(run / (name + "-temp"))]
    collect_log = run / (name + "-collect.log")
    run_command([*base, "--collect-only", *files], root, collect_log, timeout, env=subprocess_env())
    nodeids = [line.strip() for line in collect_log.read_text(encoding="utf-8", errors="replace").splitlines()
               if line.strip().startswith("tests/") and "::" in line]
    collected_files = {nodeid.split("::", 1)[0].replace("\\", "/") for nodeid in nodeids}
    if not nodeids or len(nodeids) != len(set(nodeids)) or collected_files != set(files):
        raise ValueError(f"{name}: zero, duplicate, or missing-module collection; see {collect_log.name}")
    junit = run / (name + "-junit.xml")
    run_command([*base, "-ra", "--junitxml", str(junit), *files], root,
                run / (name + "-pytest.log"), timeout, env=subprocess_env())
    result = junit_counts(junit)
    if result["total"] != len(nodeids) or any(result[key] for key in ("failed", "errors", "skipped")):
        raise ValueError(f"{name}: collection/execution count or outcome mismatch")
    return {"selectedFiles": len(files), "collected": len(nodeids), "executed": result["total"],
            "failed": 0, "errors": 0, "skipped": 0}


def run_powershell(root: Path, files: list[str], run: Path) -> list[dict]:
    results = []
    for number, file in enumerate(files, 1):
        # The validator checks parser and automatic-variable assignments before execution.
        arguments = ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(PS_VALIDATOR),
                     "-Path", str(root / file), "-Execute"]
        run_command(arguments, root, run / f"powershell-{number}.log", PS_TIMEOUT)
        results.append({"file": file, "status": "passed", "validator": "parser-and-automatic-variable"})
    return results


def _first_line(stream, messages: queue.Queue) -> None:
    try:
        messages.put(stream.readline())
    except Exception as error:
        messages.put(error)


def cli_lifecycle(root: Path, run: Path) -> dict:
    probe = root / "scripts/connectivity_probe.py"
    certs = run / "certificates"
    run_command([sys.executable, str(probe), "certificates", "--directory", str(certs)],
                root, run / "cli-certificates.log", CLI_TIMEOUT, env=subprocess_env())
    with (run / "cli-stderr.log").open("w", encoding="utf-8") as errors:
        process = subprocess.Popen([sys.executable, str(probe), "serve", "--certificates", str(certs),
                                    "--log", str(run / "cli-events.jsonl"), "--bind", "127.0.0.1",
                                    "--port", "0", "--duration", "2"], cwd=root, env=subprocess_env(),
                                   stdout=subprocess.PIPE, stderr=errors, text=True, encoding="utf-8")
        try:
            messages: queue.Queue = queue.Queue(maxsize=1)
            threading.Thread(target=_first_line, args=(process.stdout, messages), daemon=True).start()
            line = messages.get(timeout=CLI_TIMEOUT)
            if isinstance(line, Exception) or not line:
                raise ValueError("CLI did not announce a listener")
            ready = json.loads(line)
            if ready.get("bind") != "127.0.0.1" or not isinstance(ready.get("port"), int):
                raise ValueError("CLI listener identity differs from loopback ephemeral request")
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations(cafile=str(certs / "ca.pem"))
            with socket.create_connection((ready["bind"], ready["port"]), timeout=3) as raw:
                with context.wrap_socket(raw, server_hostname="localhost") as connection:
                    connection.settimeout(3)
                    connection.sendall(b"GET /__probe/health HTTP/1.1\r\nHost: localhost\r\n\r\n")
                    response = connection.recv(4096)
            if not response.startswith(b"HTTP/1.1 200"):
                raise ValueError("CLI health status was not 200")
            if process.wait(timeout=CLI_TIMEOUT) != 0:
                raise ValueError("CLI child did not exit cleanly")
            events = [json.loads(line) for line in (run / "cli-events.jsonl").read_text(encoding="utf-8").splitlines()]
            if not events or events[-1].get("state") != "PROBE_STOPPED":
                raise ValueError("CLI stop event missing")
            if (run / "cli-stderr.log").read_text(encoding="utf-8"):
                raise ValueError("CLI stderr was not empty")
            with socket.socket() as closed:
                closed.settimeout(1)
                if closed.connect_ex((ready["bind"], ready["port"])) == 0:
                    raise ValueError("CLI listener remained open")
            return {"status": "passed", "httpStatus": 200, "listenerClosed": True,
                    "childExitCode": 0, "bind": "127.0.0.1", "port": ready["port"]}
        finally:
            if process.poll() is None:
                process.terminate()  # This process is owned by this run.
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            process.stdout.close()


def upstream_validation(root: Path, run: Path, manifest: dict) -> dict:
    # Import only pure helpers after pin, fixture, and environment checks.
    from validate_first_light import (TEST_FILES, EXPECTED_TESTS, EXPECTED_SKIPS,
                                      probe_dtls_context, verify_reference, verify_environment, parse_junit)
    pin = json.loads((root / "research/upstreams.json").read_text(encoding="utf-8"))["firstLight"]
    reference = (root / pin["directory"]).resolve()
    if not reference.is_relative_to((root / "research/upstream").resolve()):
        raise ValueError("Reference path escapes ignored upstream directory")
    identity = verify_reference(reference, pin)
    verify_environment(root / "requirements-dev.lock")
    if EXPECTED_TESTS != manifest["upstream"]["expectedTests"] or len(EXPECTED_SKIPS) != manifest["upstream"]["expectedSkips"]:
        raise ValueError("Upstream expected coverage differs from profile")
    capability = probe_dtls_context(reference, run)
    files = list(TEST_FILES)
    base = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
            "--basetemp", str(run / "upstream-temp")]
    collect = run / "upstream-collect.log"
    run_command([*base, "--collect-only", *files], reference, collect, PYTHON_TIMEOUT, env=subprocess_env())
    collected = [line for line in collect.read_text(encoding="utf-8", errors="replace").splitlines()
                 if line.strip().startswith("server/") and "::" in line]
    if len(collected) != EXPECTED_TESTS or len(set(collected)) != EXPECTED_TESTS:
        raise ValueError("Upstream collection differs from pinned expected case count")
    collected_modules = {nodeid.strip().split("::", 1)[0].replace("\\", "/") for nodeid in collected}
    zero_case_modules = sorted(set(files) - collected_modules)
    if (zero_case_modules != sorted(manifest["upstream"]["zeroCaseModules"])
            or collected_modules - set(files)):
        raise ValueError("Upstream collection has unexpected empty selected modules")
    junit = run / "upstream-junit.xml"
    run_command([*base, "-ra", "--junitxml", str(junit), *files], reference,
                run / "upstream-pytest.log", PYTHON_TIMEOUT, env=subprocess_env())
    outcome = parse_junit(junit)
    if (outcome["total"] != EXPECTED_TESTS or outcome["skipped"] != len(EXPECTED_SKIPS)
            or outcome["failed"] or outcome["errors"] or outcome["unexpectedSkips"]):
        raise ValueError("Upstream execution differs from pinned expected outcomes")
    verify_reference(reference, pin)
    return {"status": "passed", "reference": identity, "dtlsCapability": capability,
            "selectedFiles": files, "collected": len(collected), "executed": outcome["total"],
            "passed": outcome["passed"], "expectedSkips": outcome["skipped"],
            "zeroCaseModules": zero_case_modules}


def validate(root: Path, profile: str, *, manifest_path: Path | None = None) -> tuple[int, Path]:
    run_root = root / ".scratch/offline-validation"
    run_root.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="run-", dir=run_root))
    receipt = {"schemaVersion": 1, "mode": "offline-validation", "profile": profile,
               "startedAtUtc": utc_now(), "newWorldClientTested": False,
               "milestone1": "not tested", "runDirectory": run.relative_to(root).as_posix(),
               "status": "running", "gitBefore": git_state(root)}
    receipt_path = run / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    code = 1
    names: list[str] = []
    before: dict[str, str] = {}
    try:
        manifest = load_manifest(manifest_path or root / "scripts/offline-test-profiles.json")
        chosen = selection(root, manifest, profile)
        receipt["selected"] = chosen
        runtime = environment_report(root)
        receipt["runtime"] = runtime
        if not runtime["ready"]:
            raise ValueError("Workspace Python/dependency lock not ready: " + ", ".join(runtime["problems"]))
        names = input_files(root, chosen)
        before = snapshot(root, names)
        receipt["inputs"] = [{"path": name, "sha256": digest} for name, digest in before.items()]
        if chosen["python"]:
            receipt["python"] = run_pytest(root, chosen["python"], run)
        if chosen["powershell"]:
            receipt["powershell"] = run_powershell(root, chosen["powershell"], run)
        if chosen["cli"]:
            receipt["cli"] = cli_lifecycle(root, run)
        if chosen["upstream"]:
            receipt["upstream"] = upstream_validation(root, run, manifest)
        code = 0
    except Exception as error:
        receipt["errorType"] = type(error).__name__
        # Raw subprocess output stays in ignored scratch. Avoid emitting private content.
        (run / "error.txt").write_text(str(error), encoding="utf-8")
    finally:
        if before:
            try:
                after = snapshot(root, names)
                changed = sorted(name for name in names if before[name] != after[name])
            except (OSError, ValueError):
                changed = ["source-unavailable-or-changing"]
            receipt["changedInputs"] = changed
            if changed:
                code = 1
                receipt["errorType"] = "InputChangedDuringRun"
        receipt["gitAfter"] = git_state(root)
        receipt["status"] = "passed" if code == 0 else "failed"
        receipt["finishedAtUtc"] = utc_now()
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return code, receipt_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="workspace")
    parser.add_argument("--list-profiles", action="store_true")
    options = parser.parse_args()
    if options.list_profiles:
        for name in load_manifest()["profiles"]:
            print(name)
        return 0
    code, receipt = validate(ROOT, options.profile)
    print(json.dumps({"status": "passed" if code == 0 else "failed",
                      "profile": options.profile, "receipt": receipt.relative_to(ROOT).as_posix(),
                      "newWorldClientTested": False}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
