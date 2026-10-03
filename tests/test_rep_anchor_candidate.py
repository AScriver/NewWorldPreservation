"""Synthetic byte-level checks; no proprietary image or retained private CA fixture."""

import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import rep_anchor_candidate as anchor


NOW = datetime(2026, 10, 2, tzinfo=timezone.utc)


def make_pem(*, rsa_key=False, ca=True, cert_sign=True,
             start=NOW - timedelta(days=1), end=NOW + timedelta(days=1)):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048) if rsa_key else ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "synthetic.invalid")])
    certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                   .public_key(key.public_key()).serial_number(0x123456789ABCDEF)
                   .not_valid_before(start).not_valid_after(end)
                   .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
                   .add_extension(x509.KeyUsage(False, False, False, False, False,
                                                cert_sign, ca, False, False), critical=True)
                   .sign(key, hashes.SHA256()))
    return certificate.public_bytes(serialization.Encoding.PEM)


def setup_synthetic(tmp_path):
    original_pem = make_pem(rsa_key=True)
    approved_pem = make_pem()
    prefix, suffix = b"prefix-control" * 5, b"suffix-control" * 5
    source = prefix + original_pem + b"\0" + suffix
    source_path, ca_path = tmp_path / "stock.bin", tmp_path / "ca.pem"
    source_path.write_bytes(source)
    ca_path.write_bytes(approved_pem)
    policy = anchor.Policy(
        source_path, len(source), anchor.sha256(source), len(prefix), len(original_pem) + 1,
        anchor.sha256(anchor.certificate_der(original_pem)), anchor.sha256(approved_pem),
        anchor.sha256(anchor.certificate_der(approved_pem)))
    assert len(approved_pem) < policy.region_capacity
    return source_path, ca_path, policy


def test_prepares_only_pinned_interval_with_independently_parsed_anchor(tmp_path):
    source_path, ca_path, policy = setup_synthetic(tmp_path)
    original = source_path.read_bytes()
    journal = anchor.prepare(source_path, ca_path, tmp_path / "new-output", policy, NOW)
    backup = Path(journal["backup_path"]).read_bytes()
    candidate = Path(journal["candidate_path"]).read_bytes()
    start, end = policy.region_offset, policy.region_offset + policy.region_capacity
    assert backup == original == source_path.read_bytes()
    assert len(candidate) == len(original)
    assert candidate[:start] == original[:start] and candidate[end:] == original[end:]
    assert candidate[start:end] == ca_path.read_bytes() + bytes(end - start - ca_path.stat().st_size)
    assert anchor.sha256(anchor.certificate_der(candidate[start:end].rstrip(b"\0"))) == policy.anchor_der_sha256
    assert journal["source_sha256"] == policy.source_sha256
    assert journal["candidate_sha256"] == anchor.sha256(candidate)
    assert journal["original_region_sha256"] == anchor.sha256(original[start:end])
    assert journal["candidate_region_sha256"] == anchor.sha256(candidate[start:end])
    assert journal["state"] == "prepared_offline_unapplied"
    assert journal["schema"] == 1 and journal["timestamp_utc"].endswith("Z")
    journal_text = (tmp_path / "new-output" / "journal.json").read_text()
    assert "BEGIN CERTIFICATE" not in journal_text and "synthetic.invalid" not in journal_text


@pytest.mark.parametrize("kind", ["wrong-root", "private-key", "multiple", "malformed",
                                  "oversize", "expired", "not-yet-valid", "non-ca", "no-cert-sign"])
def test_rejects_invalid_or_unapproved_anchor(tmp_path, kind):
    source_path, ca_path, policy = setup_synthetic(tmp_path)
    pem = ca_path.read_bytes()
    if kind == "wrong-root":
        pem = make_pem()
    elif kind == "private-key":
        pem += b"-----BEGIN PRIVATE KEY-----\nAA==\n-----END PRIVATE KEY-----\n"
    elif kind == "multiple":
        pem += pem
    elif kind == "malformed":
        pem = b"-----BEGIN CERTIFICATE-----\n%%%\n-----END CERTIFICATE-----\n"
    elif kind == "oversize":
        pem = pem.replace(b"-----END CERTIFICATE-----",
                          b"\n" * policy.region_capacity + b"-----END CERTIFICATE-----")
    elif kind == "expired":
        pem = make_pem(start=NOW - timedelta(days=3), end=NOW - timedelta(days=1))
    elif kind == "not-yet-valid":
        pem = make_pem(start=NOW + timedelta(days=1), end=NOW + timedelta(days=3))
    elif kind == "non-ca":
        pem = make_pem(ca=False, cert_sign=False)
    elif kind == "no-cert-sign":
        pem = make_pem(cert_sign=False)
    if kind != "wrong-root":
        # Admit the bytes to reach the corresponding structural/semantic guard.
        try:
            der_hash = anchor.sha256(anchor.certificate_der(pem))
        except ValueError:
            der_hash = policy.anchor_der_sha256
        policy = replace(policy, anchor_pem_sha256=anchor.sha256(pem), anchor_der_sha256=der_hash)
    with pytest.raises(ValueError):
        anchor.prepare_bytes(source_path.read_bytes(), pem, policy, NOW)


def test_rejects_changed_source_and_nul_boundary_without_writing(tmp_path):
    source_path, ca_path, policy = setup_synthetic(tmp_path)
    original = source_path.read_bytes()
    source_path.write_bytes(b"X" + original[1:])
    with pytest.raises(ValueError, match="Source image"):
        anchor.prepare(source_path, ca_path, tmp_path / "output", policy, NOW)
    assert source_path.read_bytes() == b"X" + original[1:]
    assert not (tmp_path / "output").exists()
    changed = bytearray(original)
    changed[policy.region_offset + policy.region_capacity - 1] = ord("X")
    changed_policy = replace(policy, source_sha256=anchor.sha256(changed))
    with pytest.raises(ValueError, match="NUL boundary"):
        anchor.prepare_bytes(bytes(changed), ca_path.read_bytes(), changed_policy, NOW)

    replacement = make_pem(rsa_key=True)
    assert len(replacement) == policy.region_capacity - 1
    changed[policy.region_offset:policy.region_offset + len(replacement)] = replacement
    changed[-1] = original[-1]
    changed[policy.region_offset + policy.region_capacity - 1] = 0
    changed_policy = replace(policy, source_sha256=anchor.sha256(changed))
    with pytest.raises(ValueError, match="Original certificate fingerprint"):
        anchor.prepare_bytes(bytes(changed), ca_path.read_bytes(), changed_policy, NOW)


def test_refuses_existing_output_and_source_change_during_recheck(tmp_path, monkeypatch):
    source_path, ca_path, policy = setup_synthetic(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    (output / "sentinel").write_text("keep")
    with pytest.raises(FileExistsError):
        anchor.prepare(source_path, ca_path, output, policy, NOW)
    assert (output / "sentinel").read_text() == "keep"
    assert len(list(output.iterdir())) == 1
    monkeypatch.setattr(anchor, "file_sha256", lambda _path: "0" * 64)
    with pytest.raises(ValueError, match="Source changed"):
        anchor.prepare(source_path, ca_path, tmp_path / "new-output", policy, NOW)
    assert not (tmp_path / "new-output").exists()
    assert anchor.sha256(source_path.read_bytes()) == policy.source_sha256
