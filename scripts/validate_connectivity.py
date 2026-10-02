"""Explicit synthetic loopback profile with private diagnostics and honest receipt."""
import hashlib
import argparse
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
PROFILES = {
    'probe': (19, ['tests/test_connectivity_probe.py']),
    'instrumentation': (26, ['tests/test_game_log_metadata.py', 'tests/test_hosts_redirect.py',
                            'tests/test_windows_tcp_owner.py', 'tests/test_probe_controls.py',
                            'tests/test_current_client_fixture.py'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=PROFILES, default='probe')
    options = parser.parse_args()
    expected_tests, test_paths = PROFILES[options.profile]
    scratch = ROOT / ".scratch/connectivity-validation"
    scratch.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="run-", dir=scratch))
    environment = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
                       PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    environment.pop("PYTEST_ADDOPTS", None)
    print(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                      "state": "PROBE_CONTROL_TESTS_START", "new_world_client": False}), flush=True)
    receipt_path = ROOT / ('research/evidence/connectivity-validation.json' if options.profile == 'probe'
                           else 'research/evidence/instrumentation-validation.json')
    # A timeout/parser/process failure must not leave an earlier green receipt
    # masquerading as this run's result. Final success overwrites this checkpoint.
    receipt_path.write_text(json.dumps({"observedAtUtc": datetime.now(timezone.utc).isoformat(),
                                       "status": "running", "newWorldClientTested": False,
                                       "mode": "synthetic-loopback-controls-not-new-world",
                                       "runDirectory": str(run.relative_to(ROOT))}, indent=2) + "\n", encoding="utf-8")
    with (run / "pytest-output.txt").open("w", encoding="utf-8") as output:
        process = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                                  *test_paths, "--junitxml", str(run / "results.xml")],
                                 cwd=ROOT, env=environment, stdout=output, stderr=subprocess.STDOUT, timeout=60)
    counts = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    if (run / "results.xml").exists():
        for case in ET.parse(run / "results.xml").getroot().iter("testcase"):
            counts["total"] += 1
            category = next((key for key, tag in [("failed", "failure"), ("errors", "error"),
                                                 ("skipped", "skipped")] if case.find(tag) is not None), "passed")
            counts[category] += 1
    passed = process.returncode == 0 and counts["passed"] == expected_tests and counts["total"] == expected_tests
    receipt = {"observedAtUtc": datetime.now(timezone.utc).isoformat(),
               "mode": "offline-instrumentation-controls-and-observed-metadata-fixture" if options.profile == 'instrumentation' else "synthetic-loopback-controls-not-new-world",
               "profile": options.profile,
               "status": "passed" if passed else "failed", "newWorldClientTested": False,
               "currentClientBuild": None, "currentClientTlsSolved": False,
               "runtime": {"python": platform.python_version(), "tlsLibrary": ssl.OPENSSL_VERSION},
               "tests": dict(counts, processExitCode=process.returncode, expectedTotal=expected_tests),
               "runDirectory": str(run.relative_to(ROOT)),
               "sourceSha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in
                                list(dict.fromkeys(["scripts/connectivity_probe.py", "scripts/validate_connectivity.py",
                                 "scripts/windows_tcp_owner.py", "scripts/game_log_metadata.py", "scripts/Set-ConnectivityHosts.ps1",
                                 "scripts/Observe-CurrentClient.ps1", *test_paths, "tests/fixtures/connectivity/requests.json",
                                 "tests/fixtures/connectivity/current-client-bootstrap.json"]))},
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
