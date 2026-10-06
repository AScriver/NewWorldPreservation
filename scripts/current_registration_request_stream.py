"""Pure selected V3 sender stream encoding from the current pinned source.

This models an empty ordinary stream and a fresh wrapper's proved flags0/1/3.
Optional fields are opaque caller-supplied bytes, not reconstructed runtime IDs.
The actual type index is required; map19 is not a default or observed index.
No native receive inverse or Carrier/datagram emission is provided.
"""

from __future__ import annotations

import zlib

from current_registration_request_body import (
    RegistrationRequestBody, _check_uint, _encode_count, encode_body,
)


V3_TYPE_UUID = bytes.fromhex("0b826b3389f549e0b8cbfe4433427778")
NIL_OUTER_UUID = bytes(16)
MAX_PAYLOAD_BYTES = 0xFFFFFFFF


def encode_registration_request_stream(
    record: RegistrationRequestBody, *, type_index: int,
    field_04: bytes | None = None, field_0c: bytes | None = None,
) -> bytes:
    """Encode nil outer UUID, fresh wrapper prefix, type selector and V3 BODY.

    `type_index` is explicit uint32: zero adds the fixed V3 UUID fallback,
    nonzero emits only that compact index. Optional raw8 fields select bits0/1;
    second-only is outside the stable fresh-wrapper domain and is rejected.
    CRC/count cover the complete payload; output never narrows a huge length.
    """
    if type(record) is not RegistrationRequestBody:
        raise TypeError("record must be RegistrationRequestBody")
    _check_uint("type_index", type_index, 32)
    for name, value in (("field_04", field_04), ("field_0c", field_0c)):
        if value is not None and (type(value) is not bytes or len(value) != 8):
            raise ValueError(f"{name} must be exactly eight bytes or None")
    if field_0c is not None and field_04 is None:
        raise ValueError("field_0c requires field_04 in the fresh-wrapper domain")

    flags = int(field_04 is not None) | (2 if field_0c is not None else 0)
    prefix = bytearray((flags,))
    for value in (field_04, field_0c):
        if value is not None:
            prefix.extend(value)
    prefix.append(1)  # Selected nonnull V3 message body.
    prefix.extend(_encode_count(type_index))  # Same current uint32 writer as BODY counts.
    if type_index == 0:
        prefix.extend(V3_TYPE_UUID)
    body = encode_body(record)
    size = len(NIL_OUTER_UUID) + len(prefix) + len(body)
    if size > MAX_PAYLOAD_BYTES:
        raise ValueError("complete stream payload exceeds uint32")
    payload = NIL_OUTER_UUID + bytes(prefix) + body
    return zlib.crc32(payload).to_bytes(4, "big") + size.to_bytes(4, "big") + payload
