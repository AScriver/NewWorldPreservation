"""Inert, experimental two-member type8 candidate for the pinned owned client.

The native outer record slot/count writer, runtime delivery mode, class table,
resource loading and application are unproved. This module selects no runtime
slot or class index and has no transport or player-creation side effects.
"""

from __future__ import annotations

from dataclasses import dataclass

from current_creation_member_body import AssetIdField, CreationMemberBody
from current_creation_replication_record import (
    CreationRecordMember, CreationReplicationRecord, encode_record,
)
from current_creation_trial_ref import validate_trial_ref
from current_player_identity_body import PlayerIdentityBody
from current_type8_bundle_body import BundleBody, encode_body as encode_bundle_body
from current_world_activation import BUNDLE_HEADER


OWNED_PLAYER_ASSET = AssetIdField(bytes.fromhex("a660eeebebc75cb7be6bab11eb831731"), 2)
RESOURCE_INDEX_MODE = "resource-index"
RESOURCE_PLAYER_KEY = 9


@dataclass(frozen=True)
class PlayerCreationCandidate:
    record: CreationReplicationRecord
    record_bytes: bytes
    bundle_body: BundleBody
    body_bytes: bytes
    typed_bytes: bytes


def compose_player_creation_candidate(
    *, slot: int, creation_key: int, identity_key: int,
    creation_class_index: int, identity_class_index: int,
    class_table: tuple[bytes, ...], asset_id: AssetIdField,
    assigned_gde_ref: bytes, occupied_keys: frozenset[int],
    character_id: bytes, character_name: bytes, delivery_mode: str,
) -> PlayerCreationCandidate:
    """Compose one explicit record and constructor-default bundle without sending.

    The caller owns a once-assigned reference and its occupancy snapshot. The
    resource-index/key9 case is conditional on a runtime mode and resource load
    that this pure helper cannot verify. Identity text must still be joined to
    the caller's backend queue/provider designation before any live trial.
    """
    if type(delivery_mode) is not str or delivery_mode != RESOURCE_INDEX_MODE:
        raise ValueError("delivery_mode must explicitly select resource-index")
    if identity_key != RESOURCE_PLAYER_KEY:
        raise ValueError("resource-index identity_key must be 9")
    if type(creation_key) is not int or creation_key >= identity_key:
        raise ValueError("creation_key must be strictly less than identity_key")
    if type(asset_id) is not AssetIdField or asset_id != OWNED_PLAYER_ASSET:
        raise ValueError("asset_id must be the documented owned player raw16/suffix2")
    validate_trial_ref(assigned_gde_ref, occupied_keys=occupied_keys)
    for name, value in (("character_id", character_id), ("character_name", character_name)):
        if type(value) is not bytes or not value or b"\x00" in value:
            raise ValueError(f"{name} must be nonempty NUL-free immutable bytes")

    record = CreationReplicationRecord(slot, (
        CreationRecordMember(creation_key, creation_class_index,
                             CreationMemberBody(asset_id, assigned_gde_ref)),
        CreationRecordMember(identity_key, identity_class_index,
                             PlayerIdentityBody(character_id, character_name)),
    ))
    record_bytes = encode_record(record, class_table=class_table)
    bundle_body = BundleBody(payload=record_bytes)
    body_bytes = encode_bundle_body(bundle_body)
    return PlayerCreationCandidate(record, record_bytes, bundle_body,
                                   body_bytes, BUNDLE_HEADER + body_bytes)
