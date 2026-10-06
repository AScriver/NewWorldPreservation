"""Original ephemeral identity inputs for one isolated private trial.

These local values are neither credentials nor official account records. The
name policy is deliberately narrow: 1..32 ASCII letters, digits or spaces,
starting with a letter and with no trailing space. It is an original input
policy, not a claim about native name validity. The caller owns the occupied
low64 snapshot and reuses the persisted reference without reassignment.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import uuid

from current_creation_trial_ref import new_trial_ref, validate_trial_ref
from current_player_identity_body import PlayerIdentityBody


ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = "original-private-trial-character-v1"
MAX_FILE_BYTES = 4096
NAME_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9 ]{0,31}\Z")
STAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")
FIELDS = frozenset(("classification", "session_id", "character_id", "persona_id",
                    "ticket_id", "name", "created_at", "gde_ref"))
FIXTURE_IDS = frozenset((
    "00000000-0000-4000-8000-000000000002",
    "00000000-0000-4000-8000-000000000020",
    "00000000-0000-4000-8000-000000000030",
))


def _uuid4(name: str, value: str) -> None:
    if type(value) is not str:
        raise ValueError(f"{name} must be a canonical UUIDv4 string")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{name} must be a canonical UUIDv4 string") from exc
    if str(parsed) != value or parsed.version != 4 or parsed.variant != uuid.RFC_4122:
        raise ValueError(f"{name} must be a canonical UUIDv4 string")


@dataclass(frozen=True)
class PrivateTrialCharacter:
    session_id: str
    character_id: str
    persona_id: str
    ticket_id: str
    name: str
    created_at: str
    gde_ref: bytes

    def __post_init__(self) -> None:
        names = ("session_id", "character_id", "persona_id", "ticket_id")
        for name in names:
            _uuid4(name, getattr(self, name))
        if len({getattr(self, name) for name in names}) != 4:
            raise ValueError("UUID domains must be distinct")
        if any(getattr(self, name) in FIXTURE_IDS for name in names):
            raise ValueError("private trial UUIDs must not reuse fixed fixture IDs")
        if type(self.name) is not str or not NAME_PATTERN.fullmatch(self.name) or self.name.endswith(" "):
            raise ValueError("name must follow the original 1..32 ASCII trial policy")
        if type(self.created_at) is not str or not STAMP_PATTERN.fullmatch(self.created_at):
            raise ValueError("created_at must be canonical UTC seconds")
        try:
            parsed = datetime.strptime(self.created_at, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as exc:
            raise ValueError("created_at must be a valid UTC timestamp") from exc
        if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != self.created_at:
            raise ValueError("created_at must be canonical UTC seconds")
        validate_trial_ref(self.gde_ref, occupied_keys=frozenset())

    def identity_body(self) -> PlayerIdentityBody:
        """Use exactly the selection/queue text bytes in the inert BODY codec."""
        return PlayerIdentityBody(self.character_id.encode("utf-8"), self.name.encode("utf-8"))


def new_trial_character(*, occupied_keys: frozenset[int], name: str = "Preservation"
                        ) -> PrivateTrialCharacter:
    """Generate four independent local UUID domains and one original GdeRef."""
    domains = tuple(str(uuid.uuid4()) for _ in range(4))
    record = PrivateTrialCharacter(*domains, name,
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        new_trial_ref(occupied_keys=occupied_keys))
    validate_trial_ref(record.gde_ref, occupied_keys=occupied_keys)
    return record


def _private_path(value: str | Path) -> Path:
    path = Path(value).resolve()
    if not any(path.is_relative_to(ROOT / name) for name in (".scratch", "private")):
        raise ValueError("trial character JSON must remain under project .scratch/ or private/")
    if path.is_dir():
        raise ValueError("trial character JSON path must be a file")
    return path


def _model(record: PrivateTrialCharacter) -> dict[str, str]:
    return dict(classification=CLASSIFICATION, session_id=record.session_id,
                character_id=record.character_id, persona_id=record.persona_id,
                ticket_id=record.ticket_id, name=record.name,
                created_at=record.created_at, gde_ref=record.gde_ref.hex())


def write_trial_character(path: str | Path, record: PrivateTrialCharacter) -> Path:
    """Create one bounded private record exclusively; never replace a prior one."""
    if type(record) is not PrivateTrialCharacter:
        raise ValueError("record must be PrivateTrialCharacter")
    destination = _private_path(path)
    raw = (json.dumps(_model(record), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError("trial character JSON exceeds private bound")
    destination.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    descriptor = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
    except BaseException:
        destination.unlink()
        raise
    return destination


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("duplicate trial character JSON property")
        result[name] = value
    return result


def read_trial_character(path: str | Path, *, occupied_keys: frozenset[int]
                         ) -> PrivateTrialCharacter:
    """Read only the exact private schema, checking the caller's occupancy set."""
    source = _private_path(path)
    with source.open("rb") as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError("trial character JSON exceeds private bound")
    try:
        model = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid private trial character JSON") from exc
    if type(model) is not dict or model.keys() != FIELDS or model["classification"] != CLASSIFICATION:
        raise ValueError("trial character JSON requires the exact original private schema")
    if type(model["gde_ref"]) is not str or not re.fullmatch(r"[0-9a-f]{32}", model["gde_ref"]):
        raise ValueError("gde_ref must be lowercase raw16 hex")
    record = PrivateTrialCharacter(model["session_id"], model["character_id"],
        model["persona_id"], model["ticket_id"], model["name"], model["created_at"],
        bytes.fromhex(model["gde_ref"]))
    validate_trial_ref(record.gde_ref, occupied_keys=occupied_keys)
    return record


def occupied_from_options(keys: list[str] | None, known_empty: bool) -> frozenset[int]:
    """Require an explicit caller-owned collision boundary for CLI operations."""
    if known_empty == bool(keys):
        raise ValueError("choose known-empty occupancy or supply occupied low64 keys")
    if known_empty:
        return frozenset()
    try:
        values = frozenset(int(value, 0) for value in keys or [])
    except ValueError as exc:
        raise ValueError("occupied low64 keys must be numeric") from exc
    from current_creation_trial_ref import _keys
    _keys(values)
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for operation in ("create", "verify"):
        command = commands.add_parser(operation)
        command.add_argument("--path", required=True)
        occupancy = command.add_mutually_exclusive_group(required=True)
        occupancy.add_argument("--known-empty-occupancy", action="store_true")
        occupancy.add_argument("--occupied-low64", action="append")
        if operation == "create":
            command.add_argument("--name", default="Preservation")
    options = parser.parse_args()
    try:
        occupied = occupied_from_options(options.occupied_low64, options.known_empty_occupancy)
        if options.command == "create":
            record = new_trial_character(name=options.name, occupied_keys=occupied)
            write_trial_character(options.path, record)
            print("original private trial character created")
        else:
            read_trial_character(options.path, occupied_keys=occupied)
            print("original private trial character verified")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
