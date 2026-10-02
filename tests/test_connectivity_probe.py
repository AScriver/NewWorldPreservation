"""Real loopback TLS controls. These are NOT New World client observations."""
import importlib.util
import json
import socket
import ssl
import threading
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "connectivity_probe", Path(__file__).parents[1] / "scripts/connectivity_probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


@pytest.fixture
def endpoint(tmp_path, request):
    certificates = tmp_path / "certificates"
    probe.generate_certificates(certificates, ["localhost"])
    log_path = tmp_path / "events.jsonl"
    log = probe.EventLog(log_path)
    server = probe.make_server(getattr(request, "param", "127.0.0.1"), 0, certificates, log)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    yield server, certificates, log_path
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
    assert not thread.is_alive()
    log.close()


def records(endpoint):
    # server_close joins request threads: no sleeps or sampling an unfinished log.
    server, _, log_path = endpoint
    server.shutdown()
    server.server_close()
    return [json.loads(line) for line in log_path.read_text().splitlines()]


def connect(endpoint, name="localhost", trusted=True, version=ssl.TLSVersion.TLSv1_2):
    server, certificates, _ = endpoint
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = version
    context.maximum_version = version
    if trusted:
        context.load_verify_locations(cafile=str(certificates / "ca.pem"))
    raw = socket.create_connection(server.server_address[:2], timeout=3)
    try:
        return context.wrap_socket(raw, server_hostname=name)
    except Exception:
        raw.close()
        raise


def exchange(connection, request):
    with connection:
        connection.sendall(request)
        response = bytearray()
        while chunk := connection.recv(4096):
            response.extend(chunk)
        return bytes(response)


@pytest.mark.parametrize("version", [ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_3])
def test_ca_and_hostname_validated_request_reaches_control_endpoint(endpoint, version):
    response = exchange(connect(endpoint, version=version),
                        b"GET /__probe/health HTTP/1.1\r\nHost: localhost\r\n\r\n")
    assert response.startswith(b"HTTP/1.1 200")
    events = records(endpoint)
    stages = [event["state"] for event in events]
    assert stages == ["CONNECTION_ATTEMPT", "TLS_CLIENT_HELLO", "TLS_ESTABLISHED",
                      "HTTP_REQUEST", "HTTP_RESPONSE", "CONNECTION_CLOSED"]
    assert next(e for e in events if e["state"] == "TLS_CLIENT_HELLO")["sni"] == "localhost"
    assert all(e["timestamp_utc"].endswith("Z") for e in events)
    assert len({e["connection_id"] for e in events}) == 1
    assert all(e["client_identity"] == "unattributed" for e in events)


@pytest.mark.parametrize("version", [ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_3])
def test_untrusted_ca_is_not_recorded_as_an_http_success(endpoint, version):
    with pytest.raises(ssl.SSLCertVerificationError) as failure:
        connect(endpoint, trusted=False, version=version)
    assert failure.value.verify_code == 20  # X509_V_ERR_UNABLE_TO_GET_ISSUER_CERT_LOCALLY
    events = records(endpoint)
    assert not any(e["state"] == "HTTP_REQUEST" for e in events)
    # Windows may reset before the peer consumes the TLS alert. Client-side
    # verification error is decisive; don't mislabel a reset as unknown-ca.
    assert any(e["state"] == "TLS_FAILED" for e in events)


def test_trusted_ca_does_not_hide_hostname_mismatch(endpoint):
    with pytest.raises(ssl.SSLCertVerificationError) as failure:
        connect(endpoint, name="different.invalid")
    assert failure.value.verify_code == 62  # OpenSSL X509_V_ERR_HOSTNAME_MISMATCH
    events = records(endpoint)
    assert not any(e["state"] == "HTTP_REQUEST" for e in events)
    assert next(e for e in events if e["state"] == "TLS_CLIENT_HELLO")["sni"] == "<unrecognized>"


def test_ip_san_connects_without_sni(endpoint):
    response = exchange(connect(endpoint, name="127.0.0.1"),
                        b"GET /__probe/health HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
    assert response.startswith(b"HTTP/1.1 200")
    assert next(e for e in records(endpoint) if e["state"] == "TLS_CLIENT_HELLO")["sni"] is None


@pytest.mark.parametrize("endpoint", ["::1"], indirect=True)
def test_ipv6_loopback_and_ip_san(endpoint):
    response = exchange(connect(endpoint, name="::1"),
                        b"GET /__probe/health HTTP/1.1\r\nHost: [::1]\r\n\r\n")
    assert response.startswith(b"HTTP/1.1 200")
    assert next(e for e in records(endpoint) if e["state"] == "HTTP_REQUEST")["host"] == "[::1]"


def test_request_fixture_never_exports_secrets_or_claims_auth_success(endpoint):
    fixture = json.loads((Path(__file__).parent / "fixtures/connectivity/requests.json").read_text())
    for request in fixture["requests"]:
        response = exchange(connect(endpoint), request["wire"].encode("ascii"))
        assert response.startswith(b"HTTP/1.1 501")
    events = records(endpoint)
    exported = json.dumps(events)
    for private_value in fixture["must_not_log"]:
        assert private_value not in exported
    auth = [e for e in events if e["state"] == "AUTHENTICATION_RESPONSE"]
    assert auth and all(e["status"] == 501 and e["authentication_success"] is False for e in auth)
    assert any(e["state"] == "GAME_SESSION_SELECTION_REQUEST" for e in events)
    assert not any(e["state"] == "GAME_SESSION_SELECTED" for e in events)
    assert not any(e["state"] == "GAME_TRANSPORT_CONNECTION" for e in events)


@pytest.mark.parametrize("framing", [b"Content-Length: -1", b"Content-Length: nope",
                                    b"Content-Length: 1000000", b"Transfer-Encoding: chunked",
                                    b"Content-Length: 0\r\nContent-Length: 2"])
def test_unsupported_or_ambiguous_body_framing_rejected_without_body_capture(endpoint, framing):
    response = exchange(connect(endpoint), b"POST /private-token HTTP/1.1\r\nHost: localhost\r\n" +
                        framing + b"\r\n\r\n")
    assert response.startswith(b"HTTP/1.1 400")
    assert "private-token" not in json.dumps(records(endpoint))


def test_non_tls_connection_is_diagnosed_without_logging_bytes(endpoint):
    server, _, _ = endpoint
    with socket.create_connection(server.server_address, timeout=3) as connection:
        connection.sendall(b"GET /secret-in-cleartext HTTP/1.1\r\n\r\n")
        try:
            connection.recv(1024)
        except ConnectionResetError:
            pass
    events = records(endpoint)
    assert any(e["state"] == "TLS_FAILED" for e in events)
    assert "secret-in-cleartext" not in json.dumps(events)


def test_probe_never_binds_an_all_interface_or_remote_address(tmp_path):
    # Must refuse before reading certificate files or creating a listener.
    for address in ["0.0.0.0", "::", "192.168.1.2", "localhost"]:
        with pytest.raises(ValueError, match="loopback"):
            probe.make_server(address, 0, tmp_path, None)


def test_certificate_creation_refuses_overwriting_existing_material(tmp_path):
    target = tmp_path / "certificates"
    probe.generate_certificates(target, ["localhost"])
    identity = (target / "server.pem").read_bytes()
    with pytest.raises(FileExistsError):
        probe.generate_certificates(target, ["localhost"])
    assert (target / "server.pem").read_bytes() == identity


def test_probe_log_refuses_overwriting_an_existing_run(tmp_path):
    log_path = tmp_path / "events.jsonl"
    log_path.write_text("earlier evidence\n")
    with pytest.raises(FileExistsError):
        probe.EventLog(log_path)
    assert log_path.read_text() == "earlier evidence\n"


def test_permissive_control_does_not_turn_server_logs_into_validation_proof(endpoint):
    # Deliberate NEGATIVE control in our Python process, not a game trust bypass.
    server, _, _ = endpoint
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with socket.create_connection(server.server_address[:2], timeout=3) as raw:
        response = exchange(context.wrap_socket(raw, server_hostname="wrong.invalid"),
                            b"GET /__probe/health HTTP/1.1\r\nHost: localhost\r\n\r\n")
    assert response.startswith(b"HTTP/1.1 200")
    events = records(endpoint)
    tls = next(e for e in events if e["state"] == "TLS_ESTABLISHED")
    assert tls["observation"] == "server_handshake_finished_not_proof_of_client_trust"
    assert all(e["client_identity"] == "unattributed" for e in events)


def test_absolute_target_does_not_forward_and_parser_errors_do_not_leak(endpoint, capfd):
    with socket.socket() as sentinel:
        sentinel.bind(("127.0.0.1", 0))
        sentinel.listen()
        sentinel.settimeout(0.2)
        target = f"http://127.0.0.1:{sentinel.getsockname()[1]}/prod/credentials/omni?secret=absolute-secret"
        response = exchange(connect(endpoint),
                            f"GET {target} HTTP/1.1\r\nHost: host-secret.invalid\r\nAuthorization: header-secret\r\n\r\n".encode())
        assert response.startswith(b"HTTP/1.1 501")
        with pytest.raises(TimeoutError):
            sentinel.accept()
    # BaseHTTPRequestHandler's error path historically logs the request line.
    exchange(connect(endpoint), b"GET /malformed-secret HTTP/9.9\r\n\r\n")
    events = records(endpoint)
    stdout, stderr = capfd.readouterr()
    exported = json.dumps(events) + stdout + stderr
    for secret in ["absolute-secret", "host-secret", "header-secret", "malformed-secret"]:
        assert secret not in exported
    assert stderr == ""
