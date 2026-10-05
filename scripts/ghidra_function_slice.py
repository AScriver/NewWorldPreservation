"""Pinned, function-scoped static Ghidra queries; never run whole-image analysis."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_FUNCTIONS = 8
MAX_CODE_BYTES = 1024 * 1024


class SliceError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Image:
    """Only file-backed AMD64 PE sections and x64 runtime-function metadata."""

    def __init__(self, data: bytes):
        self.data = data
        try:
            if data[:2] != b"MZ":
                raise SliceError("Expected a PE image")
            pe = struct.unpack_from("<I", data, 0x3C)[0]
            if data[pe:pe + 4] != b"PE\0\0":
                raise SliceError("Invalid PE signature")
            machine, count = struct.unpack_from("<HH", data, pe + 4)
            optional_size = struct.unpack_from("<H", data, pe + 20)[0]
            optional = pe + 24
            if (machine != 0x8664 or not 1 <= count <= 96 or optional_size < 144
                    or struct.unpack_from("<H", data, optional)[0] != 0x20B):
                raise SliceError("Expected AMD64 PE32+ with exception metadata")
            self.base = struct.unpack_from("<Q", data, optional + 24)[0]
            if struct.unpack_from("<I", data, optional + 108)[0] < 4:
                raise SliceError("Missing exception directory")
            pdata_rva, pdata_size = struct.unpack_from("<II", data, optional + 136)
            self.sections = []
            for index in range(count):
                start = optional + optional_size + index * 40
                name = data[start:start + 8].split(b"\0")[0].decode("ascii")
                virtual_size, rva, raw_size, raw_offset = struct.unpack_from("<IIII", data, start + 8)
                flags = struct.unpack_from("<I", data, start + 36)[0]
                if raw_offset + raw_size > len(data):
                    raise SliceError("Section extends beyond the image")
                self.sections.append(dict(name=name, start=self.base + rva,
                                          virtual_size=virtual_size, size=raw_size,
                                          offset=raw_offset, executable=bool(flags & 0x20000000)))
            if not pdata_size or pdata_size % 12 or pdata_size > 6_000_000:
                raise SliceError("Invalid or unbounded exception directory")
            table = self.read(self.base + pdata_rva, pdata_size)
            self.functions = [tuple(self.base + value for value in record)
                              for record in struct.iter_unpack("<III", table) if record[0]]
            if any(end <= start for start, end, _ in self.functions):
                raise SliceError("Invalid runtime-function range")
            self._owners = {}
        except (struct.error, UnicodeError) as exc:
            raise SliceError("Truncated or malformed PE metadata") from exc

    def section(self, start: int, size: int) -> dict:
        matches = [section for section in self.sections
                   if section["start"] <= start and start + size <= section["start"] + section["size"]]
        if size <= 0 or len(matches) != 1:
            raise SliceError("Range is not uniquely file-backed")
        return matches[0]

    def read(self, start: int, size: int) -> bytes:
        section = self.section(start, size)
        offset = section["offset"] + start - section["start"]
        return self.data[offset:offset + size]

    def owner(self, record: tuple, seen: tuple = ()) -> tuple:
        if record in self._owners:
            return self._owners[record]
        if record in seen or len(seen) >= 32:
            raise SliceError("Cyclic or unbounded chained unwind metadata")
        start, end, unwind = record
        header = self.read(unwind, 4)
        version, flags = header[0] & 7, header[0] >> 3
        if version not in (1, 2):
            raise SliceError("Unsupported unwind version")
        if flags & 4:
            if flags & 3:
                raise SliceError("Invalid chained unwind flags")
            offset = (4 + header[2] * 2 + 3) & ~3
            parent = tuple(self.base + value for value in struct.unpack("<III", self.read(unwind + offset, 12)))
            result = self.owner(parent, (*seen, record))
        else:
            result = record
        self._owners[record] = result
        return result

    def select(self, entries: list[int]) -> list[dict]:
        if not entries or len(entries) > MAX_FUNCTIONS or len(entries) != len(set(entries)):
            raise SliceError("Select one to eight distinct function entries")
        grouped = {entry: set() for entry in entries}
        for record in self.functions:
            parent = self.owner(record)
            if parent[0] in grouped:
                grouped[parent[0]].update((record[:2], parent[:2]))
        selected = []
        total = 0
        all_ranges = []
        for entry, ranges in grouped.items():
            if not ranges:
                raise SliceError("Entry has no evidenced PDATA/unwind owner; do not guess a leaf body")
            ordered = sorted(ranges)
            for start, end in ordered:
                if not self.section(start, end - start)["executable"]:
                    raise SliceError("Selected range is not executable file-backed code")
                total += end - start
                all_ranges.append((start, end))
            selected.append(dict(entry=entry, ranges=ordered))
        if total > MAX_CODE_BYTES:
            raise SliceError("Selected code exceeds the one MiB bound")
        ordered = sorted(all_ranges)
        if any(left[1] > right[0] for left, right in zip(ordered, ordered[1:])):
            raise SliceError("Selected function ranges overlap")
        return selected


def private_destination(path: Path, roots: list[Path], *, database: bool = False) -> Path:
    resolved = path.resolve()
    if not any(resolved.is_relative_to(root.resolve()) and resolved != root.resolve() for root in roots):
        raise SliceError("Destination must be a new directory beneath its private root")
    if database and any(part.startswith(".") for part in resolved.parts):
        raise SliceError("Ghidra database paths cannot contain dot-prefixed segments")
    if resolved.exists():
        raise SliceError("Refuse to reuse or overwrite an existing destination")
    return resolved


def decompile(image: Image, selected: list[dict], output: Path, project_path: Path,
              timeout: int, results: list[dict]) -> dict:
    # Imported only by an explicit static query; importing this module/tests never starts a JVM.
    import pyghidra
    pyghidra.start()
    from ghidra.app.cmd.disassemble import DisassembleCommand
    from ghidra.app.decompiler import DecompInterface
    from ghidra.base.project import GhidraProject
    from ghidra.framework import Application
    from ghidra.program.database import ProgramDB
    from ghidra.program.model.address import AddressSet
    from ghidra.program.model.lang import CompilerSpecID, LanguageID
    from ghidra.program.model.symbol import SourceType
    from ghidra.program.util import DefaultLanguageService
    from ghidra.util.task import TaskMonitor
    from java.io import ByteArrayInputStream
    from java.lang import Object

    language = DefaultLanguageService.getLanguageService().getLanguage(LanguageID("x86:LE:64:default"))
    consumer = Object()
    program = ProgramDB("FunctionSlices", language, language.getCompilerSpecByID(CompilerSpecID("windows")), consumer)
    project = None
    interface = None
    try:
        space = program.getAddressFactory().getDefaultAddressSpace()
        address = space.getAddress
        transaction = program.startTransaction("Import selected pinned code and data; no automatic analysis")
        success = False
        try:
            program.setImageBase(address(image.base), True)
            memory = program.getMemory()
            functions = []
            for item in selected:
                body = AddressSet()
                for start, end in item["ranges"]:
                    block = memory.createInitializedBlock(f"code_{start:x}", address(start),
                              ByteArrayInputStream(image.read(start, end - start)), end - start, TaskMonitor.DUMMY, False)
                    block.setExecute(True)
                    block.setWrite(False)
                    body.addRange(address(start), address(end - 1))
                for start, end in item["ranges"]:
                    command = DisassembleCommand(address(start), body, True)
                    if not command.applyTo(program, TaskMonitor.DUMMY):
                        raise SliceError("Selected-function disassembly failed")
                functions.append(program.getFunctionManager().createFunction(
                    f"f_{item['entry']:x}", address(item["entry"]), body, SourceType.USER_DEFINED))
            # Static data assists references; no other executable sections/functions are imported.
            for section in image.sections:
                if section["name"] not in (".rdata", ".data") or not section["size"]:
                    continue
                block = memory.createInitializedBlock(section["name"], address(section["start"]),
                          ByteArrayInputStream(image.read(section["start"], section["size"])),
                          section["size"], TaskMonitor.DUMMY, False)
                block.setWrite(section["name"] == ".data")
                if section["virtual_size"] > section["size"]:
                    memory.createUninitializedBlock(section["name"] + "_bss",
                        address(section["start"] + section["size"]), section["virtual_size"] - section["size"], False)
            success = True
        finally:
            program.endTransaction(transaction, success)
        interface = DecompInterface()
        if not interface.openProgram(program):
            raise SliceError("Decompiler could not open the sparse program")
        for item, function in zip(selected, functions):
            result = interface.decompileFunction(function, timeout, TaskMonitor.DUMMY)
            completed = bool(result.decompileCompleted())
            filename = f"function-{item['entry']:x}." + ("c" if completed else "error.txt")
            target = output / filename
            content = result.getDecompiledFunction().getC() if completed else str(result.getErrorMessage())
            with target.open("x", encoding="utf-8") as stream:
                stream.write(str(content))
            results.append(dict(entry=hex(item["entry"]), completed=completed,
                                path=filename, sha256=sha256(target.read_bytes())))
        project = GhidraProject.createProject(str(project_path), "FunctionSlices", False)
        program.addConsumer(project)
        project.saveAs(program, "/", "FunctionSlices", True)
        return {"ghidra": str(Application.getApplicationVersion()),
                "pyghidra": pyghidra.__version__}
    finally:
        if interface is not None:
            interface.dispose()
        if project is not None:
            project.close()
        program.release(consumer)


def run(image_path: Path, expected_sha256: str, entries: list[int], output: Path,
        project: Path, timeout: int, *, backend=decompile) -> dict:
    if len(expected_sha256) != 64 or any(char not in "0123456789abcdef" for char in expected_sha256):
        raise SliceError("Require an explicit lowercase SHA256")
    if not 1 <= timeout <= 60:
        raise SliceError("Per-function timeout must be between one and sixty seconds")
    image_path = image_path.resolve(strict=True)
    data = image_path.read_bytes()
    if sha256(data) != expected_sha256:
        raise SliceError("Image hash mismatch; no query or destination was created")
    image = Image(data)
    selected = image.select(entries)
    output = private_destination(output, [ROOT / ".scratch", ROOT / "private"])
    project = private_destination(project, [ROOT / "private/ghidra"], database=True)
    if output == project or output.is_relative_to(project) or project.is_relative_to(output):
        raise SliceError("Output and database destinations must be separate")
    receipt = dict(schema=1, mode="static-source-inference", automaticAnalysis=False,
                   clientExecuted=False, imageSha256=expected_sha256,
                   scriptSha256=sha256(Path(__file__).read_bytes()),
                   recordedUtc=datetime.now(timezone.utc).isoformat(), timeoutSeconds=timeout,
                   functions=[dict(entry=hex(item["entry"]), ranges=[dict(start=hex(start), end=hex(end),
                               sha256=sha256(image.read(start, end - start))) for start, end in item["ranges"]])
                              for item in selected], results=[], status="failed")
    output.mkdir(parents=True, exist_ok=False)
    project.mkdir(parents=True, exist_ok=False)
    try:
        receipt["tools"] = backend(image, selected, output, project, timeout, receipt["results"])
        if sha256(image_path.read_bytes()) != expected_sha256:
            raise SliceError("Image changed during analysis")
        receipt["sourceStable"] = True
        receipt["status"] = "passed" if all(item["completed"] for item in receipt["results"]) and len(receipt["results"]) == len(selected) else "partial"
    except Exception as exc:
        receipt["errorType"] = type(exc).__name__
        raise
    finally:
        receipt["gitHead"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        receipt["gitStatus"] = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True)
        with (output / "receipt.json").open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2)
            stream.write("\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--functions", required=True, nargs="+", type=lambda value: int(value, 16))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    options = parser.parse_args()
    try:
        receipt = run(options.image, options.expected_sha256, options.functions,
                      options.output, options.project, options.timeout)
    except (SliceError, OSError) as exc:
        print(f"Static slice rejected: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": receipt["status"], "functions": len(receipt["results"]),
                      "receipt": str(options.output / "receipt.json")}))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
