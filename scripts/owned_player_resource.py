"""File-only reconstruction of the pinned owned player's RASC catalog key.

The native RASC v1 grammar supplies raw16 plus uint32. This has the existing
creation AssetId field's representation; native path-provider binding and asset
loading remain unobserved. No slice bytes are extracted or client code executed.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
import zipfile

from current_creation_member_body import AssetIdField


PLAYER_PATH = "slices/player.dynamicslice"
CATALOG_MEMBER = "assetcatalog.catalog"
CATALOG_SHA256 = "7875baffb58ee5454507e5d6e4b035705cf28e2bf02ea1310ca6058dbfd34680"
CATALOG_BYTES = 283026856
PINNED_FILES = {
    "Bin64/NewWorld.exe": (179204176, "8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e"),
    "assets/Engine.pak": (673824605, "b5405246d9856acfdd8aa2d56f8d02d40a4b3d524542b7eaed182358a3d77329"),
    "assets/SharedDataStrm-part8.pak": (138144760, "a914b6a834c5c7832b065955b8b8bfa2ab1b90004b26ff5bcef9d8397cc36751"),
}
PLAYER_ZIP_METADATA = (367528, 44796, 15, 0xA52D1752)
MAX_CATALOG_BYTES = 300_000_000


@dataclass(frozen=True)
class PlayerResource:
    asset_id: AssetIdField
    associated_id: AssetIdField
    row_offset: int
    opaque_18: int


def parse_player_resource(catalog: bytes) -> PlayerResource:
    """Read the exact path from proved RASC fields, with stricter offline guards.

    This targeted parser accepts synthetic catalogs for tests. Use
    read_owned_player_resource for the mandatory owned build/package/hash guards.
    It does not validate unrelated dependency sections or implement RAOC.
    """
    if type(catalog) is not bytes:
        raise TypeError("catalog must be immutable bytes")
    if not 40 <= len(catalog) <= MAX_CATALOG_BYTES:
        raise ValueError("catalog size is outside the bounded domain")
    magic, version, total, uuid_pool, type_pool, directories, filenames, end, count = struct.unpack_from(
        "<4sIQ6I", catalog)
    if magic != b"RASC" or version != 1:
        raise ValueError("requires RASC version1; RAOC is not admitted")
    if total != len(catalog) or end != len(catalog):
        raise ValueError("catalog declared extent disagrees with bytes")
    rows_end = 40 + count * 40
    if not 40 <= rows_end <= uuid_pool <= type_pool <= directories <= filenames <= end:
        raise ValueError("catalog tables overlap or exceed their extents")
    if (type_pool - uuid_pool) % 16 or (directories - type_pool) % 16:
        raise ValueError("UUID table extent is not a multiple of16")

    def raw16(index: int, base: int, limit: int) -> bytes:
        offset = base + index * 16
        if offset + 16 > limit:
            raise ValueError("catalog UUID index exceeds its table")
        return catalog[offset:offset + 16]

    def cstring(index: int, base: int, limit: int) -> bytes:
        offset = base + index
        if offset >= limit or (index and catalog[offset - 1] != 0):
            raise ValueError("catalog string index is not a bounded string start")
        terminator = catalog.find(b"\0", offset, limit)
        if terminator < 0:
            raise ValueError("catalog string lacks a bounded terminator")
        return catalog[offset:terminator]

    # Names are pooled separately; a substring or nearest UUID is not a match.
    basename = b"player.dynamicslice\0"
    name_indices = set()
    cursor = filenames
    while (position := catalog.find(basename, cursor, end)) >= 0:
        if position == filenames or catalog[position - 1] == 0:
            name_indices.add(position - filenames)
        cursor = position + 1
    matches = []
    for row in range(40, rows_end, 40):
        directory_index, filename_index = struct.unpack_from("<2I", catalog, row + 32)
        if filename_index not in name_indices:
            continue
        if cstring(directory_index, directories, filenames) != b"slices/":
            continue
        first_index, suffix, second_index, second_suffix, type_index = struct.unpack_from("<5I", catalog, row)
        raw16(type_index, type_pool, directories)  # Native reader also indexes this field.
        matches.append(PlayerResource(
            AssetIdField(raw16(first_index, uuid_pool, type_pool), suffix),
            AssetIdField(raw16(second_index, uuid_pool, type_pool), second_suffix),
            row, struct.unpack_from("<Q", catalog, row + 24)[0]))
    if len(matches) != 1:
        raise ValueError(f"requires exactly one {PLAYER_PATH} record; found{len(matches)}")
    return matches[0]


def _hash_file(path: Path, expected_size: int) -> str:
    if path.stat().st_size != expected_size:
        raise ValueError("pinned file size mismatch")
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            count += len(chunk)
            if count > expected_size:
                raise ValueError("pinned file grew during lookup")
            digest.update(chunk)
    if count != expected_size:
        raise ValueError("pinned file was truncated during lookup")
    return digest.hexdigest()


def read_owned_player_resource(game_root: Path) -> PlayerResource:
    """Inspect a legitimately owned identical installed/archive/isolated copy."""
    root = game_root.resolve(strict=True)
    paths = {name: (root / name).resolve(strict=True) for name in PINNED_FILES}
    if any(not path.is_relative_to(root) for path in paths.values()):
        raise ValueError("pinned file resolves outside the supplied game root")

    def verify_files() -> None:
        for name, (size, digest) in PINNED_FILES.items():
            if _hash_file(paths[name], size) != digest:
                raise ValueError(f"pinned file SHA256 mismatch: {name}")

    verify_files()
    with zipfile.ZipFile(paths["assets/Engine.pak"]) as archive:
        entries = [entry for entry in archive.infolist() if entry.filename == CATALOG_MEMBER]
        if (len(entries) != 1 or entries[0].file_size != CATALOG_BYTES
                or entries[0].compress_size != CATALOG_BYTES
                or entries[0].compress_type != zipfile.ZIP_STORED or entries[0].flag_bits & 1):
            raise ValueError("requires one unencrypted stored pinned catalog")
        catalog = archive.read(entries[0])  # ZIP CRC checked; bounded stored member only.
    if hashlib.sha256(catalog).hexdigest() != CATALOG_SHA256:
        raise ValueError("pinned catalog SHA256 mismatch")
    result = parse_player_resource(catalog)
    with zipfile.ZipFile(paths["assets/SharedDataStrm-part8.pak"]) as archive:
        entries = [entry for entry in archive.infolist() if entry.filename == PLAYER_PATH]
        if len(entries) != 1:
            raise ValueError("requires exactly one packaged player resource")
        entry = entries[0]
        if ((entry.file_size, entry.compress_size, entry.compress_type, entry.CRC) != PLAYER_ZIP_METADATA
                or entry.flag_bits & 1):
            raise ValueError("pinned player package metadata mismatch")
        # The method15 slice is deliberately never read/decompressed.
    verify_files()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    options = parser.parse_args()
    result = read_owned_player_resource(options.game_root)
    print(json.dumps({"classification": "file-only-source-supported-candidate",
        "resourcePath": PLAYER_PATH, "catalogSha256": CATALOG_SHA256,
        "assetId": {"raw16": result.asset_id.raw16.hex(), "field_20": result.asset_id.field_20},
        "associatedIdMatches": result.associated_id == result.asset_id,
        "rowOffset": result.row_offset, "opaqueRow18": result.opaque_18,
        "clientExecuted": False, "runtimeAssetLoadObserved": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
