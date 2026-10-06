"""Literal, malformed and composition controls; fixtures are explicitly synthetic."""

from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from current_creation_member_body import CreationMemberBody, MEMBER_UUID  # noqa: E402
from current_creation_replication_record import CreationRecordMember, CreationReplicationRecord  # noqa: E402
from current_type8_bundle_body import (  # noqa: E402
    BundleBody, BundleOptionalStructure, DecodeError, decode_body, decode_creation_payload,
    encode_body, encode_creation_payload,
)
from current_world_activation import BUNDLE_HEADER, encode_empty_bundle  # noqa: E402

FIXTURE = json.loads((ROOT / "tests/fixtures/replication/current-type8-bundle-original.json").read_text())
VECTORS = FIXTURE["vectors"]
TABLE = (bytes(16), MEMBER_UUID)


def _body(vector):
    raw = vector["structure"]
    structure = BundleOptionalStructure(raw["fieldD0"], tuple(raw["items"])) if raw is not None else None
    return BundleBody(vector["sequence"], vector["field30"], vector["field31"], vector["field08"],
                      structure, bytes.fromhex(vector["payloadHex"]))


@pytest.mark.parametrize("vector", VECTORS, ids=lambda value: value["name"])
def test_synthetic_literal_goldens(vector):
    assert FIXTURE["classification"] == "synthetic"
    raw, body = bytes.fromhex(vector["bodyHex"]), _body(vector)
    assert len(raw) == vector["length"]
    assert encode_body(body) == raw
    assert decode_body(raw) == (body, len(raw))


@pytest.mark.parametrize("vector", VECTORS, ids=lambda value: value["name"])
def test_every_small_fixture_proper_truncation_rejects_without_mutation(vector):
    raw = bytes.fromhex(vector["bodyHex"])
    for size in range(len(raw)):
        source = bytearray(raw[:size])
        with pytest.raises(DecodeError) as raised:
            decode_body(source)
        assert bytes(source) == raw[:size]
        assert 0 <= raised.value.cursor <= size


@pytest.mark.parametrize("value,literal", [
    (0, "00"), (127, "7f"), (128, "8002"), (16383, "bfff"), (16384, "c00002"),
    (2097151, "dfffff"), (2097152, "e0000002"), (268435455, "efffffff"),
    (268435456, "f000000002"), (34359738367, "f7ffffffff"),
    (34359738368, "f80000000002"), (4398046511103, "fbffffffffff"),
    (4398046511104, "fc000000000002"), (562949953421311, "fdffffffffffff"),
    (562949953421312, "fe00000000000002"), (72057594037927935, "feffffffffffffff"),
    (72057594037927936, "ff0000000000000001"), (18446744073709551614, "fffeffffffffffffff"),
])
def test_literal_sequence_width_boundaries(value, literal):
    raw = b"\x01" + bytes.fromhex(literal) + bytes(5)
    body = BundleBody(sequence=value)
    assert encode_body(body) == raw
    assert decode_body(raw) == (body, len(raw))


def test_present_all_ones_sequence_and_nonminimal_zero_canonicalize():
    raw = b"\x01\xff" + b"\xff" * 8 + bytes(5)
    body, consumed = decode_body(raw)
    assert body.sequence is None and consumed == 15
    assert encode_body(body) == bytes(6)
    body, consumed = decode_body(b"\x01\x80\x00" + bytes(5))
    assert body.sequence == 0 and consumed == 8
    assert encode_body(body) == b"\x01" + bytes(6)


def test_compact64_f8_requires_six_bytes_unlike_compact32():
    with pytest.raises(DecodeError) as raised:
        decode_body(bytes.fromhex("01f800000000"))
    assert raised.value.field == "sequence"
    assert raised.value.cursor == 2
    raw = bytes(5) + bytes.fromhex("f800000000")
    assert decode_body(raw) == (BundleBody(), 10)


@pytest.mark.parametrize("position,field", [(0, "sequence presence"), (3, "field_08"), (4, "structure presence")])
@pytest.mark.parametrize("bad", [2, 128, 255])
def test_boolean_bytes_are_strict(position, field, bad):
    raw = bytearray(6)
    raw[position] = bad
    with pytest.raises(DecodeError) as raised:
        decode_body(raw)
    assert raised.value.field == field and raised.value.cursor == position
    assert raw[position] == bad


def test_absent_and_present_empty_structure_are_distinct():
    present = BundleBody(optional_structure=BundleOptionalStructure())
    assert encode_body(BundleBody()) == bytes.fromhex("000000000000")
    assert encode_body(present) == bytes.fromhex("0000000001000000")
    assert decode_body(encode_body(present))[0] == present


@pytest.mark.parametrize("scalar,literal", [
    (0, "00"), (127, "7f"), (128, "8002"), (16384, "c00002"),
    (2097152, "e0000002"), (268435456, "f000000002"), (4294967295, "f7ffffff1f"),
])
def test_optional_scalar_compact32_boundaries_and_item_endianness(scalar, literal):
    body = BundleBody(optional_structure=BundleOptionalStructure(scalar, (0, 0x1234, 0xFFFF)))
    raw = bytes.fromhex("0000000001" + literal + "0300001234ffff00")
    assert encode_body(body) == raw
    assert decode_body(raw) == (body, len(raw))


def test_compact32_scalar_and_count_aliases_are_retained_then_canonicalized():
    raw = bytes.fromhex("0000000001f100000020f00000002000")
    body, consumed = decode_body(raw)
    assert body == BundleBody(optional_structure=BundleOptionalStructure(1))
    assert consumed == len(raw)
    assert encode_body(body) == bytes.fromhex("0000000001010000")


def test_structure_count_100_is_supported_and_101_is_rejected():
    body = BundleBody(optional_structure=BundleOptionalStructure(0, (0x1234,) * 100))
    raw = bytes.fromhex("00000000010064") + b"\x12\x34" * 100 + b"\x00"
    assert encode_body(body) == raw
    assert decode_body(raw) == (body, len(raw))
    with pytest.raises(DecodeError, match="exceeds 100"):
        decode_body(bytes.fromhex("00000000010065"))
    with pytest.raises(ValueError, match="at most 100"):
        BundleOptionalStructure(0, (0,) * 101)


@pytest.mark.parametrize("size,literal", [
    (0, "00"), (127, "7f"), (128, "8002"), (2047, "bf1f"),
    (2048, "8020"), (2049, "8120"), (16383, "bfff"), (16384, "c00002"),
    (256000, "c0401f"),
])
def test_literal_payload_count_and_inline_heap_cap_boundaries(size, literal):
    payload = b"\xa5" * size
    body = BundleBody(payload=payload)
    raw = bytes(5) + bytes.fromhex(literal) + payload
    assert encode_body(body) == raw
    assert decode_body(raw + b"OUTER") == (body, len(raw))
    if size:
        with pytest.raises(DecodeError, match="payload"):
            decode_body(raw[:-1])


def test_oversized_payload_rejects_instead_of_native_success_without_retention():
    with pytest.raises(ValueError, match="256000"):
        BundleBody(payload=bytes(256001))
    raw = bytes(5) + bytes.fromhex("c1401f") + bytes(256001)
    with pytest.raises(DecodeError, match="256000") as raised:
        decode_body(raw)
    assert raised.value.field == "payload length" and raised.value.cursor == 8


def test_factory_cap_limits_payload_rather_than_entire_body():
    body = BundleBody((1 << 64) - 2, 255, 255, True,
                      BundleOptionalStructure((1 << 32) - 1, (65535,) * 100), bytes(256000))
    prefix = (b"\x01\xff\xfe" + b"\xff" * 7 + bytes.fromhex("ffff0101f7ffffff1f64")
              + b"\xff\xff" * 100 + bytes.fromhex("c0401f"))
    raw = prefix + bytes(256000)
    assert len(prefix) == 223 and len(raw) == 256223
    assert encode_body(body) == raw
    assert decode_body(raw) == (body, 256223)


def test_declared_payload_ends_before_enclosing_suffix_and_is_copied():
    source = bytearray(bytes(5) + b"\x02ABOUTER")
    body, consumed = decode_body(memoryview(source))
    assert body.payload == b"AB" and consumed == 8
    assert source[consumed:] == b"OUTER"
    source[6:8] = b"XY"
    assert body.payload == b"AB"
    with pytest.raises(DecodeError):
        decode_body(bytes(5) + b"\x03AB")
    body, consumed = decode_body(bytes(5) + bytes.fromhex("f000000020") + b"OUTER")
    assert body == BundleBody() and consumed == 10


def test_bounded_creation_record_composition_uses_explicit_synthetic_table():
    records = (
        CreationReplicationRecord(0, (CreationRecordMember(7, 1, CreationMemberBody()),)),
        CreationReplicationRecord(128, ()),
    )
    payload = bytes.fromhex("0001070100800200")
    raw = bytes.fromhex("0000000000080001070100800200")
    assert encode_creation_payload(records, class_table=TABLE) == payload
    body = BundleBody(payload=payload)
    assert encode_body(body) == raw
    decoded, consumed = decode_body(raw + b"OUTER")
    assert consumed == len(raw) and decoded == body
    assert decode_creation_payload(decoded.payload, class_table=TABLE) == records
    assert decode_creation_payload(b"", class_table=TABLE) == ()
    assert encode_creation_payload((), class_table=TABLE) == b""


def test_unknown_member_or_later_truncation_fails_whole_payload_without_mutation_or_skip():
    payload = bytes.fromhex("000107020100")
    source = bytearray(bytes(5) + bytes([len(payload)]) + payload + b"OUTER")
    body, consumed = decode_body(source)
    before = bytes(source)
    with pytest.raises(DecodeError) as raised:
        decode_creation_payload(body.payload, class_table=TABLE)
    assert raised.value.scope == "payload" and raised.value.cursor == 4
    assert source[consumed:] == b"OUTER" and bytes(source) == before
    with pytest.raises(DecodeError) as raised:
        decode_creation_payload(bytes.fromhex("000107010080"), class_table=TABLE)
    assert raised.value.cursor == 6


def test_composition_cap_and_immutable_values_are_guarded():
    member = CreationRecordMember(7, 1, CreationMemberBody())
    record = CreationReplicationRecord(0, (member,) * 255)
    with pytest.raises(ValueError, match="256000"):
        encode_creation_payload((record,) * 400, class_table=TABLE)
    with pytest.raises(DecodeError, match="256000"):
        decode_creation_payload(bytes(256001), class_table=TABLE)
    with pytest.raises(ValueError):
        encode_creation_payload([], class_table=TABLE)
    for table in ([], (), (b"x" * 16,)):
        with pytest.raises(ValueError):
            decode_creation_payload(b"", class_table=table)


@pytest.mark.parametrize("change", [
    {"sequence": -1}, {"sequence": 1 << 64}, {"sequence": (1 << 64) - 1}, {"sequence": True},
    {"field_30": 256}, {"field_30": True}, {"field_31": -1}, {"field_08": 1},
    {"optional_structure": {}}, {"payload": bytearray()}, {"payload": ""},
])
def test_body_constructor_guards(change):
    with pytest.raises(ValueError):
        replace(BundleBody(), **change)


@pytest.mark.parametrize("scalar,items", [(True, ()), (-1, ()), (1 << 32, ()), (0, []), (0, (-1,)), (0, (65536,)), (0, (True,))])
def test_structure_constructor_guards(scalar, items):
    with pytest.raises(ValueError):
        BundleOptionalStructure(scalar, items)


def test_buffer_types_and_existing_default_candidate_literal_are_stable():
    assert encode_empty_bundle() == BUNDLE_HEADER + bytes(6)
    assert decode_body(bytearray(6)) == (BundleBody(), 6)
    assert decode_body(memoryview(bytes(6))) == (BundleBody(), 6)
    for invalid in ("", [], memoryview(bytes(12))[::2]):
        with pytest.raises(TypeError):
            decode_body(invalid)
    with pytest.raises(TypeError):
        encode_body({})
