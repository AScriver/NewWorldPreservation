"""Independent field and header controls for the fixed current map candidate."""
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import current_world_activation as codec


def test_level_info_current_field_order_and_fresh_counter():
    packet = codec.encode_level_info_candidate()
    assert packet[:2] == b"\x00\x01"
    assert (packet[2] & 0x3f) | (packet[3] << 6) == 1635
    body = packet[4:]
    name_size = body[0]
    assert body[1:1 + name_size].decode("ascii") == "newworld_vitaeeterna"
    offset = 1 + name_size
    assert body[offset] == 0  # Empty second string has a compact count, no tag.
    offset += 1
    assert struct.unpack_from(">ffffQ", body, offset) == (0.0, 0.0, 0.0, 0.0, 0)
    offset += 24
    assert body[offset:offset + 5] == bytes(5)  # Empty vector, bool/context/bool/bool.
    offset += 5
    assert struct.unpack_from(">Q", body, offset)[0] == 1
    assert offset + 8 == len(body) == 59
    assert len(packet) == 63


def test_empty_bundle_small_id_and_default_presence_flags():
    packet = codec.encode_empty_bundle()
    assert packet[:3] == b"\x00\x01\x08"  # Small type ID is one byte.
    absent_sequence, context, second_byte, unreliable, optional, payload_count = packet[3:]
    assert (absent_sequence, context, second_byte, unreliable, optional, payload_count) == (0,) * 6
    assert len(packet) == 9
