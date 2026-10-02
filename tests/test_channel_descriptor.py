"""Synthetic local channel descriptors; no official response or client traffic."""
import copy
import importlib.util
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    "channel_descriptor", Path(__file__).parents[1] / "scripts/channel_descriptor.py")
descriptor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(descriptor)

HOST = "d2c74t4zimux3r.cloudfront.net"
APP_ID = "STEAM_APP_ID.1063730"
REGIONS = {
    "fra-prod": "eu-central-1", "gru-prod": "sa-east-1", "iad-prod": "us-east-1",
    "pdx-prod": "us-west-2", "syd-prod": "ap-southeast-2",
}
TAGS = ("authStack", "loginGateway", "JavelinGatewayServiceV2", "JavelinGatewayService-CF")


def sample():
    regions = {}
    for name, aws_region in REGIONS.items():
        tags = list(TAGS)
        if name == "iad-prod":
            tags[:2] = reversed(tags[:2])
        apis = []
        for tag in tags:
            api = {"awsRegion": "us-east-1" if tag == "authStack" else aws_region,
                   "version": "1.0", "apiEndpoint": HOST, "clientTag": tag}
            if tag != "JavelinGatewayService-CF":
                api["stage"] = "prod"
            apis.append(api)
        regions[name] = {"displayName": name.upper(), "localizedName": name.upper(),
                         "poolId": f"{aws_region}:00000000-0000-0000-0000-000000000000",
                         "publicApis": apis}
    return {"channelName": "Retail", **regions,
            "platformMetadata": {
                f"ENTITLEMENTS.{APP_ID}": {"app": APP_ID},
                f"OMNI.{APP_ID}": {"omniTokenUrl": f"https://{HOST}",
                                   "nwTokenUrl": f"https://{HOST}/",
                                   "omniStage": "prod", "omniGameAlias": "new-world"}}}


def test_synthetic_roundtrip_is_deterministic_and_ascii(tmp_path):
    source = sample()
    encoded = descriptor.encode_local_descriptor(source)
    assert encoded == descriptor.encode_local_descriptor(source)
    assert encoded.isascii()
    path = tmp_path / "channel.json"
    path.write_bytes(encoded)
    assert descriptor.load_local_descriptor(path) == source


@pytest.mark.parametrize("change", [
    lambda item: item["fra-prod"]["publicApis"][0].update(apiEndpoint="remote.example"),
    lambda item: item["iad-prod"]["publicApis"][2].update(apiEndpoint="remote.example"),
    lambda item: item["platformMetadata"][f"OMNI.{APP_ID}"].update(omniTokenUrl="https://remote.example"),
    lambda item: item["platformMetadata"][f"OMNI.{APP_ID}"].update(nwTokenUrl=f"https://{HOST}/?x=1"),
    lambda item: item["platformMetadata"][f"OMNI.{APP_ID}"].update(omniTokenUrl=f"https://u@{HOST}"),
    lambda item: item["platformMetadata"][f"OMNI.{APP_ID}"].update(omniTokenUrl=f"https://{HOST}/path"),
    lambda item: item["fra-prod"].update(poolId="eu-central-1:11111111-1111-1111-1111-111111111111"),
    lambda item: item["fra-prod"].update(poolId="us-east-1:00000000-0000-0000-0000-000000000000"),
    lambda item: item["fra-prod"]["publicApis"][0].update(clientTag="other"),
    lambda item: item["iad-prod"]["publicApis"].reverse(),
    lambda item: item["fra-prod"]["publicApis"][3].update(stage="prod"),
    lambda item: item["fra-prod"]["publicApis"][0].pop("stage"),
    lambda item: item["fra-prod"]["publicApis"][0].update(version="2.0"),
    lambda item: item.update(channelName="Other"),
    lambda item: item.update(extra="no"),
    lambda item: item["platformMetadata"][f"ENTITLEMENTS.{APP_ID}"].update(extra="no"),
    lambda item: item["syd-prod"].update(displayName="https://remote.example"),
    lambda item: item["syd-prod"].update(localizedName="é"),
    lambda item: item["syd-prod"].update(publicApis=[]),
    lambda item: item["syd-prod"].update(publicApis=None),
    lambda item: item["syd-prod"].update(displayName=True),
])
def test_unsafe_or_changed_structure_rejected(change):
    value = copy.deepcopy(sample())
    change(value)
    with pytest.raises(ValueError):
        descriptor.encode_local_descriptor(value)


@pytest.mark.parametrize("payload", [
    b'{"channelName":"Retail","channelName":"Other"}',
    b'{"channelName":NaN}', b'{"channelName":Infinity}',
    b'[]', b'not-json', b'\xff', b' ' * (65536 + 1),
], ids=["duplicate", "nan", "infinity", "array", "not-json", "bad-utf8", "oversized"])
def test_untrusted_file_rejected(tmp_path, payload):
    path = tmp_path / "channel.json"
    path.write_bytes(payload)
    with pytest.raises(ValueError):
        descriptor.load_local_descriptor(path)


def test_nested_duplicate_key_rejected(tmp_path):
    payload = descriptor.encode_local_descriptor(sample()).decode("ascii")
    payload = payload.replace('"app":"STEAM_APP_ID.1063730"',
                              '"app":"STEAM_APP_ID.1063730","app":"STEAM_APP_ID.1063730"')
    path = tmp_path / "channel.json"
    path.write_text(payload, encoding="ascii")
    with pytest.raises(ValueError):
        descriptor.load_local_descriptor(path)
