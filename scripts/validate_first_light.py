"""Offline validation of pinned external First Light; never launches a client."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

WORKSPACE = Path(__file__).resolve().parents[1]
TEST_FILES = (
    "server/javelin/test_parser.py",
    "server/javelin/test_codecs.py",
    "server/javelin/test_replay_substitution.py",
    "server/test_chunking.py",
    "server/test_loopback.py",
    "server/test_captures.py",
    "server/test_vlq32.py",
    "server/test_piggyback_ack.py",
    "server/test_multi_peer.py",
    "server/javelin/test_shadow_decode.py",
    "server/javelin/test_heartbeat_encode_validate.py",
)
EXPECTED_TESTS = 456
EXPECTED_SKIPS = {
    "server.javelin.test_codecs::test_v3_or_lenient_uses_strict_first_on_valid_body":
        "strict path uses existing fixtures; covered by other tests",
}


def log_state(state: str, **fields: object) -> None:
    print(json.dumps({"timeUtc": datetime.now(timezone.utc).isoformat(),
                      "state": state, **fields}), flush=True)


def git_read(reference: Path, *arguments: str) -> str:
    result = subprocess.run(["git", "-C", str(reference), *arguments],
                            capture_output=True, text=True, check=True, timeout=30)
    return result.stdout.strip()


def verify_reference(reference: Path, pin: dict) -> dict:
    if git_read(reference, "rev-parse", "HEAD") != pin["commit"]:
        raise ValueError("Reference commit differs from research/upstreams.json")
    if git_read(reference, "remote", "get-url", "origin") != pin["url"]:
        raise ValueError("Reference origin differs from research/upstreams.json")
    if git_read(reference, "status", "--porcelain"):
        raise ValueError("Reference has local changes; validation refuses an unidentified source")
    fixture = reference / pin["fixture"]
    with fixture.open("rb") as fixture_file:
        fixture_hash = hashlib.file_digest(fixture_file, "sha256").hexdigest()
    if fixture_hash != pin["fixtureSha256"]:
        raise ValueError("Public redacted reference fixture hash differs from pin")
    for relative_path in TEST_FILES:
        if not (reference / relative_path).is_file():
            raise ValueError(f"Missing explicit test module: {relative_path}")
    return {"commit": pin["commit"], "sourceWorktree": "clean",
            "fixtureSha256": fixture_hash, "fixtureBytes": fixture.stat().st_size}


def verify_environment(lock_path: Path) -> dict:
    if sys.version_info[:2] not in ((3, 11), (3, 12)):
        raise ValueError("Use supported Python 3.11 or 3.12")
    if Path(sys.prefix).resolve() != (WORKSPACE / ".venv").resolve():
        raise ValueError("Use this workspace's isolated .venv interpreter")
    locked = dict(re.findall(r"^([A-Za-z0-9_.-]+)==([^\s\\]+)",
                             lock_path.read_text(encoding="utf-8"), re.MULTILINE))
    if not {"pytest", "pyopenssl", "cryptography"}.issubset(locked):
        raise ValueError("Dependency lock is incomplete")
    for name, expected in locked.items():
        if metadata.version(name) != expected:
            raise ValueError(f"Installed {name} version differs from hash-pinned lock")
    return {"python": sys.version.split()[0], "packages": locked,
            "lockSha256": hashlib.sha256(lock_path.read_bytes()).hexdigest()}


def parse_junit(path: Path) -> dict:
    cases = list(ET.parse(path).getroot().iter("testcase"))
    result = {"total": len(cases), "passed": 0, "failed": 0,
              "errors": 0, "skipped": 0, "unexpectedSkips": []}
    for case in cases:
        case_id = f"{case.get('classname')}::{case.get('name')}"
        skip = case.find("skipped")
        if case.find("failure") is not None:
            result["failed"] += 1
        elif case.find("error") is not None:
            result["errors"] += 1
        elif skip is not None:
            result["skipped"] += 1
            if case_id not in EXPECTED_SKIPS or skip.get("message") != EXPECTED_SKIPS[case_id]:
                result["unexpectedSkips"].append(case_id)
        else:
            result["passed"] += 1
    return result


def validation_passed(result: dict, exit_code: int) -> bool:
    return (exit_code == 0 and result["total"] == EXPECTED_TESTS
            and result["failed"] == 0 and result["errors"] == 0
            and not result["unexpectedSkips"])


def probe_dtls_context(reference: Path, run_directory: Path) -> dict:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    from OpenSSL import SSL

    sys.path.insert(0, str(reference))
    from server import rep_responder

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "offline.invalid")])
    now = datetime.now(timezone.utc)
    certificate = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject)
                   .public_key(key.public_key()).serial_number(x509.random_serial_number())
                   .not_valid_before(now - timedelta(minutes=1))
                   .not_valid_after(now + timedelta(minutes=10)).sign(key, hashes.SHA256()))
    with tempfile.TemporaryDirectory(prefix="dtls-identity-", dir=run_directory) as directory:
        cert_path, key_path = Path(directory) / "cert.pem", Path(directory) / "key.pem"
        cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
        key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                             serialization.PrivateFormat.TraditionalOpenSSL,
                             serialization.NoEncryption()))
        previous_cert, previous_key = rep_responder.CERT_PATH, rep_responder.KEY_PATH
        try:
            rep_responder.CERT_PATH, rep_responder.KEY_PATH = cert_path, key_path
            context = rep_responder.make_ssl_context()
            connection = SSL.Connection(context, None)
            connection.set_accept_state()
        finally:
            rep_responder.CERT_PATH, rep_responder.KEY_PATH = previous_cert, previous_key
    return {"serverContext": "constructed", "memoryBio": "constructed",
            "certificate": "ephemeral self-generated; deleted", "handshake": "not tested"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-only", action="store_true")
    options = parser.parse_args()
    pin = json.loads((WORKSPACE / "research/upstreams.json").read_text(encoding="utf-8"))["firstLight"]
    reference = WORKSPACE / pin["directory"]
    run_root = WORKSPACE / ".scratch/validation"
    run_root.mkdir(parents=True, exist_ok=True)
    run_directory = Path(tempfile.mkdtemp(prefix="run-", dir=run_root))
    summary = {"observedAtUtc": datetime.now(timezone.utc).isoformat(), "mode": "offline-only",
               "milestone1": "not tested", "runDirectory": str(run_directory.relative_to(WORKSPACE))}
    log_state("PREFLIGHT_START")
    try:
        summary["reference"] = verify_reference(reference, pin)
        summary["runtime"] = verify_environment(WORKSPACE / "requirements-dev.lock")
        log_state("REFERENCE_AND_ENVIRONMENT_VERIFIED", commit=pin["commit"])
        summary["dtlsCapability"] = probe_dtls_context(reference, run_directory)
        log_state("DTLS_CONTEXT_VERIFIED", handshake="not tested", listener=False)
        if options.preflight_only:
            summary["status"] = "preflight passed; protocol tests not run"
            exit_code = 0
        else:
            junit_path = run_directory / "junit.xml"
            command = [sys.executable, "-m", "pytest", "-q", "-ra", "-p", "no:cacheprovider",
                       "--basetemp", str(run_directory / "pytest-temp"),
                       "--junitxml", str(junit_path), *TEST_FILES]
            environment = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1",
                           "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
            log_state("PROTOCOL_TESTS_START", selectedFiles=len(TEST_FILES))
            with (run_directory / "pytest-output.txt").open("w", encoding="utf-8") as output:
                completed = subprocess.run(command, cwd=reference, env=environment,
                                           stdout=output, stderr=subprocess.STDOUT, timeout=120)
            summary["tests"] = parse_junit(junit_path)
            summary["tests"]["processExitCode"] = completed.returncode
            summary["tests"]["selectedFiles"] = list(TEST_FILES)
            # Recheck the exact input identity after executed tests.
            verify_reference(reference, pin)
            passed = validation_passed(summary["tests"], completed.returncode)
            summary["status"] = "passed" if passed else "failed"
            exit_code = 0 if passed else 1
    except Exception as exception:
        summary["status"] = "failed"
        summary["errorType"] = type(exception).__name__
        # Never print captured packet bodies or raw subprocess diagnostics.
        (run_directory / "preflight-error.txt").write_text(str(exception), encoding="utf-8")
        exit_code = 1
    (run_directory / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    evidence_path = WORKSPACE / "research/evidence/latest-validation.json"
    evidence_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    log_state("VALIDATION_COMPLETE" if exit_code == 0 else "VALIDATION_FAILED",
              status=summary["status"], summary=str(evidence_path.relative_to(WORKSPACE)),
              tests={key: summary["tests"][key] for key in ("total", "passed", "failed", "errors", "skipped")}
              if "tests" in summary else None)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
