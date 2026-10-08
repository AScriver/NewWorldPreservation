"""Literal sender compatibility and hostile-input checks for our server decoder."""

from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import sys
import zlib

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import current_registration_request_receive as receive  # noqa: E402
from current_registration_request_body import decode_body  # noqa: E402

VECTORS = json.loads((ROOT / "tests/fixtures/registration/current-request-stream-original.json").read_text())["vectors"]


def literal(vector):
    return bytes.fromhex(vector["crc_be32"] + vector["count_be32"] + vector["payload"])


def physical(payload):
    # Rebuild only checksum/count for independent mutated payloads, never use sender.
    return zlib.crc32(payload).to_bytes(4, "big") + len(payload).to_bytes(4, "big") + payload


@pytest.mark.parametrize("vector", VECTORS, ids=lambda item: item["name"])
def test_decode_existing_literal_sender_streams(vector):
    expected_body, consumed_body = decode_body(bytes.fromhex(vector["body"]))
    result, consumed = receive.decode_registration_request_stream(
        literal(vector), expected_type_index=vector["type_index"])
    assert consumed == vector["length"]
    assert consumed_body == len(bytes.fromhex(vector["body"]))
    assert result.body == expected_body
    assert result.type_index == vector["type_index"]
    for name in ("field_04", "field_0c"):
        assert getattr(result, name) == (bytes.fromhex(vector[name]) if vector[name] is not None else None)


def test_two_records_return_only_first_extent_and_ignore_outer_suffix():
    first, second = VECTORS[0], VECTORS[-1]
    data = literal(first) + literal(second) + b"outer-tail"
    _, first_extent = receive.decode_registration_request_stream(data, expected_type_index=first["type_index"])
    result, second_extent = receive.decode_registration_request_stream(
        memoryview(data)[first_extent:], expected_type_index=second["type_index"])
    assert first_extent == first["length"]
    assert second_extent == second["length"]
    assert result.body == decode_body(bytes.fromhex(second["body"]))[0]


@pytest.mark.parametrize("kind", [bytearray, memoryview])
def test_decode_owns_all_returned_fields(kind):
    vector = next(item for item in reversed(VECTORS) if item["flags"] == 3)
    original = literal(vector)
    source = bytearray(original)
    result, consumed = receive.decode_registration_request_stream(kind(source), expected_type_index=vector["type_index"])
    source[:] = bytes(len(source))
    assert result.body == decode_body(bytes.fromhex(vector["body"]))[0]
    assert result.field_04 == bytes.fromhex(vector["field_04"])
    assert result.field_0c == bytes.fromhex(vector["field_0c"])
    assert consumed == len(original)
    with pytest.raises(FrozenInstanceError):
        result.type_index = 7


def test_parse_uses_checksummed_snapshot_even_if_source_changes_during_crc(monkeypatch):
    vector = VECTORS[0]
    source = bytearray(literal(vector))
    real_crc = zlib.crc32
    def mutate_after_crc(payload):
        checksum = real_crc(payload)
        source[vector["body_offset"]:vector["body_offset"] + 4] = b"\xff" * 4
        return checksum
    monkeypatch.setattr(receive.zlib, "crc32", mutate_after_crc)
    result, _ = receive.decode_registration_request_stream(source, expected_type_index=0)
    assert result.body.field_08 == 0


@pytest.mark.parametrize("position", range(112))
def test_every_shorter_prefix_of_literal_fallback_record_is_rejected(position):
    with pytest.raises(receive.StreamDecodeError):
        receive.decode_registration_request_stream(literal(VECTORS[0])[:position], expected_type_index=0)


@pytest.mark.parametrize("length", [0, 1, 15, 16, 17, 18, 34, 103])
def test_crc_valid_shorter_payload_reaches_controlled_prefix_or_body_failure(length):
    payload = bytes.fromhex(VECTORS[0]["payload"])[:length]
    with pytest.raises(receive.StreamDecodeError):
        receive.decode_registration_request_stream(physical(payload), expected_type_index=0)


@pytest.mark.parametrize("offset,value,reason", [
    (0, 1, "outer-uuid"), (16, 2, "wrapper-flags"), (16, 4, "wrapper-flags"),
    (16, 255, "wrapper-flags"), (17, 0, "body-presence"), (17, 2, "body-presence"),
    (18, 19, "type-mismatch"), (19, 255, "type-uuid"), (-1, 2, "body"),
])
def test_crc_valid_invalid_fields_are_rejected(offset, value, reason):
    payload = bytearray.fromhex(VECTORS[0]["payload"])
    payload[offset] = value
    with pytest.raises(receive.StreamDecodeError) as raised:
        receive.decode_registration_request_stream(physical(payload), expected_type_index=0)
    assert raised.value.reason == reason
    if reason == "body":
        assert raised.value.body_code == 4
        assert raised.value.cursor == len(physical(payload))


@pytest.mark.parametrize("selector", [b"\x80\x00", b"\xc0\x00\x00", b"\xe0\x00\x00\x00",
                                      b"\xf0\x00\x00\x00\x00", b"\xf8\x00\x00\x00\x00",
                                      b"\xf0\x00\x00\x00\x20"])
def test_noncanonical_and_uint32_wrapping_selector_aliases_are_server_policy_rejections(selector):
    payload = bytes.fromhex(VECTORS[0]["payload"])
    changed = payload[:18] + selector + payload[19:]
    with pytest.raises(receive.StreamDecodeError, match="selector-noncanonical"):
        receive.decode_registration_request_stream(physical(changed), expected_type_index=0)


@pytest.mark.parametrize("width", [1, 2, 3, 4])
def test_incomplete_five_byte_selector_is_rejected(width):
    payload = bytes(16) + b"\x00\x01" + b"\xf0" + bytes(width - 1)
    with pytest.raises(receive.StreamDecodeError, match="type-selector"):
        receive.decode_registration_request_stream(physical(payload), expected_type_index=0)


def test_body_may_not_borrow_suffix_outside_declared_payload():
    payload = bytes.fromhex(VECTORS[0]["payload"])
    changed = physical(payload[:-1]) + payload[-1:]
    with pytest.raises(receive.StreamDecodeError) as raised:
        receive.decode_registration_request_stream(changed, expected_type_index=0)
    assert raised.value.reason == "body"
    assert raised.value.body_code == 3
    assert raised.value.cursor == len(changed) - 1


def test_extra_byte_inside_selected_body_is_rejected_but_outer_suffix_is_accepted():
    vector = VECTORS[0]
    with pytest.raises(receive.StreamDecodeError, match="body-extent"):
        receive.decode_registration_request_stream(physical(bytes.fromhex(vector["payload"]) + b"\x00"), expected_type_index=0)
    _, consumed = receive.decode_registration_request_stream(literal(vector) + b"\x00", expected_type_index=0)
    assert consumed == vector["length"]


@pytest.mark.parametrize("case", ["limit", "truncated", "checksum"])
def test_envelope_rejection_precedes_body_decode(case, monkeypatch):
    data = literal(VECTORS[0])
    if case == "limit":
        data = b"\x00" * 4 + (receive.DEFAULT_MAX_PAYLOAD_BYTES + 1).to_bytes(4, "big")
    elif case == "truncated":
        data = data[:-1]
    else:
        data = b"\x00" * 4 + data[4:]
    monkeypatch.setattr(receive, "decode_body", lambda data: pytest.fail("decoded rejected envelope"))
    with pytest.raises(receive.StreamDecodeError):
        receive.decode_registration_request_stream(data, expected_type_index=0)


def test_cap_is_payload_only_and_can_be_configured_explicitly():
    data = literal(VECTORS[0])
    _, consumed = receive.decode_registration_request_stream(data + bytes(400), expected_type_index=0, max_payload_bytes=len(data) - 8)
    assert consumed == len(data)
    with pytest.raises(receive.StreamDecodeError, match="payload-limit"):
        receive.decode_registration_request_stream(data, expected_type_index=0, max_payload_bytes=len(data) - 9)


@pytest.mark.parametrize("name", ["expected_type_index", "max_payload_bytes"])
@pytest.mark.parametrize("value", [-1, 1 << 32, True, False, None, 1.0, "19", b"\x13", [], object()])
def test_invalid_configuration_is_rejected_before_buffer_read(name, value):
    parameters = {"expected_type_index": 0, name: value}
    with pytest.raises(ValueError, match=name):
        receive.decode_registration_request_stream(object(), **parameters)


def test_zero_limit_and_missing_selector_are_rejected():
    with pytest.raises(ValueError, match="positive"):
        receive.decode_registration_request_stream(b"", expected_type_index=0, max_payload_bytes=0)
    with pytest.raises(TypeError, match="expected_type_index"):
        receive.decode_registration_request_stream(b"")


@pytest.mark.parametrize("data", [None, "text", 112, [], object(), memoryview(bytes(20))[::2]])
def test_invalid_or_noncontiguous_buffer_has_fixed_diagnostic(data):
    with pytest.raises(TypeError, match="contiguous byte buffer"):
        receive.decode_registration_request_stream(data, expected_type_index=0)


def test_released_memoryview_has_controlled_diagnostic():
    data = memoryview(bytes(20))
    data.release()
    with pytest.raises(TypeError, match="contiguous byte buffer"):
        receive.decode_registration_request_stream(data, expected_type_index=0)


def test_diagnostic_does_not_echo_hostile_field_bytes():
    marker = b"private-marker-never-export"
    with pytest.raises(receive.StreamDecodeError) as raised:
        receive.decode_registration_request_stream(physical(marker + bytes(110)), expected_type_index=0)
    assert marker.decode() not in str(raised.value)
    assert marker.decode() not in repr(raised.value)
