"""Original synthetic checks for the source-backed selected sender layout."""

import json
from pathlib import Path
import sys
import zlib

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from current_registration_request_body import decode_body, encode_body  # noqa: E402
import current_registration_request_stream as stream  # noqa: E402

FIXTURE = ROOT / "tests/fixtures/registration/current-request-stream-original.json"
VECTORS = json.loads(FIXTURE.read_text(encoding="utf8"))["vectors"]
NEUTRAL, CONSUMED = decode_body(bytes.fromhex(VECTORS[0]["body"]))
assert CONSUMED == 69


@pytest.mark.parametrize("vector", VECTORS, ids=lambda item: item["name"])
def test_original_literal_width_and_bitwise_crc_goldens(vector):
    body = bytes.fromhex(vector["body"])
    record, consumed = decode_body(body)
    assert consumed == len(body)
    optional = {name: bytes.fromhex(vector[name]) if vector[name] is not None else None
                for name in ("field_04", "field_0c")}
    actual = stream.encode_registration_request_stream(record, type_index=vector["type_index"], **optional)
    expected = bytes.fromhex(vector["crc_be32"] + vector["count_be32"] + vector["payload"])
    assert actual == expected
    assert len(actual) == vector["length"]
    assert actual[8:24] == bytes(16)
    assert actual[24] == vector["flags"] in (0, 1, 3)
    assert actual[vector["body_offset"]:] == body == encode_body(record)
    assert int.from_bytes(actual[4:8], "big") == len(actual) - 8
    assert int.from_bytes(actual[:4], "big") == zlib.crc32(actual[8:])


def test_nil_outer_and_inner_fallback_are_separate():
    actual = stream.encode_registration_request_stream(NEUTRAL, type_index=0)
    assert actual[8:24] == bytes(16)
    assert actual[24:27] == b"\x00\x01\x00"  # flags, body presence, compact zero.
    assert actual[27:43] == bytes.fromhex("0b826b3389f549e0b8cbfe4433427778")
    assert actual[43:] == bytes(69)
    cached = stream.encode_registration_request_stream(NEUTRAL, type_index=19)
    assert cached[24:27] == b"\x00\x01\x13"
    assert len(cached) == len(actual) - 16
    assert cached[27:] == actual[43:]
    assert cached[:4] != actual[:4]


def test_ordered_opaque_fields_shift_presence_and_body():
    first = b"\x00\xffabcdef"; second = b"fedcba\xff\x00"
    actual = stream.encode_registration_request_stream(NEUTRAL, type_index=128,
                                                       field_04=first, field_0c=second)
    assert actual[24:43] == b"\x03" + first + second + b"\x01\x80"
    assert actual[43:44] == b"\x02"
    assert actual[44:] == bytes(69)


@pytest.mark.parametrize("value", [-1, 1 << 32, True, False, None, 1.0, "19", b"\x13", [], object()])
def test_invalid_indices_fail_before_body_encoding(value, monkeypatch):
    monkeypatch.setattr(stream, "encode_body", lambda record: pytest.fail("encoded invalid index"))
    with pytest.raises(ValueError, match="type_index"):
        stream.encode_registration_request_stream(NEUTRAL, type_index=value)


@pytest.mark.parametrize("name", ["field_04", "field_0c"])
@pytest.mark.parametrize("value", [b"", bytes(7), bytes(9), bytearray(8), memoryview(bytes(8)), "12345678", 0])
def test_opaque_fields_require_exact_immutable_bytes(name, value):
    with pytest.raises(ValueError, match=name):
        stream.encode_registration_request_stream(NEUTRAL, type_index=0, **{name: value})


@pytest.mark.parametrize("second", [bytes(8), b"\xff" * 8])
def test_second_only_is_outside_fresh_wrapper_domain(second):
    with pytest.raises(ValueError, match="requires field_04"):
        stream.encode_registration_request_stream(NEUTRAL, type_index=0, field_0c=second)


@pytest.mark.parametrize("record", [None, b"", {}, (), object()])
def test_body_record_type_is_required(record):
    with pytest.raises(TypeError, match="RegistrationRequestBody"):
        stream.encode_registration_request_stream(record, type_index=0)


def test_type_index_has_no_implicit_map_default():
    with pytest.raises(TypeError, match="type_index"):
        stream.encode_registration_request_stream(NEUTRAL)


def test_payload_count_does_not_wrap_reported_oversize(monkeypatch):
    class ReportedLargeBody:
        def __len__(self):
            return 0xffffffff
    # Only a synthetic reported extent: no huge allocation or native fault test.
    monkeypatch.setattr(stream, "encode_body", lambda record: ReportedLargeBody())
    with pytest.raises(ValueError, match="payload exceeds uint32"):
        stream.encode_registration_request_stream(NEUTRAL, type_index=0)
