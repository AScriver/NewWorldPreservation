"""Synthetic, source-constrained checks for the current response BODY only."""

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from current_registration_response_body import (  # noqa: E402
    DecodeError, RegistrationResponseBody, decode_body, encode_body,
)

FIXTURE = ROOT / "tests/fixtures/registration/current-response-body-original.json"
PREFIX = bytes(12)
EMPTY_TAIL = bytes(4)


def _vectors():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["vectors"]


@pytest.mark.parametrize("vector", _vectors(), ids=lambda item: item["name"])
def test_hand_derived_original_body_golden(vector):
    record = RegistrationResponseBody(
        vector["field_08"], vector["field_10"],
        bytes.fromhex(vector["field_18_hex"]), bytes.fromhex(vector["field_38_hex"]),
        tuple(vector["flags"]),
    )
    expected = bytes.fromhex(vector["body_hex"])
    assert encode_body(record) == expected
    assert decode_body(expected) == (record, len(expected))


@pytest.mark.parametrize("length,prefix", [
    (127, "7f"), (128, "8002"), (16383, "bfff"),
    (16384, "c00002"), (0x2FFFF, "dfff17"),
])
def test_canonical_compact_thresholds(length, prefix):
    record = RegistrationResponseBody(0, 0, b"x" * length, b"", (False,) * 4)
    encoded = encode_body(record)
    assert encoded[12:12 + len(bytes.fromhex(prefix))] == bytes.fromhex(prefix)
    assert decode_body(encoded) == (record, len(encoded))


@pytest.mark.parametrize("alias", [
    "8000", "c00000", "e0000000", "f000000000",
])
def test_reader_accepts_nonminimal_prefix(alias):
    body = PREFIX + bytes.fromhex(alias) + b"\x00" + EMPTY_TAIL
    assert decode_body(body) == (
        RegistrationResponseBody(0, 0, b"", b"", (False,) * 4), len(body))


@pytest.mark.parametrize("first", range(0xF8, 0x100))
def test_reader_accepts_f8_ff_and_uint32_wrap(first):
    # High final-byte bits wrap at the uint32 destination; the low three bits
    # of F8..FF select an independently bounded raw payload length.
    body = PREFIX + bytes((first, 0, 0, 0, 0x20)) + bytes(first & 7) + b"\x00" + EMPTY_TAIL
    decoded, consumed = decode_body(body)
    assert decoded.field_18 == bytes(first & 7)
    assert consumed == len(body)


def test_every_golden_truncation_reports_helper_code_and_consumed_cursor():
    body = bytes.fromhex(_vectors()[1]["body_hex"])
    for cut in range(len(body)):
        if cut < 4:
            code, cursor = 2, 0
        elif cut < 12:
            code, cursor = 2, 4
        elif cut == 12:
            code, cursor = 1, 12
        elif cut < 16:
            code, cursor = 1, 13
        elif cut == 16:
            code, cursor = 1, 16
        elif cut < 19:
            code, cursor = 1, 17
        else:
            code, cursor = 3, cut
        with pytest.raises(DecodeError) as raised:
            decode_body(body[:cut])
        assert (raised.value.code, raised.value.cursor) == (code, cursor)


@pytest.mark.parametrize("incomplete", ["80", "c000", "e00000", "f0000000"])
def test_incomplete_compact_tail_consumes_first_byte_only(incomplete):
    with pytest.raises(DecodeError) as raised:
        decode_body(PREFIX + bytes.fromhex(incomplete))
    assert (raised.value.code, raised.value.cursor) == (1, 13)


@pytest.mark.parametrize("declared", ["e0003000", "f000600000"])
def test_oversized_declared_count_rejected_before_payload_copy(declared):
    # 0x30000 through two different allowed prefix widths.
    with pytest.raises(DecodeError) as raised:
        decode_body(PREFIX + bytes.fromhex(declared))
    assert (raised.value.code, raised.value.cursor) == (1, 12 + len(bytes.fromhex(declared)))


def test_payload_short_leaves_prefix_consumed_and_payload_unadvanced():
    with pytest.raises(DecodeError) as raised:
        decode_body(PREFIX + b"\x03ab")
    assert (raised.value.code, raised.value.cursor) == (1, 13)


@pytest.mark.parametrize("position", range(4))
def test_invalid_boolean_is_consumed_before_failure(position):
    body = PREFIX + b"\x00\x00" + bytes(position) + b"\x02"
    with pytest.raises(DecodeError) as raised:
        decode_body(body)
    assert (raised.value.code, raised.value.cursor) == (4, 15 + position)


def test_trailing_bytes_and_mutable_source_do_not_escape_body_view():
    source = bytearray.fromhex(_vectors()[1]["body_hex"])
    source.extend(b"unused")
    record, consumed = decode_body(source)
    assert consumed == 23
    assert record.field_18 == b"\x00\xffA"
    source[14] = 0
    assert record.field_18 == b"\x00\xffA"


@pytest.mark.parametrize("field,value", [
    ("field_08", -1), ("field_08", 1 << 32), ("field_08", True),
    ("field_10", -1), ("field_10", 1 << 64), ("field_10", 1.0),
    ("field_18", bytearray(b"x")), ("field_38", memoryview(b"x")),
    ("field_18", bytes(0x30000)),
    ("flags", (False, False, False, 1)),
    ("flags", (False,) * 3), ("flags", [False] * 4),
], ids=["u32-negative", "u32-overflow", "u32-bool", "u64-negative",
        "u64-overflow", "u64-float", "bytes-mutable", "bytes-view",
        "bytes-oversize", "flags-nonbool", "flags-short", "flags-list"])
def test_record_rejects_out_of_contract_values(field, value):
    args = dict(field_08=0, field_10=0, field_18=b"", field_38=b"",
                flags=(False,) * 4)
    args[field] = value
    with pytest.raises(ValueError):
        RegistrationResponseBody(**args)


def test_encoder_requires_immutable_record():
    with pytest.raises(TypeError):
        encode_body(object())
