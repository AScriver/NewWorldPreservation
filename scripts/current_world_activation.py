"""Fixed map/context activation candidate for the pinned owned 1.400 client.

This original codec follows the current serializer and constructor defaults.
The installed map name and a fresh deduplication counter are experiment values;
they do not supply a player entity or establish playable world state.
"""

from current_type8_bundle_body import BundleBody, encode_body

MAP_NAME = "newworld_vitaeeterna"
LEVEL_INFO_TYPE_ID = 0x663
LEVEL_INFO_HEADER = b"\x00\x01\xa3\x19"
BUNDLE_TYPE_ID = 0x8
BUNDLE_HEADER = b"\x00\x01\x08"
LEVEL_INFO_BODY_BYTES = 59
BUNDLE_BODY_BYTES = 6
MAP_ASSET_SHA256 = "2a951aae4be9ce83baebee88d6b64875af249641e51de2f38f35541126ee09b9"


def encode_level_info_candidate() -> bytes:
    """Owned map, empty second name, zero defaults, context0 and dedup counter1.

    Both strings and the empty entry vector use compact counts. Four +0 f32s,
    one zero u64, four boolean/context bytes and the final counter use the
    current field order; fixed-width numeric fields use network byte order.
    """
    name = MAP_NAME.encode("ascii")
    body = bytes([len(name)]) + name + b"\x00" + bytes(16 + 8 + 1 + 4)
    body += (1).to_bytes(8, "big")
    return LEVEL_INFO_HEADER + body


def encode_empty_bundle() -> bytes:
    """Absent sequence, context0, false flags, absent structure, empty payload.

    An empty current bundle can trigger pending context activation. It contains
    no entities, historical replay, player state or replica payload.
    """
    return BUNDLE_HEADER + encode_body(BundleBody())
