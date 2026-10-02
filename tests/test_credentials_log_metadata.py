from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import bootstrap_log_metadata as metadata


def test_campfire_success_and_gateway_markers_are_narrow_and_do_not_export_identity():
    records = metadata.parse_metadata("CGame::OnCampfireLoginComplete, login successful. ownership=permanent USER-ID-SHOULD-NOT-EXPORT")
    assert records == [{"state": "CLIENT_CAMPFIRE_LOGIN_COMPLETE_MARKER",
                        "observation": "owned_log_reports_login_success_not_official_authorization",
                        "world_entry_proven": False}]
    assert metadata.parse_metadata("ConfigureLogin arbitrary user identity") == [{"state": "CLIENT_GATEWAY_CONFIGURE_LOGIN_MARKER", "observation": "fixed_log_marker_not_game_session_handoff"}]
    assert not metadata.parse_metadata("OnCampfireLoginComplete login failed")


@pytest.mark.parametrize("secret", ["Authorization", "Bearer", "accessToken", "secretAccessKey", "sessionToken", "steamTicket", "password"])
def test_sensitive_marker_lines_are_completely_dropped(secret):
    assert not metadata.parse_metadata(f"ConfigureLogin OnCampfireLoginComplete login successful getlogininfo {secret}=DO-NOT-EXPORT")


def test_login_info_marker_does_not_claim_request_or_handoff():
    assert metadata.parse_metadata("getlogininfo asynchronous callback") == [{"state": "CLIENT_GET_LOGIN_INFO_MARKER", "observation": "fixed_log_marker_not_HTTP_request_proof"}]
