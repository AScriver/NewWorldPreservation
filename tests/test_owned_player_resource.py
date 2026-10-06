"""Original synthetic RASC fixtures; no owned assets or native code in tests."""
import hashlib
from pathlib import Path
import struct
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import owned_player_resource as resource
from current_creation_member_body import AssetIdField, CreationMemberBody, encode_body


RAW16 = bytes(range(16))


def catalog(rows=None, names=b"player.dynamicslice\0", directories=b"slices/\0"):
    rows = rows if rows is not None else [(0, 2, 0, 2, 0, 0, 12345, 0, 0)]
    uuid_pool = 40 + len(rows) * 40
    type_pool = uuid_pool + 16
    dir_pool = type_pool + 16
    file_pool = dir_pool + len(directories)
    total = file_pool + len(names)
    header = struct.pack("<4sIQ6I", b"RASC", 1, total, uuid_pool, type_pool, dir_pool, file_pool, total, len(rows))
    records = b"".join(struct.pack("<6IQ2I", *row) for row in rows)
    return header + records + RAW16 + bytes([0xAB]) * 16 + directories + names


def changed(blob, offset, fmt, value):
    result = bytearray(blob)
    struct.pack_into(fmt, result, offset, value)
    return bytes(result)


def test_literal_record_join_and_existing_asset_codec():
    result = resource.parse_player_resource(catalog())
    assert result.asset_id == result.associated_id == AssetIdField(RAW16, 2)
    assert result.row_offset == 40 and result.opaque_18 == 12345
    assert encode_body(CreationMemberBody(asset_id=result.asset_id)) == bytes.fromhex(
        "0101000102030405060708090a0b0c0d0e0f00000002")


@pytest.mark.parametrize("cut", [0, 4, 8, 16, 39, 40, 79, 80, 95, 111, 119])
def test_truncation_and_declared_extents_fail(cut):
    with pytest.raises(ValueError):
        resource.parse_player_resource(catalog()[:cut])


@pytest.mark.parametrize("offset,fmt,value", [
    (0, "4s", b"RAOC"), (4, "I", 2), (8, "Q", 0), (32, "I", 0),
    (36, "I", 0xFFFFFFFF), (16, "I", 40), (20, "I", 81),
    (24, "I", 0xFFFFFFFF), (28, "I", 1),
    (40, "I", 1), (48, "I", 1), (56, "I", 1),
    (72, "I", 0xFFFFFFFF), (72, "I", 1), (76, "I", 0xFFFFFFFF),
])
def test_wrong_header_table_index_or_string_start_fails(offset, fmt, value):
    with pytest.raises(ValueError):
        resource.parse_player_resource(changed(catalog(), offset, "<" + fmt, value))


def test_missing_ambiguous_wrong_directory_and_substring_refused():
    row = (0, 2, 0, 2, 0, 0, 12345, 0, 0)
    for blob in (catalog(rows=[row, row]), catalog(names=b"xplayer.dynamicslice\0"),
                 catalog(directories=b"other/\0"), catalog(names=b"player.dynamicslice")):
        with pytest.raises(ValueError):
            resource.parse_player_resource(blob)


def test_distinct_primary_and_associated_id_are_preserved():
    result = resource.parse_player_resource(catalog(rows=[(0, 2, 0, 100, 0, 0, 5, 0, 0)]))
    assert result.asset_id.field_20 == 2
    assert result.associated_id.field_20 == 100


def test_exact_filename_and_directory_offsets_choose_player_not_neighbor():
    names = b"remoteplayer.dynamicslice\0player.dynamicslice\0"
    rows = [(0, 100, 0, 100, 0, 0, 999, 0, 0), (0, 2, 0, 2, 0, 0, 12345, 0, 26)]
    result = resource.parse_player_resource(catalog(rows=rows, names=names))
    assert result.asset_id.field_20 == 2 and result.row_offset == 80


def test_mutable_or_nonbytes_input_refused():
    for value in (bytearray(catalog()), memoryview(catalog()), None):
        with pytest.raises(TypeError):
            resource.parse_player_resource(value)


def fake_owned_root(tmp_path, monkeypatch):
    root = tmp_path / "game"
    (root / "Bin64").mkdir(parents=True)
    (root / "assets").mkdir()
    (root / "Bin64/NewWorld.exe").write_bytes(b"original synthetic image marker")
    blob = catalog()
    with zipfile.ZipFile(root / "assets/Engine.pak", "w") as archive:
        archive.writestr(resource.CATALOG_MEMBER, blob)
    with zipfile.ZipFile(root / "assets/SharedDataStrm-part8.pak", "w") as archive:
        archive.writestr(resource.PLAYER_PATH, b"never read this synthetic slice")
        entry = archive.getinfo(resource.PLAYER_PATH)
    monkeypatch.setattr(resource, "CATALOG_BYTES", len(blob))
    monkeypatch.setattr(resource, "CATALOG_SHA256", hashlib.sha256(blob).hexdigest())
    monkeypatch.setattr(resource, "PLAYER_ZIP_METADATA", (entry.file_size, entry.compress_size, entry.compress_type, entry.CRC))
    pins = {name: ((root / name).stat().st_size, hashlib.sha256((root / name).read_bytes()).hexdigest())
            for name in resource.PINNED_FILES}
    monkeypatch.setattr(resource, "PINNED_FILES", pins)
    return root


def test_owned_lookup_reads_only_catalog_and_pins_all_files(tmp_path, monkeypatch):
    root = fake_owned_root(tmp_path, monkeypatch)
    actual_read = zipfile.ZipFile.read
    reads = []
    def guarded_read(archive, name, *args, **kwargs):
        reads.append(name.filename if isinstance(name, zipfile.ZipInfo) else name)
        assert reads[-1] == resource.CATALOG_MEMBER
        return actual_read(archive, name, *args, **kwargs)
    monkeypatch.setattr(zipfile.ZipFile, "read", guarded_read)
    assert resource.read_owned_player_resource(root).asset_id == AssetIdField(RAW16, 2)
    assert reads == [resource.CATALOG_MEMBER]


@pytest.mark.parametrize("name", list(resource.PINNED_FILES))
def test_owned_lookup_rejects_changed_file_before_read(tmp_path, monkeypatch, name):
    root = fake_owned_root(tmp_path, monkeypatch)
    target = root / name
    target.write_bytes(bytes(target.stat().st_size))
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        resource.read_owned_player_resource(root)


def test_owned_lookup_rechecks_files_after_catalog_read(tmp_path, monkeypatch):
    root = fake_owned_root(tmp_path, monkeypatch)
    actual_parser = resource.parse_player_resource
    def mutating_parser(blob):
        (root / "Bin64/NewWorld.exe").write_bytes(b"changed")
        return actual_parser(blob)
    monkeypatch.setattr(resource, "parse_player_resource", mutating_parser)
    with pytest.raises(ValueError, match="size mismatch"):
        resource.read_owned_player_resource(root)


def test_owned_lookup_rejects_wrong_catalog_and_package_metadata(tmp_path, monkeypatch):
    root = fake_owned_root(tmp_path, monkeypatch)
    monkeypatch.setattr(resource, "CATALOG_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="catalog SHA256"):
        resource.read_owned_player_resource(root)
    monkeypatch.setattr(resource, "CATALOG_SHA256", hashlib.sha256(catalog()).hexdigest())
    monkeypatch.setattr(resource, "PLAYER_ZIP_METADATA", (0, 0, 0, 0))
    with pytest.raises(ValueError, match="package metadata"):
        resource.read_owned_player_resource(root)


@pytest.mark.parametrize("case", ["compressed", "duplicate_catalog", "duplicate_player"])
def test_unadmitted_zip_shapes_fail_without_resource_read(tmp_path, monkeypatch, case):
    root = fake_owned_root(tmp_path, monkeypatch)
    name = "assets/SharedDataStrm-part8.pak" if case == "duplicate_player" else "assets/Engine.pak"
    member = resource.PLAYER_PATH if case == "duplicate_player" else resource.CATALOG_MEMBER
    with zipfile.ZipFile(root / name, "w") as archive:
        archive.writestr(member, catalog(), compress_type=zipfile.ZIP_DEFLATED if case == "compressed" else zipfile.ZIP_STORED)
        if case.startswith("duplicate"):
            with pytest.warns(UserWarning, match="Duplicate name"):
                archive.writestr(member, catalog())
    pins = dict(resource.PINNED_FILES)
    pins[name] = ((root / name).stat().st_size, hashlib.sha256((root / name).read_bytes()).hexdigest())
    monkeypatch.setattr(resource, "PINNED_FILES", pins)
    with pytest.raises(ValueError, match="pinned catalog|packaged player"):
        resource.read_owned_player_resource(root)
