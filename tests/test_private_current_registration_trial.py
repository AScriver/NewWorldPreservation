"""Offline current registration admission; no transport or client runtime."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import private_current_registration_trial as trial


@pytest.fixture
def private_body():
    scratch = ROOT / ".scratch"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="registration285-test-", dir=scratch) as directory:
        path = Path(directory) / "body with spaces.bin"
        path.write_bytes(bytes(18))
        yield path


def options(path, request=0, response=3, digest=None):
    return SimpleNamespace(current_request_type_index=request,
                           current_response_type_index=response,
                           current_response_body=str(path),
                           current_response_body_sha256=digest if digest is not None
                           else hashlib.sha256(path.read_bytes()).hexdigest())


def cli(path, request="0", response="3", digest=None):
    selected = options(path, digest=digest)
    args = [sys.executable, "-B", str(SCRIPTS / "private_current_registration_trial.py"),
            "--current-request-type-index", request,
            "--current-response-type-index", response,
            "--current-response-body", str(path),
            "--current-response-body-sha256", selected.current_response_body_sha256]
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False)


def test_cli_only_emits_prepared_metadata(private_body):
    completed = cli(private_body, "0", "0xffffffff")
    assert completed.returncode == 0
    assert completed.stderr == ""
    metadata = json.loads(completed.stdout)
    assert metadata == {
        "status": "prepared-only", "client_acceptance_proven": False,
        "current_request_type_index": 0, "current_response_type_index": 4294967295,
        "body_bytes": 18,
        "body_sha256": hashlib.sha256(bytes(18)).hexdigest(),
        "typed_record_bytes": metadata["typed_record_bytes"],
        "typed_record_sha256": metadata["typed_record_sha256"],
    }
    assert 1 <= metadata["typed_record_bytes"] <= 4096
    assert str(private_body) not in completed.stdout


@pytest.mark.parametrize("selector", ["-1", "4294967296", "1.5", "true"])
def test_cli_rejects_invalid_selector(private_body, selector):
    result = cli(private_body, selector)
    assert result.returncode != 0 and not result.stdout


@pytest.mark.parametrize("raw", [b"", bytes(17), bytes(18) + b"tail",
                                  bytes(12) + b"\x80\x00" + bytes(5), bytes(4097)])
def test_cli_rejects_noncanonical_or_wrong_extent(private_body, raw):
    private_body.write_bytes(raw)
    result = cli(private_body)
    assert result.returncode != 0 and result.stdout == ""
    assert result.stderr == trial.INVALID + "\n"
    assert str(private_body) not in result.stderr


def test_cli_rejects_digest_and_outside_path(private_body):
    assert cli(private_body, digest="0" * 64).returncode != 0
    # Keep this test's outside candidate in a separate, owned temporary directory.
    with tempfile.TemporaryDirectory(prefix="registration285-outside-") as directory:
        outside = Path(directory) / "body.bin"
        outside.write_bytes(bytes(18))
        result = cli(outside)
        assert result.returncode != 0 and result.stderr == trial.INVALID + "\n"


@pytest.mark.parametrize("request_index,response_index", [(True, 3), (0, False), (1.5, 3), (-1, 3), (0, 1 << 32)])
def test_direct_prepare_rejects_non_uint32(private_body, request_index, response_index):
    with pytest.raises(ValueError, match=trial.INVALID):
        trial.prepare_current_registration(options(private_body, request_index, response_index))


def test_direct_prepare_rejects_partial_and_retains_historical_empty(private_body):
    empty = SimpleNamespace(current_request_type_index=None,
                            current_response_type_index=None,
                            current_response_body=None,
                            current_response_body_sha256=None)
    assert trial.prepare_current_registration(empty) == {}
    empty.current_response_body = str(private_body)
    with pytest.raises(ValueError, match=trial.INVALID):
        trial.prepare_current_registration(empty)
    del empty.current_response_body_sha256
    with pytest.raises(ValueError, match=trial.INVALID):
        trial.prepare_current_registration(empty)


def test_verifier_cold_import_closure_is_pure():
    program = ("import sys; sys.path.insert(0, %r); "
               "import private_current_registration_trial; "
               "forbidden={'carrier_registration_probe','connectivity_probe',"
               "'dtls_transport_probe','cryptography','current_player_creation_candidate',"
               "'current_self_ident_default'}; "
               "assert not (forbidden & set(sys.modules))") % str(SCRIPTS)
    result = subprocess.run([sys.executable, "-B", "-c", program],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
