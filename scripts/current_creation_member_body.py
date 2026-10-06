"""Pure BODY codec for the pinned current creation member's fresh factory shape.

This models one group with ordered AssetId and GdeRef fields. It does not
select a registry class, frame a replication record, choose dirty fields for
a peer, or establish that the client accepts a creation message. Unknown mask
bits and continuations are rejected by this offline codec even where the
native reader tolerates them.
"""

from __future__ import annotations

from dataclasses import dataclass


MEMBER_UUID = bytes.fromhex("203dc8c70c60454ba46f566114314b84")


def _raw16(name: str, value: bytes) -> None:
    if type(value) is not bytes or len(value) != 16:
        raise ValueError(f"{name} must be exactly 16 immutable bytes")


@dataclass(frozen=True)
class AssetIdField:
    raw16: bytes
    field_20: int

    def __post_init__(self) -> None:
        _raw16("AssetId raw16", self.raw16)
        if type(self.field_20) is not int or not 0 <= self.field_20 <= 0xFFFFFFFF:
            raise ValueError("AssetId field_20 must be uint32")


@dataclass(frozen=True)
class CreationMemberBody:
    asset_id: AssetIdField | None = None
    gde_ref: bytes | None = None

    def __post_init__(self) -> None:
        if self.asset_id is not None and type(self.asset_id) is not AssetIdField:
            raise ValueError("asset_id must be AssetIdField or absent")
        if self.gde_ref is not None:
            _raw16("GdeRef", self.gde_ref)


class DecodeError(ValueError):
    """Offline BODY rejection with a cursor relative to the supplied view."""

    def __init__(self, field: str, cursor: int, reason: str) -> None:
        self.field = field
        self.cursor = cursor
        self.reason = reason
        super().__init__(f"{field} at BODY offset {cursor}: {reason}")


def encode_body(record: CreationMemberBody) -> bytes:
    """Encode explicit caller-selected presence, not native peer dirty state."""
    if type(record) is not CreationMemberBody:
        raise TypeError("record must be CreationMemberBody")
    if record.asset_id is None and record.gde_ref is None:
        return b"\x00"
    mask = int(record.asset_id is not None) | (int(record.gde_ref is not None) << 1)
    output = bytearray((1, mask))
    if record.asset_id is not None:
        output.extend(record.asset_id.raw16)
        output.extend(record.asset_id.field_20.to_bytes(4, "big"))
    if record.gde_ref is not None:
        output.extend(record.gde_ref)
    return bytes(output)


def decode_body(data: bytes | bytearray | memoryview, *, member_uuid: bytes) -> tuple[CreationMemberBody, int]:
    """Decode one BODY prefix; return its value and byte count within *data*.

    The required class UUID is an external selector guard, not bytes consumed
    from this BODY. Suffix bytes belong to the caller and remain untouched.
    """
    _raw16("member_uuid", member_uuid)
    if member_uuid != MEMBER_UUID:
        raise ValueError("member_uuid does not select the current creation member")
    try:
        view = memoryview(data).cast("B")
    except (TypeError, ValueError) as exc:
        raise TypeError("data must be a contiguous bytes-like buffer") from exc

    def take(count: int, field: str, cursor: int) -> bytes:
        if len(view) - cursor < count:
            raise DecodeError(field, cursor, f"needs {count} bytes")
        return bytes(view[cursor:cursor + count])

    outer = take(1, "group mask", 0)[0]
    if outer & ~1:
        raise DecodeError("group mask", 1, "unsupported group bits")
    if not outer:
        return CreationMemberBody(), 1

    inner = take(1, "field mask", 1)[0]
    if inner & ~3:
        raise DecodeError("field mask", 2, "unsupported field bits or continuation")
    cursor = 2
    asset_id = None
    gde_ref = None
    if inner & 1:
        raw = take(16, "AssetId raw16", cursor)
        cursor += 16
        scalar = int.from_bytes(take(4, "AssetId field_20", cursor), "big")
        cursor += 4
        asset_id = AssetIdField(raw, scalar)
    if inner & 2:
        gde_ref = take(16, "GdeRef raw16", cursor)
        cursor += 16
    return CreationMemberBody(asset_id, gde_ref), cursor
