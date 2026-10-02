"""Whitelist metadata from our own Game.log. Never export raw log lines/URLs."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

PUBLIC_SUFFIXES = (".cloudfront.net", ".amazonaws.com", ".amazongames.com", ".amazon.com")
MARKERS = {"CHANNEL_SERVICE": r"\bChannelService\b", "CONFIGURE_LOGIN": r"\bConfigureLogin\b",
           "OMNI_SDK": r"\bOmniSDK\b", "GAME_CONNECTION_WRAPPER": r"\bGameConnectionWrapper\b",
           "REP_CONNECTION": r"\bREP connection\b", "TLS_VALIDATION_FAILURE": r"certificate verify failed|unknown ca|SSL peer certificate",
           "GENERIC_LEVEL_LOADER": r"\bLoading level\b|\bLoadLevel\b"}
SECRET_SIGNAL = re.compile(r"authorization|\bbearer\b|\bJWT\b|password|fallbackToken|steam.?ticket|access.?token|refresh.?token|session.?token", re.I)
VERSION = re.compile(r"\b[0-9]{1,2}\.[0-9]{1,4}\.[0-9]{1,6}\.[0-9]{1,8}\b")


def parse_line(line):
    # No user identifiers, body fragments, query strings or free-form errors.
    # Drop the entire line on credential signals or URL userinfo. Even a DNS
    # label in such a line can contain a secret; no endpoint outweighs privacy.
    if SECRET_SIGNAL.search(line) or re.search(r"https?://[^\s/]+@", line, re.I):
        return []
    result = []
    for match in re.finditer(r"https?://[^\s\"'<>]+", line, re.I):
        try:
            parsed = urlsplit(match.group().rstrip(").,;]"))
            hostname = parsed.hostname
            if parsed.username is not None or parsed.password is not None:
                continue
            if not hostname or not hostname.lower().endswith(PUBLIC_SUFFIXES):
                continue
            port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
        except ValueError:
            continue
        route = "unclassified"
        if parsed.path == "/STEAM_APP_ID.1063730.json":
            route = "historical_channel_discovery"
        elif parsed.path.endswith("/credentials/omni"):
            route = "historical_credentials_omni"
        elif parsed.path.endswith("/game/getlogininfo"):
            route = "historical_login_info"
        result.append({"state": "CLIENT_LOG_ENDPOINT", "hostname": hostname.lower(), "port": port,
                       "scheme": parsed.scheme.lower(), "route_class": route,
                       "observation": "URL_mentioned_in_owned_log_not_server_request_or_DNS_proof"})
    # Hostname-only references are useful too; only public service suffixes.
    for match in re.finditer(r"\b(?:[a-zA-Z0-9-]+\.)+(?:cloudfront\.net|amazonaws\.com|amazongames\.com|amazon\.com)\b", line):
        host = match.group().lower()
        if not any(item.get("hostname") == host for item in result):
            result.append({"state": "CLIENT_LOG_HOSTNAME", "hostname": host,
                           "observation": "name_mentioned_in_owned_log_not_DNS_proof"})
    for marker, pattern in MARKERS.items():
        if re.search(pattern, line, re.I):
            result.append({"state": "CLIENT_LOG_MARKER", "marker": marker,
                           "observation": "whitelisted_log_marker_only"})
    if re.search(r"\bversion\b|\bbuild\b|\bJavelin\b", line, re.I):
        for version in VERSION.findall(line):
            result.append({"state": "CLIENT_LOG_VERSION", "version": version})
    for failure in re.findall(r"\b(?:SSL_ERROR_[A-Z_]+|CURLE_[A-Z_]+|ERROR_INTERNET_[A-Z_]+)\b", line):
        result.append({"state": "CLIENT_LOG_ERROR_CODE", "code": failure})
    return result


def extract(path):
    records = []
    digest = hashlib.sha256()
    before = path.stat()
    bytes_hashed = 0
    with path.open("rb") as stream:
        for number, raw in enumerate(stream, 1):
            digest.update(raw)
            bytes_hashed += len(raw)
            if len(raw) > 65536:
                continue
            for item in parse_line(raw.decode("utf-8", errors="replace")):
                records.append({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "timestamp_basis": "extraction_not_source_event",
                                "evidence_source": "owned_game_log_whitelist", "line_number": number, **item})
    after = path.stat()
    return {"observedAtUtc": datetime.now(timezone.utc).isoformat(), "source": str(path),
            "sourceBytesHashed": bytes_hashed, "sourceReadSha256": digest.hexdigest(),
            "sourceStableDuringRead": (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
            "rawLinesExported": False, "credentialsExported": False, "records": records}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    options = parser.parse_args()
    output = Path(options.output).resolve()
    root = Path(__file__).resolve().parents[1]
    if not any(output.is_relative_to(root / folder) for folder in ["private", ".scratch"]):
        parser.error("Output must remain in ignored private/ or .scratch/")
    result = extract(Path(options.source))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"state": "OWNED_LOG_METADATA_EXTRACTED", "records": len(result["records"]),
                      "raw_lines_exported": False, "credentials_exported": False}))
