import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests/fixtures/connectivity/current-queue-handoff-result.json"


def test_observed_queue_response_precedes_owned_udp_header_not_trusted_game_session():
    result = json.loads(FIXTURE.read_text())
    queue,transport = result["queue"],result["transport"]
    assert queue["method"] == "POST" and queue["http_status"] == 200 and queue["body_bytes"] == 644
    assert queue["exact_owned_client_tcp_tuple"] and not queue["request_values_saved"]
    assert not queue["request_schema_validated"]
    assert queue["timestamp_utc"] < transport["first"]["timestamp_utc"]
    assert transport["destination"] == "127.0.0.1:64003"
    assert transport["all_datagrams_bound_port_owned_by_fresh_client"] and not transport["datagram_reply_sent"]
    assert result["claims"]["handoff_to_owned_udp_observed"]
    assert not result["claims"]["game_dtls_trust_tested"] and not result["claims"]["game_handshake_complete"]
    assert not result["claims"]["world_loading_observed"] and not result["claims"]["actor_spawn_proven"]


def test_captured_header_metadata_does_not_claim_body_validation_or_negotiation():
    first = json.loads(FIXTURE.read_text())["transport"]["first"]
    assert first["datagram_bytes"] == 159 and first["first_record_bytes"] == 146
    assert first["datagram_class"] == "dtls_client_hello_header" and first["record_version"] == "DTLS1.2"
    assert first["record_epoch"] == 0 and first["first_record_complete"]
    assert not first["client_hello_body_validated"] and not first["negotiated_version_proven"]
    assert not first["payload_saved"] and not first["handshake_established"]


def test_received_synthetic_candidate_and_historical_sources_remain_pinned():
    fixture = json.loads(FIXTURE.read_text())
    model = json.loads((ROOT / "tests/fixtures/connectivity/current-queue-parser-candidate.json").read_text())
    response = json.dumps(model,sort_keys=True,separators=(",", ":")).encode()
    assert len(response) == fixture["queue"]["response_bytes"] == 829
    assert hashlib.sha256(response).hexdigest() == fixture["queue"]["response_sha256"]
    receipt = json.loads((ROOT / "research/evidence/current-queue-handoff.json").read_text())
    for path,expected in receipt["sources"].items():
        # Keep the exact historical live inputs after the #253 fresh-input change.
        source = (subprocess.check_output(["git", "show",
                  "bbadb9d0b2108637f7cc4edb8a7d77be5b9f45f1:" + path], cwd=ROOT)
                  if path in ("scripts/queue_contract_probe.py", "scripts/session_handoff_probe.py")
                  else (ROOT / path).read_bytes())
        assert hashlib.sha256(source).hexdigest() == expected
    assert not receipt["clock_units_and_expiry_verified"] and not receipt["downstream_signature_validation_verified"]
