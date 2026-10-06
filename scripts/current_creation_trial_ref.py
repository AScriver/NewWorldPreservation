"""Original inert GdeRef input policy for a bounded creation experiment.

These inputs avoid the inspected offline-ID routing predicate and collisions
in the explicitly supplied low64 key set. They do not establish native identity
validity, live map occupancy, resource remapping or successful player creation.
The caller owns assignment/persistence and must reuse the returned raw16.
"""
from __future__ import annotations

from secrets import token_bytes


MAX_DRAWS = 128


def _keys(value: frozenset[int]) -> None:
    if (type(value) is not frozenset
            or any(type(key) is not int or not 0 <= key <= 0xFFFFFFFFFFFFFFFF for key in value)):
        raise ValueError("occupied_keys must be an immutable uint64 frozenset")


def _low_key(raw16: bytes) -> int:
    if type(raw16) is not bytes or len(raw16) != 16:
        raise ValueError("GdeRef must be exactly 16 immutable bytes")
    return int.from_bytes(raw16[:8], "little")


def validate_trial_ref(raw16: bytes, *, occupied_keys: frozenset[int]) -> int:
    """Return low64 if the original trial policy passes; do not alter input.

    Even low64 with nonzero upper32 avoids every inspected mode/helper branch
    of 146165f20. The high half may be zero. Distinct raw16 values with the same
    low64 collide in the shown native maps and in this policy.
    """
    _keys(occupied_keys)
    key = _low_key(raw16)
    if key & 1 or key >> 32 == 0:
        raise ValueError("trial low64 must be even with nonzero upper32")
    if key in occupied_keys:
        raise ValueError("trial low64 is already occupied")
    return key


def new_trial_ref(*, occupied_keys: frozenset[int]) -> bytes:
    """Select one unmodified random raw16 for explicit caller-owned assignment.

    This is an original experiment policy, not a reconstruction of a native
    or community hash generator. Draws stop after MAX_DRAWS. The supplied set
    is the caller's collision boundary; no live client state is inspected.
    """
    _keys(occupied_keys)
    for _ in range(MAX_DRAWS):
        candidate = token_bytes(16)
        key = _low_key(candidate)
        if not key & 1 and key >> 32 and key not in occupied_keys:
            return candidate
    raise RuntimeError("no original trial reference passed within the draw bound")
