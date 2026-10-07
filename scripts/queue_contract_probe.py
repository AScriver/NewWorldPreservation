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
from contextlib import ExitStack

from private_trial_lifetime import UserStop, add_lifetime_options, resolve_lifetime_options
from urllib.parse import urlsplit

import session_handoff_probe as selection
from private_trial_character import (
    PrivateTrialCharacter, occupied_from_options, read_trial_character,
)

QUEUE_ROUTE = re.compile(r"/prod/game/login/queue/v2/[^/?#]{1,128}/omni")
CASES = ("token-empty", "token-loopback")


def queue_target_matches(target):
    try:
        parsed = urlsplit(target)
    except ValueError:
        return False
    return not (parsed.scheme or parsed.netloc or "#" in target) and bool(QUEUE_ROUTE.fullmatch(parsed.path))


def response_case(case, *, trial_character: PrivateTrialCharacter | None = None):
    if case not in CASES:
        raise ValueError("Unknown queue contract case")
    if trial_character is not None:
        if type(trial_character) is not PrivateTrialCharacter or case != "token-loopback":
            raise ValueError("trial_character requires token-loopback and an exact private record")
    path = Path(__file__).parents[1] / "tests/fixtures/connectivity/current-queue-parser-candidate.json"
    model = json.loads(path.read_text())
    if case == "token-empty":
        model["LoginQueueResponse"]["Token"] = {}
    elif trial_character is not None:
        queue = model["LoginQueueResponse"]
        token = queue["Token"]
        queue["TicketId"] = trial_character.ticket_id
        token.update(CharacterId=trial_character.character_id,
                     PersonaId=trial_character.persona_id,
                     TicketId=trial_character.ticket_id)
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


def make_server(bind, port, certificates, events, descriptor, *, case,
                trial_character: PrivateTrialCharacter | None = None):
    body = response_case(case, trial_character=trial_character)
    server = selection.make_server(bind,port,certificates,events,descriptor,
                                   case="seed-character", trial_character=trial_character)
    server.RequestHandlerClass = QueueContractHandler
    server.queue_response,server.queue_case = body,case
    return server


def serve(server, duration, *, stop=None):
    if duration is None:
        if stop is None:
            raise ValueError("user-stop lifetime requires an owned stop guard")
        server.timeout = 0.1
        while not stop.is_set():
            server.handle_request()
        return
    timer = threading.Timer(duration, server.shutdown)
    try:
        timer.start()
        server.serve_forever(poll_interval=0.1)
    finally:
        timer.cancel()
        timer.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("certificates","descriptor","log"):
        parser.add_argument("--"+name,required=True)
    parser.add_argument("--bind",choices=["127.0.0.1","::1"],default="127.0.0.1")
    parser.add_argument("--port",type=int,default=443)
    add_lifetime_options(parser)
    parser.add_argument("--case",choices=CASES,required=True)
    parser.add_argument("--observe-local-socket-owner",action="store_true")
    parser.add_argument("--trial-character")
    parser.add_argument("--trial-character-sha256")
    occupancy = parser.add_mutually_exclusive_group()
    occupancy.add_argument("--trial-known-empty-occupancy", action="store_true")
    occupancy.add_argument("--trial-occupied-low64", action="append")
    options = parser.parse_args()
    resolve_lifetime_options(parser, options, default_seconds=600)
    if options.trial_character is None:
        if (options.trial_known_empty_occupancy or options.trial_occupied_low64 or
                options.trial_character_sha256 is not None):
            parser.error("trial digest and occupancy require --trial-character")
        trial_character = None
    else:
        try:
            if options.trial_character_sha256 is None:
                raise ValueError("--trial-character-sha256 is required with --trial-character")
            occupied = occupied_from_options(options.trial_occupied_low64,
                                             options.trial_known_empty_occupancy)
            trial_character = read_trial_character(options.trial_character,
                occupied_keys=occupied, expected_sha256=options.trial_character_sha256)
            response_case(options.case, trial_character=trial_character)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
    with ExitStack() as resources:
        stop = (resources.enter_context(UserStop(options.until_stopped))
                if options.until_stopped is not None else None)
        return run_probe(options, trial_character, stop=stop)


def run_probe(options, trial_character, *, stop=None):
    bootstrap = selection.credentials.token.bootstrap
    certificates = bootstrap.probe.private_directory(options.certificates)
    descriptor = bootstrap.load_local_descriptor(bootstrap.probe.private_directory(options.descriptor),token_routing="original-hostnames")
    path = bootstrap.probe.private_directory(options.log)
    path.parent.mkdir(parents=True,exist_ok=True)
    events = bootstrap.probe.EventLog(path)
    server = make_server(options.bind,options.port,certificates,events,descriptor,
                         case=options.case, trial_character=trial_character)
    if options.observe_local_socket_owner:
        from windows_tcp_owner import owner_of_connection
        server.socket_owner_lookup = owner_of_connection
    try:
        events.emit("QUEUE_CONTRACT_PROBE_LISTENING",bind=options.bind,port=server.server_port,case=options.case,
                    secure_private_accounts_implemented=False,game_transport_implemented=False)
        serve(server, options.duration, stop=stop)
    finally:
        server.server_close()
        events.emit("QUEUE_CONTRACT_PROBE_STOPPED")
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
