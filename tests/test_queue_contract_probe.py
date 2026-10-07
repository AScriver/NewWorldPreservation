import json
from pathlib import Path
import sys
import threading

import pytest
ROOT = Path(__file__).parents[1]
sys.path.insert(0,str(ROOT / "scripts"))
import queue_contract_probe as contract
from test_token_contract_probe import exchange, events


@pytest.fixture(params=contract.CASES)
def endpoint(tmp_path,request):
    bootstrap = contract.selection.credentials.token.bootstrap
    certificates = tmp_path / "certificates"
    bootstrap.probe.generate_certificates(certificates,[bootstrap.BOOTSTRAP_HOST,contract.selection.credentials.token.TOKEN_HOST,"prod.newworld.com"])
    path = tmp_path / "events.jsonl"
    log = bootstrap.probe.EventLog(path)
    descriptor = bootstrap.load_local_descriptor(ROOT / "tests/fixtures/connectivity/local-channel-token-hostnames.json",token_routing="original-hostnames")
    server = contract.make_server("127.0.0.1",0,certificates,log,descriptor,case=request.param)
    thread = threading.Thread(target=server.serve_forever,kwargs={"poll_interval":0.05})
    thread.start()
    yield server,certificates,path
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
    assert not thread.is_alive()
    log.close()


def request_queue(endpoint,**overrides):
    options = dict(method="POST",host=contract.selection.credentials.token.bootstrap.BOOTSTRAP_HOST,
                   path="/prod/game/login/queue/v2/PRIVATE-ID/omni?private=SECRET-QUERY",
                   body=b"SECRET-REQUEST-BODY",authorization="SECRET-AUTHORIZATION")
    options.update(overrides)
    return exchange(endpoint,**options)


def test_synthetic_queue_case_returns_fixed_bytes_without_claiming_auth_or_transport(endpoint):
    response = request_queue(endpoint)
    assert response.startswith(b"HTTP/1.1 200")
    assert response.split(b"\r\n\r\n",1)[1] == contract.response_case(endpoint[0].queue_case)
    records = events(endpoint)
    proof = next(item for item in records if item["state"] == "PRIVATE_GAME_HANDOFF_CANDIDATE")
    assert not proof["secure_private_ticket_issued"] and not proof["game_transport_established"] and not proof["world_entry_proven"]
    assert proof["synthetic_values_only"] and not proof["request_values_saved"]
    assert "SECRET" not in json.dumps(records) and "PRIVATE-ID" not in json.dumps(records)
    request = next(item for item in records if item["state"] == "PRIVATE_QUEUE_CONTRACT_REQUEST")
    assert not request["request_schema_validated"]


@pytest.mark.parametrize("overrides", [
    {"method":"GET"},{"authorization":None},{"body":b""},
    {"host":contract.selection.credentials.token.TOKEN_HOST},
    {"path":"/prod/game/login/queue/v1/PRIVATE/omni"},
    {"path":"/prod/game/login/queue/v2/PRIVATE/omni#fragment"},
    {"path":"https://d2c74t4zimux3r.cloudfront.net/prod/game/login/queue/v2/PRIVATE/omni"},
    {"path":"/prod/users/login_queue/PRIVATE"},
])
def test_unknown_queue_paths_framing_or_authorization_are_not_served(endpoint,overrides):
    assert request_queue(endpoint,**overrides).startswith(b"HTTP/1.1 501")
    assert not any(item["state"] == "PRIVATE_GAME_HANDOFF_CANDIDATE" for item in events(endpoint))


def test_oversized_request_rejected_before_candidate_without_exporting_payload(endpoint):
    assert request_queue(endpoint,body=b"SECRET"*12000).startswith(b"HTTP/1.1 400")
    assert "SECRET" not in json.dumps(events(endpoint))


def test_synthetic_queue_identity_matches_original_local_selection_not_real_credentials():
    token = json.loads(contract.response_case("token-loopback"))["LoginQueueResponse"]["Token"]
    selected = json.loads(contract.selection.response_case("seed-character"))["LoginInfoList"]["Characters"][0]
    for name in ("CharacterId","WorldId","PersonaId"):
        assert token[name] == selected[name]
    assert token["RepAddress"] == "127.0.0.1:64003" and token["SteamUserId"] == ""
    assert isinstance(token["IssueTime"],float) and isinstance(token["GenerateTime"],float)
    root = json.loads(contract.response_case("token-loopback"))["LoginQueueResponse"]
    assert "Ready" not in root and "Ready" not in token
    assert json.loads(contract.response_case("token-empty"))["LoginQueueResponse"]["Token"] == {}


def test_unknown_case_refused_before_certificate_material_or_bind():
    with pytest.raises(ValueError):
        contract.make_server("127.0.0.1",0,Path("not-read"),None,{},case="assume-game-ready")


def test_user_stop_https_service_has_no_elapsed_timer(monkeypatch):
    stop = threading.Event()

    class Server:
        requests = 0
        timeout = None

        def handle_request(self):
            self.requests += 1
            if self.requests == 5:
                stop.set()

    def forbidden_timer(*_arguments):
        raise AssertionError("manual service must not schedule elapsed shutdown")
    monkeypatch.setattr(contract.threading, "Timer", forbidden_timer)
    server = Server()
    contract.serve(server, None, stop=stop)
    assert server.requests == 5 and server.timeout == 0.1


def test_manual_https_service_requires_explicit_stop_guard():
    with pytest.raises(ValueError, match="owned stop guard"):
        contract.serve(None, None)
