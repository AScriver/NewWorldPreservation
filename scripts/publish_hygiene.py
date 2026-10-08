"""Bounded, read-only checks of exact staged or committed public Git blobs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 32 * 1024 * 1024
MAX_FILES = 5000
MAX_INVENTORY_BYTES = 2 * 1024 * 1024
MAX_FINDINGS = 64
GIT_TIMEOUT = 15
OID = re.compile(rb"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
PRIVATE_KEY = re.compile(rb"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----")
CREDENTIAL = re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|\bgh[pousr]_[A-Za-z0-9]{36,255}\b|\bgithub_pat_[A-Za-z0-9_]{60,255}\b")
PRIVATE_PARTS = {".scratch", "private", ".venv", ".git"}
ARTIFACT_SUFFIXES = {".pcap", ".pcapng", ".pem", ".key", ".exe", ".dll", ".pak", ".xex", ".zip", ".7z", ".rar"}
ARCHIVE_PREFIXES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08", b"7z\xbc\xaf\x27\x1c", b"Rar!\x1a\x07")
CAPTURE_PREFIXES = (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d", b"\x0a\x0d\x0d\x0a")
# Reviewed original rejection test: its deliberately invalid AA== marker is not
# key material. Bind this one rule exception to the exact path and Git blob bytes;
# any edit requires review again. Other rules still apply to this candidate.
REVIEWED_MARKERS = {
    ("tests/test_rep_anchor_candidate.py", "private-key"):
        "416787834d1c909b7e7e3ad66ff7687c8ba76dfc8dc06dbdea0261902d40d702",
}


class ScanFailure(Exception):
    """Only an allowlisted rule ID crosses the diagnostic boundary."""


@dataclass(frozen=True)
class Entry:
    mode: bytes
    oid: bytes
    path: str
    stage: bytes = b"0"


def git_output(repo: Path, arguments: list[str], limit: int) -> bytes:
    environment = os.environ.copy()
    # Bind this repository's normal index/object store, not caller-selected stores.
    for name in list(environment):
        if name in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG",
                    "GIT_CONFIG_COUNT"} or name.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")):
            environment.pop(name)
    environment.update(GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0")
    command = ["git", "--no-lazy-fetch", "--no-replace-objects", "-c", "core.fsmonitor=false",
               "-C", str(repo), *arguments]
    try:
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL, env=environment,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except OSError:
        raise ScanFailure("git-unavailable") from None
    received: queue.Queue = queue.Queue(maxsize=1)

    def read_stdout() -> None:
        try:
            received.put(child.stdout.read(limit + 1))
        except (OSError, ValueError):
            received.put(None)

    reader = threading.Thread(target=read_stdout, daemon=True)
    reader.start()
    deadline = time.monotonic() + GIT_TIMEOUT
    try:
        output = received.get(timeout=GIT_TIMEOUT)
        if output is None:
            raise ScanFailure("git-read")
        if len(output) > limit:
            raise ScanFailure("git-output-cap")
        if child.wait(timeout=max(0.01, deadline - time.monotonic())) != 0:
            raise ScanFailure("git-command")
        return output
    except (queue.Empty, subprocess.TimeoutExpired):
        raise ScanFailure("git-timeout") from None
    finally:
        if child.poll() is None:
            child.kill()
        try:
            child.wait(timeout=2)
        except subprocess.TimeoutExpired:
            raise ScanFailure("git-cleanup") from None
        reader.join(timeout=2)
        if not reader.is_alive():
            child.stdout.close()


def inventory(repo: Path, mode: str, commit: str | None) -> tuple[bytes, list[Entry]]:
    arguments = ["ls-files", "--stage", "-z"] if mode == "staged" else ["ls-tree", "-r", "-z", "--full-tree", commit]
    raw = git_output(repo, arguments, MAX_INVENTORY_BYTES)
    if raw and not raw.endswith(b"\0"):
        raise ScanFailure("git-inventory")
    entries = []
    for record in raw.split(b"\0")[:-1]:
        metadata, separator, path = record.partition(b"\t")
        fields = metadata.split(b" ")
        if not separator or len(fields) != 3 or not OID.fullmatch(fields[1] if mode == "staged" else fields[2]):
            raise ScanFailure("git-inventory")
        if mode == "staged":
            entry = Entry(fields[0], fields[1], path.decode("utf-8", "surrogateescape"), fields[2])
        else:
            if fields[1] not in (b"blob", b"commit"):
                raise ScanFailure("git-inventory")
            entry = Entry(fields[0], fields[2], path.decode("utf-8", "surrogateescape"))
        entries.append(entry)
    return raw, entries


def path_rule(entry: Entry) -> str | None:
    path = entry.path
    parts = path.lower().replace("\\", "/").split("/")
    if any(part in PRIVATE_PARTS for part in parts) or parts[:2] == ["research", "upstream"]:
        return "forbidden-path"
    if not path or path.startswith("/") or "\\" in path or ":" in path or any(part in ("", ".", "..") for part in parts):
        return "unsafe-path"
    if any(0xD800 <= ord(character) <= 0xDFFF for character in path):
        return "unsafe-path"
    if entry.stage != b"0":
        return "unmerged-index"
    if entry.mode == b"120000":
        return "symlink"
    if entry.mode not in (b"100644", b"100755"):
        return "unsupported-mode"
    name = parts[-1]
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return "environment-file"
    if Path(name).suffix in ARTIFACT_SUFFIXES:
        return "private-artifact"
    return None


def content_rules(blob: bytes) -> list[str]:
    rules = []
    if PRIVATE_KEY.search(blob):
        rules.append("private-key")
    if CREDENTIAL.search(blob):
        rules.append("credential-token")
    if blob.startswith((b"MZ", b"\x7fELF", *ARCHIVE_PREFIXES)):
        rules.append("binary-artifact")
    if blob.startswith(CAPTURE_PREFIXES):
        rules.append("packet-capture")
    return rules


def report_path(path: str | None) -> str | None:
    if path is not None and (CREDENTIAL.search(path.encode("utf-8", "surrogatepass"))
                             or PRIVATE_KEY.search(path.encode("utf-8", "surrogatepass"))):
        return "[redacted-path]"
    return path


def scan(repo: Path, mode: str = "staged", *, max_file_bytes: int = MAX_FILE_BYTES,
         max_total_bytes: int = MAX_TOTAL_BYTES, max_files: int = MAX_FILES) -> dict:
    report = {"schemaVersion": 1, "mode": mode, "commit": None, "inventorySha256": None,
              "files": 0, "blobsScanned": 0, "bytesScanned": 0, "complete": True,
              "findings": [], "reviewedMarkers": [], "status": "incomplete"}
    current_path = None

    def finding(rule: str, path: str | None = None) -> None:
        if len(report["findings"]) >= MAX_FINDINGS - 1:
            raise ScanFailure("finding-cap")
        report["findings"].append({"rule": rule, "path": report_path(path)})

    try:
        if mode not in ("staged", "committed") or min(max_file_bytes, max_total_bytes, max_files) <= 0:
            raise ScanFailure("invalid-options")
        top = git_output(repo, ["rev-parse", "--show-toplevel"], 8192).strip()
        if Path(top.decode("utf-8")).resolve() != repo.resolve():
            raise ScanFailure("repository-root")
        if mode == "committed":
            commit_bytes = git_output(repo, ["rev-parse", "--verify", "HEAD^{commit}"], 128).strip()
            if not OID.fullmatch(commit_bytes):
                raise ScanFailure("git-inventory")
            report["commit"] = commit_bytes.decode("ascii")
        raw, entries = inventory(repo, mode, report["commit"])
        report["inventorySha256"] = hashlib.sha256(raw).hexdigest()
        report["files"] = len(entries)
        if len(entries) > max_files:
            raise ScanFailure("file-count-cap")
        for entry in entries:
            current_path = entry.path
            rejected = path_rule(entry)
            if rejected:
                finding(rejected, current_path)
                continue
            oid = entry.oid.decode("ascii")
            size_text = git_output(repo, ["cat-file", "-s", oid], 64).strip()
            if not size_text.isdigit():
                raise ScanFailure("git-object")
            size = int(size_text)
            if size > max_file_bytes:
                raise ScanFailure("file-byte-cap")
            if report["bytesScanned"] + size > max_total_bytes:
                raise ScanFailure("total-byte-cap")
            blob = git_output(repo, ["cat-file", "blob", oid], size)
            digest = hashlib.sha1 if len(oid) == 40 else hashlib.sha256
            if len(blob) != size or digest(b"blob " + str(size).encode("ascii") + b"\0" + blob).hexdigest() != oid:
                raise ScanFailure("git-object")
            report["blobsScanned"] += 1
            report["bytesScanned"] += size
            for rule in content_rules(blob):
                if REVIEWED_MARKERS.get((current_path, rule)) == hashlib.sha256(blob).hexdigest():
                    report["reviewedMarkers"].append({"rule": rule, "path": report_path(current_path)})
                else:
                    finding(rule, current_path)
        current_path = None
        if mode == "staged" and inventory(repo, mode, None)[0] != raw:
            raise ScanFailure("index-changed")
    except ScanFailure as failure:
        report["complete"] = False
        report["findings"].append({"rule": str(failure), "path": report_path(current_path)})
    except (OSError, ValueError):
        report["complete"] = False
        report["findings"].append({"rule": "scan-read", "path": report_path(current_path)})
    report["status"] = "incomplete" if not report["complete"] else ("rejected" if report["findings"] else "passed")
    return report


def positive(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Use a positive integer.") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("Use a positive integer.")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--mode", choices=("staged", "committed"), default="staged")
    parser.add_argument("--max-file-bytes", type=positive, default=MAX_FILE_BYTES)
    parser.add_argument("--max-total-bytes", type=positive, default=MAX_TOTAL_BYTES)
    parser.add_argument("--max-files", type=positive, default=MAX_FILES)
    options = parser.parse_args(argv)
    report = scan(options.repo, options.mode, max_file_bytes=options.max_file_bytes,
                  max_total_bytes=options.max_total_bytes, max_files=options.max_files)
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 2 if not report["complete"] else (1 if report["findings"] else 0)


if __name__ == "__main__":
    sys.exit(main())
