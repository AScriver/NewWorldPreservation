"""Build-bound observed-metadata regressions; never launches a client or reads its log."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import token_contract_probe as contract

FIXTURE_PATH = ROOT / "tests/fixtures/connectivity/current-token-contract-result.json"
OBSERVED = json.loads(FIXTURE_PATH.read_text())


@pytest.mark.parametrize("case", ["model-with-account", "model-without-account"])
def test_served_synthetic_models_still_match_observed_wire_hash_and_actual_handoff(case):
    trial = next(item for item in OBSERVED["trials"] if item["case"] == case)
    token = next(item for item in trial["connections"] if item["request"]["path"] == contract.TOKEN_PATH)
    credentials = next(item for item in trial["connections"] if item["request"]["path"] == "/prod/credentials/omni")
    body = contract.response_case(case)
    assert token["response"]["body_sha256"] == hashlib.sha256(body).hexdigest()
    assert token["response"]["body_bytes"] == len(body)
    assert trial["client_sdk_result_codes"] == [0]
    assert token["tls"]["tls_version"] == "TLSv1.3"
    assert credentials["tls"]["tls_version"] == "TLSv1.2"
    assert token["response_time_utc"] <= credentials["request_time_utc"]
    assert token["owner_process_id"] == credentials["owner_process_id"] == trial["owned_client"]["process_id"]
    assert credentials["request"]["authorization_present"] is True
    assert credentials["response"]["status"] == 501
    assert trial["token_model_acceptance_observed"] is True
    assert trial["game_authentication_success_observed"] is False
    assert trial["world_entry_observed"] is False


def test_empty_object_control_rejected_without_handoff_or_credential_capture():
    trial = next(item for item in OBSERVED["trials"] if item["case"] == "empty-object")
    assert trial["client_sdk_result_codes"] == [203]
    assert trial["token_model_acceptance_observed"] is False
    assert not any(item["request"]["path"] == "/prod/credentials/omni" for item in trial["connections"])
    assert not any(OBSERVED["privacy"].values())
    assert OBSERVED["milestone_1_achieved"] is False


def test_receipt_pins_fixture_and_distinguishes_retained_trust_from_cleanup_failure():
    receipt = json.loads((ROOT / "research/evidence/current-token-contract.json").read_text())
    assert receipt["fixture_sha256"] == hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()
    assert receipt["retained_ca"]["state"] == "TEST_CA_RETAINED_BY_EXPLICIT_USER_REQUEST"
    assert receipt["retained_ca"]["trust_readback_count"] == 1
    assert receipt["retained_ca"]["trust_removed"] is False
    assert receipt["retained_ca"]["owned_rules_absent"] is True
    assert receipt["canceled_comparison"]["client_launched"] is False
    assert receipt["process_memory_accessed"] is False
