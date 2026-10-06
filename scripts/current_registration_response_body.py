"""Pure, current-image registration response BODY codec (no message framing).

The native writer substitutes an empty string for inputs above 0x2ffff bytes.
This encoder instead rejects them, so caller data cannot be silently discarded.
The decoder checks a declared payload's full extent before copying it; this is
stronger bounds handling than the observed native copy-before-extent-check path.
"""

from __future__ import annotations

from dataclasses import dataclass


MAX_STRING_BYTES = 0x2FFFF


class DecodeError(ValueError):
    """A native helper failure code and the body cursor consumed at failure."""

    def __init__(self, code: int, cursor: int) -> None:
        self.code = code
        self.cursor = cursor
        super().__init__(f"body decode failed: code {code} at offset {cursor}")


@dataclass(frozen=True)
class RegistrationResponseBody:
    field_08: int
    field_10: int
    field_18: bytes
    field_38: bytes
    flags: tuple[bool, bool, bool, bool]

    def __post_init__(self) -> None:
        for name, bits in (("field_08", 32), ("field_10", 64)):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value < 1 << bits:
                raise ValueError(f"{name} must be a {bits}-bit unsigned bit pattern")
        for name in ("field_18", "field_38"):
            value = getattr(self, name)
            if type(value) is not bytes or len(value) > MAX_STRING_BYTES:
                raise ValueError(f"{name} must be bytes of at most {MAX_STRING_BYTES} bytes")
        if (type(self.flags) is not tuple or len(self.flags) != 4
                or any(type(flag) is not bool for flag in self.flags)):
            raise ValueError("flags must be a tuple of four booleans")


def _encode_count(value: int) -> bytes:
    for width, payload_bits, limit, prefix in (
        (1, 7, 1 << 7, 0),
        (2, 6, 1 << 14, 0x80),
        (3, 5, 1 << 21, 0xC0),
        (4, 4, 1 << 28, 0xE0),
        (5, 3, 1 << 32, 0xF0),
    ):
        if value < limit:
            result = bytearray((prefix | (value & ((1 << payload_bits) - 1)),))
            value >>= payload_bits
            for _ in range(width - 1):
                result.append(value & 0xFF)
                value >>= 8
            return bytes(result)
    raise ValueError("compact count exceeds uint32")


def encode_body(record: RegistrationResponseBody) -> bytes:
    """Encode canonical body bytes; no type, record prefix, or Carrier wrapper."""
    if type(record) is not RegistrationResponseBody:
        raise TypeError("record must be RegistrationResponseBody")
    return b"".join((
        record.field_08.to_bytes(4, "big"),
        record.field_10.to_bytes(8, "big"),
        _encode_count(len(record.field_18)), record.field_18,
        _encode_count(len(record.field_38)), record.field_38,
        bytes(record.flags),
    ))


def decode_body(data: bytes | bytearray | memoryview) -> tuple[RegistrationResponseBody, int]:
    """Decode one body and return (record, consumed); trailing bytes are untouched."""
    view = memoryview(data).cast("B")
    cursor = 0

    def fixed(size: int, code: int) -> bytes:
        nonlocal cursor
        if size > len(view) - cursor:
            raise DecodeError(code, cursor)
        value = bytes(view[cursor:cursor + size])
        cursor += size
        return value

    def count() -> int:
        nonlocal cursor
        if cursor >= len(view):
            raise DecodeError(1, cursor)
        first = view[cursor]
        cursor += 1
        if first < 0x80:
            return first
        if first < 0xC0:
            width, bits = 2, 6
        elif first < 0xE0:
            width, bits = 3, 5
        elif first < 0xF0:
            width, bits = 4, 4
        else:
            width, bits = 5, 3
        tail = width - 1
        if tail > len(view) - cursor:
            raise DecodeError(1, cursor)
        value = first & ((1 << bits) - 1)
        for index in range(tail):
            value |= view[cursor + index] << (bits + 8 * index)
        cursor += tail
        return value & 0xFFFFFFFF

    def counted_bytes() -> bytes:
        length = count()
        if length > MAX_STRING_BYTES:
            raise DecodeError(1, cursor)
        return fixed(length, 1)

    field_08 = int.from_bytes(fixed(4, 2), "big")
    field_10 = int.from_bytes(fixed(8, 2), "big")
    field_18 = counted_bytes()
    field_38 = counted_bytes()
    flags = []
    for _ in range(4):
        value = fixed(1, 3)[0]
        if value >= 2:
            raise DecodeError(4, cursor)
        flags.append(bool(value))
    return RegistrationResponseBody(field_08, field_10, field_18, field_38,
                                    tuple(flags)), cursor
