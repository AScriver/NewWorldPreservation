"""Explicit synthetic loopback profile with private diagnostics and honest receipt."""
import hashlib
import json
import os
import platform
import ssl
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TESTS = 19


def main():
    scratch = ROOT / ".scratch/connectivity-validation"
    scratch.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="run-", dir=scratch))
    environment = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
                       PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    environment.pop("PYTEST_ADDOPTS", None)
    print(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                      "state": "PROBE_CONTROL_TESTS_START", "new_world_client": False}), flush=True)
    receipt_path = ROOT / "research/evidence/connectivity-validation.json"
    # A timeout/parser/process failure must not leave an earlier green receipt
    # masquerading as this run's result. Final success overwrites this checkpoint.
    receipt_path.write_text(json.dumps({"observedAtUtc": datetime.now(timezone.utc).isoformat(),
                                       "status": "running", "newWorldClientTested": False,
                                       "mode": "synthetic-loopback-controls-not-new-world",
                                       "runDirectory": str(run.relative_to(ROOT))}, indent=2) + "\n", encoding="utf-8")
    with (run / "pytest-output.txt").open("w", encoding="utf-8") as output:
        process = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                                  "tests/test_connectivity_probe.py", "--junitxml", str(run / "results.xml")],
                                 cwd=ROOT, env=environment, stdout=output, stderr=subprocess.STDOUT, timeout=60)
    counts = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    if (run / "results.xml").exists():
        for case in ET.parse(run / "results.xml").getroot().iter("testcase"):
            counts["total"] += 1
            category = next((key for key, tag in [("failed", "failure"), ("errors", "error"),
                                                 ("skipped", "skipped")] if case.find(tag) is not None), "passed")
            counts[category] += 1
    passed = process.returncode == 0 and counts["passed"] == EXPECTED_TESTS and counts["total"] == EXPECTED_TESTS
    receipt = {"observedAtUtc": datetime.now(timezone.utc).isoformat(),
               "mode": "synthetic-loopback-controls-not-new-world",
               "status": "passed" if passed else "failed", "newWorldClientTested": False,
               "currentClientBuild": None, "currentClientTlsSolved": False,
               "runtime": {"python": platform.python_version(), "tlsLibrary": ssl.OPENSSL_VERSION},
               "tests": dict(counts, processExitCode=process.returncode, expectedTotal=EXPECTED_TESTS),
               "runDirectory": str(run.relative_to(ROOT)),
               "sourceSha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in
                                ["scripts/connectivity_probe.py", "scripts/validate_connectivity.py",
                                 "tests/test_connectivity_probe.py", "tests/fixtures/connectivity/requests.json"]},
               "trustStoreModified": False, "hostsModified": False,
               "listeners": "ephemeral IPv4/IPv6 loopback, closed by fixture cleanup",
               "controls": ["TLS1.2/TLS1.3 trusted CA+SAN", "untrusted CA rejected",
                            "wrong hostname rejected", "IP SAN and IPv6", "SNI metadata",
                            "HTTP framing/credential-log rejection", "501 never authentication success"]}
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"timestamp_utc": receipt["observedAtUtc"],
                      "state": "PROBE_CONTROL_TESTS_COMPLETE" if passed else "PROBE_CONTROL_TESTS_FAILED",
                      "tests": receipt["tests"], "new_world_client": False}), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
