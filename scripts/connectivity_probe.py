"""Original, loopback-only HTTPS diagnostic. No game authentication or forwarding.

No raw URLs, query strings, header values or request bodies enter the log. TLS
is delegated to Python/OpenSSL, not an invented New World protocol parser.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import re
import socket
import ssl
import threading
import uuid
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

WORKSPACE = Path(__file__).resolve().parents[1]
MAX_BODY = 65536


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class EventLog:
    """One append-free evidence file per run, flushed on every transition."""

    def __init__(self, path: Path):
        self.path = path
        self.run_id = str(uuid.uuid4())
        self._stream = path.open("x", encoding="utf-8")
        self._lock = threading.Lock()
        self._sequence = 0

    def emit(self, state: str, *, connection_id: str | None = None, **metadata):
        with self._lock:
            self._sequence += 1
            event = {"schema": 1, "timestamp_utc": timestamp(), "event_sequence": self._sequence,
                     "run_id": self.run_id, "state": state, "connection_id": connection_id,
                     "client_identity": "unattributed", "evidence_source": "local_probe",
                     **metadata}
            self._stream.write(json.dumps(event, sort_keys=True) + "\n")
            self._stream.flush()

    def close(self):
        self._stream.close()


def generate_certificates(directory: Path, hostnames: list[str]) -> dict:
    """Fresh short-lived CA and SAN leaf; CA key never saved; no trust-store edits."""
    names = sorted(set(hostnames))
    if not names or any(len(name) > 253 or not re.fullmatch(
            r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?", name) for name in names):
        raise ValueError("Explicit ASCII DNS hostnames required; no URLs or wildcards")
    directory.mkdir(parents=True, exist_ok=False)
    now = datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,
                                           "NewWorldPreservation local probe " + uuid.uuid4().hex[:12])])
    ca = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name)
          .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=7))
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False), critical=True)
          .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False)
          .sign(ca_key, hashes.SHA256()))
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, names[0])])
    leaf = (x509.CertificateBuilder().subject_name(server_name).issuer_name(ca_name)
            .public_key(server_key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=7))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.KeyUsage(True, False, True, False, False, False, False, False, False), critical=True)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(server_key.public_key()), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False)
            .add_extension(x509.SubjectAlternativeName(
                [x509.DNSName(name) for name in names] +
                [x509.IPAddress(ipaddress.ip_address(value)) for value in ["127.0.0.1", "::1"]]), critical=False)
            .sign(ca_key, hashes.SHA256()))
    (directory / "ca.pem").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    (directory / "server.pem").write_bytes(leaf.public_bytes(serialization.Encoding.PEM))
    (directory / "server.key").write_bytes(server_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    manifest = {"created_at_utc": timestamp(), "dns_sans": names, "ip_sans": ["127.0.0.1", "::1"],
                "ca_sha256": ca.fingerprint(hashes.SHA256()).hex(),
                "leaf_sha256": leaf.fingerprint(hashes.SHA256()).hex(),
                "expires_at_utc": leaf.not_valid_after_utc.isoformat(), "trust_store_modified": False}
    (directory / "certificate-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def route_id(target: str) -> tuple[str, str]:
    """Only allowlisted route classes. Never export caller-controlled path pieces."""
    try:
        path = urlsplit(target).path
    except ValueError:
        return "unclassified", "none"
    fixed = {"/__probe/health": ("probe_health", "probe_control"),
             "/STEAM_APP_ID.1063730.json": ("channel_discovery", "historical_first_light"),
             "/prod/credentials/omni": ("credentials_omni", "historical_first_light"),
             "/credentials/omni": ("credentials_omni", "historical_first_light"),
             "/prod/game/getlogininfo": ("login_info", "historical_first_light")}
    if path in fixed:
        return fixed[path]
    if any(path == prefix or path.startswith(prefix + "/") for prefix in
           ["/prod/game/login/queue", "/prod/users/login_queue"]):
        return "login_queue", "historical_first_light"
    return "unclassified", "none"


def safe_reason(exception: BaseException) -> str:
    # OpenSSL mnemonic only, never arbitrary exception text (which may contain data).
    value = getattr(exception, "reason", None)
    if isinstance(value, str) and re.fullmatch(r"[A-Z0-9_]{1,100}", value):
        return value
    return type(exception).__name__


class ProbeHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "LocalConnectivityProbe"
    sys_version = ""

    def log_message(self, format, *args):
        # BaseHTTPRequestHandler otherwise logs raw request lines on errors.
        pass

    def emit(self, state, **metadata):
        self.server.events.emit(state, connection_id=self.request.probe_connection_id, **metadata)

    def handle(self):
        try:
            super().handle()
        except (ssl.SSLError, OSError, TimeoutError) as failure:
            self.emit("TLS_FAILED" if isinstance(failure, ssl.SSLError) else "HTTP_IO_FAILED",
                      phase="http", reason=safe_reason(failure))

    def send_error(self, code, message=None, explain=None):
        self.emit("HTTP_REJECTED", status=code, reason="malformed_or_unsupported_http")
        self.respond(code)

    def respond(self, status, *, authentication=False):
        body = json.dumps({"probe": "connectivity-only", "authentication_implemented": False}).encode("ascii")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if getattr(self, "command", None) != "HEAD":
            self.wfile.write(body)
        self.wfile.flush()
        self.close_connection = True
        self.emit("HTTP_RESPONSE", status=status, semantics="probe_control" if status == 200 else "diagnostic_rejection")
        if authentication:
            self.emit("AUTHENTICATION_RESPONSE", status=status, authentication_success=False,
                      semantics="diagnostic_rejection", route_basis="historical_first_light")

    def handle_request(self):
        lengths = self.headers.get_all("Content-Length", [])
        if self.headers.get("Transfer-Encoding") or len(lengths) > 1 or (
                lengths and (not re.fullmatch(r"[0-9]{1,8}", lengths[0]) or int(lengths[0]) > MAX_BODY)):
            self.send_error(400)
            return
        length = int(lengths[0]) if lengths else 0
        route, basis = route_id(self.path)
        method = self.command if self.command in {"GET", "POST", "HEAD", "PUT", "PATCH", "DELETE", "OPTIONS"} else "OTHER"
        self.emit("HTTP_REQUEST", method=method, route=route, route_basis=basis,
                  declared_body_bytes=length, authorization_present="Authorization" in self.headers,
                  cookie_present="Cookie" in self.headers,
                  host=self.server.safe_hostname(self.headers.get("Host")))
        if route == "credentials_omni":
            self.emit("AUTHENTICATION_REQUEST", route=route, route_basis=basis, semantics="route_observed_only")
        elif route in {"login_queue", "login_info"}:
            self.emit("GAME_SESSION_SELECTION_REQUEST", route=route, route_basis=basis, semantics="route_observed_only")
        # Bounded in-memory discard; never parse credentials or persist bodies.
        if length and len(self.rfile.read(length)) != length:
            self.emit("HTTP_REJECTED", status=400, reason="truncated_body")
            self.respond(400)
            return
        self.respond(200 if route == "probe_health" and method in {"GET", "HEAD"} else 501,
                     authentication=route == "credentials_omni")

    do_GET = do_POST = do_HEAD = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = handle_request


class ProbeServer(ThreadingHTTPServer):
    daemon_threads = False  # server_close waits for bounded request workers.
    block_on_close = True
    allow_reuse_address = False

    def safe_hostname(self, value):
        if value is None:
            return None
        if value.lower() in self.allowed_hosts:
            return value.lower()
        if value.lower() in {"[::1]", "[::1]:" + str(self.server_port)}:
            return value.lower()
        # HTTP Host can include our port. Don't export arbitrary header contents.
        if value.lower() in {name + ":" + str(self.server_port) for name in self.allowed_hosts}:
            return value.lower()
        return "<unrecognized>"

    def finish_request(self, request, client_address):
        connection_id = str(uuid.uuid4())
        peer = {"address": client_address[0], "port": client_address[1]}
        self.events.emit("CONNECTION_ATTEMPT", connection_id=connection_id,
                         observation="server_tcp_accept", peer=peer,
                         local={"address": self.server_address[0], "port": self.server_address[1]})
        tls_socket = None
        request.settimeout(3)
        try:
            tls_socket = self.context.wrap_socket(request, server_side=True, do_handshake_on_connect=False)
            tls_socket.probe_connection_id = connection_id
            tls_socket.do_handshake()
            self.events.emit("TLS_ESTABLISHED", connection_id=connection_id,
                             tls_version=tls_socket.version(), cipher=tls_socket.cipher()[0],
                             selected_alpn=tls_socket.selected_alpn_protocol(),
                             observation="server_handshake_finished_not_proof_of_client_trust")
            self.RequestHandlerClass(tls_socket, client_address, self)
        except (ssl.SSLError, OSError, TimeoutError) as failure:
            self.events.emit("TLS_FAILED", connection_id=connection_id, phase="handshake",
                             reason=safe_reason(failure))
        finally:
            if tls_socket is not None:
                tls_socket.close()
            self.events.emit("CONNECTION_CLOSED", connection_id=connection_id)

    def handle_error(self, request, client_address):
        # No traceback containing parsed URLs/header/body values in stdout.
        self.events.emit("PROBE_INTERNAL_ERROR", reason="request_worker_failed")


def make_server(bind: str, port: int, certificates: Path, events: EventLog) -> ProbeServer:
    if bind not in {"127.0.0.1", "::1"}:
        raise ValueError("This diagnostic only permits explicit loopback addresses")
    manifest = json.loads((certificates / "certificate-manifest.json").read_text(encoding="utf-8"))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(str(certificates / "server.pem"), str(certificates / "server.key"))
    context.set_alpn_protocols(["http/1.1"])
    server_class = ProbeServer
    if bind == "::1":
        class IPv6ProbeServer(ProbeServer):
            address_family = socket.AF_INET6
        server_class = IPv6ProbeServer
    server = server_class((bind, port), ProbeHandler)
    server.events = events
    server.context = context
    server.allowed_hosts = set(manifest["dns_sans"] + manifest["ip_sans"])

    def sni_observed(tls_socket, name, selected_context):
        events.emit("TLS_CLIENT_HELLO", connection_id=tls_socket.probe_connection_id,
                    observation="openssl_sni_callback", sni=server.safe_hostname(name))

    context.sni_callback = sni_observed
    return server


def private_directory(value: str) -> Path:
    path = Path(value).resolve()
    if not any(path.is_relative_to(WORKSPACE / name) for name in ["private", ".scratch"]):
        raise ValueError("Certificates/logs must remain under this workspace's ignored private/ or .scratch/")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("certificates", help="Generate fresh local CA/leaf; does not install CA")
    create.add_argument("--directory", required=True)
    create.add_argument("--hostname", action="append", default=None)
    serve = commands.add_parser("serve", help="Loopback TLS/SNI/HTTP probe, no authentication/forwarding")
    serve.add_argument("--certificates", required=True)
    serve.add_argument("--log", required=True)
    serve.add_argument("--bind", choices=["127.0.0.1", "::1"], default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8443)
    serve.add_argument("--duration", type=int, default=60, help="Bounded lifetime in seconds (1..600)")
    options = parser.parse_args()
    if options.command == "certificates":
        manifest = generate_certificates(private_directory(options.directory), options.hostname or ["localhost"])
        print(json.dumps({"state": "PROBE_CERTIFICATES_CREATED", **manifest}))
        return 0
    if not 1 <= options.duration <= 600:
        parser.error("duration must be 1..600 seconds")
    log_path = private_directory(options.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    events = EventLog(log_path)
    server = None
    timer = None
    try:
        server = make_server(options.bind, options.port, private_directory(options.certificates), events)
        events.emit("PROBE_LISTENING", bind=options.bind, port=server.server_port,
                    tls_minimum="TLSv1.2", alpn_supported=["http/1.1"],
                    dns_observed=False, new_world_client_observed=False,
                    authentication_implemented=False, game_transport_implemented=False)
        print(json.dumps({"timestamp_utc": timestamp(), "state": "PROBE_LISTENING",
                          "bind": options.bind, "port": server.server_port, "run_id": events.run_id}), flush=True)
        timer = threading.Timer(options.duration, server.shutdown)
        timer.start()
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if timer is not None:
            timer.cancel()
            timer.join()
        if server is not None:
            server.server_close()
        events.emit("PROBE_STOPPED")
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
