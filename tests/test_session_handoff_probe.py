import hashlib
import json
from pathlib import Path
import sys
import threading

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import session_handoff_probe as contract
from test_token_contract_probe import exchange, events


@pytest.fixture(params=contract.CASES)
def endpoint(tmp_path, request):
    certificates = tmp_path / "certificates"
    bootstrap = contract.credentials.token.bootstrap
    bootstrap.probe.generate_certificates(certificates, [bootstrap.BOOTSTRAP_HOST, contract.credentials.token.TOKEN_HOST, "prod.newworld.com"])
    path = tmp_path / "events.jsonl"
    event_log = bootstrap.probe.EventLog(path)
    descriptor = bootstrap.load_local_descriptor(ROOT / "tests/fixtures/connectivity/local-channel-token-hostnames.json", token_routing="original-hostnames")
    server = contract.make_server("127.0.0.1", 0, certificates, event_log, descriptor, case=request.param)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    yield server, certificates, path
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
    assert not thread.is_alive()
    event_log.close()


def request_discovery(endpoint, **overrides):
    options = dict(method="GET", host=contract.credentials.token.bootstrap.BOOTSTRAP_HOST,
                   path="/prod/game/getlogininfo/PRIVATE-IDENTIFIER-DO-NOT-EXPORT/omni",
                   authorization="AWS4-HMAC-SHA256 SYNTHETIC-SIGNATURE-DO-NOT-EXPORT")
    options.update(overrides)
    return exchange(endpoint, **options)


def test_current_login_info_shape_returned_without_exporting_identity_or_signature(endpoint):
    response = request_discovery(endpoint)
    headers, body = response.split(b"\r\n\r\n", 1)
    assert headers.startswith(b"HTTP/1.1 200")
    assert body == contract.response_case(endpoint[0].discovery_case)
    records = events(endpoint)
    proof = next(r for r in records if r["state"] == "LOGIN_INFO_CONTRACT_TEST_RESPONSE")
    assert proof["response_sha256"] == hashlib.sha256(body).hexdigest()
    assert not proof["private_game_ticket_issued"] and not proof["world_entry_proven"]
    assert "PRIVATE-IDENTIFIER-DO-NOT-EXPORT" not in json.dumps(records)
    assert "SYNTHETIC-SIGNATURE-DO-NOT-EXPORT" not in json.dumps(records)
    assert any(r["state"] == "GAME_SESSION_SELECTION_REQUEST" for r in records)


@pytest.mark.parametrize("overrides", [
    {"method":"POST"}, {"authorization":None}, {"host":contract.credentials.token.TOKEN_HOST},
    {"path":"https://d2c74t4zimux3r.cloudfront.net/prod/game/getlogininfo/a/omni"},
    {"path":"/prod/game/getlogininfo/a/omni#PRIVATE-FRAGMENT"},
    {"path":"/prod/game/getlogininfo/a/b/omni"},
    {"path":"/prod/game/login/queue"}, {"body":b"SYNTHETIC-PRIVATE-BODY"},
])
def test_unestablished_paths_methods_hosts_or_framing_are_not_successfully_served(endpoint, overrides):
    assert request_discovery(endpoint,**overrides).startswith(b"HTTP/1.1 501")
    records = events(endpoint)
    assert not any(r["state"] == "LOGIN_INFO_CONTRACT_TEST_RESPONSE" for r in records)
    assert "SYNTHETIC-PRIVATE-BODY" not in json.dumps(records)


def test_synthetic_model_cases_differ_only_by_character_rows():
    seeded = json.loads(contract.response_case("seed-character"))["LoginInfoList"]
    empty = json.loads(contract.response_case("empty-characters"))["LoginInfoList"]
    assert empty["Characters"] == []
    assert seeded["Worlds"] == empty["Worlds"]
    assert seeded["Characters"][0]["WorldId"] == seeded["Worlds"][0]["WorldId"]
    assert isinstance(seeded["Worlds"][0]["WorldStatus"],str)
    assert set(seeded["Worlds"][0]["WorldMetrics"]) == {"QueueSize","QueueWaitTimeSec","WorldAgeDays"}
    assert "worlds" not in json.loads(contract.response_case("seed-character"))


def test_unknown_case_refused_before_certificates_or_bind():
    with pytest.raises(ValueError):
        contract.make_server("127.0.0.1",0,Path("not-read"),None,{},case="assume-world-ready")


@pytest.mark.parametrize("target,expected", [
    ("/prod/game/getlogininfo/PRIVATE-ID/omni", {"path_matches_candidate":True,"raw_target_matches_candidate":True,"query_present":False,"absolute_form":False}),
    ("/prod/game/getlogininfo/PRIVATE-ID/omni?private=SECRET", {"path_matches_candidate":True,"raw_target_matches_candidate":False,"query_present":True,"absolute_form":False}),
    ("https://SECRET.invalid/prod/game/getlogininfo/PRIVATE-ID/omni", {"path_matches_candidate":True,"raw_target_matches_candidate":False,"query_present":False,"absolute_form":True}),
    ("/prod/game/getlogininfo/PRIVATE-ID/omni/", {"path_matches_candidate":False,"raw_target_matches_candidate":False,"trailing_slash":True}),
])
def test_uri_shape_diagnostics_export_flags_not_uri_values(target, expected):
    shape = contract.login_info_target_shape(target)
    assert all(shape[key] is value for key,value in expected.items())
    assert "PRIVATE-ID" not in json.dumps(shape) and "SECRET" not in json.dumps(shape)


def test_observed_query_shape_is_served_without_exporting_query_or_identity(endpoint):
    response = request_discovery(endpoint,path="/prod/game/getlogininfo/PRIVATE-ID/omni?private=SECRET")
    assert response.startswith(b"HTTP/1.1 200")
    assert response.split(b"\r\n\r\n",1)[1] == contract.response_case(endpoint[0].discovery_case)
    records = events(endpoint)
    shape = next(item for item in records if item["state"] == "LOGIN_INFO_ROUTE_GUARD")
    assert shape["path_matches_candidate"] and not shape["raw_target_matches_candidate"]
    assert shape["query_present"] and not shape["uri_values_saved"]
    assert "PRIVATE-ID" not in json.dumps(records) and "SECRET" not in json.dumps(records)


def test_unrelated_and_malformed_targets_have_no_diagnostic():
    assert contract.login_info_target_shape("/unrelated/SECRET") is None
    assert contract.login_info_target_shape("https://[invalid") is None
