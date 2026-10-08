"""Offline, private current registration response preparation; no runtime imports."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from current_registration_response_body import decode_body, encode_body
from current_registration_response_record import encode_registration_response_record


WORKSPACE = Path(__file__).resolve().parents[1]
MAX_REGISTRATION_BYTES = 4096
INVALID = "Invalid private current registration response configuration"


def _selector(value: str) -> int:
    try:
        selected = int(value, 0)
    except ValueError:
        raise argparse.ArgumentTypeError("selector must be a uint32 integer") from None
    if not 0 <= selected < 1 << 32:
        raise argparse.ArgumentTypeError("selector must be a uint32 integer")
    return selected


def prepare_current_registration(options):
    """Return the adapter's existing selection after exact, bounded validation."""
    values = tuple(getattr(options, name, None) for name in (
        "current_request_type_index", "current_response_type_index",
        "current_response_body", "current_response_body_sha256"))
    if all(value is None for value in values):
        return {}
    try:
        request_index, response_index, body_path, digest = values
        if (any(value is None for value in values)
                or any(type(index) is not int or not 0 <= index < 1 << 32
                       for index in (request_index, response_index))
                or type(body_path) is not str or not body_path
                or type(digest) is not str or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest.lower())):
            raise ValueError
        path = Path(body_path).resolve()
        if not any(path.is_relative_to(WORKSPACE / name)
                   for name in ("private", ".scratch")):
            raise ValueError
        with path.open("rb") as stream:
            raw = stream.read(MAX_REGISTRATION_BYTES + 1)
        if not 1 <= len(raw) <= MAX_REGISTRATION_BYTES:
            raise ValueError
        if hashlib.sha256(raw).hexdigest() != digest.lower():
            raise ValueError
        body, consumed = decode_body(raw)
        if consumed != len(raw) or encode_body(body) != raw:
            raise ValueError
        response = encode_registration_response_record(body, type_index=response_index)
        if len(response) > MAX_REGISTRATION_BYTES:
            raise ValueError
    except (OSError, ValueError, TypeError, AttributeError):
        raise ValueError(INVALID) from None
    return {"current_request_type_index": request_index,
            "current_response_type_index": response_index,
            "current_response_body": body}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-request-type-index", required=True, type=_selector)
    parser.add_argument("--current-response-type-index", required=True, type=_selector)
    parser.add_argument("--current-response-body", required=True)
    parser.add_argument("--current-response-body-sha256", required=True)
    options = parser.parse_args(argv)
    try:
        prepared = prepare_current_registration(options)
    except ValueError:
        parser.exit(2, INVALID + "\n")
    body = prepared["current_response_body"]
    encoded = encode_body(body)
    typed = encode_registration_response_record(
        body, type_index=prepared["current_response_type_index"])
    print(json.dumps({
        "status": "prepared-only", "client_acceptance_proven": False,
        "current_request_type_index": prepared["current_request_type_index"],
        "current_response_type_index": prepared["current_response_type_index"],
        "body_bytes": len(encoded), "body_sha256": hashlib.sha256(encoded).hexdigest(),
        "typed_record_bytes": len(typed),
        "typed_record_sha256": hashlib.sha256(typed).hexdigest(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
