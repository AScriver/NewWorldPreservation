"""Validate an original, synthetic channel descriptor for a local bootstrap probe.

The sole advertised hostname is temporarily redirected to loopback by the
caller. This module never fetches or forwards a descriptor.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


MAX_DESCRIPTOR_BYTES = 65536
BOOTSTRAP_HOST = "d2c74t4zimux3r.cloudfront.net"
APP_ID = "STEAM_APP_ID.1063730"
ZERO_UUID = "00000000-0000-0000-0000-000000000000"
REGIONS = {
    "fra-prod": "eu-central-1",
    "gru-prod": "sa-east-1",
    "iad-prod": "us-east-1",
    "pdx-prod": "us-west-2",
    "syd-prod": "ap-southeast-2",
}
TAGS = ("authStack", "loginGateway", "JavelinGatewayServiceV2", "JavelinGatewayService-CF")
DISPLAY_NAME = re.compile(r"[A-Za-z][A-Za-z0-9 ._-]{0,63}\Z")


def _keys(value: object, expected: set[str]) -> None:
    if type(value) is not dict or value.keys() != expected:
        raise ValueError("Unexpected channel descriptor fields")


def _literal(value: object, expected: str) -> None:
    if type(value) is not str or value != expected:
        raise ValueError("Unexpected channel descriptor value")


def _validate(value: object) -> dict:
    _keys(value, {"channelName", "platformMetadata", *REGIONS})
    _literal(value["channelName"], "Retail")
    for region, aws_region in REGIONS.items():
        item = value[region]
        _keys(item, {"displayName", "localizedName", "poolId", "publicApis"})
        for key in ("displayName", "localizedName"):
            if type(item[key]) is not str or not DISPLAY_NAME.fullmatch(item[key]):
                raise ValueError("Invalid local display name")
        _literal(item["poolId"], f"{aws_region}:{ZERO_UUID}")
        apis = item["publicApis"]
        if type(apis) is not list or len(apis) != len(TAGS):
            raise ValueError("Invalid local API list")
        tags = TAGS if region != "iad-prod" else (TAGS[1], TAGS[0], *TAGS[2:])
        for api, tag in zip(apis, tags):
            fields = {"awsRegion", "version", "apiEndpoint", "clientTag"}
            if tag != "JavelinGatewayService-CF":
                fields.add("stage")
            _keys(api, fields)
            _literal(api["awsRegion"], "us-east-1" if tag == "authStack" else aws_region)
            _literal(api["version"], "1.0")
            _literal(api["apiEndpoint"], BOOTSTRAP_HOST)
            _literal(api["clientTag"], tag)
            if "stage" in fields:
                _literal(api["stage"], "prod")
    platform = value["platformMetadata"]
    _keys(platform, {f"ENTITLEMENTS.{APP_ID}", f"OMNI.{APP_ID}"})
    entitlement = platform[f"ENTITLEMENTS.{APP_ID}"]
    _keys(entitlement, {"app"})
    _literal(entitlement["app"], APP_ID)
    omni = platform[f"OMNI.{APP_ID}"]
    _keys(omni, {"omniTokenUrl", "nwTokenUrl", "omniStage", "omniGameAlias"})
    for key, expected in {
        "omniTokenUrl": f"https://{BOOTSTRAP_HOST}",
        "nwTokenUrl": f"https://{BOOTSTRAP_HOST}/",
        "omniStage": "prod", "omniGameAlias": "new-world",
    }.items():
        _literal(omni[key], expected)
    return value


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate channel descriptor field")
        result[key] = value
    return result


def _invalid_constant(_value: str) -> None:
    raise ValueError("Non-JSON numeric constant")


def load_local_descriptor(path: str | Path) -> dict:
    """Read at most 64 KiB and return only a fully validated local descriptor."""
    with Path(path).open("rb") as source:
        data = source.read(MAX_DESCRIPTOR_BYTES + 1)
    if len(data) > MAX_DESCRIPTOR_BYTES:
        raise ValueError("Channel descriptor exceeds 64 KiB")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs,
                           parse_constant=_invalid_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as failure:
        raise ValueError("Invalid channel descriptor JSON") from failure
    return _validate(value)


def encode_local_descriptor(value: dict) -> bytes:
    """Deterministic ASCII JSON for a fully validated synthetic descriptor."""
    _validate(value)
    data = json.dumps(value, ensure_ascii=True, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("ascii")
    if len(data) > MAX_DESCRIPTOR_BYTES:
        raise ValueError("Channel descriptor exceeds 64 KiB")
    return data
