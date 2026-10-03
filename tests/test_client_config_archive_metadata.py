import importlib.util
import json
import struct
import warnings
import zipfile
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("client_config_archive_metadata", Path(__file__).parents[1] / "scripts/client_config_archive_metadata.py")
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


def make_archive(tmp_path, names=("client.json",), compression=zipfile.ZIP_STORED):
    path = tmp_path / "owned-fixture.pak"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(path, "w", compression=compression) as archive:
            for name in names:
                archive.writestr(name, b'{"password":"private-secret","client-connection":{"type":"UDP"}}')
    return path


def patch_method(path, method):
    data = bytearray(path.read_bytes())
    struct.pack_into("<H", data, data.index(b"PK\x03\x04") + 8, method)
    struct.pack_into("<H", data, data.index(b"PK\x01\x02") + 10, method)
    path.write_bytes(data)


@pytest.mark.parametrize("compression", [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED])
def test_metadata_only_never_decodes_or_exports_content(tmp_path, monkeypatch, compression):
    path = make_archive(tmp_path, compression=compression)
    before = path.read_bytes()
    monkeypatch.setattr(zipfile.ZipFile, "open", lambda *a, **k: pytest.fail("Member decoding was attempted"))
    result = metadata.inspect_archive(path)
    assert result["memberFound"] and result["sourceStableDuringRead"]
    assert result["memberMetadata"]["compressionMethod"] == compression
    assert len(result["memberMetadata"]["compressedReadSha256"]) == 64
    assert result["contentDecoded"] is False and result["runtimeLoadingObserved"] is False
    assert result["memberMetadata"]["crcVerified"] is False
    assert "private-secret" not in json.dumps(result) and "password" not in json.dumps(result)
    assert path.read_bytes() == before


def test_unknown_method_is_index_metadata_not_a_guessed_codec(tmp_path):
    path = make_archive(tmp_path)
    patch_method(path, 15)
    result = metadata.inspect_archive(path)
    assert result["memberMetadata"]["compressionMethod"] == 15
    assert result["contentDecoded"] is False
    assert "codec" not in json.dumps(result).lower()


def test_missing_exact_member_does_not_export_other_names(tmp_path):
    result = metadata.inspect_archive(make_archive(tmp_path, ("private-person.json", "Client.json")))
    assert result["memberFound"] is False
    assert "private-person" not in json.dumps(result)
    assert "memberMetadata" not in result


def test_duplicate_exact_member_rejected(tmp_path):
    with pytest.raises(metadata.MetadataError, match="^ambiguous_member$"):
        metadata.inspect_archive(make_archive(tmp_path, ("client.json", "client.json")))


@pytest.mark.parametrize("encrypted", [False, True])
def test_normalized_nonexact_member_is_not_selected(tmp_path, encrypted):
    path = make_archive(tmp_path, ("client.jsonXprivate-tail",))
    data = bytearray(path.read_bytes())
    local = data.index(b"PK\x03\x04")
    central = data.index(b"PK\x01\x02")
    data[local + 30 + len(metadata.MEMBER)] = 0
    data[central + 46 + len(metadata.MEMBER)] = 0
    if encrypted:
        struct.pack_into("<H", data, local + 6, 1)
        struct.pack_into("<H", data, central + 8, 1)
    path.write_bytes(data)
    result = metadata.inspect_archive(path)
    assert result["memberFound"] is False
    assert "memberMetadata" not in result
    assert "private-tail" not in json.dumps(result)


def test_encrypted_member_is_not_read(tmp_path, monkeypatch):
    path = make_archive(tmp_path)
    data = bytearray(path.read_bytes())
    struct.pack_into("<H", data, data.index(b"PK\x03\x04") + 6, 1)
    struct.pack_into("<H", data, data.index(b"PK\x01\x02") + 8, 1)
    path.write_bytes(data)
    monkeypatch.setattr(metadata, "compressed_member_hash", lambda *a: pytest.fail("Encrypted payload was read"))
    result = metadata.inspect_archive(path)
    assert result["memberMetadata"]["encrypted"] is True
    assert "compressedReadSha256" not in result["memberMetadata"]


def test_index_limits_checked_before_zipfile_parsing(tmp_path, monkeypatch):
    path = make_archive(tmp_path)
    monkeypatch.setattr(metadata, "MAX_INDEX_BYTES", 1)
    monkeypatch.setattr(zipfile, "ZipFile", lambda *a: pytest.fail("Oversized index reached parser"))
    with pytest.raises(metadata.MetadataError, match="^index_limit_exceeded$"):
        metadata.inspect_archive(path)


def test_member_limit_rejected_before_payload_read(tmp_path, monkeypatch):
    monkeypatch.setattr(metadata, "MAX_COMPRESSED_BYTES", 1)
    with pytest.raises(metadata.MetadataError, match="^member_limit_exceeded$"):
        metadata.inspect_archive(make_archive(tmp_path))


@pytest.mark.parametrize("mutation,code", [("method", "member_header_mismatch"), ("name", "member_name_mismatch"),
                                         ("size", "member_size_mismatch"), ("offset", "invalid_member_bounds")])
def test_inconsistent_local_header_rejected(tmp_path, mutation, code):
    path = make_archive(tmp_path)
    data = bytearray(path.read_bytes())
    local = data.index(b"PK\x03\x04")
    central = data.index(b"PK\x01\x02")
    if mutation == "method":
        struct.pack_into("<H", data, local + 8, 15)
    elif mutation == "name":
        data[local + 30] = ord("X")
    elif mutation == "size":
        struct.pack_into("<I", data, local + 18, 500)
    else:
        struct.pack_into("<I", data, central + 42, central)
    path.write_bytes(data)
    with pytest.raises(metadata.MetadataError, match=f"^{code}$"):
        metadata.inspect_archive(path)


@pytest.mark.parametrize("mutation,code", [("zip64", "zip64_index_unsupported"), ("disk", "multi_volume_index_unsupported"),
                                         ("offset", "noncontiguous_index_unsupported"), ("tail", "invalid_zip_end")])
def test_unsupported_or_malformed_end_rejected(tmp_path, mutation, code):
    path = make_archive(tmp_path)
    data = bytearray(path.read_bytes())
    end = data.index(b"PK\x05\x06")
    if mutation == "zip64":
        struct.pack_into("<H", data, end + 10, 0xffff)
    elif mutation == "disk":
        struct.pack_into("<H", data, end + 4, 1)
    elif mutation == "offset":
        struct.pack_into("<I", data, end + 16, 1)
    else:
        data.extend(b"trailing")
    path.write_bytes(data)
    with pytest.raises(metadata.MetadataError, match=f"^{code}$"):
        metadata.inspect_archive(path)


def test_changed_source_rejected(tmp_path, monkeypatch):
    path = make_archive(tmp_path)
    original = metadata.compressed_member_hash

    def mutate_after_read(stream, info, offset):
        result = original(stream, info, offset)
        path.write_bytes(path.read_bytes() + b"changed")
        return result

    monkeypatch.setattr(metadata, "compressed_member_hash", mutate_after_read)
    with pytest.raises(metadata.MetadataError, match="^archive_changed$"):
        metadata.inspect_archive(path)


def test_cli_output_guard_and_no_overwrite(tmp_path, capsys, monkeypatch):
    source = make_archive(tmp_path)
    root = tmp_path / "tool-workspace"
    monkeypatch.setattr(metadata, "__file__", str(root / "scripts" / "client_config_archive_metadata.py"))
    with pytest.raises(SystemExit):
        metadata.main(["--archive", str(source), "--output", str(tmp_path / "public-output.json")])
    assert not (tmp_path / "public-output.json").exists()
    output = root / ".scratch" / "new-output.json"
    try:
        assert metadata.main(["--archive", str(source), "--output", str(output)]) == 0
        before = output.read_bytes()
        with pytest.raises(SystemExit):
            metadata.main(["--archive", str(source), "--output", str(output)])
        assert output.read_bytes() == before
        assert "private-secret" not in capsys.readouterr().out
    finally:
        output.unlink(missing_ok=True)


def test_cli_fixed_errors_do_not_echo_raw_member_data(tmp_path, capsys, monkeypatch):
    source = tmp_path / "private-secret.pak"
    source.write_bytes(b"private-secret")
    root = tmp_path / "tool-workspace"
    monkeypatch.setattr(metadata, "__file__", str(root / "scripts" / "client_config_archive_metadata.py"))
    output = root / ".scratch" / "new-output.json"
    assert metadata.main(["--archive", str(source), "--output", str(output)]) == 1
    assert not output.exists()
    assert json.loads(capsys.readouterr().out) == {"state": "ARCHIVE_METADATA_REJECTED", "code": "missing_zip_index"}
