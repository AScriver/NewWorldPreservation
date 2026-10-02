"""Version-bound observed metadata; not a replay or proof of world entry."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests/fixtures/connectivity/current-login-info-result.json"


def test_failed_guard_is_not_misreported_as_candidate_rejection():
    cases = json.loads(FIXTURE.read_text())["cases"]
    for case in cases[:2]:
        assert not case["login_info_candidate_sent"]
        assert not case["character_rendered_user_report"]
        assert all(item["http_status"] == 501 for item in case["observations"])
    shape = cases[1]["observations"][0]["target_shape"]
    assert shape["query_present"] and shape["path_matches_candidate"]
    assert not shape["raw_target_matches_candidate"] and not shape["absolute_form"]
    assert shape["host_matches"] and shape["method_matches"] and shape["empty_body"]


def test_observed_character_selection_then_queue_is_not_world_entry():
    case = json.loads(FIXTURE.read_text())["cases"][-1]
    discovery, queue = case["observations"]
    assert discovery["method"] == "GET" and discovery["http_status"] == 200
    assert discovery["request_body_bytes"] == 0 and discovery["response_bytes"] == 965
    assert queue["method"] == "POST" and queue["http_status"] == 501 and queue["request_body_bytes"] == 644
    assert discovery["timestamp_utc"] < queue["timestamp_utc"]
    assert case["character_rendered_user_report"] and case["play_clicked_user_report"]
    assert not case["game_session_ticket_issued"] and not case["world_entry_proven"]
    for item in (discovery, queue):
        assert item["exact_owned_client_tcp_tuple"] and not item["request_values_saved"]


def test_received_synthetic_model_and_exercised_sources_remain_pinned():
    case = json.loads(FIXTURE.read_text())["cases"][-1]
    model = json.loads((ROOT / "tests/fixtures/connectivity/current-login-info-candidate.json").read_text())
    body = json.dumps(model,sort_keys=True,separators=(",", ":")).encode()
    assert hashlib.sha256(body).hexdigest() == case["observations"][0]["response_sha256"]
    receipt = json.loads((ROOT / "research/evidence/current-login-info.json").read_text())
    for path, expected in receipt["sources"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    assert not receipt["game_transport_proven"] and not receipt["actor_spawn_proven"]
    assert not receipt["query_names_values_or_identifiers_exported"]
