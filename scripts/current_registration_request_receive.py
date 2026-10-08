"""Original server decoder for the proved selected V3 client sender stream.

This is a safe inverse of the sender contract, not recovered native receive code.
Carrier placement, runtime selector binding and authentication remain unproved.
The default limit and canonical-selector/exact-BODY checks are receiver policy.
"""

from __future__ import annotations

from dataclasses import dataclass
import zlib

from current_registration_request_body import (
    DecodeError as BodyDecodeError, RegistrationRequestBody,
    _Reader, _check_uint, _encode_count, decode_body,
)
from current_registration_request_stream import NIL_OUTER_UUID, V3_TYPE_UUID

DEFAULT_MAX_PAYLOAD_BYTES = 1024 * 1024


class StreamDecodeError(ValueError):
    """Fixed failure reason and absolute stream cursor; no raw field values."""

    def __init__(self, reason: str, cursor: int, *, body_code: int | None = None) -> None:
        self.reason = reason
        self.cursor = cursor
        self.body_code = body_code
        super().__init__(f"registration stream decode failed: {reason} at offset {cursor}")


@dataclass(frozen=True)
class DecodedRegistrationRequest:
    """Decoder-owned immutable values, with opaque wrapper bytes kept distinct."""

    body: RegistrationRequestBody
    type_index: int
    field_04: bytes | None
    field_0c: bytes | None


def decode_registration_request_stream(
    data: bytes | bytearray | memoryview, *, expected_type_index: int,
    max_payload_bytes: int = DEFAULT_MAX_PAYLOAD_BYTES,
) -> tuple[DecodedRegistrationRequest, int]:
    """Decode one selected physical stream; return owned values and its extent.

    The caller must bind the selector explicitly; zero requires the fixed V3
    UUID fallback. The cap covers this record's payload, not any outer suffix.
    Check size before snapshot/CRC, then parse the exact checksummed snapshot.
    Require canonical selector bytes and complete selected BODY consumption.
    """
    _check_uint("expected_type_index", expected_type_index, 32)
    _check_uint("max_payload_bytes", max_payload_bytes, 32)
    if max_payload_bytes == 0:
        raise ValueError("max_payload_bytes must be positive")
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("data must be a contiguous byte buffer")
    try:
        view = memoryview(data).cast("B")
    except (TypeError, ValueError):
        raise TypeError("data must be a contiguous byte buffer") from None
    if len(view) < 8:
        raise StreamDecodeError("header-truncated", 0)
    header = bytes(view[:8])
    checksum = int.from_bytes(header[:4], "big")
    length = int.from_bytes(header[4:], "big")
    if length > max_payload_bytes:
        raise StreamDecodeError("payload-limit", 8)
    end = 8 + length
    if end > len(view):
        raise StreamDecodeError("payload-truncated", 8)
    payload = bytes(view[8:end])
    if zlib.crc32(payload) != checksum:
        raise StreamDecodeError("checksum", 0)

    reader = _Reader(payload)
    stage = "outer-uuid"
    try:
        if reader.fixed(16, 1) != NIL_OUTER_UUID:
            raise StreamDecodeError(stage, 8)
        stage = "wrapper-flags"
        flags = reader.byte(1)
        if flags not in (0, 1, 3):
            raise StreamDecodeError(stage, 8 + reader.cursor - 1)
        stage = "wrapper-fields"
        field_04 = reader.fixed(8, 1) if flags & 1 else None
        field_0c = reader.fixed(8, 1) if flags & 2 else None
        stage = "body-presence"
        if reader.byte(1) != 1:
            raise StreamDecodeError(stage, 8 + reader.cursor - 1)
        stage = "type-selector"
        start = reader.cursor
        type_index = reader.count()
        if payload[start:reader.cursor] != _encode_count(type_index):
            raise StreamDecodeError("selector-noncanonical", 8 + start)
        if type_index != expected_type_index:
            raise StreamDecodeError("type-mismatch", 8 + start)
        stage = "type-uuid"
        if type_index == 0 and reader.fixed(16, 1) != V3_TYPE_UUID:
            raise StreamDecodeError(stage, 8 + reader.cursor - 16)
    except BodyDecodeError as failure:
        raise StreamDecodeError(stage, 8 + failure.cursor) from None

    start = reader.cursor
    try:
        body, consumed = decode_body(memoryview(payload)[start:])
    except BodyDecodeError as failure:
        raise StreamDecodeError("body", 8 + start + failure.cursor,
                                body_code=failure.code) from None
    if start + consumed != len(payload):
        raise StreamDecodeError("body-extent", 8 + start + consumed)
    return DecodedRegistrationRequest(body, type_index, field_04, field_0c), end
