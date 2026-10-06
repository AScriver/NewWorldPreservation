"""Original literals/controls for the current identity subset; no native run."""
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from current_player_identity_body import (
    PlayerIdentityBody, DecodeError, MAX_STRING_BYTES, MEMBER_UUID, encode_body, decode_body,
)


ID=b"00000000-0000-4000-8000-000000000020"
NAME=b"Preservation"
LITERAL=bytes.fromhex("02030024")+ID+bytes.fromhex("0c")+NAME


def test_literal_preservation_id_name_order_and_prefix_suffix():
    expected=PlayerIdentityBody(ID,NAME)
    assert encode_body(expected)==LITERAL
    decoded,cursor=decode_body(LITERAL+b"suffix",member_uuid=MEMBER_UUID)
    assert decoded==expected and cursor==53


@pytest.mark.parametrize("body,literal",[
    (PlayerIdentityBody(),b"\x00"), (PlayerIdentityBody(b"",None),b"\x02\x01\x00\x00"),
    (PlayerIdentityBody(None,b""),b"\x02\x02\x00"), (PlayerIdentityBody(b"",b""),b"\x02\x03\x00\x00\x00"),
    (PlayerIdentityBody(b"A",None),b"\x02\x01\x00\x01A"), (PlayerIdentityBody(None,b"B"),b"\x02\x02\x01B"),
])
def test_presence_empty_values_and_each_field(body,literal):
    assert encode_body(body)==literal
    assert decode_body(literal,member_uuid=MEMBER_UUID)==(body,len(literal))


@pytest.mark.parametrize("count,prefix",[(127,b"\x7f"),(128,b"\x80\x02"),(16383,b"\xbf\xff"),
                                         (16384,b"\xc0\x00\x02"),(MAX_STRING_BYTES,b"\xdf\xff\x17")])
@pytest.mark.parametrize("field",["character_id","character_name"])
def test_source_prefix_boundaries_and_byte_passthrough(count,prefix,field):
    value=(b"\xff\x00\xc3"*((count+2)//3))[:count]
    body=PlayerIdentityBody(**{field:value})
    header=b"\x02\x01\x00" if field=="character_id" else b"\x02\x02"
    encoded=encode_body(body)
    assert encoded==header+prefix+value
    assert decode_body(encoded,member_uuid=MEMBER_UUID)==(body,len(encoded))


@pytest.mark.parametrize("cut",[0,1,2,3,4,5,20,39,40,41,42,52])
def test_truncated_literal_never_returns_partial_identity(cut):
    with pytest.raises(DecodeError):
        decode_body(LITERAL[:cut],member_uuid=MEMBER_UUID)


@pytest.mark.parametrize("data",[b"\x01",b"\x03",b"\x04",b"\x80",b"\x02\x04",b"\x02\x80",b"\x02\x83",b"\x02\x01\x01",b"\x02\x01\x08"])
def test_other_groups_fields_continuation_and_id_flags_refused(data):
    with pytest.raises(DecodeError):
        decode_body(data,member_uuid=MEMBER_UUID)


def test_native_noncanonical_compact_and_zero_field_mask_preserved():
    assert decode_body(b"\x02\x02\x80\x00tail",member_uuid=MEMBER_UUID)==(PlayerIdentityBody(None,b""),4)
    assert decode_body(b"\x02\x00tail",member_uuid=MEMBER_UUID)==(PlayerIdentityBody(),2)
    assert decode_body(b"\x02\x02\xf8\x00\x00\x00\x00tail",member_uuid=MEMBER_UUID)==(PlayerIdentityBody(None,b""),7)


@pytest.mark.parametrize("field",["character_id","character_name"])
def test_oversize_guard_and_decoded_extent_before_copy(field):
    with pytest.raises(ValueError):
        PlayerIdentityBody(**{field:b"x"*(MAX_STRING_BYTES+1)})
    header=b"\x02\x01\x00" if field=="character_id" else b"\x02\x02"
    with pytest.raises(DecodeError,match="string limit"):
        decode_body(header+b"\xc0\x00\x18",member_uuid=MEMBER_UUID)
    with pytest.raises(DecodeError,match="truncated"):
        decode_body(header+b"\xdf\xff\x17",member_uuid=MEMBER_UUID)


@pytest.mark.parametrize("value",["text",bytearray(b"text"),memoryview(b"text"),42])
def test_fields_are_immutable_bytes(value):
    with pytest.raises(ValueError):PlayerIdentityBody(value)


@pytest.mark.parametrize("uuid",[bytes(16),bytes(15),bytearray(MEMBER_UUID),"bddda784a6e7416ba041449920d90fb6"])
def test_wrong_or_mutable_selector_refused_before_input(uuid):
    with pytest.raises(ValueError,match="member_uuid"):
        decode_body(b"",member_uuid=uuid)


def test_contiguous_memoryview_supported_and_strided_buffer_refused():
    assert decode_body(memoryview(LITERAL),member_uuid=MEMBER_UUID)==(PlayerIdentityBody(ID,NAME),53)
    with pytest.raises(TypeError,match="contiguous"):
        decode_body(memoryview(LITERAL)[::2],member_uuid=MEMBER_UUID)
