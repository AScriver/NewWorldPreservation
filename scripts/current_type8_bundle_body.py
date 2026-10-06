"""Original current type8 BODY codec and bounded creation-payload composition.

The paired native reader/writer support this field grammar. Values model fresh
immutable storage, not native partial mutation, sticky errors or allocator state.
No type selector, outer record writer, Carrier framing or gameplay is supplied.
"""

from __future__ import annotations

from dataclasses import dataclass

from current_creation_replication_record import (
    CreationReplicationRecord, DecodeError as RecordDecodeError,
    _table as _check_table, decode_record, encode_record,
)
from current_registration_request_body import _check_bool, _check_uint, _encode_count

MAX_PAYLOAD_BYTES = 256000
MAX_STRUCTURE_ITEMS = 100
_ABSENT_SEQUENCE = 0xFFFFFFFFFFFFFFFF


@dataclass(frozen=True)
class BundleOptionalStructure:
    """Raw helper-relative +d0 scalar and u16 entries; meanings are unproved."""

    field_d0: int = 0
    items: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        _check_uint("field_d0", self.field_d0, 32)
        if type(self.items) is not tuple or len(self.items) > MAX_STRUCTURE_ITEMS:
            raise ValueError("items must be an immutable tuple of at most 100 u16 values")
        for value in self.items:
            _check_uint("structure item", value, 16)


@dataclass(frozen=True)
class BundleBody:
    sequence: int | None = None
    field_30: int = 0
    field_31: int = 0
    field_08: bool = False
    optional_structure: BundleOptionalStructure | None = None
    payload: bytes = b""

    def __post_init__(self) -> None:
        if self.sequence is not None:
            _check_uint("sequence", self.sequence, 64)
            if self.sequence == _ABSENT_SEQUENCE:
                raise ValueError("use None for the native all-ones absent sequence sentinel")
        _check_uint("field_30", self.field_30, 8)
        _check_uint("field_31", self.field_31, 8)
        _check_bool("field_08", self.field_08)
        if self.optional_structure is not None and type(self.optional_structure) is not BundleOptionalStructure:
            raise ValueError("optional_structure must be BundleOptionalStructure or None")
        if type(self.payload) is not bytes or len(self.payload) > MAX_PAYLOAD_BYTES:
            raise ValueError("payload must be immutable bytes of at most 256000 bytes")


class DecodeError(ValueError):
    """Local diagnostic offset; no native error-code or mutation equivalence."""

    def __init__(self, field: str, cursor: int, reason: str, *, scope: str = "BODY") -> None:
        self.field, self.cursor, self.reason, self.scope = field, cursor, reason, scope
        super().__init__(f"{field} at {scope} offset {cursor}: {reason}")


def _encode_sequence(value: int) -> bytes:
    for width in range(1, 9):
        bits = 8 - width
        if value < 1 << (bits + 8 * (width - 1)):
            prefix = ((0xFF << (9 - width)) & 0xFF) if width > 1 else 0
            return bytes([prefix | (value & ((1 << bits) - 1))]) + (value >> bits).to_bytes(width - 1, "little")
    return b"\xff" + value.to_bytes(8, "little")


def encode_body(body: BundleBody) -> bytes:
    """Encode the established BODY only; reject native lossy/capacity cases."""
    if type(body) is not BundleBody:
        raise TypeError("body must be BundleBody")
    output = bytearray([body.sequence is not None])
    if body.sequence is not None:
        output.extend(_encode_sequence(body.sequence))
    output.extend((body.field_30, body.field_31, body.field_08, body.optional_structure is not None))
    structure = body.optional_structure
    if structure is not None:
        output.extend(_encode_count(structure.field_d0))
        output.extend(_encode_count(len(structure.items)))
        for value in structure.items:
            output.extend(value.to_bytes(2, "big"))
    output.extend(_encode_count(len(body.payload)))
    output.extend(body.payload)
    return bytes(output)


class _Reader:
    def __init__(self, data: bytes | bytearray | memoryview) -> None:
        try:
            self.view = memoryview(data).cast("B")
        except (TypeError, ValueError) as exc:
            raise TypeError("data must be a contiguous bytes-like buffer") from exc
        self.cursor = 0

    def take(self, size: int, field: str) -> bytes:
        if size > len(self.view) - self.cursor:
            raise DecodeError(field, self.cursor, f"needs {size} bytes")
        value = bytes(self.view[self.cursor:self.cursor + size])
        self.cursor += size
        return value

    def boolean(self, field: str) -> bool:
        start = self.cursor
        value = self.take(1, field)[0]
        if value > 1:
            raise DecodeError(field, start, "requires Boolean byte 0 or 1")
        return bool(value)

    def compact(self, field: str, bits: int = 32) -> int:
        first = self.take(1, field)[0]
        width, flag = 1, 0x80
        while width < (5 if bits == 32 else 9) and first & flag:
            width += 1
            flag >>= 1
        payload_bits = max(8 - width, 0)
        tail = self.take(width - 1, field)
        value = (first & ((1 << payload_bits) - 1)) | (int.from_bytes(tail, "little") << payload_bits)
        return value & ((1 << bits) - 1)


def decode_body(data: bytes | bytearray | memoryview) -> tuple[BundleBody, int]:
    """Decode one prefix, copying only its declared payload after safe bounds.

    Compact aliases survive; a present all-ones sequence canonicalizes to None.
    >100 items and >256000 payload bytes reject before copying. These guards do
    not emulate the native writer's zero substitution or decoder's sticky errors.
    Trailing enclosing bytes are left outside the returned payload and consumed
    count. Failure returns no partial value and does not modify the input.
    """
    reader = _Reader(data)
    sequence = reader.compact("sequence", 64) if reader.boolean("sequence presence") else None
    if sequence == _ABSENT_SEQUENCE:
        sequence = None
    field_30 = reader.take(1, "field_30")[0]
    field_31 = reader.take(1, "field_31")[0]
    field_08 = reader.boolean("field_08")
    structure = None
    if reader.boolean("structure presence"):
        scalar = reader.compact("structure field_d0")
        count = reader.compact("structure item count")
        if count > MAX_STRUCTURE_ITEMS:
            raise DecodeError("structure item count", reader.cursor, "exceeds 100")
        raw = reader.take(count * 2, "structure items")
        items = tuple(int.from_bytes(raw[index:index + 2], "big") for index in range(0, len(raw), 2))
        structure = BundleOptionalStructure(scalar, items)
    size = reader.compact("payload length")
    if size > MAX_PAYLOAD_BYTES:
        raise DecodeError("payload length", reader.cursor, "exceeds fresh factory cap 256000")
    payload = reader.take(size, "payload")
    return BundleBody(sequence, field_30, field_31, field_08, structure, payload), reader.cursor


def encode_creation_payload(records: tuple[CreationReplicationRecord, ...], *, class_table: tuple[bytes, ...]) -> bytes:
    """Concatenate explicit reader-inverse records; native outer writer unjoined."""
    _check_table(class_table)
    if type(records) is not tuple or any(type(record) is not CreationReplicationRecord for record in records):
        raise ValueError("records must be an immutable tuple of CreationReplicationRecords")
    output = bytearray()
    for record in records:
        raw = encode_record(record, class_table=class_table)
        if len(raw) > MAX_PAYLOAD_BYTES - len(output):
            raise ValueError("creation payload exceeds fresh factory cap 256000")
        output.extend(raw)
    return bytes(output)


def decode_creation_payload(data: bytes | bytearray | memoryview, *, class_table: tuple[bytes, ...]
                            ) -> tuple[CreationReplicationRecord, ...]:
    """Parse only the supplied payload extent; fail the whole result on errors.

    No partial application, unknown-class skip or native stream drain is modeled.
    The caller supplies the explicit immutable UUID table. Diagnostic offsets
    refer to the payload, independently of any enclosing BODY prefix.
    """
    _check_table(class_table)
    reader = _Reader(data)
    if len(reader.view) > MAX_PAYLOAD_BYTES:
        raise DecodeError("payload length", 0, "exceeds fresh factory cap 256000", scope="payload")
    records = []
    while reader.cursor < len(reader.view):
        try:
            record, consumed = decode_record(reader.view[reader.cursor:], class_table=class_table)
        except RecordDecodeError as exc:
            raise DecodeError(exc.field, reader.cursor + exc.cursor, exc.reason, scope="payload") from exc
        records.append(record)
        reader.cursor += consumed
    return tuple(records)
