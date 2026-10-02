"""Bounded owned Game.log metadata: local descriptor markers and numeric results.

No raw text, identity strings, tickets, tokens or arbitrary messages are exported.
Extraction timestamps are not represented as the original client event times.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from game_log_metadata import SECRET_SIGNAL

ROOT = Path(__file__).resolve().parents[1]
MAX_LOG_BYTES = 5_000_000
REGION = re.compile(r"\bNWPLocalBootstrap (fra-prod|gru-prod|iad-prod|pdx-prod|syd-prod)\b")
SESSION_RESULT = re.compile(r"(?:Omni CreateSession[^\r\n]*?result:|Failed to create session for Omni, result code:)\s*([0-9]{1,5})\b")


def parse_metadata(line):
    if SECRET_SIGNAL.search(line):
        return []
    records = [{"state": "CLIENT_CHANNEL_REGION_PARSED", "region": region}
               for region in REGION.findall(line)]
    if "NW_Frontend_NightHaven" in line:
        records.append({"state": "CLIENT_FRONTEND_LEVEL_MARKER", "level": "NW_Frontend_NightHaven",
                        "world_entry_proven": False})
    for code in SESSION_RESULT.findall(line):
        records.append({"state": "CLIENT_OMNI_SESSION_RESULT", "result_code": int(code),
                        "meaning_on_this_build": "unknown", "identity_exported": False})
    if "OnCampfireLoginComplete" in line and "login successful" in line:
        records.append({"state": "CLIENT_CAMPFIRE_LOGIN_COMPLETE_MARKER",
                        "observation": "owned_log_reports_login_success_not_official_authorization",
                        "world_entry_proven": False})
    if "ConfigureLogin" in line:
        records.append({"state": "CLIENT_GATEWAY_CONFIGURE_LOGIN_MARKER",
                        "observation": "fixed_log_marker_not_game_session_handoff"})
    if "getlogininfo" in line.lower():
        records.append({"state": "CLIENT_GET_LOGIN_INFO_MARKER",
                        "observation": "fixed_log_marker_not_HTTP_request_proof"})
    return records


def extract(path):
    path = Path(path)
    before = path.stat()
    with path.open("rb") as stream:
        data = stream.read(MAX_LOG_BYTES + 1)
    if len(data) > MAX_LOG_BYTES:
        raise ValueError("Owned log exceeds bounded input")
    now = datetime.now(timezone.utc).isoformat()
    records = []
    for number, raw in enumerate(data.splitlines(), 1):
        if len(raw) > 65536:
            continue
        for item in parse_metadata(raw.decode("utf-8", errors="replace")):
            records.append({"timestamp_utc": now, "timestamp_basis": "extraction_not_client_event",
                            "evidence_source": "owned_log_fixed_marker_whitelist", "line": number, **item})
    after = path.stat()
    return {"observedAtUtc": now, "sourceBytes": len(data), "sourceSha256": hashlib.sha256(data).hexdigest(),
            "sourceStableDuringRead": (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
            "rawTextExported": False, "credentialsExported": False, "records": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Only our own legitimate session log")
    parser.add_argument("--output", required=True)
    options = parser.parse_args()
    target = Path(options.output).resolve()
    if not any(target.is_relative_to(ROOT / directory) for directory in ("private", ".scratch")):
        parser.error("Metadata output must remain ignored private/ or .scratch/")
    receipt = extract(options.source)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
    print(json.dumps({"state": "OWNED_BOOTSTRAP_LOG_METADATA_EXTRACTED", "source_sha256": receipt["sourceSha256"],
                      "record_count": len(receipt["records"]), "raw_text_exported": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
