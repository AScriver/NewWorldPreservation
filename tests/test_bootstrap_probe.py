"""Real local HTTPS controls, not New World acceptance or private auth."""
import copy
import json
import socket
import ssl
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bootstrap_probe as bootstrap
from channel_descriptor import load_local_descriptor


@pytest.fixture
def endpoint(tmp_path):
    certificates = tmp_path / "certificates"
    bootstrap.probe.generate_certificates(certificates, [bootstrap.BOOTSTRAP_HOST])
    path = tmp_path / "events.jsonl"
    events = bootstrap.probe.EventLog(path)
    descriptor = load_local_descriptor(ROOT / "tests/fixtures/connectivity/local-channel.json")
    server = bootstrap.make_server("127.0.0.1", 0, certificates, events, descriptor)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    yield server, certificates, path, descriptor
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
    assert not thread.is_alive()
    events.close()


def exchange(endpoint, wire):
    server, certificates, _, _ = endpoint
    context = ssl.create_default_context(cafile=str(certificates / "ca.pem"))
    raw = socket.create_connection(server.server_address, timeout=3)
    with context.wrap_socket(raw, server_hostname=bootstrap.BOOTSTRAP_HOST) as connection:
        connection.sendall(wire)
        result = bytearray()
        while chunk := connection.recv(65536):
            result.extend(chunk)
    return bytes(result)


def records(endpoint):
    server, _, path, _ = endpoint
    server.shutdown()
    server.server_close()
    return [json.loads(line) for line in path.read_text().splitlines()]


def request(path=bootstrap.BOOTSTRAP_PATH, method="GET", host=bootstrap.BOOTSTRAP_HOST, extra="", body=""):
    return (f"{method} {path} HTTP/1.1\r\nHost: {host}\r\n" + extra + "\r\n" + body).encode("ascii")


def test_evidenced_descriptor_is_served_but_not_declared_client_accepted(endpoint):
    response = exchange(endpoint, request())
    headers, body = response.split(b"\r\n\r\n", 1)
    assert headers.startswith(b"HTTP/1.1 200")
    assert b"Content-Type: application/octet-stream" in headers
    assert json.loads(body) == endpoint[3]
    events = records(endpoint)
    descriptor = next(e for e in events if e["state"] == "CHANNEL_DESCRIPTOR_RESPONSE")
    assert descriptor["authentication_success"] is False
    assert descriptor["client_acceptance_observed"] is False
    assert not any(e["state"] == "AUTHENTICATION_RESPONSE" for e in events)
    assert all(e["timestamp_utc"].endswith("Z") for e in events)


@pytest.mark.parametrize("wire", [
    request(method="POST"), request(method="HEAD"), request(host="unknown.invalid"),
    request(path=bootstrap.BOOTSTRAP_PATH + "?secret=not-for-logs"),
    request(extra="Content-Length: 1\r\n", body="x"),
    request(extra="Authorization: Bearer not-for-logs\r\n"),
    request(extra="Cookie: session=not-for-logs\r\n"),
], ids=["post", "head", "host", "query", "body", "authorization", "cookie"])
def test_only_exact_secret_free_observed_channel_request_gets_descriptor(endpoint, wire):
    assert exchange(endpoint, wire).startswith(b"HTTP/1.1 501")
    events = records(endpoint)
    assert not any(e["state"] == "CHANNEL_DESCRIPTOR_RESPONSE" for e in events)
    assert "not-for-logs" not in json.dumps(events)


def test_own_authentication_is_rejected_and_secrets_are_not_logged(endpoint):
    response = exchange(endpoint, request("/prod/credentials/omni", method="POST",
        extra="Authorization: Bearer not-for-logs\r\nContent-Length: 12\r\n", body="not-for-logs"))
    assert response.startswith(b"HTTP/1.1 501")
    events = records(endpoint)
    assert "not-for-logs" not in json.dumps(events)
    assert any(e["state"] == "AUTHENTICATION_REQUEST" for e in events)
    assert any(e["state"] == "AUTHENTICATION_RESPONSE" and not e["authentication_success"] for e in events)


def test_rejects_malformed_http_even_before_headers_exist(endpoint):
    response = exchange(endpoint, b"GET / HTTP/not-a-version\r\n\r\n")
    # Invalid version fails before a response version is selected (HTTP/0.9).
    assert json.loads(response)["authentication_implemented"] is False
    assert any(e["state"] == "HTTP_REJECTED" and e["status"] == 400 for e in records(endpoint))


def test_remote_descriptor_is_refused_before_bind_or_certificate_access():
    descriptor = load_local_descriptor(ROOT / "tests/fixtures/connectivity/local-channel.json")
    value = copy.deepcopy(descriptor)
    value["pdx-prod"]["publicApis"][0]["apiEndpoint"] = "remote.invalid"
    with pytest.raises(ValueError):
        bootstrap.make_server("127.0.0.1", 0, Path("not-read"), None, value)


def test_health_remains_a_control_not_authentication(endpoint):
    assert exchange(endpoint, request("/__probe/health")).startswith(b"HTTP/1.1 200")
    assert not any(e["state"] == "CHANNEL_DESCRIPTOR_RESPONSE" for e in records(endpoint))


def test_unknown_route_template_never_exports_identifiers_queries_or_fragments(endpoint):
    assert exchange(endpoint, request("/prod/games/new-world/session/private-account?ticket=not-for-logs#private-fragment")).startswith(b"HTTP/1.1 501")
    events = records(endpoint)
    output = json.dumps(events)
    assert not any(word in output for word in ("private-account", "not-for-logs", "private-fragment"))
    assert any(e.get("path_template") == "/prod/games/new-world/session/<redacted>" for e in events)
