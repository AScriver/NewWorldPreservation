import hashlib
import json
from pathlib import Path
import sys
import threading

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import credentials_contract_probe as contract
from test_token_contract_probe import exchange, events


@pytest.fixture(params=contract.CASES)
def endpoint(tmp_path, request):
    certificates = tmp_path / "certificates"
    contract.token.bootstrap.probe.generate_certificates(certificates, [contract.token.bootstrap.BOOTSTRAP_HOST, contract.token.TOKEN_HOST, "prod.newworld.com"])
    path = tmp_path / "events.jsonl"
    event_log = contract.token.bootstrap.probe.EventLog(path)
    descriptor = contract.token.bootstrap.load_local_descriptor(ROOT / "tests/fixtures/connectivity/local-channel-token-hostnames.json", token_routing="original-hostnames")
    server = contract.make_server("127.0.0.1", 0, certificates, event_log, descriptor, case=request.param)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    yield server, certificates, path
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
    assert not thread.is_alive()
    event_log.close()


def request_credentials(endpoint, **overrides):
    options = dict(method="GET", host=contract.token.bootstrap.BOOTSTRAP_HOST,
                   path=contract.CREDENTIALS_PATH, authorization="Bearer SYNTHETIC-DO-NOT-EXPORT")
    options.update(overrides)
    return exchange(endpoint, **options)


def test_credentials_response_is_deterministic_and_never_logs_incoming_secrets(endpoint):
    response = request_credentials(endpoint)
    headers, body = response.split(b"\r\n\r\n", 1)
    assert headers.startswith(b"HTTP/1.1 200")
    assert body == contract.response_case(endpoint[0].credentials_case)
    records = events(endpoint)
    proof = next(r for r in records if r["state"] == "CREDENTIALS_CONTRACT_TEST_RESPONSE")
    assert proof["response_sha256"] == hashlib.sha256(body).hexdigest()
    assert proof["response_bytes"] == len(body)
    assert proof["synthetic_values_only"]
    assert not proof["official_authentication_success"]
    assert not proof["client_acceptance_observed"]
    assert "SYNTHETIC-DO-NOT-EXPORT" not in json.dumps(records)


@pytest.mark.parametrize("overrides", [
    {"method": "POST"}, {"host": contract.token.TOKEN_HOST},
    {"path": contract.CREDENTIALS_PATH + "?private=secret"},
    {"path": "/prod/game/getlogininfo"}, {"authorization": None},
    {"body": b"SYNTHETIC-BODY-DO-NOT-EXPORT"},
])
def test_unestablished_requests_remain_rejected(endpoint, overrides):
    assert request_credentials(endpoint, **overrides).startswith(b"HTTP/1.1 501")
    records = events(endpoint)
    assert not any(r["state"] == "CREDENTIALS_CONTRACT_TEST_RESPONSE" for r in records)
    assert "SYNTHETIC-BODY-DO-NOT-EXPORT" not in json.dumps(records)


def test_verified_token_model_response_is_preserved(endpoint):
    response = exchange(endpoint)
    assert response.startswith(b"HTTP/1.1 200")
    assert response.split(b"\r\n\r\n", 1)[1] == contract.token.response_case("model-with-account")


def test_numeric_candidate_and_historical_comparison_differ_only_in_expiration_type():
    current = json.loads(contract.response_case("flat-numeric-expiration"))
    historical = json.loads(contract.response_case("flat-string-expiration"))
    assert set(current) == {"accessKeyId", "secretAccessKey", "sessionToken", "expiration"}
    assert isinstance(current["expiration"], int)
    assert isinstance(historical["expiration"], str)
    assert {k:v for k,v in current.items() if k != "expiration"} == {k:v for k,v in historical.items() if k != "expiration"}
    assert all("NWP" in v.upper() for k,v in current.items() if k != "expiration")


def test_unknown_case_is_refused_before_certificates_or_listener_access():
    with pytest.raises(ValueError):
        contract.make_server("127.0.0.1", 0, Path("not-read"), None, {}, case="guessed-game-login")
