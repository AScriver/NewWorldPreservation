"""Synthetic literal controls for the inert current two-member candidate."""

from dataclasses import replace
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from current_creation_member_body import AssetIdField, CreationMemberBody, MEMBER_UUID as CREATION_UUID  # noqa: E402
from current_creation_replication_record import (  # noqa: E402
    CreationRecordMember, CreationReplicationRecord, DecodeError as RecordDecodeError,
    decode_record, encode_record,
)
from current_player_creation_candidate import (  # noqa: E402
    OWNED_PLAYER_ASSET, PlayerCreationCandidate, compose_player_creation_candidate,
)
from current_player_identity_body import MEMBER_UUID as IDENTITY_UUID, PlayerIdentityBody  # noqa: E402
from current_type8_bundle_body import decode_body as decode_bundle_body, decode_creation_payload  # noqa: E402
from current_world_activation import BUNDLE_HEADER  # noqa: E402


# Original synthetic values: neither a captured session nor a backend identity.
GDE_REF = bytes.fromhex("0200000001000000aabbccddeeff1122")
CHARACTER_ID = b"IIIIIIIIIIIIIIII"
CHARACTER_NAME = b"NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"
INDEXED_TABLE = tuple(
    IDENTITY_UUID if index == 3935 else CREATION_UUID if index == 10 else bytes(16)
    for index in range(3936)
)
RAW_RECORD = bytes.fromhex(
    "0002"
    "0000203dc8c70c60454ba46f566114314b84"
    "0103a660eeebebc75cb7be6bab11eb83173100000002"
    "0200000001000000aabbccddeeff1122"
    "0900bddda784a6e7416ba041449920d90fb6"
    "020300104949494949494949"
    "4949494949494949"
    "204e4e4e4e4e4e4e4e"
    "4e4e4e4e4e4e4e4e"
    "4e4e4e4e4e4e4e4e"
    "4e4e4e4e4e4e4e4e"
)
INDEXED_RECORD = bytes.fromhex(
    "0002000a"
    "0103a660eeebebc75cb7be6bab11eb83173100000002"
    "0200000001000000aabbccddeeff1122"
    "099f3d"
    "020300104949494949494949"
    "4949494949494949"
    "204e4e4e4e4e4e4e4e"
    "4e4e4e4e4e4e4e4e"
    "4e4e4e4e4e4e4e4e"
    "4e4e4e4e4e4e4e4e"
)


def candidate(**changes):
    values = dict(
        slot=0, creation_key=0, identity_key=9,
        creation_class_index=0, identity_class_index=0,
        class_table=INDEXED_TABLE, asset_id=OWNED_PLAYER_ASSET,
        assigned_gde_ref=GDE_REF, occupied_keys=frozenset(),
        character_id=CHARACTER_ID, character_name=CHARACTER_NAME,
        delivery_mode="resource-index",
    )
    values.update(changes)
    return compose_player_creation_candidate(**values)


@pytest.mark.parametrize("creation_index,identity_index,expected,prefix", [
    (0, 0, RAW_RECORD, b"\x81\x02"),
    (10, 3935, INDEXED_RECORD, b"\x62"),
])
def test_literal_record_and_type8_candidate(creation_index, identity_index, expected, prefix):
    result = candidate(creation_class_index=creation_index,
                       identity_class_index=identity_index)
    assert type(result) is PlayerCreationCandidate
    assert result.record_bytes == expected
    assert len(expected) == (129 if creation_index == 0 else 98)
    assert result.body_bytes == b"\x00" * 5 + prefix + expected
    assert result.typed_bytes == BUNDLE_HEADER + result.body_bytes
    assert len(result.body_bytes) == (136 if creation_index == 0 else 104)
    assert len(result.typed_bytes) == (139 if creation_index == 0 else 107)
    assert decode_record(expected, class_table=INDEXED_TABLE) == (result.record, len(expected))
    assert decode_creation_payload(result.bundle_body.payload,
                                   class_table=INDEXED_TABLE) == (result.record,)
    assert decode_bundle_body(result.typed_bytes[len(BUNDLE_HEADER):]) == (
        result.bundle_body, len(result.body_bytes))


def test_mixed_selectors_and_record_extent_with_suffix():
    for creation_index, identity_index in ((0, 3935), (10, 0)):
        result = candidate(creation_class_index=creation_index,
                           identity_class_index=identity_index)
        source = bytearray(result.record_bytes + b"suffix")
        original = bytes(source)
        decoded, consumed = decode_record(source, class_table=INDEXED_TABLE)
        assert decoded == result.record
        assert consumed == len(result.record_bytes)
        assert source[consumed:] == b"suffix"
        assert bytes(source) == original
        assert encode_record(decoded, class_table=INDEXED_TABLE) == result.record_bytes


@pytest.mark.parametrize("raw", (RAW_RECORD, INDEXED_RECORD))
def test_every_proper_record_truncation_is_nondestructive(raw):
    for size in range(len(raw)):
        source = bytearray(raw[:size])
        with pytest.raises(RecordDecodeError) as raised:
            decode_record(source, class_table=INDEXED_TABLE)
        assert source == raw[:size]
        assert 0 <= raised.value.cursor <= size


@pytest.mark.parametrize("creation_index,identity_index", ((0, 0), (10, 3935)))
def test_every_proper_bundle_body_truncation_is_nondestructive(creation_index, identity_index):
    raw = candidate(creation_class_index=creation_index,
                    identity_class_index=identity_index).body_bytes
    for size in range(len(raw)):
        source = bytearray(raw[:size])
        with pytest.raises(ValueError):
            decode_bundle_body(source)
        assert source == raw[:size]


def test_identity_body_failure_reports_absolute_record_offset():
    # Raw record's identity BODY begins at byte 76; ID flag is byte 78.
    source = bytearray(RAW_RECORD)
    source[78] = 1
    with pytest.raises(RecordDecodeError) as raised:
        decode_record(source, class_table=INDEXED_TABLE)
    assert (raised.value.field, raised.value.cursor) == (
        "member 1 character_id flag", 79)


def test_unknown_and_mismatched_selectors_reject():
    for changes in (
        dict(creation_class_index=3935), dict(identity_class_index=10),
        dict(creation_class_index=3936), dict(identity_class_index=3936),
    ):
        with pytest.raises(ValueError, match="class_index"):
            candidate(**changes)
    for raw, field in ((b"\x00\x01\x00\x00" + b"x" * 16 + b"\x00", "class UUID"),
                       (b"\x00\x01\x00\x01", "class UUID")):
        with pytest.raises(RecordDecodeError, match=field):
            decode_record(raw, class_table=(bytes(16), b"x" * 16))


@pytest.mark.parametrize("changes", [
    dict(asset_id=AssetIdField(bytes.fromhex("a660eeebebc75cb7be6bab11eb831731"), 3)),
    dict(asset_id=AssetIdField(b"x" * 16, 2)),
    dict(identity_key=8), dict(identity_key=10), dict(creation_key=9),
    dict(creation_key=10), dict(delivery_mode="assigned-index"),
    dict(delivery_mode=None), dict(character_id=b""),
    dict(character_name=b""), dict(character_id=b"a\x00b"),
    dict(character_name=b"a\x00b"),
    dict(assigned_gde_ref=b"\x02" + bytes(15)),
    dict(occupied_keys=frozenset({0x100000002})),
])
def test_candidate_rejects_unsupported_or_missing_inputs(changes):
    with pytest.raises(ValueError):
        candidate(**changes)


def test_creation_order_and_identity_presence_are_explicit():
    result = candidate()
    assert len(result.record.members) == 2
    assert result.record.members[0] == CreationRecordMember(
        0, 0, CreationMemberBody(OWNED_PLAYER_ASSET, GDE_REF))
    assert result.record.members[1] == CreationRecordMember(
        9, 0, PlayerIdentityBody(CHARACTER_ID, CHARACTER_NAME))
    assert result.bundle_body == replace(result.bundle_body, payload=RAW_RECORD)
