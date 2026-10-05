"""Fixed default SelfIdentification candidate for the pinned owned 1.400 client.

The current serializer and default constructor establish this encoding. Its
acceptance and the usefulness of null identities require a private-client trial.
This is not a general actor identity or world-state encoder.
"""

OWNED_IMAGE_SHA256 = "8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e"
OWNED_MAPPING_SHA256 = "f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75"
TYPE_ID = 0x65C
TYPE_HEADER = b"\x00\x01\x9c\x19"
BODY_BYTES = 127


def encode_default() -> bytes:
    """Encode only current constructor defaults, including all outer members.

    Empty tagged string (2B), three null identity records (36B each), default
    settings (15B), then a second empty tagged string (2B). Settings contain a
    zero u32, an empty variable-count vector, two false booleans and two +0 f32s.
    """
    return TYPE_HEADER + bytes(BODY_BYTES)
