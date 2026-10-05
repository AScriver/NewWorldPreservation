"""Current-image contract controls for the bounded default actor candidate."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import current_self_ident_default as codec


def test_current_mapped_type_and_complete_default_footprint():
    payload = codec.encode_default()
    # The current mapped-ID writer uses six low bits then continuation bytes.
    assert payload[:2] == b"\x00\x01"
    assert payload[2] & 0x80
    assert (payload[2] & 0x3F) | (payload[3] << 6) == 1628
    assert len(payload) == 4 + 2 + 3 * 36 + (4 + 1 + 2 + 8) + 2
    assert payload[4:] == bytes(127)
    # Neither historical trigger-only nor settings-only candidates are complete.
    assert len(payload) not in (4, 25)
