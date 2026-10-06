"""Pure current V3 registration request BODY codec, without type or framing.

Fields are named by native object offset because their meanings are unproved.
The encoder rejects oversize values instead of reproducing native zero
substitution. The decoder checks string extent before copying, a stronger safe
bound than the native copy-before-extent path.
"""

from __future__ import annotations

from dataclasses import dataclass


MAX_STRING_BYTES = 0x2FFFF
MAX_COLLECTION_PAIRS = 0x02000000


class DecodeError(ValueError):
    """An ordinary native helper failure code and consumed BODY cursor."""

    def __init__(self, code: int, cursor: int) -> None:
        self.code = code
        self.cursor = cursor
        super().__init__(f"body decode failed: code {code} at offset {cursor}")


def _check_uint(name: str, value: int, bits: int) -> None:
    if type(value) is not int or not 0 <= value < 1 << bits:
        raise ValueError(f"{name} must be a {bits}-bit unsigned bit pattern")


def _check_bytes(name: str, value: bytes, size: int = MAX_STRING_BYTES) -> None:
    if type(value) is not bytes or len(value) > size:
        raise ValueError(f"{name} must be bytes of at most {size} bytes")


def _check_bool(name: str, value: bool) -> None:
    if type(value) is not bool:
        raise ValueError(f"{name} must be a boolean")


_C0_STRINGS = ("field_00", "field_20", "field_40", "field_60", "field_80",
               "field_a8", "field_c8", "field_e8", "field_108", "field_128",
               "field_158", "field_180", "field_1a8", "field_1c8", "field_1e8")
_C0_UINTS = ("field_a0", "field_148", "field_14c", "field_150", "field_178")


@dataclass(frozen=True)
class FieldC0:
    field_00: bytes
    field_20: bytes
    field_40: bytes
    field_60: bytes
    field_80: bytes
    field_a0: int
    field_a8: bytes
    field_c8: bytes
    field_e8: bytes
    field_108: bytes
    field_128: bytes
    field_148: int
    field_14c: int
    field_150: int
    field_158: bytes
    field_178: int
    field_17c: int
    field_180: bytes
    field_1a0: bool | None
    field_1a8: bytes
    field_1c8: bytes
    field_1e8: bytes

    def __post_init__(self) -> None:
        for name in _C0_STRINGS:
            _check_bytes(name, getattr(self, name))
        for name in _C0_UINTS:
            _check_uint(name, getattr(self, name), 32)
        _check_uint("field_17c", self.field_17c, 8)
        if self.field_1a0 is not None:
            _check_bool("field_1a0", self.field_1a0)


_FIELD_2C8_STRINGS = ("field_08", "field_28", "field_48", "field_70",
                      "field_90", "field_b0", "field_d0", "field_f0")


@dataclass(frozen=True)
class Field2C8:
    field_00: int
    field_110: bool
    field_04: int
    field_08: bytes
    field_28: bytes
    field_48: bytes
    field_68: int
    field_70: bytes
    field_90: bytes
    field_b0: bytes
    field_d0: bytes
    field_f0: bytes

    def __post_init__(self) -> None:
        for name in ("field_00", "field_04", "field_68"):
            _check_uint(name, getattr(self, name), 32)
        _check_bool("field_110", self.field_110)
        for name in _FIELD_2C8_STRINGS:
            _check_bytes(name, getattr(self, name))


@dataclass(frozen=True)
class TaggedField:
    field_30: int
    field_00: bytes | None = None
    field_20: bytes | None = None

    def __post_init__(self) -> None:
        _check_uint("field_30", self.field_30, 8)
        if self.field_30 & 1:
            if self.field_00 is not None or type(self.field_20) is not bytes or len(self.field_20) != 16:
                raise ValueError("odd tag requires only a 16-byte field_20")
        elif self.field_20 is not None:
            raise ValueError("even tag requires only field_00")
        else:
            _check_bytes("field_00", self.field_00)


def _parse_lookup_uuid(text: bytes) -> bytes | None:
    if not 32 <= len(text) <= 38:
        return None
    cursor = int(text.startswith(b"{"))
    hyphenated = False
    raw = bytearray()
    for index in range(16):
        if index == 4 and text[cursor:cursor + 1] == b"-":
            hyphenated = True
            cursor += 1
        elif hyphenated and index in (6, 8, 10):
            if text[cursor:cursor + 1] != b"-":
                return None
            cursor += 1
        pair = text[cursor:cursor + 2]
        if len(pair) != 2 or any(byte not in b"0123456789ABCDEFabcdef" for byte in pair):
            return None
        raw.append(int(pair, 16))
        cursor += 2
    # The selected parser does not check a closing brace or full consumption.
    return bytes(raw)


def tagged_from_lookup_text(text: bytes) -> TaggedField:
    """Convert a bounded owned lookup string in the proved ASCII domain.

    Truncate at its first NUL. Invalid parses and mixed lettercase retain that
    prefix as text; valid single-case parses produce the active raw16/tag arm.
    Non-ASCII prefixes and full inputs over MAX_STRING_BYTES are rejected.
    Native inactive storage, locale and allocation behavior are not modeled.
    """
    _check_bytes("lookup text", text)
    prefix = text.split(b"\x00", 1)[0]
    if not prefix.isascii():
        raise ValueError("lookup text before its first NUL must be ASCII")
    raw = _parse_lookup_uuid(prefix)
    lower = any(97 <= byte <= 122 for byte in prefix)
    upper = any(65 <= byte <= 90 for byte in prefix)
    if raw is None or lower and upper:
        return TaggedField(0, field_00=prefix)
    tag = (1 | (2 if prefix.startswith(b"{") else 0)
           | (4 if prefix[8] == 45 or prefix[9] == 45 else 0)
           | (0 if lower else 8))
    return TaggedField(tag, field_20=raw)


@dataclass(frozen=True)
class RegistrationRequestBody:
    field_08: int
    field_10: tuple[tuple[int, bytes], ...]
    field_a0: bytes
    field_c0: FieldC0
    field_2c8: Field2C8
    field_3e0: TaggedField
    field_420: TaggedField
    field_460: bool

    def __post_init__(self) -> None:
        _check_uint("field_08", self.field_08, 32)
        if type(self.field_10) is not tuple or len(self.field_10) > MAX_COLLECTION_PAIRS:
            raise ValueError("field_10 must be a bounded immutable collection")
        seen = set()
        for pair in self.field_10:
            if type(pair) is not tuple or len(pair) != 2:
                raise ValueError("field_10 entries must be key/value tuples")
            key, value = pair
            _check_uint("field_10 key", key, 32)
            _check_bytes("field_10 value", value)
            if key in seen:
                raise ValueError("field_10 keys must be unique")
            seen.add(key)
        _check_bytes("field_a0", self.field_a0)
        for name, kind in (("field_c0", FieldC0), ("field_2c8", Field2C8),
                           ("field_3e0", TaggedField), ("field_420", TaggedField)):
            if type(getattr(self, name)) is not kind:
                raise ValueError(f"{name} must be {kind.__name__}")
        _check_bool("field_460", self.field_460)


def _encode_count(value: int) -> bytes:
    for width, low_bits, limit, prefix in (
        (1, 7, 1 << 7, 0), (2, 6, 1 << 14, 0x80),
        (3, 5, 1 << 21, 0xC0), (4, 4, 1 << 28, 0xE0),
        (5, 3, 1 << 32, 0xF0),
    ):
        if value < limit:
            result = bytearray((prefix | (value & ((1 << low_bits) - 1)),))
            value >>= low_bits
            for _ in range(width - 1):
                result.append(value & 0xFF)
                value >>= 8
            return bytes(result)
    raise ValueError("compact count exceeds uint32")


def _write_string(output: bytearray, value: bytes) -> None:
    output.extend(_encode_count(len(value)))
    output.extend(value)


def _write_uint(output: bytearray, value: int) -> None:
    output.extend(value.to_bytes(4, "big"))


def _write_c0(output: bytearray, value: FieldC0) -> None:
    for name in _C0_STRINGS[:5]:
        _write_string(output, getattr(value, name))
    _write_uint(output, value.field_a0)
    for name in _C0_STRINGS[5:10]:
        _write_string(output, getattr(value, name))
    for name in ("field_148", "field_14c", "field_150"):
        _write_uint(output, getattr(value, name))
    _write_string(output, value.field_158)
    _write_uint(output, value.field_178)
    output.append(value.field_17c)
    _write_string(output, value.field_180)
    output.append(value.field_1a0 is not None)
    if value.field_1a0 is not None:
        output.append(value.field_1a0)
    for name in _C0_STRINGS[12:]:
        _write_string(output, getattr(value, name))


def _write_2c8(output: bytearray, value: Field2C8) -> None:
    _write_uint(output, value.field_00)
    output.append(value.field_110)
    _write_uint(output, value.field_04)
    for name in _FIELD_2C8_STRINGS[:3]:
        _write_string(output, getattr(value, name))
    _write_uint(output, value.field_68)
    for name in _FIELD_2C8_STRINGS[3:]:
        _write_string(output, getattr(value, name))


def _write_tagged(output: bytearray, value: TaggedField) -> None:
    output.append(value.field_30)
    if value.field_30 & 1:
        output.extend(value.field_20)
    else:
        _write_string(output, value.field_00)


def encode_body(record: RegistrationRequestBody) -> bytes:
    """Encode the canonical selected BODY without a type or Carrier wrapper."""
    if type(record) is not RegistrationRequestBody:
        raise TypeError("record must be RegistrationRequestBody")
    output = bytearray()
    _write_uint(output, record.field_08)
    output.extend(_encode_count(len(record.field_10)))
    for key, value in record.field_10:
        _write_uint(output, key)
        _write_string(output, value)
    _write_string(output, record.field_a0)
    _write_c0(output, record.field_c0)
    _write_2c8(output, record.field_2c8)
    _write_tagged(output, record.field_3e0)
    _write_tagged(output, record.field_420)
    output.append(record.field_460)
    return bytes(output)


class _Reader:
    def __init__(self, data: bytes | bytearray | memoryview) -> None:
        self.view = memoryview(data).cast("B")
        self.cursor = 0

    def fixed(self, size: int, code: int) -> bytes:
        if size > len(self.view) - self.cursor:
            raise DecodeError(code, self.cursor)
        value = bytes(self.view[self.cursor:self.cursor + size])
        self.cursor += size
        return value

    def uint(self) -> int:
        return int.from_bytes(self.fixed(4, 2), "big")

    def byte(self, code: int) -> int:
        return self.fixed(1, code)[0]

    def boolean(self) -> bool:
        value = self.byte(3)
        if value > 1:
            raise DecodeError(4, self.cursor)
        return bool(value)

    def count(self) -> int:
        first = self.byte(1)
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
        if tail > len(self.view) - self.cursor:
            raise DecodeError(1, self.cursor)
        value = first & ((1 << bits) - 1)
        for index in range(tail):
            value |= self.view[self.cursor + index] << (bits + 8 * index)
        self.cursor += tail
        return value & 0xFFFFFFFF

    def string(self, *, element: bool = False) -> bytes:
        length = self.count()
        if length > MAX_STRING_BYTES:
            raise DecodeError(4 if element else 1, self.cursor)
        available = len(self.view) - self.cursor
        if length > available:
            if element:
                self.cursor += available
                raise DecodeError(2, self.cursor)
            raise DecodeError(1, self.cursor)
        return self.fixed(length, 1)


def _read_c0(reader: _Reader) -> FieldC0:
    values = {}
    for name in _C0_STRINGS[:5]:
        values[name] = reader.string()
    values["field_a0"] = reader.uint()
    for name in _C0_STRINGS[5:10]:
        values[name] = reader.string()
    for name in ("field_148", "field_14c", "field_150"):
        values[name] = reader.uint()
    values["field_158"] = reader.string()
    values["field_178"] = reader.uint()
    values["field_17c"] = reader.byte(1)
    values["field_180"] = reader.string()
    present = reader.boolean()
    values["field_1a0"] = reader.boolean() if present else None
    for name in _C0_STRINGS[12:]:
        values[name] = reader.string()
    return FieldC0(**values)


def _read_2c8(reader: _Reader) -> Field2C8:
    values = {"field_00": reader.uint(), "field_110": reader.boolean(),
              "field_04": reader.uint()}
    for name in _FIELD_2C8_STRINGS[:3]:
        values[name] = reader.string()
    values["field_68"] = reader.uint()
    for name in _FIELD_2C8_STRINGS[3:]:
        values[name] = reader.string()
    return Field2C8(**values)


def _read_tagged(reader: _Reader) -> TaggedField:
    tag = reader.byte(2)
    if tag & 1:
        return TaggedField(tag, field_20=reader.fixed(16, 1))
    return TaggedField(tag, field_00=reader.string())


def decode_body(data: bytes | bytearray | memoryview) -> tuple[RegistrationRequestBody, int]:
    """Decode one BODY; return its immutable values and consumed byte count."""
    reader = _Reader(data)
    field_08 = reader.uint()
    count = reader.count()
    if count > MAX_COLLECTION_PAIRS:
        raise DecodeError(4, reader.cursor)
    pairs = []
    seen = set()
    for _ in range(count):
        key = reader.uint()
        value = reader.string(element=True)
        if key not in seen:
            pairs.append((key, value))
            seen.add(key)
    field_a0 = reader.string()
    field_c0 = _read_c0(reader)
    field_2c8 = _read_2c8(reader)
    field_3e0 = _read_tagged(reader)
    field_420 = _read_tagged(reader)
    field_460 = reader.boolean()
    return RegistrationRequestBody(field_08, tuple(pairs), field_a0, field_c0,
                                   field_2c8, field_3e0, field_420, field_460), reader.cursor
