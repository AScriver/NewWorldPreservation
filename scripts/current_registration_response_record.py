"""Pure typed response record for the proved compact-record callback boundary.

The caller supplies the type binding and opaque wrapper fields. This does not
establish the full incoming Carrier/physical envelope or client acceptance.
The fresh wrapper domain is flags0/1/3; no runtime identity or status is inferred.
"""

from __future__ import annotations

from current_registration_response_body import (
    RegistrationResponseBody, _encode_count, encode_body,
)

RESPONSE_TYPE_UUID = bytes.fromhex("104145a7ff9544f1946821fb41c8ac2b")


def encode_registration_response_record(
    record: RegistrationResponseBody, *, type_index: int,
    field_04: bytes | None = None, field_0c: bytes | None = None,
) -> bytes:
    """Return compact length followed by typed wrapper and existing response BODY.

    Require an explicit true uint32 selector. Zero emits the response UUID
    fallback. Ordered optional eight-byte fields select fresh flag bits0/1;
    second-only is rejected within this deliberately selected wrapper domain.
    No sender CRC/outer descriptor or Carrier header is appended.
    """
    if type(record) is not RegistrationResponseBody:
        raise TypeError("record must be RegistrationResponseBody")
    if type(type_index) is not int or not 0 <= type_index < 1 << 32:
        raise ValueError("type_index must be a 32-bit unsigned bit pattern")
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
    prefix.append(1)
    prefix.extend(_encode_count(type_index))
    if type_index == 0:
        prefix.extend(RESPONSE_TYPE_UUID)
    payload = bytes(prefix) + encode_body(record)
    return _encode_count(len(payload)) + payload
