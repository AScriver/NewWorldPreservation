"""Empty spawn-point notification from the pinned owned client's current codec."""

TYPE_ID = 0x651
TYPE_HEADER = b"\x00\x01\x91\x19"


def encode_notification() -> bytes:
    """The current factory serializer has no body fields; coordinates are absent.

    Live dispatch, useful spawn state and playable-world readiness remain unproven.
    """
    return TYPE_HEADER
