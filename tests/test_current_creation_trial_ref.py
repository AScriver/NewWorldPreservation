"""Original trial-input controls; no native execution or game observations."""
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import current_creation_trial_ref as trial
from current_creation_member_body import CreationMemberBody, encode_body, decode_body, MEMBER_UUID


def raw(key, high=0):
    return key.to_bytes(8, "little") + high.to_bytes(8, "little")


@pytest.mark.parametrize("key,high", [(0x100000002, 0), (0xFFFFFFFFFFFFFFFE, 1), (0x100000000, 0xFFFFFFFFFFFFFFFF)])
def test_preserved_input_key_endianness_high_zero_and_creation_codec(key, high):
    candidate = raw(key, high)
    assert trial.validate_trial_ref(candidate, occupied_keys=frozenset()) == key
    encoded = encode_body(CreationMemberBody(gde_ref=candidate))
    decoded, cursor = decode_body(encoded, member_uuid=MEMBER_UUID)
    assert encoded == b"\x01\x02" + candidate
    assert decoded.gde_ref == candidate and cursor == 18


@pytest.mark.parametrize("key", [0, 2, 0xFFFFFFFE, 0xFFFFFFFF, 0x100000001, 0x100000003, 0xFFFFFFFFFFFFFFFF])
def test_rejects_small_upper32_and_both_odd_helper_counterexamples(key):
    with pytest.raises(ValueError, match="even with nonzero upper32"):
        trial.validate_trial_ref(raw(key, 0xA5), occupied_keys=frozenset())


def test_same_low_different_high_collides():
    occupied = frozenset({0x100000002})
    for high in (0, 1, 0xFFFFFFFFFFFFFFFF):
        with pytest.raises(ValueError, match="occupied"):
            trial.validate_trial_ref(raw(0x100000002, high), occupied_keys=occupied)


@pytest.mark.parametrize("candidate", [bytes(15), bytes(17), bytearray(16), memoryview(bytes(16)), "0" * 16, None])
def test_rejects_wrong_reference_shape(candidate):
    with pytest.raises(ValueError, match="16 immutable"):
        trial.validate_trial_ref(candidate, occupied_keys=frozenset())


@pytest.mark.parametrize("occupied", [set(), (), frozenset({True}), frozenset({-1}), frozenset({1 << 64}), frozenset({1.5}), None])
def test_rejects_mutable_or_wrong_key_set_before_draw(occupied):
    with patch.object(trial, "token_bytes") as draw:
        for function in (lambda: trial.validate_trial_ref(raw(0x100000002), occupied_keys=occupied),
                         lambda: trial.new_trial_ref(occupied_keys=occupied)):
            with pytest.raises(ValueError, match="uint64 frozenset"):
                function()
        draw.assert_not_called()


def test_draws_reject_wrong_gate_and_collisions_without_rewriting_candidate():
    chosen = raw(0x100000008, 0)
    candidates = [raw(3), raw(2), raw(0x100000002, 42), chosen]
    with patch.object(trial, "token_bytes", side_effect=candidates) as draw:
        result = trial.new_trial_ref(occupied_keys=frozenset({0x100000002}))
    assert result is chosen
    assert draw.call_count == 4 and all(call.args == (16,) for call in draw.call_args_list)


def test_draw_bound_failure_returns_no_assignment():
    with patch.object(trial, "token_bytes", return_value=raw(3)) as draw:
        with pytest.raises(RuntimeError, match="draw bound"):
            trial.new_trial_ref(occupied_keys=frozenset())
    assert draw.call_count == 128


def test_broken_random_provider_fails_without_retrying_or_coercing():
    with patch.object(trial, "token_bytes", return_value=bytearray(16)) as draw:
        with pytest.raises(ValueError, match="immutable"):
            trial.new_trial_ref(occupied_keys=frozenset())
    assert draw.call_count == 1
