"""Local discovery/session contract experiment; no gameplay or official auth.

Only current field-read-backed synthetic metadata. No incoming identifiers,
signature values, tickets or bodies are persisted or forwarded. Not a private
account implementation; use only an owned loopback trial under containment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import threading
from urllib.parse import urlsplit

import credentials_contract_probe as credentials

LOGIN_INFO_ROUTE = re.compile(r"/prod/game/getlogininfo/[^/?#]{1,128}/omni")
CASES = ("empty-characters", "seed-character")


def login_info_target_shape(target):
    """Fixed flags/counts only; never return caller-controlled URI content."""
    try:
        parsed = urlsplit(target)
    except ValueError:
        return None
    if not parsed.path.startswith("/prod/game/getlogininfo/"):
        return None
    segments = parsed.path.split("/")
    return {
        "path_matches_candidate": bool(LOGIN_INFO_ROUTE.fullmatch(parsed.path)),
        "raw_target_matches_candidate": bool(LOGIN_INFO_ROUTE.fullmatch(target)),
        "query_present": "?" in target,
        "fragment_present": "#" in target,
        "absolute_form": bool(parsed.scheme or parsed.netloc),
        "trailing_slash": parsed.path.endswith("/"),
        "repeated_separator": "//" in parsed.path,
        "path_segment_count": min(len(segments) - 1, 65536),
        "identifier_length": min(len(segments[4]), 65536) if len(segments) > 4 else 0,
    }


def response_case(name):
    if name not in CASES:
        raise ValueError("Unknown controlled discovery case")
    fixture = Path(__file__).resolve().parents[1] / "tests/fixtures/connectivity/current-login-info-candidate.json"
    model = json.loads(fixture.read_text(encoding="utf-8"))
    if name == "empty-characters":
        model["LoginInfoList"]["Characters"] = []
    return json.dumps(model, sort_keys=True, separators=(",", ":")).encode("utf-8")


class SessionHandoffHandler(credentials.CredentialsContractHandler):
    def respond(self, status, *, authentication=False):
        shape = login_info_target_shape(getattr(self, "path", ""))
        if status == 501 and shape is not None:
            self.emit("LOGIN_INFO_ROUTE_GUARD", **shape,
                      method_matches=self.command == "GET",
                      host_matches=self.server.safe_hostname(self.headers.get("Host")) == credentials.token.bootstrap.BOOTSTRAP_HOST,
                      authorization_present=bool(self.headers.get("Authorization")),
                      empty_body=int(self.headers.get("Content-Length", "0")) == 0,
                      uri_values_saved=False)
        # The owned current client sends a query (observed 2026-10-02). This
        # diagnostic serves a fixed model by path; query values stay discarded.
        # Do not accept proxy absolute-form targets or fragments.
        if (status != 501 or self.command != "GET" or shape is None
                or not shape["path_matches_candidate"] or shape["absolute_form"] or shape["fragment_present"]
                or self.server.safe_hostname(self.headers.get("Host")) != credentials.token.bootstrap.BOOTSTRAP_HOST
                or not self.headers.get("Authorization")
                or int(self.headers.get("Content-Length", "0")) != 0):
            return super().respond(status, authentication=authentication)
        body = self.server.login_info_response
        self.emit("GAME_SESSION_SELECTION_REQUEST", route="current_gateway_login_info",
                  path_template="/prod/game/getlogininfo/<redacted>/omni",
                  request_identifier_saved=False, authorization_value_saved=False)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
        self.close_connection = True
        self.emit("HTTP_RESPONSE", status=200, semantics="synthetic_local_discovery_experiment")
        self.emit("LOGIN_INFO_CONTRACT_TEST_RESPONSE", status=200, case=self.server.discovery_case,
                  response_bytes=len(body), response_sha256=hashlib.sha256(body).hexdigest(),
                  synthetic_values_only=True, client_acceptance_observed=False,
                  private_game_ticket_issued=False, world_entry_proven=False)


def make_server(bind, port, certificates, events, descriptor, *, case):
    body = response_case(case)
    server = credentials.make_server(bind, port, certificates, events, descriptor, case="flat-numeric-expiration")
    server.RequestHandlerClass = SessionHandoffHandler
    server.login_info_response = body
    server.discovery_case = case
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--descriptor", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--bind", choices=["127.0.0.1", "::1"], default="127.0.0.1")
    parser.add_argument("--port", type=int, default=443)
    parser.add_argument("--duration", type=int, default=600)
    parser.add_argument("--observe-local-socket-owner", action="store_true")
    parser.add_argument("--case", choices=CASES, required=True)
    options = parser.parse_args()
    if not 1 <= options.duration <= 600:
        parser.error("duration must be 1..600 seconds")
    bootstrap = credentials.token.bootstrap
    certificates = bootstrap.probe.private_directory(options.certificates)
    descriptor = bootstrap.load_local_descriptor(bootstrap.probe.private_directory(options.descriptor), token_routing="original-hostnames")
    path = bootstrap.probe.private_directory(options.log)
    path.parent.mkdir(parents=True, exist_ok=True)
    events = bootstrap.probe.EventLog(path)
    server = make_server(options.bind, options.port, certificates, events, descriptor, case=options.case)
    if options.observe_local_socket_owner:
        from windows_tcp_owner import owner_of_connection
        server.socket_owner_lookup = owner_of_connection
    timer = threading.Timer(options.duration, server.shutdown)
    try:
        events.emit("SESSION_HANDOFF_PROBE_LISTENING", bind=options.bind, port=server.server_port,
                    case=options.case, game_transport_implemented=False, private_accounts_implemented=False)
        timer.start()
        server.serve_forever(poll_interval=0.1)
    finally:
        timer.cancel()
        timer.join()
        server.server_close()
        events.emit("SESSION_HANDOFF_PROBE_STOPPED")
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
