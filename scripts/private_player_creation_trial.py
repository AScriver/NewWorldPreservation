"""Prepare one inert current-image creation candidate from pinned private inputs.

The mapping digest and local character digest bind preparation inputs, not a
runtime registry. Native slot/table activation, resource-index mode, loading,
application and player control remain unproved. No transport lives here.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from current_creation_member_body import MEMBER_UUID as CREATION_UUID
from current_player_creation_candidate import (
    OWNED_PLAYER_ASSET, RESOURCE_INDEX_MODE, compose_player_creation_candidate,
)
from current_player_identity_body import MEMBER_UUID as IDENTITY_UUID
from private_trial_character import (
    PrivateTrialCharacter, ROOT, occupied_from_options, read_trial_character,
)


TYPE_INDEX_SHA256 = "f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75"
TYPE_INDEX_COUNT = 7052
MAX_MAPPING_BYTES = 1024 * 1024
CREATION_INDEX = 10
IDENTITY_INDEX = 3935
UUID_HEX32 = re.compile(r"[0-9a-fA-F]{32}\Z")


@dataclass(frozen=True)
class PreparedPlayerCreation:
    trial_character: PrivateTrialCharacter
    typed_bytes: bytes
    typed_sha256: str

    def __post_init__(self) -> None:
        if type(self.trial_character) is not PrivateTrialCharacter or type(self.typed_bytes) is not bytes:
            raise ValueError("prepared creation requires exact immutable private inputs")
        table = [bytes(16)] * (IDENTITY_INDEX + 1)
        table[CREATION_INDEX], table[IDENTITY_INDEX] = CREATION_UUID, IDENTITY_UUID
        identity = self.trial_character.identity_body()
        canonical = compose_player_creation_candidate(
            slot=0, creation_key=0, identity_key=9,
            creation_class_index=CREATION_INDEX, identity_class_index=IDENTITY_INDEX,
            class_table=tuple(table), asset_id=OWNED_PLAYER_ASSET,
            assigned_gde_ref=self.trial_character.gde_ref, occupied_keys=frozenset(),
            character_id=identity.character_id, character_name=identity.character_name,
            delivery_mode=RESOURCE_INDEX_MODE)
        if (self.typed_bytes != canonical.typed_bytes or len(self.typed_bytes) >= 128 or
                type(self.typed_sha256) is not str or
                not re.fullmatch(r"[0-9a-f]{64}", self.typed_sha256) or
                hashlib.sha256(self.typed_bytes).hexdigest() != self.typed_sha256):
            raise ValueError("prepared creation typed bytes or digest are noncanonical")


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate type mapping property")
        result[key] = value
    return result


def read_type_index(path: str | Path) -> tuple[bytes, ...]:
    """Verify exact pinned private mapping bytes, shape and selected UUID slots."""
    source = Path(path).resolve()
    if not any(source.is_relative_to(ROOT / part) for part in ("private", ".scratch")):
        raise ValueError("type mapping must be under project private/ or .scratch/")
    with source.open("rb") as stream:
        raw = stream.read(MAX_MAPPING_BYTES + 1)
    if len(raw) > MAX_MAPPING_BYTES or hashlib.sha256(raw).hexdigest() != TYPE_INDEX_SHA256:
        raise ValueError("type mapping extent or pinned SHA256 mismatch")
    try:
        model = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid type mapping JSON") from exc
    if type(model) is not dict or type(model.get("typeIndex")) is not list:
        raise ValueError("type mapping requires typeIndex array")
    values = model["typeIndex"]
    if len(values) != TYPE_INDEX_COUNT or any(
        type(item) is not str or UUID_HEX32.fullmatch(item) is None for item in values
    ):
        raise ValueError("type mapping count or UUID shape mismatch")
    table = tuple(bytes.fromhex(item) for item in values)
    if (table[0] != bytes(16) or table[CREATION_INDEX] != CREATION_UUID or
            table[IDENTITY_INDEX] != IDENTITY_UUID):
        raise ValueError("type mapping nil or selected class mismatch")
    return table


def prepare_player_creation(*, trial_character: PrivateTrialCharacter,
                            mapping_path: str | Path, occupied_keys: frozenset[int],
                            delivery_mode: str) -> PreparedPlayerCreation:
    """Use only selected indexed classes and a typed body shorter than 128 bytes."""
    if type(trial_character) is not PrivateTrialCharacter:
        raise ValueError("trial_character must be an exact original private record")
    table = read_type_index(mapping_path)
    identity = trial_character.identity_body()
    candidate = compose_player_creation_candidate(
        slot=0, creation_key=0, identity_key=9,
        creation_class_index=CREATION_INDEX, identity_class_index=IDENTITY_INDEX,
        class_table=table, asset_id=OWNED_PLAYER_ASSET,
        assigned_gde_ref=trial_character.gde_ref, occupied_keys=occupied_keys,
        character_id=identity.character_id, character_name=identity.character_name,
        delivery_mode=delivery_mode)
    if len(candidate.typed_bytes) >= 128:
        raise ValueError("typed creation candidate exceeds one-byte length boundary")
    return PreparedPlayerCreation(trial_character, candidate.typed_bytes,
                                  hashlib.sha256(candidate.typed_bytes).hexdigest())


def prepare_from_files(*, trial_character_path: str | Path,
                       trial_character_sha256: str, mapping_path: str | Path,
                       occupied_keys: frozenset[int], delivery_mode: str,
                       ) -> PreparedPlayerCreation:
    """Read one exact pinned private character, then prepare its inert bytes."""
    record = read_trial_character(trial_character_path, occupied_keys=occupied_keys,
                                  expected_sha256=trial_character_sha256)
    return prepare_player_creation(trial_character=record, mapping_path=mapping_path,
        occupied_keys=occupied_keys, delivery_mode=delivery_mode)


def main(argv=None) -> int:
    """Read-only admission check; reveal only candidate extent and digest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial-character", required=True)
    parser.add_argument("--trial-character-sha256", required=True)
    parser.add_argument("--type-index", required=True)
    parser.add_argument("--delivery-mode", choices=(RESOURCE_INDEX_MODE,), required=True)
    occupancy = parser.add_mutually_exclusive_group(required=True)
    occupancy.add_argument("--trial-known-empty-occupancy", action="store_true")
    occupancy.add_argument("--trial-occupied-low64", action="append")
    options = parser.parse_args(argv)
    try:
        occupied = occupied_from_options(options.trial_occupied_low64,
                                         options.trial_known_empty_occupancy)
        prepared = prepare_from_files(
            trial_character_path=options.trial_character,
            trial_character_sha256=options.trial_character_sha256,
            mapping_path=options.type_index, occupied_keys=occupied,
            delivery_mode=options.delivery_mode)
    except (OSError, ValueError):
        parser.error("private creation candidate input rejected")
    print(json.dumps({"typed_bytes": len(prepared.typed_bytes),
                      "typed_sha256": prepared.typed_sha256}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
