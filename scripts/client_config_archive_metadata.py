"""Inspect only client.json archive metadata; never decode or export client content.

The archive index is not evidence that a running client loads this member or
that it supplies a REP trust setting. Unknown compression methods stay unknown.
"""
import argparse
import hashlib
import json
import os
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MEMBER = "client.json"
MAX_INDEX_BYTES = 16 * 1024 * 1024
MAX_ENTRIES = 50000
MAX_COMPRESSED_BYTES = 1024 * 1024
END = struct.Struct("<4s4H2IH")
LOCAL = struct.Struct("<4s5H3I2H")


class MetadataError(ValueError):
    """A fixed error code, without archive names, raw bytes or library errors."""


def identity(stat):
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def read_exact(stream, count):
    data = stream.read(count)
    if len(data) != count:
        raise MetadataError("truncated_archive")
    return data


def central_directory(stream, size):
    # Only ordinary, single-volume ZIP indexes are supported. Reject ZIP64
    # before zipfile can read an unbounded index or expand its entry list.
    tail_size = min(size, END.size + 65535)
    stream.seek(size - tail_size)
    tail = read_exact(stream, tail_size)
    end_at = tail.rfind(b"PK\x05\x06")
    if end_at < 0 or len(tail) - end_at < END.size:
        raise MetadataError("missing_zip_index")
    signature, disk, start_disk, disk_entries, entries, index_bytes, offset, comment_bytes = END.unpack_from(tail, end_at)
    if end_at + END.size + comment_bytes != len(tail):
        raise MetadataError("invalid_zip_end")
    if entries == 0xffff or disk_entries == 0xffff or index_bytes == 0xffffffff or offset == 0xffffffff:
        raise MetadataError("zip64_index_unsupported")
    if disk or start_disk or disk_entries != entries:
        raise MetadataError("multi_volume_index_unsupported")
    if entries > MAX_ENTRIES or index_bytes > MAX_INDEX_BYTES:
        raise MetadataError("index_limit_exceeded")
    end_offset = size - tail_size + end_at
    if offset + index_bytes != end_offset:
        raise MetadataError("noncontiguous_index_unsupported")
    stream.seek(offset)
    index_hash = hashlib.sha256(read_exact(stream, index_bytes)).hexdigest()
    return offset, entries, index_bytes, index_hash


def compressed_member_hash(stream, info, index_offset):
    if info.compress_size > MAX_COMPRESSED_BYTES:
        raise MetadataError("member_limit_exceeded")
    if info.header_offset < 0 or info.header_offset + LOCAL.size > index_offset:
        raise MetadataError("invalid_member_bounds")
    stream.seek(info.header_offset)
    fields = LOCAL.unpack(read_exact(stream, LOCAL.size))
    signature, _, flags, method, _, _, crc, compressed_size, decoded_size, name_size, extra_size = fields
    if signature != b"PK\x03\x04" or flags != info.flag_bits or method != info.compress_type:
        raise MetadataError("member_header_mismatch")
    name = read_exact(stream, name_size)
    expected_name = MEMBER.encode("utf-8" if flags & 0x800 else "cp437")
    if name != expected_name:
        raise MetadataError("member_name_mismatch")
    if not flags & 8 and (crc, compressed_size, decoded_size) != (info.CRC, info.compress_size, info.file_size):
        raise MetadataError("member_size_mismatch")
    payload_offset = info.header_offset + LOCAL.size + name_size + extra_size
    if payload_offset + info.compress_size > index_offset:
        raise MetadataError("invalid_member_bounds")
    stream.seek(payload_offset)
    return hashlib.sha256(read_exact(stream, info.compress_size)).hexdigest()


def inspect_archive(path):
    path = Path(path)
    before = path.stat()
    with path.open("rb") as stream:
        if identity(os.fstat(stream.fileno())) != identity(before):
            raise MetadataError("archive_changed")
        index_offset, entries, index_bytes, index_hash = central_directory(stream, before.st_size)
        try:
            with zipfile.ZipFile(stream) as archive:
                infos = archive.infolist()
                if len(infos) != entries or archive.start_dir != index_offset:
                    raise MetadataError("index_count_or_offset_mismatch")
                matches = [info for info in infos if info.filename == MEMBER]
                if len(matches) > 1:
                    raise MetadataError("ambiguous_member")
                result = {"schemaVersion": 1, "observedAtUtc": datetime.now(timezone.utc).isoformat(),
                          "archiveBytes": before.st_size, "archiveFullyHashed": False,
                          "indexEntries": entries, "indexBytes": index_bytes, "indexSha256": index_hash,
                          "member": MEMBER, "memberFound": bool(matches), "contentDecoded": False,
                          "rawContentExported": False, "runtimeLoadingObserved": False}
                if matches:
                    info = matches[0]
                    encrypted = bool(info.flag_bits & (1 | 0x40 | 0x2000))
                    result["memberMetadata"] = {"declaredBytes": info.file_size, "compressedBytes": info.compress_size,
                                                "compressionMethod": info.compress_type, "declaredCrc32": f"{info.CRC:08x}",
                                                "crcVerified": False, "encrypted": encrypted}
                    # No passwords, decryption, codec guesses or extraction.
                    if not encrypted:
                        result["memberMetadata"]["compressedReadSha256"] = compressed_member_hash(stream, info, index_offset)
        except (zipfile.BadZipFile, UnicodeError, NotImplementedError):
            raise MetadataError("invalid_zip_index") from None
        if identity(os.fstat(stream.fileno())) != identity(before) or identity(path.stat()) != identity(before):
            raise MetadataError("archive_changed")
    result["sourceStableDuringRead"] = True
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--output", required=True)
    options = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    output = Path(options.output).resolve()
    if not any(output.is_relative_to(root / folder) for folder in ("private", ".scratch")):
        parser.error("Output must remain in ignored private/ or .scratch/")
    if output.exists():
        parser.error("Output already exists")
    try:
        result = inspect_archive(Path(options.archive))
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    except (MetadataError, OSError) as failure:
        code = str(failure) if isinstance(failure, MetadataError) else "file_access_failed"
        print(json.dumps({"state": "ARCHIVE_METADATA_REJECTED", "code": code}))
        return 1
    print(json.dumps({"state": "CLIENT_CONFIG_ARCHIVE_INDEX_INSPECTED", "memberFound": result["memberFound"],
                      "contentDecoded": False, "rawContentExported": False, "runtimeLoadingObserved": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
