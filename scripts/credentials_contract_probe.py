"""Owned-endpoint credentials contract experiment, not production authentication.

Reuse the verified bootstrap/token responses. Incoming credentials, headers and
bodies are never exported or forwarded. Only synthetic local response values.
Unknown gateway/session routes remain rejected until independently established.
"""
import argparse
import hashlib
import json
from pathlib import Path
import threading

import token_contract_probe as token

CREDENTIALS_PATH = "/prod/credentials/omni"
CASES = ("empty-object", "flat-numeric-expiration", "flat-string-expiration")


def response_case(name):
    if name == "empty-object":
        return b"{}"
    if name not in CASES:
        raise ValueError("Unknown controlled credentials case")
    fixture = Path(__file__).resolve().parents[1] / "tests/fixtures/connectivity/current-credentials-parser-candidate.json"
    model = json.loads(fixture.read_text(encoding="utf-8"))
    if name == "flat-string-expiration":
        # Historical mock comparison; not presumed compatible with this build.
        model["expiration"] = "2030-01-01T00:00:00Z"
    return json.dumps(model, sort_keys=True, separators=(",", ":")).encode("utf-8")


class CredentialsContractHandler(token.TokenContractHandler):
    def respond(self, status, *, authentication=False):
        if (status != 501 or self.command != "GET" or self.path != CREDENTIALS_PATH
                or self.server.safe_hostname(self.headers.get("Host")) != token.bootstrap.BOOTSTRAP_HOST
                or not self.headers.get("Authorization")
                or int(self.headers.get("Content-Length", "0")) != 0):
            return super().respond(status, authentication=authentication)
        body = self.server.credentials_response
        self.emit("HTTP_PATH_TEMPLATE", path_template=CREDENTIALS_PATH,
                  observation="fixed_owned_test_route")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
        self.close_connection = True
        self.emit("HTTP_RESPONSE", status=200, semantics="synthetic_owned_credentials_experiment")
        self.emit("CREDENTIALS_CONTRACT_TEST_RESPONSE", status=200,
                  case=self.server.credentials_case, response_bytes=len(body),
                  response_sha256=hashlib.sha256(body).hexdigest(), synthetic_values_only=True,
                  official_authentication_success=False, client_acceptance_observed=False)


def make_server(bind, port, certificates, events, descriptor, *, case):
    body = response_case(case)
    server = token.make_server(bind, port, certificates, events, descriptor, case="model-with-account")
    server.RequestHandlerClass = CredentialsContractHandler
    server.credentials_response = body
    server.credentials_case = case
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
    bootstrap = token.bootstrap
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
        events.emit("CREDENTIALS_CONTRACT_LISTENING", bind=options.bind, port=server.server_port,
                    case=options.case, synthetic_values_only=True, game_transport_implemented=False)
        timer.start()
        server.serve_forever(poll_interval=0.1)
    finally:
        timer.cancel()
        timer.join()
        server.server_close()
        events.emit("CREDENTIALS_CONTRACT_STOPPED")
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
