"""Pure identity-only BODY codec for the pinned UUID-registered member.

Supports group1 fields0/1: CharacterId's flag0 text branch and characterName
bytes. Explicit presence is caller selection, not constructor dirty metadata.
Other groups/fields, UUID sidecars and continuation masks are rejected by this
offline codec. Registry selection, delivery and local designation are separate.
"""
from __future__ import annotations

from dataclasses import dataclass

from current_registration_request_body import (
    MAX_STRING_BYTES, DecodeError as BufferDecodeError, _Reader, _check_bytes, _encode_count,
)


MEMBER_UUID = bytes.fromhex("bddda784a6e7416ba041449920d90fb6")


@dataclass(frozen=True)
class PlayerIdentityBody:
    character_id: bytes | None = None
    character_name: bytes | None = None

    def __post_init__(self) -> None:
        for name in ("character_id", "character_name"):
            value = getattr(self, name)
            if value is not None:
                _check_bytes(name, value)


class DecodeError(ValueError):
    """Offline rejection cursor; does not reproduce native cleanup/error codes."""
    def __init__(self, field: str, cursor: int, reason: str) -> None:
        self.field, self.cursor, self.reason = field, cursor, reason
        super().__init__(f"{field} at BODY offset {cursor}: {reason}")


def encode_body(body: PlayerIdentityBody) -> bytes:
    """Encode only explicit selected identity fields with unchanged text bytes."""
    if type(body) is not PlayerIdentityBody:
        raise TypeError("body must be PlayerIdentityBody")
    mask = int(body.character_id is not None) | (int(body.character_name is not None) << 1)
    if mask == 0:
        return b"\x00"
    output = bytearray((2, mask))
    if body.character_id is not None:
        output.append(0)  # Native stored-string branch, no UUID sidecar.
        output.extend(_encode_count(len(body.character_id)))
        output.extend(body.character_id)
    if body.character_name is not None:
        output.extend(_encode_count(len(body.character_name)))
        output.extend(body.character_name)
    return bytes(output)


def decode_body(data: bytes | bytearray | memoryview, *, member_uuid: bytes
                ) -> tuple[PlayerIdentityBody, int]:
    """Read one strict identity BODY prefix, leaving caller suffix untouched.

    UUID is an external selector guard. Native compact32 aliases/narrowing are
    retained; text length/extent is checked before copying. Oversize values are
    rejected, while native writers can normalize an oversize string to empty.
    """
    if type(member_uuid) is not bytes or member_uuid != MEMBER_UUID:
        raise ValueError("member_uuid must select the current player identity member")
    try:
        reader = _Reader(data)
    except (TypeError, ValueError) as exc:
        raise TypeError("data must be a contiguous bytes-like buffer") from exc
    field = "group mask"
    try:
        group = reader.byte(1)
        if group not in (0, 2):
            raise DecodeError(field, reader.cursor, "unsupported groups")
        if group == 0:
            return PlayerIdentityBody(), reader.cursor
        field = "field mask"
        mask = reader.byte(1)
        if mask & ~3:
            raise DecodeError(field, reader.cursor, "unsupported fields or continuation")
        values = {}
        for bit, name in ((1, "character_id"), (2, "character_name")):
            if mask & bit:
                if bit == 1:
                    field = "character_id flag"
                    if reader.byte(1) != 0:
                        raise DecodeError(field, reader.cursor, "only flag0 stored text is supported")
                field = name + " length"
                length = reader.count()
                if length > MAX_STRING_BYTES:
                    raise DecodeError(field, reader.cursor, "exceeds current string limit")
                field = name + " bytes"
                values[name] = reader.fixed(length, 1)
        return PlayerIdentityBody(**values), reader.cursor
    except BufferDecodeError as exc:
        raise DecodeError(field, exc.cursor, "truncated input") from exc
