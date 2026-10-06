"""Original literal and boundary checks; no native/client execution."""

from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from current_creation_member_body import AssetIdField, CreationMemberBody, MEMBER_UUID  # noqa: E402
from current_creation_replication_record import (  # noqa: E402
    CreationRecordMember, CreationReplicationRecord, DecodeError, decode_record, encode_record,
)

FIXTURE = json.loads((ROOT / "tests/fixtures/replication/current-creation-record-original.json")
                     .read_text(encoding="utf8"))
VECTORS = FIXTURE["vectors"]
TABLE = (bytes(16), MEMBER_UUID, b"x" * 16)


def _table(name):
    value = FIXTURE["tables"][name]
    if isinstance(value, list):
        return tuple(bytes.fromhex(raw) for raw in value)
    items = [bytes.fromhex(value["fill"])] * value["size"]
    for index, raw in value["entries"].items():
        items[int(index)] = bytes.fromhex(raw)
    return tuple(items)


def _record(vector):
    members = []
    for value in vector["members"]:
        fields = value["body"]
        asset = fields["assetId"]
        body = CreationMemberBody(
            AssetIdField(bytes.fromhex(asset["raw16"]), asset["field_20"]) if asset else None,
            bytes.fromhex(fields["gdeRef"]) if fields["gdeRef"] is not None else None,
        )
        members.append(CreationRecordMember(value["key"], value["classIndex"], body))
    return CreationReplicationRecord(vector["slot"], tuple(members))


@pytest.mark.parametrize("vector", VECTORS, ids=lambda value: value["name"])
def test_original_literal_record_goldens(vector):
    assert FIXTURE["classification"] == "synthetic"
    assert FIXTURE["memberUuid"] == MEMBER_UUID.hex()
    expected = bytes.fromhex(vector["recordHex"])
    table, record = _table(vector["table"]), _record(vector)
    assert len(expected) == vector["length"]
    assert encode_record(record, class_table=table) == expected
    assert decode_record(expected, class_table=table) == (record, len(expected))


@pytest.mark.parametrize("vector", VECTORS, ids=lambda value: value["name"])
def test_all_proper_truncations_fail_without_modifying_input(vector):
    raw = bytes.fromhex(vector["recordHex"])
    for size in range(len(raw)):
        source = bytearray(raw[:size])
        with pytest.raises(DecodeError) as raised:
            decode_record(source, class_table=_table(vector["table"]))
        assert bytes(source) == raw[:size]
        assert 0 <= raised.value.cursor <= size


@pytest.mark.parametrize("key,literal", [
    (0, "00"), (127, "7f"), (128, "8002"), (16383, "bfff"),
    (16384, "c00002"), (2097151, "dfffff"), (2097152, "e0000002"),
    (268435455, "efffffff"), (268435456, "f000000002"), (4294967295, "f7ffffff1f"),
])
def test_literal_compact_key_width_boundaries(key, literal):
    record = CreationReplicationRecord(0, (CreationRecordMember(key, 1, CreationMemberBody()),))
    raw = b"\x00\x01" + bytes.fromhex(literal) + b"\x01\x00"
    assert encode_record(record, class_table=TABLE) == raw
    assert decode_record(raw, class_table=TABLE) == (record, len(raw))


@pytest.mark.parametrize("wire,slot,key,index", [
    ("800000", 0, None, None),
    ("f80000000000", 0, None, None),
    ("f00000002000", 0, None, None),
    ("c0000800", 0, None, None),
    ("f7ffffff1f00", 65535, None, None),
    ("000180000100", 0, 0, 1),
    ("000100810000", 0, 0, 1),
    ("0001f0000000200100", 0, 0, 1),
])
def test_native_compact_aliases_and_record_slot_narrowing(wire, slot, key, index):
    expected = CreationReplicationRecord(slot, () if key is None else
        (CreationRecordMember(key, index, CreationMemberBody()),))
    raw = bytes.fromhex(wire)
    assert decode_record(raw, class_table=TABLE) == (expected, len(raw))
    assert decode_record(encode_record(expected, class_table=TABLE), class_table=TABLE)[0] == expected


@pytest.mark.parametrize("wire,field,cursor", [
    ("", "record slot", 0), ("80", "record slot", 1),
    ("e00000", "record slot", 1), ("00", "member count", 1),
    ("0001", "member 0 key", 2), ("000180", "member 0 key", 3),
    ("00010080", "member 0 class index", 4),
    ("00010000" + "00" * 15, "member 0 class UUID", 4),
    ("00010001", "member 0 group mask", 4),
    ("0001000102", "member 0 group mask", 5),
])
def test_offline_failure_diagnostic_offsets(wire, field, cursor):
    with pytest.raises(DecodeError) as raised:
        decode_record(bytes.fromhex(wire), class_table=TABLE)
    assert (raised.value.field, raised.value.cursor) == (field, cursor)


def test_invalid_index_has_no_raw_fallback_and_unknown_class_has_no_skip():
    for prefix, field in ((b"\x00\x01\x00\x03", "member 0 class index"),
                          (b"\x00\x02\x00\x02", "member 0 class UUID")):
        source = bytearray(prefix + MEMBER_UUID + b"\x00\x01\x01\x00")
        original = bytes(source)
        with pytest.raises(DecodeError) as raised:
            decode_record(source, class_table=TABLE)
        assert (raised.value.field, raised.value.cursor) == (field, 4)
        assert bytes(source) == original
    for raw in (bytes(16), b"x" * 16):
        with pytest.raises(DecodeError, match="unsupported member class"):
            decode_record(b"\x00\x01\x00\x00" + raw + b"\x00", class_table=TABLE)


def test_prefix_suffix_slice_and_owned_values():
    vector = VECTORS[4]
    raw = bytes.fromhex(vector["recordHex"])
    second = bytes.fromhex(VECTORS[0]["recordHex"])
    storage = bytearray(b"start" + raw + second + b"tail")
    view = memoryview(storage)[5:]
    record, consumed = decode_record(view, class_table=TABLE)
    assert record == _record(vector)
    assert consumed == len(raw)
    assert view[consumed:].tobytes() == second + b"tail"
    assert decode_record(view[consumed:], class_table=TABLE) == (_record(VECTORS[0]), 2)
    storage[:] = bytes(len(storage))
    assert encode_record(record, class_table=TABLE) == raw


def test_count_domain_empty_and_255_without_application_claim():
    member = CreationRecordMember(0, 1, CreationMemberBody())
    for count in (0, 1, 32, 33, 254, 255):
        record = CreationReplicationRecord(0, (member,) * count)
        raw = b"\x00" + bytes((count,)) + b"\x00\x01\x00" * count
        assert encode_record(record, class_table=TABLE) == raw
        assert decode_record(raw, class_table=TABLE) == (record, len(raw))
    with pytest.raises(ValueError, match="255"):
        CreationReplicationRecord(0, (member,) * 256)


def test_body_alias_is_consumed_and_canonicalized():
    raw = b"\x00\x01\x00\x01\x01\x00"
    record, consumed = decode_record(raw + b"suffix", class_table=TABLE)
    assert consumed == 6
    assert encode_record(record, class_table=TABLE) == b"\x00\x01\x00\x01\x00"


@pytest.mark.parametrize("bad", [-1, 65536, True, 1.0])
def test_slot_domain_rejects_lossy_constructor_values(bad):
    with pytest.raises(ValueError):
        CreationReplicationRecord(bad, ())


@pytest.mark.parametrize("bad", [-1, 1 << 32, True, 1.0])
def test_member_uint32_domains(bad):
    with pytest.raises(ValueError):
        CreationRecordMember(bad, 1, CreationMemberBody())
    with pytest.raises(ValueError):
        CreationRecordMember(0, bad, CreationMemberBody())


@pytest.mark.parametrize("bad", [(), [], (MEMBER_UUID,), (bytes(16), bytes(15)),
                                 (bytes(16), bytearray(16))])
def test_table_shape_and_reserved_nil_are_required(bad):
    with pytest.raises(ValueError, match="class_table"):
        decode_record(b"", class_table=bad)
    with pytest.raises(ValueError, match="class_table"):
        encode_record(CreationReplicationRecord(0, ()), class_table=bad)


def test_encode_table_guard_and_record_types():
    for index in (2, 3, 0xFFFFFFFF):
        record = CreationReplicationRecord(0, (CreationRecordMember(0, index, CreationMemberBody()),))
        with pytest.raises(ValueError, match="class_index"):
            encode_record(record, class_table=TABLE)
    with pytest.raises(TypeError):
        encode_record(object(), class_table=TABLE)
    with pytest.raises(ValueError):
        CreationReplicationRecord(0, [])
    with pytest.raises(ValueError):
        CreationRecordMember(0, 0, bytes(1))
    with pytest.raises(ValueError):
        replace(CreationReplicationRecord(0, ()), members=(object(),))
    with pytest.raises(TypeError):
        decode_record(memoryview(bytes(4))[::2], class_table=TABLE)
