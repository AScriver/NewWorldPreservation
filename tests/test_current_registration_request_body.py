"""Original synthetic checks for the selected V3 request BODY only."""

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from current_registration_request_body import (  # noqa: E402
    DecodeError, Field2C8, FieldC0, RegistrationRequestBody, TaggedField,
    decode_body, encode_body,
)

FIXTURE = ROOT / "tests/fixtures/registration/current-request-body-original.json"
VECTORS = json.loads(FIXTURE.read_text(encoding="utf-8"))["vectors"]


def _record(values):
    def value_or_bytes(value):
        if isinstance(value, str):
            return int(value, 16) if value.startswith("0x") else bytes.fromhex(value)
        return value

    c0 = {name: b"" for name in (
        "field_00", "field_20", "field_40", "field_60", "field_80",
        "field_a8", "field_c8", "field_e8", "field_108", "field_128",
        "field_158", "field_180", "field_1a8", "field_1c8", "field_1e8")}
    c0.update({name: 0 for name in ("field_a0", "field_148", "field_14c",
                                      "field_150", "field_178", "field_17c")})
    c0["field_1a0"] = None
    c0.update({key: value_or_bytes(value)
               for key, value in values.get("field_c0", {}).items()})
    two_c8 = {name: b"" for name in ("field_08", "field_28", "field_48", "field_70",
                                          "field_90", "field_b0", "field_d0", "field_f0")}
    two_c8.update(field_00=0, field_04=0, field_68=0, field_110=False)
    two_c8.update({key: value_or_bytes(value)
                   for key, value in values.get("field_2c8", {}).items()})

    def tagged(name):
        item = values.get(name, {"field_30": 0, "field_00": ""})
        return TaggedField(item["field_30"],
                           field_00=bytes.fromhex(item["field_00"]) if "field_00" in item else None,
                           field_20=bytes.fromhex(item["field_20"]) if "field_20" in item else None)

    return RegistrationRequestBody(
        values.get("field_08", 0),
        tuple((value_or_bytes(key), bytes.fromhex(value)) for key, value in values.get("field_10", [])),
        bytes.fromhex(values.get("field_a0", "")), FieldC0(**c0), Field2C8(**two_c8),
        tagged("field_3e0"), tagged("field_420"), values.get("field_460", False),
    )


def _golden(vector):
    wire = vector["wire"]
    groups = (wire[name] for name in ("field_08", "field_10", "field_a0", "field_c0",
                                      "field_2c8", "field_3e0", "field_420", "field_460"))
    return bytes.fromhex("".join(part for group in groups
                                 for part in (group if isinstance(group, list) else [group])))


MINIMUM = _golden(VECTORS[0])


def _failure(data, code, cursor):
    with pytest.raises(DecodeError) as raised:
        decode_body(data)
    assert (raised.value.code, raised.value.cursor) == (code, cursor)


@pytest.mark.parametrize("vector", VECTORS, ids=lambda item: item["name"])
def test_hand_derived_original_goldens(vector):
    expected = _golden(vector)
    record = _record(vector["values"])
    assert len(expected) == vector["length"]
    assert encode_body(record) == expected
    assert decode_body(expected) == (record, len(expected))


def test_minimum_offsets_and_truncation_failure_codes():
    assert len(MINIMUM) == 69
    for cut, code, cursor in (
        (0, 2, 0), (3, 2, 0), (4, 1, 4),
        (6, 1, 6), (10, 1, 10), (11, 2, 11), (14, 2, 11),
        (37, 1, 37), (39, 3, 39), (43, 2, 43), (47, 3, 47),
        (64, 2, 64), (66, 2, 66), (68, 3, 68),
    ):
        _failure(MINIMUM[:cut], code, cursor)


@pytest.mark.parametrize("length,prefix", [
    (127, "7f"), (128, "8002"), (16383, "bfff"),
    (16384, "c00002"), (0x2FFFF, "dfff17"),
])
def test_canonical_compact_string_thresholds(length, prefix):
    record = _record({"field_a0": (b"x" * length).hex()})
    encoded = encode_body(record)
    assert encoded[5:5 + len(bytes.fromhex(prefix))] == bytes.fromhex(prefix)
    assert decode_body(encoded) == (record, len(encoded))


@pytest.mark.parametrize("alias", ["8000", "c00000", "e0000000", "f000000000"])
def test_nonminimal_string_prefixes(alias):
    body = MINIMUM[:5] + bytes.fromhex(alias) + MINIMUM[6:]
    assert decode_body(body) == (_record({}), len(body))


@pytest.mark.parametrize("first", range(0xF8, 0x100))
def test_f8_ff_compact_prefix_wraps_to_uint32(first):
    payload = bytes(first & 7)
    body = MINIMUM[:5] + bytes((first, 0, 0, 0, 0x20)) + payload + MINIMUM[6:]
    decoded, consumed = decode_body(body)
    assert decoded.field_a0 == payload
    assert consumed == len(body)


def test_collection_first_value_wins_but_all_pairs_consumed():
    # Two original wire pairs with the same key; the second value is discarded.
    collection = bytes.fromhex("0201020304024100010203040142")
    body = MINIMUM[:4] + collection + MINIMUM[5:]
    record, consumed = decode_body(body)
    assert record.field_10 == ((0x01020304, b"A\x00"),)
    assert consumed == len(body)
    assert encode_body(record) == MINIMUM[:4] + bytes.fromhex("0101020304024100") + MINIMUM[5:]


def test_collection_count_nonminimal_and_oversize():
    body = MINIMUM[:4] + bytes.fromhex("f000000000") + MINIMUM[5:]
    assert decode_body(body) == (_record({}), len(body))
    _failure(MINIMUM[:4] + bytes.fromhex("f000000004"), 4, 9)


@pytest.mark.parametrize("prefix", ["80", "c000", "e00000", "f0000000"])
def test_incomplete_compact_tail_commits_only_tag(prefix):
    _failure(MINIMUM[:5] + bytes.fromhex(prefix), 1, 6)


def test_collection_element_failure_cursors_differ_from_other_strings():
    pair_prefix = MINIMUM[:4] + bytes.fromhex("0101020304")
    _failure(pair_prefix[:8], 2, 5)  # BE32 key is incomplete.
    _failure(pair_prefix + bytes.fromhex("e0003000"), 4, 13)
    _failure(pair_prefix + bytes.fromhex("034142"), 2, 12)
    _failure(MINIMUM[:5] + bytes.fromhex("e0003000"), 1, 9)
    _failure(MINIMUM[:5] + bytes.fromhex("034142"), 1, 6)


@pytest.mark.parametrize("offset,code,cursor", [
    (37, 1, 37), (39, 3, 39), (47, 3, 47), (64, 2, 64), (66, 2, 66), (68, 3, 68),
])
def test_missing_field_failures(offset, code, cursor):
    _failure(MINIMUM[:offset], code, cursor)


@pytest.mark.parametrize("offset", [39, 47, 68])
def test_invalid_boolean_or_presence_consumes_byte(offset):
    body = bytearray(MINIMUM)
    body[offset] = 2
    _failure(body, 4, offset + 1)


def test_present_optional_missing_and_invalid_value():
    body = bytearray(MINIMUM)
    body[39] = 1
    _failure(body[:40], 3, 40)
    body.insert(40, 2)
    _failure(body, 4, 41)
    body[40] = 0
    decoded, consumed = decode_body(body)
    assert decoded.field_c0.field_1a0 is False
    assert consumed == 70


def test_tag_branch_short_odd_and_even_string_failure():
    odd = MINIMUM[:64] + b"\xfd" + bytes(15)
    _failure(odd, 1, 65)
    even = MINIMUM[:64] + b"\xfe\x03ab"
    _failure(even, 1, 66)


@pytest.mark.parametrize("tag", range(256))
def test_every_raw_tag_preserved_with_only_active_payload(tag):
    item = TaggedField(tag, field_20=bytes(range(16))) if tag & 1 else TaggedField(tag, field_00=b"\x00Z")
    record = _record({})
    record = RegistrationRequestBody(record.field_08, record.field_10, record.field_a0,
                                     record.field_c0, record.field_2c8, item,
                                     record.field_420, record.field_460)
    decoded, consumed = decode_body(encode_body(record))
    assert decoded.field_3e0 == item
    assert consumed == len(encode_body(record))


def test_immutable_owned_bytes_and_trailing_data():
    data = bytearray(_golden(VECTORS[1]) + b"trailing")
    decoded, consumed = decode_body(data)
    assert consumed == VECTORS[1]["length"]
    assert decoded.field_a0 == b"\x00\xff"
    assert decoded.field_3e0.field_20 == bytes(range(16))
    data[:] = b"\x00" * len(data)
    assert decoded.field_a0 == b"\x00\xff"
    assert decoded.field_3e0.field_20 == bytes(range(16))


@pytest.mark.parametrize("change", [
    {"field_08": -1}, {"field_08": 1 << 32}, {"field_08": True},
    {"field_10": ((1, b"A"), (1, b"B"))},
    {"field_10": ((1, bytearray(b"A")),)},
    {"field_a0": bytearray(b"A")}, {"field_a0": bytes(0x30000)},
    {"field_460": 1},
])
def test_record_rejects_invalid_or_lossy_encoder_inputs(change):
    record = _record({})
    fields = record.__dict__.copy()
    fields.update(change)
    with pytest.raises(ValueError):
        RegistrationRequestBody(**fields)


def test_nested_records_reject_inactive_or_invalid_values():
    with pytest.raises(ValueError):
        TaggedField(1, field_00=b"", field_20=bytes(16))
    with pytest.raises(ValueError):
        TaggedField(0, field_00=b"", field_20=bytes(16))
    with pytest.raises(ValueError):
        TaggedField(1, field_20=bytes(15))
    with pytest.raises(ValueError):
        FieldC0(**{**_record({}).field_c0.__dict__, "field_1a0": 1})
    with pytest.raises(ValueError):
        Field2C8(**{**_record({}).field_2c8.__dict__, "field_110": 1})
    with pytest.raises(TypeError):
        encode_body(object())
