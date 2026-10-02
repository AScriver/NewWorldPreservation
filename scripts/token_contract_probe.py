"""Local response-contract diagnostic, not an authentication implementation.

All incoming bodies are discarded by the existing probe. No forwarding,
official token replay, credential decoding, game protocol or memory changes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import threading

import bootstrap_probe as bootstrap

TOKEN_HOST = "tokenservice.amazongames.com"
TOKEN_PATH = "/games/new-world/tokens"
CASES = ("empty-object", "malformed-json", "model-with-account", "model-without-account")


def response_case(name):
    # Current-binary model-read evidence supports these SYNTHETIC candidates.
    # Serving one does not establish current client or downstream acceptance.
    cases = {"empty-object": b"{}", "malformed-json": b"{"}
    if name in cases:
        return cases[name]
    if name not in CASES:
        raise ValueError("Unknown controlled response case")
    fixture = Path(__file__).resolve().parents[1] / "tests/fixtures/connectivity/current-token-parser-candidate.json"
    model = json.loads(fixture.read_text(encoding="utf-8"))
    if name == "model-without-account":
        del model["account"]
    return json.dumps(model, sort_keys=True, separators=(",", ":")).encode("utf-8")


class TokenContractHandler(bootstrap.BootstrapHandler):
    def respond(self, status, *, authentication=False):
        if (status != 501 or self.command != "POST" or self.path != TOKEN_PATH
                or self.server.safe_hostname(self.headers.get("Host")) != TOKEN_HOST):
            return super().respond(status, authentication=authentication)
        body = self.server.token_response
        self.emit("HTTP_PATH_TEMPLATE", path_template=TOKEN_PATH,
                  observation="fixed_owned_test_route")
        self.emit("TOKEN_SESSION_REQUEST", route="games_new_world_tokens", request_body_saved=False,
                  semantics="request_observed_not_auth_success")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
        self.close_connection = True
        self.emit("HTTP_RESPONSE", status=200, semantics="controlled_contract_experiment_not_authentication")
        self.emit("TOKEN_CONTRACT_TEST_RESPONSE", status=200, case=self.server.token_case,
                  response_bytes=len(body), response_sha256=hashlib.sha256(body).hexdigest(),
                  authentication_success=False, client_model_acceptance_observed=False)


def make_server(bind, port, certificates, events, descriptor, *, case):
    body = response_case(case)
    server = bootstrap.make_server(bind, port, certificates, events, descriptor,
                                   token_routing="original-hostnames")
    server.RequestHandlerClass = TokenContractHandler
    server.token_response = body
    server.token_case = case
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
        events.emit("TOKEN_CONTRACT_LISTENING", bind=options.bind, port=server.server_port,
                    case=options.case, authentication_implemented=False, game_transport_implemented=False)
        timer.start()
        server.serve_forever(poll_interval=0.1)
    finally:
        timer.cancel()
        timer.join()
        server.server_close()
        events.emit("TOKEN_CONTRACT_STOPPED")
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
