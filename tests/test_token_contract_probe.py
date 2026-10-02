import json
from pathlib import Path
import socket
import ssl
import sys
import threading

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import token_contract_probe as contract


@pytest.fixture(params=["empty-object", "malformed-json", "model-with-account", "model-without-account"])
def endpoint(tmp_path, request):
    certificates = tmp_path / "certificates"
    contract.bootstrap.probe.generate_certificates(certificates, [contract.bootstrap.BOOTSTRAP_HOST, contract.TOKEN_HOST, "prod.newworld.com"])
    path = tmp_path / "events.jsonl"
    events = contract.bootstrap.probe.EventLog(path)
    descriptor = contract.bootstrap.load_local_descriptor(ROOT / "tests/fixtures/connectivity/local-channel-token-hostnames.json", token_routing="original-hostnames")
    server = contract.make_server("127.0.0.1", 0, certificates, events, descriptor, case=request.param)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    yield server, certificates, path
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
    assert not thread.is_alive()
    events.close()


def exchange(endpoint, *, method="POST", host=contract.TOKEN_HOST, path=contract.TOKEN_PATH, body=b"", authorization=None):
    server, certificates, _ = endpoint
    context = ssl.create_default_context(cafile=str(certificates / "ca.pem"))
    authentication_header = "" if authorization is None else f"Authorization: {authorization}\r\n"
    wire = (f"{method} {path} HTTP/1.1\r\nHost: {host}\r\n{authentication_header}Content-Length: {len(body)}\r\n\r\n").encode() + body
    with socket.create_connection(server.server_address, timeout=3) as raw:
        with context.wrap_socket(raw, server_hostname=host) as connection:
            connection.sendall(wire)
            result = bytearray()
            while chunk := connection.recv(65536):
                result.extend(chunk)
    return bytes(result)


def events(endpoint):
    endpoint[0].shutdown()
    return [json.loads(line) for line in endpoint[2].read_text().splitlines()]


def test_controlled_response_discards_request_secrets_and_never_claims_authentication(endpoint):
    response = exchange(endpoint, body=b"SYNTHETIC-REQUEST-TICKET-DO-NOT-LOG")
    headers, body = response.split(b"\r\n\r\n", 1)
    assert headers.startswith(b"HTTP/1.1 200")
    assert b"Content-Type: application/json" in headers
    assert body == contract.response_case(endpoint[0].token_case)
    records = events(endpoint)
    assert "SYNTHETIC-REQUEST-TICKET-DO-NOT-LOG" not in json.dumps(records)
    assert any(item["state"] == "TOKEN_SESSION_REQUEST" and item["request_body_saved"] is False for item in records)
    assert any(item["state"] == "TOKEN_CONTRACT_TEST_RESPONSE" and not item["authentication_success"] for item in records)
    assert not any(item.get("authentication_success") is True for item in records)


@pytest.mark.parametrize("overrides", [{"method": "GET"}, {"path": contract.TOKEN_PATH + "?private=value"}, {"host": contract.bootstrap.BOOTSTRAP_HOST}])
def test_contract_case_is_not_served_to_other_methods_hosts_or_query_paths(endpoint, overrides):
    assert exchange(endpoint, **overrides).startswith(b"HTTP/1.1 501")
    assert not any(item["state"] == "TOKEN_CONTRACT_TEST_RESPONSE" for item in events(endpoint))


def test_existing_channel_descriptor_is_preserved(endpoint):
    response = exchange(endpoint, method="GET", host=contract.bootstrap.BOOTSTRAP_HOST, path=contract.bootstrap.BOOTSTRAP_PATH)
    assert response.startswith(b"HTTP/1.1 200")
    body = json.loads(response.split(b"\r\n\r\n", 1)[1])
    assert body["platformMetadata"]["OMNI.STEAM_APP_ID.1063730"]["omniTokenUrl"] == "https://" + contract.TOKEN_HOST
    assert not any(item["state"] == "TOKEN_CONTRACT_TEST_RESPONSE" for item in events(endpoint))


def test_follow_on_credentials_route_remains_rejected_without_exporting_authorization(endpoint):
    secret = "Bearer SYNTHETIC-LOCAL-CREDENTIAL-DO-NOT-EXPORT"
    response = exchange(endpoint, method="GET", host=contract.bootstrap.BOOTSTRAP_HOST,
                        path="/prod/credentials/omni", authorization=secret)
    assert response.startswith(b"HTTP/1.1 501")
    records = events(endpoint)
    assert any(item["state"] == "HTTP_REQUEST" and item["authorization_present"] is True for item in records)
    assert any(item.get("path_template") == "/prod/credentials/omni" for item in records)
    assert secret not in json.dumps(records)
    assert "SYNTHETIC-LOCAL-CREDENTIAL-DO-NOT-EXPORT" not in json.dumps(records)
    assert not any(item.get("authentication_success") is True for item in records)


def test_unknown_case_is_refused_before_binding_or_reading_certificates():
    with pytest.raises(ValueError):
        contract.make_server("127.0.0.1", 0, Path("not-read"), None, {}, case="invented-success")


def test_synthetic_model_variants_differ_only_by_account_and_are_deterministic():
    with_account = json.loads(contract.response_case("model-with-account"))
    without_account = json.loads(contract.response_case("model-without-account"))
    assert "account" not in without_account
    assert without_account == {key: value for key, value in with_account.items() if key != "account"}
    assert set(without_account["platformAccount"]) == {"identityType", "identityId", "personaId", "ageGroup"}
    assert isinstance(without_account["expiresIn"], int)
    assert without_account["accessToken"].startswith("nwp-synthetic-")
    assert without_account["fallbackToken"].startswith("nwp-synthetic-")
    assert contract.response_case("model-with-account") == contract.response_case("model-with-account")
