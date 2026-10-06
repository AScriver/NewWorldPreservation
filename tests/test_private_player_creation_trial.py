"""Synthetic-only pinned preparation controls; no client or protocol send."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import private_player_creation_trial as preparation  # noqa: E402
from private_trial_character import PrivateTrialCharacter, write_trial_character  # noqa: E402


UUIDS = (
    "11000000-0000-4000-8000-000000000001",
    "22000000-0000-4000-8000-000000000002",
    "33000000-0000-4000-8000-000000000003",
    "44000000-0000-4000-8000-000000000004",
)
GDE_REF = bytes.fromhex("0200000001000000aabbccddeeff1122")


@pytest.fixture
def private_area():
    root = ROOT / ".scratch" / "creation254-implementer"
    root.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="pure-", dir=root) as directory:
        yield Path(directory)


def character(name="Preservation"):
    return PrivateTrialCharacter(*UUIDS, name, "2026-10-06T22:00:00Z", GDE_REF)


def mapping(path, *, creation=None, identity=None, nil=None):
    values = ["00000000000000000000000000000000"] * preparation.TYPE_INDEX_COUNT
    values[0] = nil or values[0]
    values[10] = creation or "203dc8c70c60454ba46f566114314b84"
    values[3935] = identity or "bddda784a6e7416ba041449920d90fb6"
    path.write_text(json.dumps({"typeIndex": values}, separators=(",", ":")), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_pinned_shape_and_typed_extent(private_area, monkeypatch):
    path = private_area / "typeindex.json"
    digest = mapping(path)
    monkeypatch.setattr(preparation, "TYPE_INDEX_SHA256", digest)
    table = preparation.read_type_index(path)
    assert (len(table), table[0], table[10], table[3935]) == (
        7052, bytes(16), preparation.CREATION_UUID, preparation.IDENTITY_UUID)
    source = character()
    prepared = preparation.prepare_player_creation(trial_character=source,
        mapping_path=path, occupied_keys=frozenset(), delivery_mode="resource-index")
    assert prepared.trial_character is source
    assert len(prepared.typed_bytes) == 107
    assert prepared.typed_bytes.startswith(b"\x00\x01\x08")
    assert source.character_id.encode() in prepared.typed_bytes
    assert prepared.typed_sha256 == hashlib.sha256(prepared.typed_bytes).hexdigest()
    with pytest.raises(ValueError, match="noncanonical"):
        preparation.PreparedPlayerCreation(source, b"\x00\x01\x08\x00",
            hashlib.sha256(b"\x00\x01\x08\x00").hexdigest())
    with pytest.raises(ValueError, match="noncanonical"):
        preparation.PreparedPlayerCreation(source, prepared.typed_bytes, "0" * 64)
    longest = preparation.prepare_player_creation(trial_character=replace(source, name="A" * 32),
        mapping_path=path, occupied_keys=frozenset(), delivery_mode="resource-index")
    assert len(longest.typed_bytes) == 127
    with pytest.raises(ValueError, match="resource-index"):
        preparation.prepare_player_creation(trial_character=source,
            mapping_path=path, occupied_keys=frozenset(), delivery_mode="assigned-index")
    with pytest.raises(ValueError, match="occupied"):
        preparation.prepare_player_creation(trial_character=source,
            mapping_path=path, occupied_keys=frozenset({0x100000002}),
            delivery_mode="resource-index")


def test_same_bounded_character_bytes_and_digest_feed_preparation(private_area, monkeypatch, capsys):
    type_path = private_area / "typeindex.json"
    monkeypatch.setattr(preparation, "TYPE_INDEX_SHA256", mapping(type_path))
    trial_path = private_area / "character.json"
    write_trial_character(trial_path, character())
    digest = hashlib.sha256(trial_path.read_bytes()).hexdigest()
    prepared = preparation.prepare_from_files(trial_character_path=trial_path,
        trial_character_sha256=digest, mapping_path=type_path,
        occupied_keys=frozenset(), delivery_mode="resource-index")
    assert prepared.trial_character == character()
    assert preparation.main([
        "--trial-character", str(trial_path), "--trial-character-sha256", digest,
        "--type-index", str(type_path), "--delivery-mode", "resource-index",
        "--trial-known-empty-occupancy",
    ]) == 0
    output = capsys.readouterr().out
    assert json.loads(output) == {"typed_bytes": len(prepared.typed_bytes),
                                  "typed_sha256": prepared.typed_sha256}
    assert prepared.trial_character.character_id not in output
    assert prepared.trial_character.gde_ref.hex() not in output
    with pytest.raises(SystemExit) as raised:
        preparation.main([
            "--trial-character", str(trial_path), "--trial-character-sha256", "0" * 64,
            "--type-index", str(type_path), "--delivery-mode", "resource-index",
            "--trial-known-empty-occupancy",
        ])
    assert raised.value.code == 2
    with pytest.raises(ValueError, match="SHA256"):
        preparation.prepare_from_files(trial_character_path=trial_path,
            trial_character_sha256="0" * 64, mapping_path=type_path,
            occupied_keys=frozenset(), delivery_mode="resource-index")


@pytest.mark.parametrize("change", [
    dict(creation="00000000000000000000000000000000"),
    dict(identity="00000000000000000000000000000000"),
    dict(nil="203dc8c70c60454ba46f566114314b84"),
])
def test_selected_slots_and_nil_refuse_mismatch(private_area, monkeypatch, change):
    path = private_area / "typeindex.json"
    monkeypatch.setattr(preparation, "TYPE_INDEX_SHA256", mapping(path, **change))
    with pytest.raises(ValueError, match="selected class|nil"):
        preparation.read_type_index(path)


def test_wrong_digest_path_count_duplicate_and_extent(private_area, monkeypatch):
    path = private_area / "typeindex.json"
    digest = mapping(path)
    with pytest.raises(ValueError, match="SHA256"):
        preparation.read_type_index(path)
    monkeypatch.setattr(preparation, "TYPE_INDEX_SHA256", digest)
    with TemporaryDirectory(prefix="nwp-outside-map-", dir=ROOT.parent) as external:
        outside = Path(external) / "typeindex.json"
        outside.write_bytes(path.read_bytes())
        with pytest.raises(ValueError, match="private"):
            preparation.read_type_index(outside)
    path.write_text('{"typeIndex":[],"typeIndex":[]}', encoding="utf-8")
    monkeypatch.setattr(preparation, "TYPE_INDEX_SHA256", hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError, match="duplicate"):
        preparation.read_type_index(path)
    path.write_bytes(b" " * (preparation.MAX_MAPPING_BYTES + 1))
    with pytest.raises(ValueError, match="extent"):
        preparation.read_type_index(path)


def test_braced_uuid_text_is_not_the_pinned_mapping_shape(private_area, monkeypatch):
    path = private_area / "typeindex.json"
    mapping(path)
    model = json.loads(path.read_text(encoding="utf-8"))
    model["typeIndex"][10] = "{203dc8c7-0c60-454b-a46f-566114314b84}"
    path.write_text(json.dumps(model), encoding="utf-8")
    monkeypatch.setattr(preparation, "TYPE_INDEX_SHA256", hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError, match="shape"):
        preparation.read_type_index(path)
