"""Loopback current-channel diagnostic; all authentication still rejects.

An HTTP200 channel response is NOT client acceptance or authentication success.
No forwarding, request-body capture, token decoding, or official endpoints.
"""
import argparse
import hashlib
import threading
from urllib.parse import urlsplit

import connectivity_probe as probe
from channel_descriptor import encode_local_descriptor, load_local_descriptor

BOOTSTRAP_HOST = "d2c74t4zimux3r.cloudfront.net"
BOOTSTRAP_PATH = "/STEAM_APP_ID.1063730.json"
PUBLIC_ROUTE_WORDS = frozenset({"prod", "v1", "v2", "auth", "authenticate", "login", "logout", "game", "games",
    "new-world", "session", "sessions", "steam", "credentials", "omni", "token", "tokens", "exchange",
    "users", "accounts", "queue", "login_queue", "getlogininfo", ".well-known", "openid-configuration"})


def path_template(target):
    """Only fixed public words survive; all query/fragment/unknown pieces discarded."""
    try:
        path = urlsplit(target).path
    except ValueError:
        return "<unclassified>"
    if path == BOOTSTRAP_PATH:
        return BOOTSTRAP_PATH
    if path == "/__probe/health":
        return "/__probe/health"
    parts = path.split("/")
    if not path.startswith("/") or len(parts) > 12:
        return "<unclassified>"
    return "/" + "/".join(word if word in PUBLIC_ROUTE_WORDS else "<redacted>" for word in parts[1:] if word)


class BootstrapHandler(probe.ProbeHandler):
    def respond(self, status, *, authentication=False):
        if status != 501:
            # Parser errors may happen before BaseHTTPRequestHandler sets headers.
            return super().respond(status, authentication=authentication)
        self.emit("HTTP_PATH_TEMPLATE", path_template=path_template(self.path),
                  observation="fixed_public_words_only_not_raw_target_or_protocol_semantics")
        hostname = self.server.safe_hostname(self.headers.get("Host"))
        allowed = {BOOTSTRAP_HOST, BOOTSTRAP_HOST + ":" + str(self.server.server_port)}
        if (self.command == "GET" and self.path == BOOTSTRAP_PATH
                and hostname in allowed and self.headers.get("Content-Length", "0") == "0"
                and "Authorization" not in self.headers and "Cookie" not in self.headers):
            body = self.server.channel_payload
            self.send_response(200)
            # Matches the observed public resource's MIME, not a guessed auth API.
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()
            self.close_connection = True
            self.emit("HTTP_RESPONSE", status=200, semantics="local_channel_descriptor_not_authentication")
            self.emit("CHANNEL_DESCRIPTOR_RESPONSE", status=200, response_bytes=len(body),
                      descriptor_sha256=self.server.channel_sha256, destinations="bootstrap_loopback_mapping_only",
                      client_acceptance_observed=False, authentication_success=False)
            return
        super().respond(status, authentication=authentication)


def make_server(bind, port, certificates, events, descriptor):
    # Validate containment before opening a socket or reading certificate material.
    body = encode_local_descriptor(descriptor)
    server = probe.make_server(bind, port, certificates, events)
    server.RequestHandlerClass = BootstrapHandler
    server.channel_payload = body
    server.channel_sha256 = hashlib.sha256(body).hexdigest()
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--descriptor", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--bind", choices=["127.0.0.1", "::1"], default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--observe-local-socket-owner", action="store_true")
    options = parser.parse_args()
    if not 1 <= options.duration <= 600:
        parser.error("duration must be 1..600 seconds")
    descriptor = load_local_descriptor(probe.private_directory(options.descriptor))
    certificates = probe.private_directory(options.certificates)
    log_path = probe.private_directory(options.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    events = probe.EventLog(log_path)
    server = None
    timer = None
    try:
        server = make_server(options.bind, options.port, certificates, events, descriptor)
        if options.observe_local_socket_owner:
            from windows_tcp_owner import owner_of_connection
            server.socket_owner_lookup = owner_of_connection
        events.emit("BOOTSTRAP_LISTENING", bind=options.bind, port=server.server_port,
                    descriptor_sha256=server.channel_sha256, tls_minimum="TLSv1.2",
                    authentication_implemented=False, game_transport_implemented=False,
                    client_acceptance_observed=False)
        timer = threading.Timer(options.duration, server.shutdown)
        timer.start()
        server.serve_forever(poll_interval=0.1)
    finally:
        if timer is not None:
            timer.cancel()
            timer.join()
        if server is not None:
            server.server_close()
        events.emit("BOOTSTRAP_STOPPED")
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
