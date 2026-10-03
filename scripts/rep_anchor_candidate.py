"""Prepare an offline, current-build REP trust-anchor candidate; never edit the client."""

import argparse
import base64
import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import serialization


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = ROOT / "private" / "connectivity"
RETAINED_CA = PRIVATE_ROOT / "retained-test-ca.json"
PEM_PATTERN = re.compile(rb"-----BEGIN CERTIFICATE-----\r?\n([A-Za-z0-9+/=\r\n]+)-----END CERTIFICATE-----(?:\r?\n)?\Z")


@dataclass(frozen=True)
class Policy:
    source_path: Path
    image_size: int
    source_sha256: str
    region_offset: int
    region_capacity: int
    original_der_sha256: str
    anchor_pem_sha256: str
    anchor_der_sha256: str


CURRENT = Policy(
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\New World\Bin64\NewWorld.exe"),
    179204176,
    "8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e",
    0x858EC60,
    1350,
    "62880372376f5d9b4e63e453c7eaaf906a9b3d11bf8e3e9e2c8cbdd98c28ffe3",
    "30bba23f8800ddad69f199c96746aec5eed7e5ce405e130206c630d516573b19",
    "2c9f403d47318a0c1f801d5bc5ea11a33cef83612221248a0df8c5ca3e34bbeb",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def certificate_der(pem: bytes) -> bytes:
    """Require one certificate and no other PEM objects or trailing material."""
    match = PEM_PATTERN.fullmatch(pem)
    if match is None:
        raise ValueError("Expected exactly one certificate-only PEM")
    try:
        der = base64.b64decode(re.sub(rb"\s", b"", match.group(1)), validate=True)
        certificate = x509.load_der_x509_certificate(der)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid certificate DER") from exc
    if certificate.public_bytes(serialization.Encoding.DER) != der:
        raise ValueError("Noncanonical or trailing certificate DER")
    return der


def approved_anchor(pem: bytes, policy: Policy, now: datetime | None = None) -> bytes:
    if sha256(pem) != policy.anchor_pem_sha256:
        raise ValueError("Approved anchor PEM hash mismatch")
    der = certificate_der(pem)
    if sha256(der) != policy.anchor_der_sha256:
        raise ValueError("Approved anchor DER hash mismatch")
    certificate = x509.load_der_x509_certificate(der)
    try:
        basic = certificate.extensions.get_extension_for_class(x509.BasicConstraints).value
    except x509.ExtensionNotFound as exc:
        raise ValueError("Anchor lacks CA basic constraint") from exc
    if not basic.ca:
        raise ValueError("Anchor is not a CA")
    try:
        usage = certificate.extensions.get_extension_for_class(x509.KeyUsage).value
    except x509.ExtensionNotFound:
        usage = None
    if usage is not None and not usage.key_cert_sign:
        raise ValueError("Anchor key usage forbids certificate signing")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Validation time must be timezone aware")
    if not certificate.not_valid_before_utc <= current <= certificate.not_valid_after_utc:
        raise ValueError("Anchor is outside its validity interval")
    return der


def prepare_bytes(source: bytes, pem: bytes, policy: Policy, now: datetime | None = None) -> bytes:
    if len(source) != policy.image_size or sha256(source) != policy.source_sha256:
        raise ValueError("Source image identity mismatch")
    start, end = policy.region_offset, policy.region_offset + policy.region_capacity
    if start < 0 or policy.region_capacity < 2 or end > len(source):
        raise ValueError("Invalid pinned certificate region")
    original = source[start:end]
    if not original.endswith(b"\0") or b"\0" in original[:-1]:
        raise ValueError("Original certificate NUL boundary mismatch")
    if sha256(certificate_der(original[:-1])) != policy.original_der_sha256:
        raise ValueError("Original certificate fingerprint mismatch")
    anchor_der = approved_anchor(pem, policy, now)
    if len(pem) >= policy.region_capacity:
        raise ValueError("Approved anchor exceeds NUL-terminated region capacity")
    replacement = pem + bytes(policy.region_capacity - len(pem))
    candidate = source[:start] + replacement + source[end:]
    if (len(candidate) != len(source) or candidate[:start] != source[:start]
            or candidate[end:] != source[end:] or candidate[start:end] != replacement):
        raise AssertionError("Candidate changed bytes outside the approved interval")
    if sha256(certificate_der(candidate[start:end].rstrip(b"\0"))) != sha256(anchor_der):
        raise AssertionError("Candidate certificate failed independent DER reparse")
    return candidate


def _write_new(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def prepare(source_path: Path, ca_path: Path, output_dir: Path, policy: Policy,
            now: datetime | None = None) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"Refusing existing output directory: {output_dir}")
    source = source_path.read_bytes()
    pem = ca_path.read_bytes()
    candidate = prepare_bytes(source, pem, policy, now)
    if file_sha256(source_path) != policy.source_sha256:
        raise ValueError("Source changed during candidate preparation")
    output_dir.mkdir()
    backup_path, candidate_path = output_dir / "stock-backup.bin", output_dir / "candidate.bin"
    _write_new(backup_path, source)
    _write_new(candidate_path, candidate)
    if (file_sha256(backup_path) != policy.source_sha256
            or file_sha256(candidate_path) != sha256(candidate)
            or file_sha256(source_path) != policy.source_sha256):
        raise ValueError("Written artifact or source changed; no valid journal created")
    start, end = policy.region_offset, policy.region_offset + policy.region_capacity
    journal = {
        "schema": 1,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "state": "prepared_offline_unapplied",
        "source_path": str(source_path.resolve()),
        "backup_path": str(backup_path.resolve()),
        "candidate_path": str(candidate_path.resolve()),
        "source_sha256": policy.source_sha256,
        "candidate_sha256": sha256(candidate),
        "image_size": len(source),
        "region_offset": start,
        "region_capacity": policy.region_capacity,
        "original_region_sha256": sha256(source[start:end]),
        "candidate_region_sha256": sha256(candidate[start:end]),
        "anchor_der_sha256": policy.anchor_der_sha256,
        "anchor_pem_sha256": policy.anchor_pem_sha256,
    }
    _write_new(output_dir / "journal.json", (json.dumps(journal, indent=2) + "\n").encode("utf-8"))
    return journal


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "prepare"))
    parser.add_argument("--output-dir", type=Path)
    arguments = parser.parse_args()
    if arguments.action == "prepare":
        if arguments.output_dir is None:
            parser.error("prepare requires --output-dir")
        if arguments.output_dir.parent.resolve() != PRIVATE_ROOT.resolve():
            parser.error("output directory must be a new direct child of private/connectivity")
    elif arguments.output_dir is not None:
        parser.error("plan does not take --output-dir")
    retained = json.loads(RETAINED_CA.read_text(encoding="utf-8"))
    ca_path = Path(retained["certificate_directory"]) / "ca.pem"
    if retained["ca_sha256"].lower() != CURRENT.anchor_der_sha256:
        raise ValueError("Retained CA receipt differs from approved anchor")
    if arguments.action == "prepare":
        result = prepare(CURRENT.source_path, ca_path, arguments.output_dir, CURRENT)
    else:
        source = CURRENT.source_path.read_bytes()
        candidate = prepare_bytes(source, ca_path.read_bytes(), CURRENT)
        if file_sha256(CURRENT.source_path) != CURRENT.source_sha256:
            raise ValueError("Source changed during planning")
        result = {"state": "offline_plan_only", "source_sha256": CURRENT.source_sha256,
                  "candidate_sha256": sha256(candidate), "image_size": len(source),
                  "region_offset": CURRENT.region_offset, "region_capacity": CURRENT.region_capacity,
                  "anchor_der_sha256": CURRENT.anchor_der_sha256,
                  "anchor_pem_sha256": CURRENT.anchor_pem_sha256}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
