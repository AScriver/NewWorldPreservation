"""Synthetic private archive safety/integrity tests; never touch the installed game."""
import json
from pathlib import Path

import pytest

from scripts import preserve_owned_client as p


def setup_inputs(tmp_path):
    root = tmp_path / "install"
    (root / "Bin64").mkdir(parents=True)
    (root / "Bin64" / "NewWorld.exe").write_bytes(b"synthetic executable")
    (root / "bootstrap.cfg").write_bytes(b"synthetic static input")
    manifest = tmp_path / "appmanifest.acf"
    manifest.write_text('"appid" "1063730"\n"buildid" "123"\n"LastOwner" "must-not-copy"')
    return root, manifest


def test_full_copy_and_verification_excludes_sensitive_inputs(tmp_path, monkeypatch):
    root, manifest = setup_inputs(tmp_path)
    (root / "Game.log").write_text("Bearer forbidden")
    (root / "credentials.json").write_text("forbidden")
    (root / "logs").mkdir()
    (root / "logs" / "unknown.txt").write_text("forbidden")
    destination = tmp_path / "archive"
    monkeypatch.setattr(p.shutil, "disk_usage", lambda _: type("Space", (), {"free": 10**12})())
    value = p.archive(root, destination, manifest, "1.2.3.4")
    assert value["verified"] and value["source_and_destination_fully_rehashed"]
    assert value["files"] == 2
    assert not value["archive_restoration_or_offline_launch_tested"]
    assert not (destination / "owned-install" / "Game.log").exists()
    assert not (destination / "owned-install" / "credentials.json").exists()
    assert "must-not-copy" not in (destination / "inventory.json").read_text()
    assert value["ended_monotonic_ns"] >= value["started_monotonic_ns"]
    assert json.loads((destination / "inventory.json").read_text())["inventory_sha256"] == value["inventory_sha256"]


@pytest.mark.parametrize("where", ["same", "inside", "parent"])
def test_rejects_source_destination_overlap(tmp_path, where):
    root, manifest = setup_inputs(tmp_path)
    destination = {"same": root, "inside": root / "copy", "parent": root.parent}[where]
    with pytest.raises(p.PreservationError, match="overlapping_archive"):
        p.archive(root, destination, manifest, "1.2.3.4")


def test_rejects_source_change_during_copy(tmp_path, monkeypatch):
    root, manifest = setup_inputs(tmp_path)
    original = p.copy_one
    def changed(source, destination, expected):
        digest = original(source, destination, expected)
        source.write_bytes(b"changed after copy")
        return digest
    monkeypatch.setattr(p, "copy_one", changed)
    with pytest.raises(p.PreservationError, match="source_changed"):
        p.archive(root, tmp_path / "archive", manifest, "1.2.3.4")
    assert not (tmp_path / "archive" / "inventory.json").exists()


def test_rejects_copy_corruption(tmp_path, monkeypatch):
    root, manifest = setup_inputs(tmp_path)
    original = p.copy_one
    def corrupted(source, destination, expected):
        digest = original(source, destination, expected)
        destination.write_bytes(b"corrupted")
        return digest
    monkeypatch.setattr(p, "copy_one", corrupted)
    with pytest.raises(p.PreservationError, match="archive_hash_mismatch"):
        p.archive(root, tmp_path / "archive", manifest, "1.2.3.4")


def test_rejects_symlink(tmp_path):
    root, _ = setup_inputs(tmp_path)
    try:
        (root / "outside").symlink_to(tmp_path, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(p.PreservationError, match="reparse"):
        p.inventory(root)


def test_rejects_identity_ambiguity_and_wrong_app(tmp_path):
    manifest = tmp_path / "manifest"
    manifest.write_text('"appid" "1" "buildid" "2"')
    with pytest.raises(p.PreservationError, match="wrong_steam_app"):
        p.steam_identity(manifest)
    manifest.write_text('"appid" "1063730" "buildid" "2" "buildid" "3"')
    with pytest.raises(p.PreservationError, match="steam_identity_ambiguous"):
        p.steam_identity(manifest)


def test_rejects_existing_archive_without_overwrite(tmp_path):
    root, manifest = setup_inputs(tmp_path)
    archive = tmp_path / "archive"
    archive.mkdir()
    marker = archive / "untouched"
    marker.write_text("retain")
    with pytest.raises(p.PreservationError, match="archive_exists"):
        p.archive(root, archive, manifest, "1.2.3.4")
    assert marker.read_text() == "retain"


def test_inventory_file_bound(tmp_path, monkeypatch):
    root, _ = setup_inputs(tmp_path)
    monkeypatch.setattr(p, "MAX_FILES", 1)
    with pytest.raises(p.PreservationError, match="inventory_bound"):
        p.inventory(root)


def test_sensitive_content_in_normal_configuration_is_rejected(tmp_path):
    root, manifest = setup_inputs(tmp_path)
    (root / "bootstrap.cfg").write_text("account_id=FAKE_ACCOUNT_444\ncredential=FAKE_CREDENTIAL_555")
    with pytest.raises(p.PreservationError, match="loose_text_sensitive_signal"):
        p.archive(root, tmp_path / "archive", manifest, "1.2.3.4")
    assert not (tmp_path / "archive" / "owned-install" / "bootstrap.cfg").exists()
