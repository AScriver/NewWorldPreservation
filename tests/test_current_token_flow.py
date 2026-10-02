"""Replay observed request metadata locally with synthetic bodies, not tickets.

These are Python TLS controls, not a new live-client or successful-login claim.
"""
import hashlib
import json
from pathlib import Path
import socket
import ssl
import sys
import threading

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bootstrap_probe as bootstrap
from channel_descriptor import load_local_descriptor

OBSERVED = json.loads((ROOT / "tests/fixtures/connectivity/current-client-token-result.json").read_text())


@pytest.fixture
def private_endpoint(tmp_path):
    certificates = tmp_path / "certificates"
    bootstrap.probe.generate_certificates(certificates, [bootstrap.BOOTSTRAP_HOST,
        "tokenservice.amazongames.com", "prod.newworld.com"])
    path = tmp_path / "events.jsonl"
    events = bootstrap.probe.EventLog(path)
    descriptor = load_local_descriptor(ROOT / "tests/fixtures/connectivity/local-channel-token-hostnames.json",
        token_routing="original-hostnames")
    server = bootstrap.make_server("127.0.0.1", 0, certificates, events, descriptor,
        token_routing="original-hostnames")
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    try:
        yield server, certificates, path
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        assert not thread.is_alive()
        events.close()


def replay_metadata(endpoint, observed, synthetic_body=b""):
    server, certificates, _ = endpoint
    request = observed["request"]
    assert len(synthetic_body) == request["declared_body_bytes"]
    version = {"TLSv1.2": ssl.TLSVersion.TLSv1_2, "TLSv1.3": ssl.TLSVersion.TLSv1_3}[observed["tls"]["tls_version"]]
    context = ssl.create_default_context(cafile=str(certificates / "ca.pem"))
    context.minimum_version = version
    context.maximum_version = version
    wire = (f'{request["method"]} {request["path"]} {request["http_version"]}\r\n'
        f'Host: {request["host"]}\r\nContent-Length: {len(synthetic_body)}\r\n\r\n').encode("ascii") + synthetic_body
    with socket.create_connection(server.server_address, timeout=3) as raw:
        with context.wrap_socket(raw, server_hostname=observed["sni"]) as connection:
            connection.sendall(wire)
            response = bytearray()
            while chunk := connection.recv(65536):
                response.extend(chunk)
    return bytes(response)


def read_events(endpoint):
    endpoint[0].shutdown()
    return [json.loads(line) for line in endpoint[2].read_text().splitlines()]


def test_observed_bootstrap_profile_retains_canonical_payload_over_tls12(private_endpoint):
    observed = OBSERVED["bootstrap"]
    response = replay_metadata(private_endpoint, observed)
    headers, body = response.split(b"\r\n\r\n", 1)
    assert headers.startswith(b"HTTP/1.1 200")
    assert len(body) == observed["response"]["body_bytes"]
    assert hashlib.sha256(body).hexdigest() == observed["response"]["canonical_descriptor_sha256"]
    events = read_events(private_endpoint)
    assert any(event.get("tls_version") == "TLSv1.2" for event in events)
    assert any(event.get("token_routing") == "original-hostnames" and event["state"] == "CHANNEL_DESCRIPTOR_RESPONSE" for event in events)


def test_observed_token_tls13_route_rejects_without_secret_capture_or_auth_claim(private_endpoint):
    observed = OBSERVED["token_requests"][0]
    # Observed Content-Length is session-specific, not a protocol constant.
    body = b"SYNTHETIC-SECRET-NOT-FOR-LOGS".ljust(observed["request"]["declared_body_bytes"], b"x")
    response = replay_metadata(private_endpoint, observed, body)
    assert response.startswith(b"HTTP/1.1 501")
    events = read_events(private_endpoint)
    assert any(event.get("sni") == "tokenservice.amazongames.com" for event in events)
    assert any(event.get("tls_version") == "TLSv1.3" for event in events)
    assert any(event.get("declared_body_bytes") == len(body) and event.get("method") == "POST" for event in events)
    assert any(event["state"] == "TOKEN_SESSION_REQUEST" and event["request_body_saved"] is False for event in events)
    assert any(event["state"] == "TOKEN_SESSION_RESPONSE" and event["authentication_success"] is False for event in events)
    assert "SYNTHETIC-SECRET-NOT-FOR-LOGS" not in json.dumps(events)
    assert not any(event.get("authentication_success") is True for event in events)
