"""Original literal and reader-boundary checks; no native or Carrier execution."""

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from current_registration_response_body import (  # noqa: E402
    MAX_STRING_BYTES, RegistrationResponseBody, decode_body, encode_body,
)
import current_registration_response_record as response  # noqa: E402

BODY_VECTORS = json.loads((ROOT / "tests/fixtures/registration/current-response-body-original.json").read_text())["vectors"]
BODIES = {row["name"]: decode_body(bytes.fromhex(row["body_hex"]))[0] for row in BODY_VECTORS}
VECTORS = json.loads((ROOT / "tests/fixtures/registration/current-response-record-original.json").read_text())["vectors"]
MINIMUM = BODIES["minimum"]
FIRST, SECOND = bytes(range(8)), bytes(range(248, 256))


def read_compact(data, cursor=0):
    """Selected native-reader model; allows width aliases, checks available tail."""
    first = data[cursor]
    cursor += 1
    width, bits = next((width, bits) for bound, width, bits in (
        (0x80, 1, 7), (0xC0, 2, 6), (0xE0, 3, 5), (0xF0, 4, 4), (0x100, 5, 3),
    ) if first < bound)
    tail = data[cursor:cursor + width - 1]
    assert len(tail) == width - 1
    value = ((first & ((1 << bits) - 1)) | (int.from_bytes(tail, "little") << bits)) & 0xFFFFFFFF
    return value, cursor + width - 1


def read_record(data, expected_index, fields):
    length, start = read_compact(data)
    end = start + length
    assert end <= len(data)
    payload = data[start:end]
    expected_flags = int(fields[0] is not None) | (2 if fields[1] is not None else 0)
    assert payload[0] == expected_flags
    cursor = 1
    for value in fields:
        if value is not None:
            assert payload[cursor:cursor + 8] == value
            cursor += 8
    assert payload[cursor] == 1
    index, cursor = read_compact(payload, cursor + 1)
    assert index == expected_index
    if index == 0:
        assert payload[cursor:cursor + 16] == bytes.fromhex("104145a7ff9544f1946821fb41c8ac2b")
        cursor += 16
    body, consumed = decode_body(payload[cursor:])
    assert cursor + consumed == len(payload)
    return body, end


@pytest.mark.parametrize("vector", VECTORS, ids=lambda row: row["name"])
def test_hand_derived_record_literals(vector):
    fields = tuple(bytes.fromhex(vector[key]) if vector[key] is not None else None
                   for key in ("field_04", "field_0c"))
    actual = response.encode_registration_response_record(BODIES[vector["bodyName"]],
        type_index=vector["type_index"], field_04=fields[0], field_0c=fields[1])
    assert actual == bytes.fromhex(vector["record_hex"])
    length, prefix = read_compact(actual)
    assert length == vector["payloadBytes"] == len(actual) - prefix
    decoded, consumed = read_record(actual, vector["type_index"], fields)
    assert decoded == BODIES[vector["bodyName"]] and consumed == len(actual)


@pytest.mark.parametrize("index,selector", [
    (0, "00"), (3, "03"), (127, "7f"), (128, "8002"),
    (16383, "bfff"), (16384, "c00002"), (0x1FFFFF, "dfffff"),
    (0x200000, "e0000002"), (0xFFFFFFF, "efffffff"),
    (0x10000000, "f000000002"), (0xFFFFFFFF, "f7ffffff1f"),
])
@pytest.mark.parametrize("fields", [(None, None), (FIRST, None), (FIRST, SECOND)])
@pytest.mark.parametrize("body", BODIES.values())
def test_reader_compatibility_with_all_selector_widths(index, selector, fields, body):
    actual = response.encode_registration_response_record(body, type_index=index,
        field_04=fields[0], field_0c=fields[1])
    _, start = read_compact(actual)
    selector_start = start + 2 + 8 * sum(value is not None for value in fields)
    assert actual[selector_start:selector_start + len(bytes.fromhex(selector))] == bytes.fromhex(selector)
    decoded, consumed = read_record(actual + b"outer-suffix", index, fields)
    assert decoded == body and actual[consumed:] == b""


@pytest.mark.parametrize("string_size,prefix,length", [
    (106, "7f", 127), (107, "8002", 128),
    (16361, "bfff", 16383), (16362, "c00002", 16384),
])
def test_outer_length_boundaries_include_actual_count_prefixes(string_size, prefix, length):
    body = RegistrationResponseBody(0, 0, b"x" * string_size, b"", (False,) * 4)
    actual = response.encode_registration_response_record(body, type_index=3)
    assert actual.startswith(bytes.fromhex(prefix))
    assert len(actual) == length + len(bytes.fromhex(prefix))
    assert read_record(actual, 3, (None, None))[0] == body


@pytest.mark.parametrize("index", [0, 3, 0xFFFFFFFF])
def test_maximum_valid_body_and_opaque_fields(index):
    body = RegistrationResponseBody(0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF,
        b"\x00\xff" * (MAX_STRING_BYTES // 2) + b"\x00",
        b"z" * MAX_STRING_BYTES, (True,) * 4)
    actual = response.encode_registration_response_record(body, type_index=index,
        field_04=FIRST, field_0c=SECOND)
    assert read_record(actual, index, (FIRST, SECOND)) == (body, len(actual))


def test_concatenated_records_have_independent_declared_extents():
    first = response.encode_registration_response_record(MINIMUM, type_index=3)
    second = response.encode_registration_response_record(BODIES["endian-raw-nul-bool-order"], type_index=0)
    decoded, consumed = read_record(first + second, 3, (None, None))
    assert decoded == MINIMUM and consumed == len(first)
    assert read_record((first + second)[consumed:], 0, (None, None))[0] == BODIES["endian-raw-nul-bool-order"]


@pytest.mark.parametrize("value", [-1, 1 << 32, True, False, None, 1.0, "3", b"\x03", [], object()])
def test_invalid_binding_is_rejected_before_body_encoding(value, monkeypatch):
    monkeypatch.setattr(response, "encode_body", lambda record: pytest.fail("invalid binding encoded BODY"))
    with pytest.raises(ValueError, match="type_index"):
        response.encode_registration_response_record(MINIMUM, type_index=value)


@pytest.mark.parametrize("name", ["field_04", "field_0c"])
@pytest.mark.parametrize("value", [b"", bytes(7), bytes(9), bytearray(8), memoryview(bytes(8)), "12345678", 0])
def test_opaque_fields_are_exact_immutable_bytes(name, value):
    with pytest.raises(ValueError, match=name):
        response.encode_registration_response_record(MINIMUM, type_index=3, **{name: value})


def test_second_only_is_outside_selected_fresh_domain():
    with pytest.raises(ValueError, match="requires field_04"):
        response.encode_registration_response_record(MINIMUM, type_index=3, field_0c=SECOND)


@pytest.mark.parametrize("record", [None, b"", {}, (), object()])
def test_body_record_type_is_required(record):
    with pytest.raises(TypeError, match="RegistrationResponseBody"):
        response.encode_registration_response_record(record, type_index=3)


def test_no_implicit_runtime_type_binding():
    with pytest.raises(TypeError, match="type_index"):
        response.encode_registration_response_record(MINIMUM)


def test_typed_record_has_no_sender_crc_or_outer_descriptor():
    actual = response.encode_registration_response_record(MINIMUM, type_index=3)
    assert actual == b"\x15\x00\x01\x03" + encode_body(MINIMUM)
    assert len(actual) == 22
