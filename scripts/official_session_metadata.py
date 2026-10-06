"""Bounded official observation records: fixed categories, no raw logs or wire bodies.

Only normal own-client logs and user observations are admitted. Socket sampling
is supplied by the separate reviewed PowerShell entry point. Synthetic input is
always labelled synthetic. No API requests, hooks, memory, capture or decryption.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
from contextlib import contextmanager
from functools import wraps

try:
    from .preserve_owned_client import ordinary, plain_parents, stable_hash, steam_identity
except ImportError:
    from preserve_owned_client import ordinary, plain_parents, stable_hash, steam_identity

MAX_READ = 1024 * 1024
MAX_LINE = 16384
MAX_EVENTS = 10000
COLLECTION_SCOPE = "Fixed own-log categories and explicit user observations; process/socket metadata only with available exact image identity; no packet payloads or raw logs."
REJECT_LINE = re.compile(r"authorization|bearer|password|cookie|ticket|token|secret|\bJWT\b|session.?id|account.?id|character.?id|steam.?id|access.?key|private.?key", re.I)
MARKERS = {
    "CHANNEL_DISCOVERY": r"\bChannelService\b",
    "LOGIN_CONFIGURATION": r"\bConfigureLogin\b",
    "SDK_ACTIVITY": r"\bOmniSDK\b",
    "GAME_CONNECTION_WRAPPER": r"\bGameConnectionWrapper\b",
    "REP_CONNECTION": r"\bREP connection\b",
    "LEVEL_LOAD_MARKER": r"\bLoading level\b|\bLoadLevel\b",
    "TLS_FAILURE_MARKER": r"certificate verify failed|unknown ca|SSL peer certificate",
    "TRANSPORT_SECURITY_FAILURE": r"\bmm_csdkerr_transport_security_error\b",
}
ACTION_EXPECTATIONS = {
    "login_malfunction_visible": "ordinary_ui_login_error_encountered_without_forcing_failure",
    "supported_play_pressed": "ordinary_supported_play_action",
    "cold_start": "ordinary_steam_launcher_eac_start",
    "discovery_visible": "supported_discovery_ui_visible",
    "character_selection_visible": "own_character_selection_ui_visible",
    "queue_visible": "ordinary_queue_ui_or_immediate_entry",
    "connection_transition": "supported_connection_transition_visible",
    "loading_visible": "world_loading_ui_visible",
    "local_spawn_visible": "own_player_and_usable_world_view_visible",
    "friend_consent_confirmed": "second_own_account_client_and_observation_consent_confirmed",
    "b_enters_view": "b_appears_in_a_view",
    "b_leaves_view": "b_disappears_from_a_view",
    "a_stationary_b_walks": "a_sees_b_walk_while_a_stationary",
    "b_turns": "a_sees_b_turn",
    "b_stops": "a_sees_b_stop",
    "b_jumps": "a_sees_b_jump",
    "b_stationary_a_walks": "b_sees_a_walk_while_b_stationary",
    "a_turns": "b_sees_a_turn",
    "a_stops": "b_sees_a_stop",
    "a_jumps": "b_sees_a_jump",
    "ordinary_logout": "supported_logout_returns_to_selection",
    "remote_actor_removed": "consenting_remote_view_sees_actor_departure",
    "ordinary_relogin": "same_user_selected_character_returns_to_world",
    "remote_actor_reappeared": "consenting_remote_view_sees_actor_return",
    "ordinary_client_exit": "owned_client_exits_normally",
}
SCENARIOS = {
    "normal-entry": ("cold_start", "discovery_visible", "character_selection_visible", "queue_visible", "connection_transition", "loading_visible", "local_spawn_visible"),
    "consenting-movement": ("friend_consent_confirmed", "b_enters_view", "b_leaves_view", "a_stationary_b_walks", "b_turns", "b_stops", "b_jumps", "b_stationary_a_walks", "a_turns", "a_stops", "a_jumps"),
    "ordinary-relogin": ("ordinary_logout", "ordinary_relogin"),
}


class ObservationError(ValueError):
    """Fixed privacy/integrity failure code."""


def utc():
    return datetime.now(timezone.utc).isoformat()


def private_run(path: Path):
    path = Path(os.path.abspath(path))
    allowed = Path(__file__).resolve().parents[1] / "private" / "official-sessions"
    if not path.is_relative_to(allowed) or path == allowed:
        raise ObservationError("private_output_required")
    plain_parents(path)
    return path


def atomic_json(path: Path, value):
    plain_parents(path.parent)
    if path.exists():
        ordinary(path)
    temporary = path.with_name(path.name + ".next")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
    os.replace(temporary, path)


def load_state(run: Path):
    ordinary(run / "collector-state.json")
    state = json.loads((run / "collector-state.json").read_text())
    if state["closed"]:
        raise ObservationError("observation_closed")
    return state


@contextmanager
def run_lock(run: Path):
    plain_parents(run)
    path = run / "collector.lock"
    if path.exists():
        ordinary(path)
    with path.open("a+b") as stream:
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        deadline = time.monotonic() + 2
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise ObservationError("collector_busy") from None
                time.sleep(0.01)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def serialized(function):
    @wraps(function)
    def guarded(run, *arguments, **keywords):
        with run_lock(run):
            return function(run, *arguments, **keywords)
    return guarded


@serialized
def sample(run: Path):
    state = load_state(run)
    events, cursor = tail_markers(Path(state["log_path"]), state["cursor"])
    for event in events:
        append_event(run, state, {"kind": "owned_log_marker", "classification": state["classification"],
                                "evidence": "locally_exposed_marker_not_wire_schema", **event})
    state["cursor"] = cursor
    atomic_json(run / "collector-state.json", state)
    return len(events)


@serialized
def mark(run: Path, action: str, observed: str, viewpoint: str, source: str):
    if action not in ACTION_EXPECTATIONS or observed not in {"observed", "not_observed", "failed", "not_applicable"}:
        raise ObservationError("invalid_action")
    if observed == "not_applicable" and action != "queue_visible":
        raise ObservationError("invalid_not_applicable_action")
    if viewpoint not in {"A", "B"} or source not in {"user_report", "reviewed_recording", "synthetic"}:
        raise ObservationError("invalid_observation_source")
    state = load_state(run)
    if source == "synthetic" and state["classification"] != "synthetic":
        raise ObservationError("synthetic_live_evidence_rejected")
    if (action.startswith(("a_", "b_", "friend_", "remote_actor")) and action != "friend_consent_confirmed"
            and state["consent"]["friend"] != "confirmed_own_legitimate_client_account_and_observation_consent"):
        raise ObservationError("friend_consent_required")
    if action == "friend_consent_confirmed" and observed == "observed":
        state["consent"]["friend"] = "confirmed_own_legitimate_client_account_and_observation_consent"
    append_event(run, state, {"kind": "rendered_observation", "action": action,
                            "expected": ACTION_EXPECTATIONS[action], "observed": observed,
                            "viewpoint": viewpoint, "source": source,
                            "timestamp_basis": "report_collection_time_not_exact_game_action_time"})
    atomic_json(run / "collector-state.json", state)


@serialized
def attach_recording(run: Path, source: Path, viewpoint: str):
    state = load_state(run)
    if viewpoint not in {"A", "B"}:
        raise ObservationError("invalid_viewpoint")
    if viewpoint == "B" and state["consent"]["friend"] != "confirmed_own_legitimate_client_account_and_observation_consent":
        raise ObservationError("friend_consent_required")
    if source.suffix.lower() not in {".mp4", ".mkv", ".webm"}:
        raise ObservationError("recording_format_rejected")
    ordinary(source)
    if source.stat().st_size > 20 * 1024**3:
        raise ObservationError("recording_size_bound")
    # Register in place, never copy or inspect pixels. User must attest review.
    metadata = {"kind": "gameplay_recording", "viewpoint": viewpoint, "private_path": str(source.absolute()),
                "sha256": stable_hash(source), "bytes": source.stat().st_size,
                "classification": "rendered_recording", "redaction": "user_attested_no_secrets_or_third_party_identifiers_content_review_unverified"}
    manifest = json.loads((run / "manifest.json").read_text())
    manifest["artifacts"].append(metadata)
    manifest["redaction"]["video"] = "user_attested_content_review_unverified"
    atomic_json(run / "manifest.json", manifest)


@serialized
def finalize(run: Path):
    state = load_state(run)
    manifest = json.loads((run / "manifest.json").read_text())
    for resource_name in ("resource-ownership.json", "log-only-resource-ownership.json"):
        resource_path = run / resource_name
        if resource_path.exists():
            ordinary(resource_path)
            if not json.loads(resource_path.read_text(encoding="utf-8-sig"))["collector_closed"]:
                raise ObservationError("collector_still_running")
            resource = json.loads(resource_path.read_text(encoding="utf-8-sig"))
            if resource.get("end_reason") == "identity_unavailable":
                manifest["remaining_unknowns"].append("Live executable image identity unavailable; installed hash is not runtime image proof")
            if resource_name == "log-only-resource-ownership.json":
                manifest["remaining_unknowns"].append("Own-log attribution uses user-confirmed normal session and public PID/name/creation time; no sockets or protected path retry")
    events_file = run / "events.jsonl"
    events = []
    if events_file.exists():
        ordinary(events_file)
        if events_file.stat().st_size > 20 * 1024 * 1024:
            raise ObservationError("event_file_bound")
        events = [json.loads(line) for line in events_file.read_text().splitlines()]
        if len(events) > MAX_EVENTS:
            raise ObservationError("event_bound_exceeded")
    observations = [event for event in events if event.get("kind") == "rendered_observation"]
    successful = {event["action"] for event in observations if event["observed"] in {"observed", "not_applicable"}}
    for artifact in manifest["artifacts"]:
        if stable_hash(Path(artifact["private_path"])) != artifact["sha256"]:
            raise ObservationError("recording_changed")
    for name in ("events.jsonl", "transport.jsonl", "resource-ownership.json", "log-only-resource-ownership.json"):
        path = run / name
        if path.exists():
            manifest["artifacts"].append({"kind": "allowlisted_metadata", "name": name,
                                         "sha256": stable_hash(path), "bytes": path.stat().st_size})
    manifest.update(status="collection_closed", collection_scope=COLLECTION_SCOPE, consent=state["consent"], observations=observations,
                    scenarios={name: {"missing": [action for action in actions if action not in successful],
                                      "reported_coverage_only": True,
                                      "both_viewpoints_and_clock_alignment_verified": False}
                               for name, actions in SCENARIOS.items()})
    manifest["timing"].update(closed_utc=utc(), closed_monotonic_ns=time.monotonic_ns())
    manifest["private_server_gameplay_acceptance"] = False
    manifest["metadata_artifact_hashes_verified"] = True
    scenario_root = run / "scenarios"
    scenario_root.mkdir(exist_ok=True)
    plain_parents(scenario_root)
    for name, actions in SCENARIOS.items():
        relevant_actions = (*actions, "login_malfunction_visible", "supported_play_pressed") if name == "normal-entry" else actions
        scenario = {"schema": 1, "scenario_id": name, "classification": state["classification"],
                    "build": state["build"], "consent_scope": state["consent"], "timing": manifest["timing"],
                    "expected_actions": [{"action": action, "expected": ACTION_EXPECTATIONS[action]} for action in actions],
                    "observed": [event for event in observations if event["action"] in relevant_actions],
                    "coverage": manifest["scenarios"][name], "artifacts": manifest["artifacts"],
                    "redaction": manifest["redaction"], "remaining_unknowns": manifest["remaining_unknowns"],
                    "private_server_gameplay_acceptance": False}
        scenario["status"] = "reported_actions_observed" if not scenario["coverage"]["missing"] else (
            "partially_observed" if scenario["observed"] else "not_collected")
        if name == "ordinary-relogin":
            scenario["remaining_unknowns"] = [*scenario["remaining_unknowns"], "Remote actor removal/reappearance and protocol identity continuity unobserved"]
        scenario_path = scenario_root / (name + ".json")
        if scenario_path.exists():
            raise ObservationError("scenario_output_exists")
        atomic_json(scenario_path, scenario)
    atomic_json(run / "manifest.json", manifest)
    state["closed"] = True
    atomic_json(run / "collector-state.json", state)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("arm", "sample", "mark", "recording", "finalize"))
    parser.add_argument("--run", required=True)
    parser.add_argument("--log")
    parser.add_argument("--steam-manifest")
    parser.add_argument("--executable")
    parser.add_argument("--version")
    parser.add_argument("--action", choices=tuple(ACTION_EXPECTATIONS))
    parser.add_argument("--observed", choices=("observed", "not_observed", "failed", "not_applicable"), default="observed")
    parser.add_argument("--viewpoint", choices=("A", "B"), default="A")
    parser.add_argument("--source", choices=("user_report", "reviewed_recording"), default="user_report")
    parser.add_argument("--recording")
    parser.add_argument("--attest-no-secrets-or-third-party-identifiers", action="store_true")
    options = parser.parse_args(argv)
    try:
        run = private_run(Path(options.run))
        if options.command == "arm":
            if not all((options.log, options.steam_manifest, options.executable, options.version)):
                raise ObservationError("missing_arm_inputs")
            # Live log source is exactly the conventional own-user Game.log.
            allowed_log = Path(os.environ["LOCALAPPDATA"]) / "AGS" / "New World" / "Game.log"
            if Path(os.path.abspath(options.log)) != allowed_log:
                raise ObservationError("owned_log_path_required")
            arm(run, allowed_log, Path(options.steam_manifest), Path(options.executable), options.version,
                classification="official-observation")
        elif options.command == "sample":
            sample(run)
        elif options.command == "mark":
            mark(run, options.action, options.observed, options.viewpoint, options.source)
        elif options.command == "recording":
            if not options.recording or not options.attest_no_secrets_or_third_party_identifiers:
                raise ObservationError("reviewed_recording_attestation_required")
            source = Path(os.path.abspath(options.recording))
            private_root = Path(__file__).resolve().parents[1] / "private"
            if not source.is_relative_to(private_root):
                raise ObservationError("private_recording_required")
            plain_parents(source.parent)
            attach_recording(run, source, options.viewpoint)
        else:
            finalize(run)
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({"state": "OFFICIAL_OBSERVATION_REJECTED"}))
        return 1
    print(json.dumps({"state": "OFFICIAL_OBSERVATION_COMMAND_COMPLETE", "command": options.command}))
    return 0


def fixed_markers(line: str):
    if len(line) > MAX_LINE or REJECT_LINE.search(line):
        return []
    return [name for name, pattern in MARKERS.items() if re.search(pattern, line, re.I)]


def tail_markers(path: Path, cursor: dict):
    """Read at most 1MiB; persist offsets only, never partial raw lines."""
    if not path.exists():
        return [], {**cursor, "unavailable": True}
    value = ordinary(path)
    file_id = [value.st_dev, value.st_ino]
    changed = cursor.get("file_id") != file_id or value.st_size < cursor["offset"]
    offset = 0 if changed else cursor["offset"]
    events = [{"marker": "LOG_ROTATED_OR_TRUNCATED", "source_timestamp_utc": None}] if changed else []
    with path.open("rb") as stream:
        if [os.fstat(stream.fileno()).st_dev, os.fstat(stream.fileno()).st_ino] != file_id:
            raise ObservationError("log_identity_changed")
        stream.seek(offset)
        data = stream.read(MAX_READ)
    newline = data.rfind(b"\n")
    consumed = newline + 1
    dropping = cursor.get("dropping_oversized", False) and not changed
    if consumed:
        lines = data[:consumed].splitlines()
        if dropping:
            lines = lines[1:]
            dropping = False
        for raw in lines:
            if len(raw) > MAX_LINE:
                continue
            line = raw.decode("utf-8", errors="replace")
            for marker in fixed_markers(line):
                # Only a source's explicit UTC timestamp is retained. No local-time inference.
                timestamp = re.search(r"\b(20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,7})?Z)\b", line)
                source_utc = None
                if timestamp:
                    try:
                        source_utc = datetime.fromisoformat(timestamp[1]).astimezone(timezone.utc).isoformat()
                    except ValueError:
                        pass
                events.append({"marker": marker, "source_timestamp_utc": source_utc})
    elif len(data) > MAX_LINE:
        consumed = len(data)
        dropping = True
    return events, {"file_id": file_id, "offset": offset + consumed,
                    "dropping_oversized": dropping, "unavailable": False}


def append_event(run: Path, state: dict, event: dict):
    if state["event_count"] >= MAX_EVENTS:
        raise ObservationError("event_bound_exceeded")
    path = run / "events.jsonl"
    if path.exists():
        ordinary(path)
    event = {"schema": 1, "collected_utc": utc(), "collector_monotonic_ns": time.monotonic_ns(), **event}
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True) + "\n")
    state["event_count"] += 1


def arm(run: Path, log: Path, manifest: Path, executable: Path, version: str, *, classification: str):
    if run.exists():
        raise ObservationError("run_exists")
    if classification not in {"official-observation", "synthetic"}:
        raise ObservationError("invalid_classification")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){3}", version):
        raise ObservationError("invalid_version")
    build_identity = steam_identity(manifest)
    image_hash = stable_hash(executable)
    if classification == "official-observation" and (build_identity["buildid"] != "22469132" or image_hash != "8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e"):
        raise ObservationError("archived_build_identity_required")
    start = time.monotonic_ns()
    log_stat = ordinary(log) if log.exists() else None
    state = {"schema": 1, "closed": False, "event_count": 0, "classification": classification,
             "armed_utc": utc(), "armed_monotonic_ns": start, "log_path": str(log),
             "cursor": {"file_id": [log_stat.st_dev, log_stat.st_ino] if log_stat else None,
                        "offset": log_stat.st_size if log_stat else 0, "dropping_oversized": False},
             "build": {"steam": build_identity, "version": version,
                       "executable_sha256": image_hash},
             "consent": {"own_session": "user_october6_authorization", "friend": "not_confirmed"}}
    run.mkdir(parents=True)
    atomic_json(run / "collector-state.json", state)
    atomic_json(run / "manifest.json", {"schema": 1, "classification": classification,
                "status": "armed_no_session_evidence", "build": state["build"], "consent": state["consent"],
                "timing": {"armed_utc": state["armed_utc"], "armed_monotonic_ns": start,
                           "clock": "host_monotonic_ns", "cross_client_clock_alignment": "unavailable"},
                "collection_scope": COLLECTION_SCOPE,
                "redaction": {"raw_log_lines_retained": False, "secrets_or_identifiers_exported_by_parser": False,
                              "video": "not_collected"}, "artifacts": [],
                "remaining_unknowns": ["No decoded wire schema, Carrier ordering or authority", "UDP remote endpoint/version/cipher unavailable from socket table", "Remote addresses omitted because peer/service ownership is unverified", "Rendered transitions require user observation or reviewed recording", "User marks use report collection time; exact gameplay action timestamps unavailable", "Same-inode overwrite past the previous log offset may omit early events"]})
    return state


if __name__ == "__main__":
    raise SystemExit(main())
