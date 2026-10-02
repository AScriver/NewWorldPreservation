"""Owned queue response experiment; no secure account/ticket/game implementation.

Only source-read-backed JSON members and original synthetic values. Request
bodies remain bounded-discarded by the existing handler. Query/header values
are not exported. Token clocks/signatures/readiness are candidate semantics,
not proven contracts. Unknown follow-up routes stay rejected.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import threading
from urllib.parse import urlsplit

import session_handoff_probe as selection

QUEUE_ROUTE = re.compile(r"/prod/game/login/queue/v2/[^/?#]{1,128}/omni")
CASES = ("token-empty", "token-loopback")


def queue_target_matches(target):
    try:
        parsed = urlsplit(target)
    except ValueError:
        return False
    return not (parsed.scheme or parsed.netloc or "#" in target) and bool(QUEUE_ROUTE.fullmatch(parsed.path))


def response_case(case):
    if case not in CASES:
        raise ValueError("Unknown queue contract case")
    path = Path(__file__).parents[1] / "tests/fixtures/connectivity/current-queue-parser-candidate.json"
    model = json.loads(path.read_text())
    if case == "token-empty":
        model["LoginQueueResponse"]["Token"] = {}
    return json.dumps(model,sort_keys=True,separators=(",", ":")).encode()


class QueueContractHandler(selection.SessionHandoffHandler):
    def respond(self, status, *, authentication=False):
        if (status != 501 or self.command != "POST" or not queue_target_matches(self.path)
                or self.server.safe_hostname(self.headers.get("Host")) != selection.credentials.token.bootstrap.BOOTSTRAP_HOST
                or not self.headers.get("Authorization") or int(self.headers.get("Content-Length","0")) == 0):
            return super().respond(status,authentication=authentication)
        body = self.server.queue_response
        self.emit("PRIVATE_QUEUE_CONTRACT_REQUEST",path_template="/prod/game/login/queue/v2/<redacted>/omni",
                  request_body_saved=False,request_schema_validated=False,query_values_saved=False,authorization_value_saved=False)
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Connection","close")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
        self.close_connection = True
        self.emit("HTTP_RESPONSE",status=200,semantics="synthetic_queue_contract_experiment")
        self.emit("PRIVATE_GAME_HANDOFF_CANDIDATE",case=self.server.queue_case,response_bytes=len(body),
                  response_sha256=hashlib.sha256(body).hexdigest(),synthetic_values_only=True,
                  destination="127.0.0.1:64003" if self.server.queue_case == "token-loopback" else None,
                  request_values_saved=False,secure_private_ticket_issued=False,client_acceptance_observed=False,
                  game_transport_established=False,world_entry_proven=False)


def make_server(bind, port, certificates, events, descriptor, *, case):
    body = response_case(case)
    server = selection.make_server(bind,port,certificates,events,descriptor,case="seed-character")
    server.RequestHandlerClass = QueueContractHandler
    server.queue_response,server.queue_case = body,case
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("certificates","descriptor","log"):
        parser.add_argument("--"+name,required=True)
    parser.add_argument("--bind",choices=["127.0.0.1","::1"],default="127.0.0.1")
    parser.add_argument("--port",type=int,default=443)
    parser.add_argument("--duration",type=int,default=600)
    parser.add_argument("--case",choices=CASES,required=True)
    parser.add_argument("--observe-local-socket-owner",action="store_true")
    options = parser.parse_args()
    if not 1 <= options.duration <= 600:
        parser.error("Duration1..600 required")
    bootstrap = selection.credentials.token.bootstrap
    certificates = bootstrap.probe.private_directory(options.certificates)
    descriptor = bootstrap.load_local_descriptor(bootstrap.probe.private_directory(options.descriptor),token_routing="original-hostnames")
    path = bootstrap.probe.private_directory(options.log)
    path.parent.mkdir(parents=True,exist_ok=True)
    events = bootstrap.probe.EventLog(path)
    server = make_server(options.bind,options.port,certificates,events,descriptor,case=options.case)
    if options.observe_local_socket_owner:
        from windows_tcp_owner import owner_of_connection
        server.socket_owner_lookup = owner_of_connection
    timer = threading.Timer(options.duration,server.shutdown)
    try:
        events.emit("QUEUE_CONTRACT_PROBE_LISTENING",bind=options.bind,port=server.server_port,case=options.case,
                    secure_private_accounts_implemented=False,game_transport_implemented=False)
        timer.start()
        server.serve_forever(poll_interval=0.1)
    finally:
        timer.cancel()
        timer.join()
        server.server_close()
        events.emit("QUEUE_CONTRACT_PROBE_STOPPED")
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
