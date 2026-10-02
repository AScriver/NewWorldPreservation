import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import credentials_contract_probe as contract


def load():
    return json.loads((ROOT / "tests/fixtures/connectivity/current-credentials-contract-result.json").read_text())


def test_owned_credentials_response_progresses_to_gateway_but_not_game_handoff():
    fixture = load()
    requests = fixture["requests"]
    credentials = next(r for r in requests if r["path_template"] == contract.CREDENTIALS_PATH)
    token = next(r for r in requests if r["path_template"] == contract.token.TOKEN_PATH)
    gateway = [r for r in requests if r["path_template"] == "/prod/game/getlogininfo/<redacted>/omni"]
    assert gateway
    assert token["timestamp_utc"] <= credentials["timestamp_utc"] < gateway[0]["timestamp_utc"]
    assert credentials["case"] == "flat-numeric-expiration"
    assert credentials["response_status"] == 200
    assert credentials["response_sha256"] == hashlib.sha256(contract.response_case(credentials["case"])).hexdigest()
    assert credentials["response_bytes"] == 188
    assert credentials["authorization_present"] and not credentials["cookie_present"]
    assert credentials["tls_version"] == "TLSv1.2"
    assert credentials["host"] == credentials["sni"] == contract.token.bootstrap.BOOTSTRAP_HOST
    assert all(r["method"] == "GET" and r["response_status"] == 501 for r in gateway)
    assert all(r["owner_process_id"] == fixture["client"]["process_id"] for r in requests)
    assert not any(fixture["limits"][k] for k in ("game_session_handoff","game_transport","world_entry","actor_spawn","milestone_1","gateway_signature_verified"))


def test_client_log_marker_order_is_preserved_without_exporting_identity():
    fixture = load()
    records = fixture["owned_client_log"]["records"]
    sdk = next(r for r in records if r["state"] == "CLIENT_OMNI_SESSION_RESULT")
    campfire = next(r for r in records if r["state"] == "CLIENT_CAMPFIRE_LOGIN_COMPLETE_MARKER")
    gateway = next(r for r in records if r["state"] == "CLIENT_GATEWAY_CONFIGURE_LOGIN_MARKER")
    assert sdk["result_code"] == 0
    assert sdk["line"] < campfire["line"] < gateway["line"]
    assert all(r["timestamp_basis"] == "extraction_not_client_event" for r in records)
    assert fixture["owned_client_log"]["stable_during_read"]
    assert fixture["user_observation"]["character_selection_frontend_visible"]
    assert not fixture["limits"]["pristine_user_cache"]


def test_candidate_and_exercised_sources_match_recorded_provenance():
    receipt = json.loads((ROOT / "research/evidence/current-credentials-contract.json").read_text())
    for filename in ("scripts/credentials_contract_probe.py", "tests/fixtures/connectivity/current-credentials-parser-candidate.json"):
        assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == receipt["sources"][filename]
    assert receipt["exercised_sources_dirty"]
    assert receipt["retained_ca"]["reused_not_reimported"]
    assert not receipt["live_negative_credentials_controls_run"]
    assert receipt["claims"]["credentials_response_accepted"]
    assert not receipt["claims"]["game_session_handoff"]
