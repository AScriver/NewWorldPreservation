"""Private static-file preservation. No user stores, logs, game launch or network.

Inventory and file contents remain in an explicitly chosen private archive.
Stdout uses fixed status fields only. A verified copy is not launch/gameplay proof.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import time

CHUNK = 4 * 1024 * 1024
MAX_FILES = 50000
MAX_BYTES = 250 * 1024**3
EXCLUDED_DIRS = {"logs", "logbackups", "crashdb", "savedata", "userdata"}
EXCLUDED_SUFFIXES = {".log", ".dmp", ".mdmp", ".pcap", ".pcapng", ".key", ".pem"}
SENSITIVE_NAME = re.compile(r"(?:credential|password|cookie|ticket|token|secret|analytics_uuid)", re.I)
TEXT_SUFFIXES = {".cfg", ".ini", ".json", ".vdf", ".xml", ".txt", ".lst", ".yaml", ".yml", ".csv"}
SENSITIVE_TEXT = re.compile(r"credential|password|cookie|ticket|token|secret|authorization|\bbearer\b|account[ _-]?id|steam[ _-]?id|character[ _-]?id|private[ _-]?key|access[ _-]?key", re.I)
OWNED_SHADER_LIST_SHA256 = "87eea1d260c85fa6dde26d98edef80183439306d9bb325f027d2a914f0e97685"


class PreservationError(ValueError):
    """Fixed failure codes; do not echo paths or file content."""


def utc():
    return datetime.now(timezone.utc).isoformat()


def identity(value):
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns


def ordinary(path: Path, *, directory=False):
    value = path.lstat()
    if path.is_symlink() or getattr(value, "st_file_attributes", 0) & 0x400:
        raise PreservationError("reparse_point_rejected")
    if not (stat.S_ISDIR(value.st_mode) if directory else stat.S_ISREG(value.st_mode)):
        raise PreservationError("nonordinary_file_rejected")
    return value


def plain_parents(path: Path):
    for parent in (path, *path.parents):
        if parent.exists():
            ordinary(parent, directory=True)


def excluded(relative: Path):
    return (any(part.lower() in EXCLUDED_DIRS for part in relative.parts[:-1])
            or relative.suffix.lower() in EXCLUDED_SUFFIXES
            or (relative.suffix.lower() not in {".exe", ".dll", ".pak"}
                and bool(SENSITIVE_NAME.search(relative.name))))


def inventory(root: Path):
    plain_parents(root)
    rows = []
    exclusions = 0
    total = 0
    for folder, folders, filenames in os.walk(root, followlinks=False):
        base = Path(folder)
        for name in folders[:]:
            candidate = base / name
            ordinary(candidate, directory=True)
            if name.lower() in EXCLUDED_DIRS:
                folders.remove(name)
                exclusions += 1
        for name in sorted(filenames):
            candidate = base / name
            value = ordinary(candidate)
            relative = candidate.relative_to(root)
            if excluded(relative):
                exclusions += 1
                continue
            total += value.st_size
            if len(rows) >= MAX_FILES or total > MAX_BYTES:
                raise PreservationError("inventory_bound_exceeded")
            rows.append({"path": relative.as_posix(), "bytes": value.st_size,
                         "identity": list(identity(value))})
    rows.sort(key=lambda row: row["path"])
    if not rows:
        raise PreservationError("empty_static_inventory")
    return rows, exclusions, total


def stable_hash(path: Path, expected=None):
    before = ordinary(path)
    if expected is not None and list(identity(before)) != expected:
        raise PreservationError("source_changed")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        if identity(os.fstat(stream.fileno())) != identity(before):
            raise PreservationError("source_changed")
        while data := stream.read(CHUNK):
            digest.update(data)
        if identity(os.fstat(stream.fileno())) != identity(before):
            raise PreservationError("source_changed")
    if identity(ordinary(path)) != identity(before):
        raise PreservationError("source_changed")
    return digest.hexdigest()


def review_static_text(path: Path):
    """Conservative sensitive-signal screen, not proof about arbitrary bytes."""
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    value = ordinary(path)
    if value.st_size > 32 * 1024 * 1024:
        raise PreservationError("loose_text_review_bound")
    raw = path.read_bytes()
    if identity(ordinary(path)) != identity(value):
        raise PreservationError("source_changed")
    try:
        text = raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
    except UnicodeError:
        raise PreservationError("loose_text_encoding_unreviewed") from None
    # This exact owned-build shader permutation list uses "cookie" as a shader
    # feature. Admit only its reviewed hash and complete static-list grammar.
    if (path.name == "shaderlist_pc.txt" and hashlib.sha256(raw).hexdigest() == OWNED_SHADER_LIST_SHA256
            and all(re.fullmatch(r"<[^<>\r\n]{1,16}>[^()\r\n]{1,256}(?:\([^()\r\n]{0,512}\)){6}", line)
                    for line in text.splitlines() if line)):
        return
    if SENSITIVE_TEXT.search(text):
        raise PreservationError("loose_text_sensitive_signal")


def copy_one(source: Path, destination: Path, expected):
    if list(identity(ordinary(source))) != expected:
        raise PreservationError("source_changed")
    destination.parent.mkdir(parents=True, exist_ok=True)
    plain_parents(destination.parent)
    digest = hashlib.sha256()
    with source.open("rb") as incoming, destination.open("xb") as outgoing:
        if list(identity(os.fstat(incoming.fileno()))) != expected:
            raise PreservationError("source_changed")
        while data := incoming.read(CHUNK):
            outgoing.write(data)
            digest.update(data)
        outgoing.flush()
        os.fsync(outgoing.fileno())
        if list(identity(os.fstat(incoming.fileno()))) != expected:
            raise PreservationError("source_changed")
    if list(identity(ordinary(source))) != expected:
        raise PreservationError("source_changed")
    return digest.hexdigest()


def steam_identity(path: Path):
    ordinary(path)
    if path.stat().st_size > 1024 * 1024:
        raise PreservationError("manifest_bound_exceeded")
    text = path.read_text(encoding="utf-8")
    result = {}
    for key in ("appid", "buildid"):
        values = re.findall(r'"' + key + r'"\s+"([0-9]+)"', text)
        if len(values) != 1:
            raise PreservationError("steam_identity_ambiguous")
        result[key] = values[0]
    if result["appid"] != "1063730":
        raise PreservationError("wrong_steam_app")
    # Raw ACF is never copied: it may contain account ownership fields.
    result["source_read_sha256"] = stable_hash(path)
    result["raw_manifest_archived"] = False
    return result


def write_json(path: Path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def archive(root: Path, destination: Path, manifest: Path, version: str, dependencies=()):
    root = Path(os.path.abspath(root))
    destination = Path(os.path.abspath(destination))
    if root == destination or root in destination.parents or destination in root.parents:
        raise PreservationError("overlapping_archive_rejected")
    plain_parents(destination.parent)
    if destination.exists():
        raise PreservationError("archive_exists")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){3}", version):
        raise PreservationError("invalid_version")
    steam = steam_identity(manifest)
    executable = root / "Bin64" / "NewWorld.exe"
    executable_hash = stable_hash(executable)
    rows, exclusions, total = inventory(root)
    sources = [{"label": "owned-install", "root": str(root), "files": rows,
                "excluded_count": exclusions, "bytes": total}]
    for number, dependency in enumerate(dependencies, 1):
        dependency = Path(dependency).absolute()
        if dependency == destination or dependency in destination.parents or destination in dependency.parents:
            raise PreservationError("overlapping_archive_rejected")
        if dependency.is_dir():
            dep_rows, dep_exclusions, dep_total = inventory(dependency)
        else:
            plain_parents(dependency.parent)
            value = ordinary(dependency)
            if excluded(Path(dependency.name)):
                raise PreservationError("excluded_dependency")
            dep_rows = [{"path": dependency.name, "bytes": value.st_size,
                         "identity": list(identity(value))}]
            dep_exclusions, dep_total = 0, value.st_size
        total += dep_total
        if total > MAX_BYTES:
            raise PreservationError("inventory_bound_exceeded")
        sources.append({"label": f"launch-dependency-{number}", "root": str(dependency),
                        "files": dep_rows, "excluded_count": dep_exclusions, "bytes": dep_total})
    nearest = next(parent for parent in (destination.parent, *destination.parents) if parent.exists())
    if shutil.disk_usage(nearest).free < total + 2 * 1024**3:
        raise PreservationError("insufficient_archive_space")
    start = time.monotonic_ns()
    result = {"schema": 1, "classification": "owned-static-file-archive", "started_utc": utc(),
              "started_monotonic_ns": start, "steam": steam, "version": version,
              "executable_sha256": executable_hash, "sources": sources,
              "scope": "Static owned install and explicit static launch dependencies; excludes user stores/logs/secret-named loose inputs.",
              "credentials_collected": False, "game_launched": False,
              "archive_restoration_or_offline_launch_tested": False,
              "remaining_unknowns": ["Future Steam/EAC service availability and offline launch viability"],
              "status": "copy_started", "verified": False}
    destination.mkdir(parents=True)
    write_json(destination / "scope.json", {key: value for key, value in result.items() if key != "sources"})
    completed = 0
    for group in sources:
        source_root = Path(group["root"])
        for row in group["files"]:
            source = source_root / row["path"] if source_root.is_dir() else source_root
            output = destination / group["label"] / row["path"]
            review_static_text(source)
            row["sha256"] = copy_one(source, output, row["identity"])
            completed += 1
            if completed % 100 == 0:
                print(json.dumps({"state": "STATIC_ARCHIVE_PROGRESS", "files_copied": completed}), flush=True)
    # Verify every source again and every destination, not just the copy digest.
    for group in sources:
        source_root = Path(group["root"])
        for row in group["files"]:
            source = source_root / row["path"] if source_root.is_dir() else source_root
            output = destination / group["label"] / row["path"]
            if stable_hash(source, row["identity"]) != row["sha256"] or stable_hash(output) != row["sha256"]:
                raise PreservationError("archive_hash_mismatch")
        if source_root.is_dir() and inventory(source_root)[0] != [
                {key: row[key] for key in ("path", "bytes", "identity")} for row in group["files"]]:
            raise PreservationError("source_inventory_changed")
    if steam_identity(manifest) != steam:
        raise PreservationError("steam_identity_changed")
    canonical = [{"group": group["label"], "path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]}
                 for group in sources for row in group["files"]]
    if next(row["sha256"] for row in rows if row["path"] == "Bin64/NewWorld.exe") != executable_hash:
        raise PreservationError("executable_identity_changed")
    result.update(status="verified", verified=True, files=completed, bytes=total,
                  ended_utc=utc(), ended_monotonic_ns=time.monotonic_ns(),
                  inventory_sha256=hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest(),
                  source_and_destination_fully_rehashed=True)
    write_json(destination / "inventory.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-root", required=True)
    parser.add_argument("--archive-root", required=True)
    parser.add_argument("--steam-manifest", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--dependency", action="append", default=[])
    options = parser.parse_args(argv)
    destination = Path(options.archive_root).absolute()
    repo = Path(__file__).resolve().parents[1]
    if destination == repo or repo in destination.parents:
        parser.error("Archive must be outside the source repository")
    try:
        result = archive(Path(options.client_root), destination, Path(options.steam_manifest),
                         options.version, options.dependency)
    except (OSError, PreservationError):
        print(json.dumps({"state": "STATIC_ARCHIVE_REJECTED", "verified": False}))
        return 1
    print(json.dumps({"state": "STATIC_ARCHIVE_VERIFIED", "files": result["files"], "bytes": result["bytes"],
                      "steam_build": result["steam"]["buildid"], "version": result["version"],
                      "executable_sha256": result["executable_sha256"], "inventory_sha256": result["inventory_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
