import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("game_log_metadata", Path(__file__).parents[1] / "scripts/game_log_metadata.py")
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


def test_preserves_service_host_without_query_path_or_account_values():
    line = 'fetch https://d2c74t4zimux3r.cloudfront.net/STEAM_APP_ID.1063730.json?secret=query-secret account=account-secret'
    records = metadata.parse_line(line)
    serialized = json.dumps(records)
    assert records[0]["hostname"] == "d2c74t4zimux3r.cloudfront.net"
    assert records[0]["route_class"] == "historical_channel_discovery"
    assert "query-secret" not in serialized and "account-secret" not in serialized


@pytest.mark.parametrize("secret", ["Authorization: Bearer header-secret", "steam_ticket=ticket-secret", "password=password-secret"])
def test_secret_lines_do_not_export_free_form_content_or_state_claims(secret):
    records = metadata.parse_line(secret + " ConfigureLogin failed")
    assert records == []


def test_only_allowlisted_version_markers_exported():
    assert metadata.parse_line("Javelin build 1.400.6031.6004151 username=private-name") == [
        {"state": "CLIENT_LOG_VERSION", "version": "1.400.6031.6004151"}]


def test_extractor_exports_line_provenance_not_source_text(tmp_path):
    source = tmp_path / "Game.log"
    source.write_text("private-user private-body\nhttps://tokenservice.amazongames.com/secret/path\n")
    result = metadata.extract(source)
    assert result["records"][0]["line_number"] == 2
    assert result["rawLinesExported"] is False
    assert "private-body" not in json.dumps(result)
    assert "/secret/path" not in json.dumps(result)
    assert result["sourceBytesHashed"] == len(source.read_bytes())
    assert result["sourceStableDuringRead"] is True
    assert result["records"][0]["timestamp_basis"] == "extraction_not_source_event"


@pytest.mark.parametrize("line", [
    "Authorization: Bearer secret https://secret.cloudfront.net/credentials/omni",
    "fetch https://user:secret@d2c74t4zimux3r.cloudfront.net/route",
])
def test_credential_url_lines_are_completely_discarded(line):
    assert metadata.parse_line(line) == []


def test_generic_level_loading_does_not_claim_world_entry():
    assert metadata.parse_line("Loading level") == [
        {"state": "CLIENT_LOG_MARKER", "marker": "GENERIC_LEVEL_LOADER",
         "observation": "whitelisted_log_marker_only"}]
