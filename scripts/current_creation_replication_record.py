"""Original inverse of the current replication record reader's bounded grammar.

Member key/selector/BODY composition has a paired current writer. The native
outer slot/count writer remains unjoined. This codec selects only the proved
creation and player-identity members, requires an explicit immutable UUID table,
and models no native registry cache, error cleanup, application, bundle or datagram.
"""

from __future__ import annotations

from dataclasses import dataclass

from current_creation_member_body import (
    CreationMemberBody, DecodeError as CreationBodyDecodeError,
    MEMBER_UUID as CREATION_MEMBER_UUID, decode_body as decode_creation_body,
    encode_body as encode_creation_body,
)
from current_player_identity_body import (
    PlayerIdentityBody, DecodeError as IdentityBodyDecodeError,
    MEMBER_UUID as IDENTITY_MEMBER_UUID, decode_body as decode_identity_body,
    encode_body as encode_identity_body,
)
from current_registration_request_body import _check_uint, _encode_count


@dataclass(frozen=True)
class CreationRecordMember:
    key: int
    class_index: int
    body: CreationMemberBody | PlayerIdentityBody

    def __post_init__(self) -> None:
        _check_uint("member key", self.key, 32)
        _check_uint("class_index", self.class_index, 32)
        if type(self.body) not in (CreationMemberBody, PlayerIdentityBody):
            raise ValueError("body must be CreationMemberBody or PlayerIdentityBody")


@dataclass(frozen=True)
class CreationReplicationRecord:
    slot: int
    members: tuple[CreationRecordMember, ...]

    def __post_init__(self) -> None:
        _check_uint("record slot", self.slot, 16)
        if (type(self.members) is not tuple or len(self.members) > 255
                or any(type(member) is not CreationRecordMember for member in self.members)):
            raise ValueError("members must be an immutable tuple of at most 255 CreationRecordMembers")


class DecodeError(ValueError):
    """Offline diagnostic offset, not the native failure cleanup cursor/code."""

    def __init__(self, field: str, cursor: int, reason: str) -> None:
        self.field = field
        self.cursor = cursor
        self.reason = reason
        super().__init__(f"{field} at record offset {cursor}: {reason}")


def _table(value: tuple[bytes, ...]) -> None:
    if (type(value) is not tuple or not value or len(value) > 0x100000000
            or any(type(raw) is not bytes or len(raw) != 16 for raw in value)
            or value[0] != bytes(16)):
        raise ValueError("class_table must be an immutable UUID16 tuple with reserved nil slot 0")


def encode_record(record: CreationReplicationRecord, *, class_table: tuple[bytes, ...]) -> bytes:
    """Encode explicit values using the reader grammar and paired member writer.

    Index zero writes the UUID corresponding to the BODY type; a nonzero index
    must resolve to that UUID in the supplied table. No registration or mapping
    position is selected automatically. Member order and duplicate keys survive.
    """
    if type(record) is not CreationReplicationRecord:
        raise TypeError("record must be CreationReplicationRecord")
    _table(class_table)
    output = bytearray(_encode_count(record.slot))
    output.append(len(record.members))
    for member in record.members:
        index = member.class_index
        if type(member.body) is CreationMemberBody:
            uuid, body_bytes = CREATION_MEMBER_UUID, encode_creation_body(member.body)
        else:
            uuid, body_bytes = IDENTITY_MEMBER_UUID, encode_identity_body(member.body)
        if index and (index >= len(class_table) or class_table[index] != uuid):
            raise ValueError("class_index must resolve to the member BODY class")
        output.extend(_encode_count(member.key))
        output.extend(_encode_count(index))
        if index == 0:
            output.extend(uuid)
        output.extend(body_bytes)
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
        result = bytes(self.view[self.cursor:self.cursor + size])
        self.cursor += size
        return result

    def compact(self, field: str) -> int:
        first = self.take(1, field)[0]
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
        tail = self.take(width - 1, field)
        value = first & ((1 << bits) - 1)
        for ordinal, byte in enumerate(tail):
            value |= byte << (bits + ordinal * 8)
        return value & 0xFFFFFFFF  # Current compact reader aliases and narrowing.


def decode_record(data: bytes | bytearray | memoryview, *, class_table: tuple[bytes, ...]
                  ) -> tuple[CreationReplicationRecord, int]:
    """Decode one prefix; unknown classes cannot be skipped without a schema.

    Native compact aliases and record-slot narrowing are preserved. BODY mask
    policy is deliberately stricter than native. Failures return no partial
    record and neither mutate nor drain input; native member failure drains its
    current stream and the surrounding native record parser returns zero.
    """
    _table(class_table)
    reader = _Reader(data)
    slot = reader.compact("record slot") & 0xFFFF
    count = reader.take(1, "member count")[0]
    members = []
    for ordinal in range(count):
        prefix = f"member {ordinal}"
        key = reader.compact(f"{prefix} key")
        index = reader.compact(f"{prefix} class index")
        if index == 0:
            uuid = reader.take(16, f"{prefix} class UUID")
        elif index >= len(class_table):
            raise DecodeError(f"{prefix} class index", reader.cursor, "outside supplied class table")
        else:
            uuid = class_table[index]
        if uuid not in (CREATION_MEMBER_UUID, IDENTITY_MEMBER_UUID):
            raise DecodeError(f"{prefix} class UUID", reader.cursor, "unsupported member class")
        start = reader.cursor
        try:
            if uuid == CREATION_MEMBER_UUID:
                body, consumed = decode_creation_body(reader.view[start:], member_uuid=uuid)
            else:
                body, consumed = decode_identity_body(reader.view[start:], member_uuid=uuid)
        except (CreationBodyDecodeError, IdentityBodyDecodeError) as exc:
            raise DecodeError(f"{prefix} {exc.field}", start + exc.cursor, exc.reason) from exc
        reader.cursor += consumed
        members.append(CreationRecordMember(key, index, body))
    return CreationReplicationRecord(slot, tuple(members)), reader.cursor
