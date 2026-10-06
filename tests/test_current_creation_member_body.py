"""Deterministic offline checks for the pinned creation member's BODY only."""

from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from current_creation_member_body import (  # noqa: E402
    AssetIdField, CreationMemberBody, DecodeError, MEMBER_UUID, decode_body, encode_body,
)


FIXTURE = json.loads((ROOT / "tests/fixtures/replication/current-creation-member-original.json")
                     .read_text(encoding="utf-8"))
VECTORS = FIXTURE["vectors"]


def _record(vector):
    asset = vector["assetId"]
    return CreationMemberBody(
        AssetIdField(bytes.fromhex(asset["raw16"]), asset["field_20"]) if asset is not None else None,
        bytes.fromhex(vector["gdeRef"]) if vector["gdeRef"] is not None else None,
    )


@pytest.mark.parametrize("vector", VECTORS, ids=lambda item: item["name"])
def test_literal_synthetic_body_goldens(vector):
    record = _record(vector)
    expected = bytes.fromhex(vector["bodyHex"])
    assert len(expected) == vector["length"]
    assert encode_body(record) == expected
    assert decode_body(expected, member_uuid=MEMBER_UUID) == (record, len(expected))


def test_guard_runs_before_body_parse():
    assert MEMBER_UUID.hex() == FIXTURE["memberUuid"]
    with pytest.raises(ValueError, match="member_uuid"):
        decode_body(b"", member_uuid=bytes(16))
    with pytest.raises(ValueError, match="member_uuid"):
        decode_body(b"", member_uuid=MEMBER_UUID[:-1])
    with pytest.raises(TypeError):
        decode_body(object(), member_uuid=MEMBER_UUID)


@pytest.mark.parametrize("vector", VECTORS, ids=lambda item: item["name"])
def test_every_proper_prefix_is_rejected_without_partial_value(vector):
    body = bytes.fromhex(vector["bodyHex"])
    for cut in range(len(body)):
        with pytest.raises(DecodeError) as raised:
            decode_body(body[:cut], member_uuid=MEMBER_UUID)
        assert 0 <= raised.value.cursor <= cut
        assert raised.value.field


@pytest.mark.parametrize("body,field,cursor", [
    (b"", "group mask", 0),
    (b"\x01", "field mask", 1),
    (b"\x01\x01" + bytes(15), "AssetId raw16", 2),
    (b"\x01\x01" + bytes(16) + bytes(3), "AssetId field_20", 18),
    (b"\x01\x03" + bytes(16) + bytes(4) + bytes(15), "GdeRef raw16", 22),
])
def test_failure_field_and_cursor(body, field, cursor):
    with pytest.raises(DecodeError) as raised:
        decode_body(body, member_uuid=MEMBER_UUID)
    assert (raised.value.field, raised.value.cursor) == (field, cursor)


def test_sliced_nonzero_origin_buffer_and_untouched_suffix():
    body = bytes.fromhex(VECTORS[-1]["bodyHex"])
    storage = bytearray(b"prefix" + body + b"suffix")
    view = memoryview(storage)[6:]
    record, consumed = decode_body(view, member_uuid=MEMBER_UUID)
    assert record == _record(VECTORS[-1])
    assert consumed == len(body)
    assert view[consumed:].tobytes() == b"suffix"
    assert storage == b"prefix" + body + b"suffix"
    storage[:] = bytes(len(storage))
    assert encode_body(record) == body  # raw values own immutable copies


def test_empty_group_alias_canonicalizes_without_consuming_suffix():
    record, consumed = decode_body(b"\x01\x00tail", member_uuid=MEMBER_UUID)
    assert record == CreationMemberBody()
    assert consumed == 2
    assert encode_body(record) == b"\x00"


@pytest.mark.parametrize("body,field,cursor", [
    (b"\x02", "group mask", 1),
    (b"\x80", "group mask", 1),
    (b"\x01\x04", "field mask", 2),
    (b"\x01\x40", "field mask", 2),
    (b"\x01\x80\x01", "field mask", 2),
])
def test_unsupported_mask_policy(body, field, cursor):
    with pytest.raises(DecodeError) as raised:
        decode_body(body, member_uuid=MEMBER_UUID)
    assert (raised.value.field, raised.value.cursor) == (field, cursor)


def test_raw_gde_bytes_survive_first_qword_collision():
    first = b"abcdefgh12345678"
    second = b"abcdefghABCDEFGH"
    assert first[:8] == second[:8]
    for raw in (first, second):
        record = CreationMemberBody(gde_ref=raw)
        assert decode_body(encode_body(record), member_uuid=MEMBER_UUID)[0].gde_ref == raw
    assert encode_body(CreationMemberBody(gde_ref=first)) != encode_body(CreationMemberBody(gde_ref=second))


@pytest.mark.parametrize("bad", [-1, 1 << 32, True, 1.0])
def test_uint32_rejects_lossy_or_invalid_values(bad):
    with pytest.raises(ValueError, match="uint32"):
        AssetIdField(bytes(16), bad)


@pytest.mark.parametrize("bad", [b"", bytes(15), bytes(17), bytearray(16), memoryview(bytes(16))])
def test_raw16_requires_exact_immutable_bytes(bad):
    with pytest.raises(ValueError):
        AssetIdField(bad, 0)
    with pytest.raises(ValueError):
        CreationMemberBody(gde_ref=bad)


def test_record_type_and_explicit_zero_presence():
    zero = CreationMemberBody(AssetIdField(bytes(16), 0), bytes(16))
    assert encode_body(zero) != encode_body(CreationMemberBody())
    with pytest.raises(ValueError):
        replace(zero, asset_id=bytes(16))
    with pytest.raises(TypeError):
        encode_body(object())
