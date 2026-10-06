"""Isolated synthetic observation/privacy/integrity checks, never a live session."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import pytest

from scripts import official_session_metadata as c


def synthetic_run(tmp_path):
    log = tmp_path / "Game.log"
    log.write_text("old session ChannelService\n")
    manifest = tmp_path / "steam.acf"
    manifest.write_text('"appid" "1063730" "buildid" "123" "LastOwner" "DO_NOT_COPY"')
    executable = tmp_path / "NewWorld.exe"
    executable.write_bytes(b"synthetic")
    run = tmp_path / "run"
    state = c.arm(run, log, manifest, executable, "1.2.3.4", classification="synthetic")
    return run, log, state


@pytest.mark.parametrize("line", [
    "ChannelService Bearer TOP_SECRET", "LoadLevel cookie=SECRET", "REP connection ticket=SECRET",
    "OmniSDK password=SECRET", "ConfigureLogin account_id=PRIVATE", "LoadLevel characterId=PRIVATE",
])
def test_secret_lines_are_dropped(line):
    assert c.fixed_markers(line) == []


def test_variable_urls_and_identifiers_never_exported():
    line = "ChannelService https://FAKE_SECRET.example.com/?x=SECRET_123 12345678901234567 11111111-2222-3333-4444-555555555555"
    assert c.fixed_markers(line) == []
    assert c.fixed_markers(line.replace("SECRET", "OPAQUE")) == ["CHANNEL_DISCOVERY"]


def test_fresh_suffix_timing_and_partial_line(tmp_path):
    run, log, _ = synthetic_run(tmp_path)
    with log.open("a") as stream:
        stream.write("2026-10-06T19:00:00Z LoadLevel partial")
    assert c.sample(run) == 0
    with log.open("a") as stream:
        stream.write("\n")
    assert c.sample(run) == 1
    event = json.loads((run / "events.jsonl").read_text())
    assert event["marker"] == "LEVEL_LOAD_MARKER"
    assert event["source_timestamp_utc"].startswith("2026-10-06T19:00:00")
    assert "old session" not in (run / "events.jsonl").read_text()
    assert event["collector_monotonic_ns"] > 0


def test_rotation_and_oversized_line(tmp_path):
    run, log, _ = synthetic_run(tmp_path)
    log.unlink()
    log.write_text("LoadLevel\n")
    assert c.sample(run) >= 1
    with log.open("a") as stream:
        stream.write("ChannelService " + "X" * (c.MAX_LINE + 1) + "\n")
    assert c.sample(run) == 0


def test_manifest_cannot_claim_private_gameplay(tmp_path):
    run, _, _ = synthetic_run(tmp_path)
    c.mark(run, "local_spawn_visible", "observed", "A", "synthetic")
    value = c.finalize(run)
    assert value["classification"] == "synthetic"
    assert value["private_server_gameplay_acceptance"] is False
    assert value["scenarios"]["normal-entry"]["missing"]
    assert value["scenarios"]["normal-entry"]["reported_coverage_only"]
    assert value["metadata_artifact_hashes_verified"]
    for scenario in c.SCENARIOS:
        scenario_value = json.loads((run / "scenarios" / (scenario + ".json")).read_text())
        assert scenario_value["classification"] == "synthetic"
        assert scenario_value["expected_actions"] and scenario_value["build"]


def test_friend_consent_and_invalid_free_text(tmp_path):
    run, _, _ = synthetic_run(tmp_path)
    with pytest.raises(c.ObservationError, match="consent"):
        c.mark(run, "b_jumps", "observed", "A", "synthetic")
    with pytest.raises(c.ObservationError, match="invalid_action"):
        c.mark(run, "TOP_SECRET", "observed", "A", "synthetic")
    c.mark(run, "friend_consent_confirmed", "observed", "A", "synthetic")
    c.mark(run, "b_jumps", "observed", "A", "synthetic")
    assert "DO_NOT_COPY" not in (run / "collector-state.json").read_text()


def test_fake_build_cannot_be_armed_as_official(tmp_path):
    run, log, _ = synthetic_run(tmp_path)
    with pytest.raises(c.ObservationError, match="archived_build"):
        c.arm(tmp_path / "fake-official", log, tmp_path / "steam.acf", tmp_path / "NewWorld.exe",
              "1.2.3.4", classification="official-observation")


def test_finalize_refuses_running_collector(tmp_path):
    run, _, _ = synthetic_run(tmp_path)
    (run / "resource-ownership.json").write_text(json.dumps({"collector_closed": False}))
    with pytest.raises(c.ObservationError, match="still_running"):
        c.finalize(run)


def test_denied_image_and_uncollected_scenarios_remain_explicit(tmp_path):
    run, _, _ = synthetic_run(tmp_path)
    (run / "resource-ownership.json").write_text(json.dumps({"collector_closed": True, "end_reason": "identity_unavailable"}))
    (run / "log-only-resource-ownership.json").write_text(json.dumps({"collector_closed": True}))
    value = c.finalize(run)
    assert any("not runtime image proof" in text for text in value["remaining_unknowns"])
    scenario = json.loads((run / "scenarios/consenting-movement.json").read_text())
    assert scenario["status"] == "not_collected"
    assert not scenario["observed"]
    assert scenario["classification"] == "synthetic"


def test_concurrent_marks_are_serialized(tmp_path):
    run, _, _ = synthetic_run(tmp_path)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(c.mark, run, "loading_visible", "observed", "A", "synthetic") for _ in range(12)]
        for future in futures:
            future.result()
    state = json.loads((run / "collector-state.json").read_text())
    assert state["event_count"] == 12
    assert len((run / "events.jsonl").read_text().splitlines()) == 12


def test_raw_recording_change_blocks_final_verification(tmp_path):
    run, _, _ = synthetic_run(tmp_path)
    recording = tmp_path / "view.mp4"
    recording.write_bytes(b"synthetic video, no pixels verified")
    c.attach_recording(run, recording, "A")
    recording.write_bytes(b"modified")
    with pytest.raises(c.ObservationError, match="recording_changed"):
        c.finalize(run)


def test_private_path_and_no_overwrite(tmp_path):
    with pytest.raises(c.ObservationError, match="private_output"):
        c.private_run(tmp_path)
    run, log, _ = synthetic_run(tmp_path)
    with pytest.raises(c.ObservationError, match="run_exists"):
        c.arm(run, log, tmp_path / "steam.acf", tmp_path / "NewWorld.exe", "1.2.3.4", classification="synthetic")


def test_event_bound(tmp_path, monkeypatch):
    run, _, _ = synthetic_run(tmp_path)
    monkeypatch.setattr(c, "MAX_EVENTS", 1)
    c.mark(run, "loading_visible", "observed", "A", "synthetic")
    with pytest.raises(c.ObservationError, match="event_bound"):
        c.mark(run, "loading_visible", "observed", "A", "synthetic")
