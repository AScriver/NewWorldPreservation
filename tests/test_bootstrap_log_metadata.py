import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bootstrap_log_metadata as metadata


def test_only_exact_local_region_marker_proves_parse_not_world_entry():
    records = metadata.parse_metadata("Name: NWPLocalBootstrap pdx-prod")
    assert records == [{"state": "CLIENT_CHANNEL_REGION_PARSED", "region": "pdx-prod"}]
    assert metadata.parse_metadata("Name: US West") == []
    loader = metadata.parse_metadata("Loading NW_Frontend_NightHaven")[0]
    assert loader["world_entry_proven"] is False


def test_numeric_session_result_never_exports_identity_or_invents_meaning():
    records = metadata.parse_metadata("Omni CreateSession complete with result: 204, id: private-identity")
    assert records[0]["result_code"] == 204
    assert records[0]["meaning_on_this_build"] == "unknown"
    assert "private-identity" not in json.dumps(records)


def test_credential_signaled_lines_are_dropped_entirely():
    for signal in ("Authorization", "Bearer", "password", "fallbackToken", "steam ticket"):
        assert metadata.parse_metadata(f"{signal}: private-value; Name: NWPLocalBootstrap pdx-prod") == []


def test_extraction_pins_read_bytes_and_marks_timestamp_basis(tmp_path):
    data = b"Name: NWPLocalBootstrap pdx-prod\nFailed to create session for Omni, result code: 204\n"
    path = tmp_path / "owned.log"
    path.write_bytes(data)
    result = metadata.extract(path)
    assert result["sourceSha256"] == hashlib.sha256(data).hexdigest()
    assert result["sourceBytes"] == len(data)
    assert result["sourceStableDuringRead"] is True
    assert all(r["timestamp_basis"] == "extraction_not_client_event" for r in result["records"])
    assert result["rawTextExported"] is False


def test_oversized_log_refused_before_unbounded_read(tmp_path, monkeypatch):
    path = tmp_path / "owned.log"
    path.write_bytes(b"12345")
    monkeypatch.setattr(metadata, "MAX_LOG_BYTES", 4)
    with pytest.raises(ValueError, match="bounded"):
        metadata.extract(path)
