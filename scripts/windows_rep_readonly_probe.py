"""Explicit, bounded own-client observation; never called by offline validation.

Only QUERY_LIMITED_INFORMATION / VM_READ handles, GetProcessTimes, own-process
module enumeration, and four fixed reads. No debugger, privilege adjustment,
memory writes, remote threads, drivers, arbitrary address CLI, or raw dumps.
Microsoft API references and current-build address provenance are in
docs/REP_TRUST_POLICY.md. Access denial is a result, not a bypass invitation.
"""
import argparse
import calendar
import ctypes
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

STOCK_SHA256 = "8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e"
STOCK_OWNER_SHA256 = "e2efeabbac183b1f472197da3d61c33a6011a53eed9bdbd0188df41168917a45"
CLIENT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\New World\Bin64\NewWorld.exe")
QUERY_LIMITED = 0x1000
VM_READ = 0x10
ROOT_POINTER_RVA = 0x9F80D90
ROOT_TEXT_RVA = 0x8590460
ROOT_TEXT_BYTES = 1350
HOLDER_POINTER_RVA = 0xA2E5E98
INITIALIZER_INDEX_RVA = 0x9E7C890
MAX_MODULES = 512
WINDOWS_EPOCH_TICKS = 116444736000000000


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def start_ticks(value):
    """Preserve all seven FILETIME fractional digits; datetime alone loses one."""
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,7}))?(?:Z|\+00:00)", value)
    if match is None:
        raise ValueError("UTC ownership timestamp required")
    stamp = datetime.strptime(match[1], "%Y-%m-%dT%H:%M:%S")
    return WINDOWS_EPOCH_TICKS + calendar.timegm(stamp.timetuple()) * 10000000 + int((match[2] or "").ljust(7, "0") or "0")


def load_owner(run, root):
    run = run.resolve(strict=True)
    private = (root / "private" / "connectivity").resolve(strict=True)
    if run == private or private not in run.parents or (run / "stop.request").exists():
        raise ValueError("fresh active private connectivity run required")
    files = {name: run / name for name in ("run-manifest.json", "owned-client.json", "anchor-launch-manifest.json")}
    records = {name: json.loads(path.read_text(encoding="utf-8-sig")) for name, path in files.items()}
    trial, owner, launch = (records[name] for name in files)
    if any(Path(record["run_directory"]).resolve() != run for record in records.values()):
        raise ValueError("run identity conflict")
    if trial["source_identity"]["stock_control_window_sha256"] != STOCK_OWNER_SHA256:
        raise ValueError("unchanged-stock containment owner required")
    if launch["candidate_sha256"] != STOCK_SHA256 or owner["installed_candidate_sha256_after_launch"] != STOCK_SHA256:
        raise ValueError("stock-only observation required")
    if Path(owner["launch_manifest"]).resolve() != files["anchor-launch-manifest.json"]:
        raise ValueError("ownership manifest conflict")
    process_id = owner["process_id"]
    if type(process_id) is not int or not 0 < process_id < 2**32:
        raise ValueError("positive owned PID required")
    expected_start = start_ticks(owner["start_time_utc"])
    if expected_start < start_ticks(owner["launch_boundary_utc"]):
        raise ValueError("process predates own launch")
    if digest(CLIENT) != STOCK_SHA256:
        raise ValueError("installed stock image changed")
    bindings = {name: digest(path) for name, path in files.items()}
    return run, process_id, expected_start, bindings


def observe(api, process_id, expected_start, emit, *, active=lambda: True):
    """API facade is injectable for offline fault tests; no unbounded retry."""
    handle, error_code = api.open(QUERY_LIMITED, process_id)
    try:
        emit("PROCESS_QUERY_OPEN", opened=bool(handle), win32_error=error_code)
        if not handle:
            return
        created, error_code = api.created(handle)
        emit("PROCESS_START_READBACK", observed=created is not None,
             matches_owned_start=created == expected_start, win32_error=error_code)
        if created != expected_start or not active():
            return
        path, error_code = api.path(handle)
        path_matches = path is not None and os.path.normcase(path) == os.path.normcase(str(CLIENT))
        emit("PROCESS_IMAGE_PATH", observed=path is not None, matches_stock_path=path_matches,
             win32_error=error_code)
        if not path_matches:
            return
    finally:
        if handle:
            api.close(handle)
    if not active():
        return
    # QueryFullProcessImageName must already have identified the stock process.
    # Require an exact module-path match too; module enumeration alone cannot
    # establish the main executable's identity. No VM_READ before both checks.
    module, error_code = api.module(process_id)
    emit("OWNED_MAIN_MODULE", observed=module is not None, win32_error=error_code,
         stock_module_path_verified=module is not None)
    if module is None:
        return
    base, size = module
    if base <= 0 or size < max(ROOT_POINTER_RVA + 8, ROOT_TEXT_RVA + ROOT_TEXT_BYTES,
                              HOLDER_POINTER_RVA + 8, INITIALIZER_INDEX_RVA + 4):
        emit("MODULE_RANGE_REFUSED")
        return
    emit("OWNED_MODULE_RANGE", base_hex=hex(base), size=size)
    if not active():
        return
    read_handle, error_code = api.open(QUERY_LIMITED | VM_READ, process_id)
    try:
        emit("PROCESS_VM_READ_OPEN", opened=bool(read_handle), win32_error=error_code,
             requested_access=QUERY_LIMITED | VM_READ)
        if not read_handle:
            return
        created, error_code = api.created(read_handle)
        if created != expected_start or not active():
            emit("PROCESS_READ_IDENTITY_REFUSED", matches_owned_start=created == expected_start,
                 win32_error=error_code)
            return
        # Values only, not arbitrary heap traversal. Holder/index are diagnostic
        # globals, not a claim that their live objects are the settings provider.
        for label, rva, count in (("REP_ROOT_POINTER", ROOT_POINTER_RVA, 8),
                                  ("SETTINGS_HOLDER_POINTER", HOLDER_POINTER_RVA, 8),
                                  ("SETTINGS_INITIALIZER_INDEX", INITIALIZER_INDEX_RVA, 4)):
            if not active():
                return
            data, error_code = api.read(read_handle, base + rva, count)
            okay = data is not None and len(data) == count
            details = dict(observed=okay, requested_bytes=count, win32_error=error_code)
            if okay:
                value = int.from_bytes(data, "little")
                if count == 8:
                    details.update(pointer_hex=hex(value), points_inside_main_image=base <= value < base + size)
                else:
                    details["value"] = value
                if label == "REP_ROOT_POINTER":
                    details["matches_static_embedded_text_address"] = value == base + ROOT_TEXT_RVA
            emit(label, **details)
            # A denied/partial read ends this observation. No rights escalation.
            if not okay:
                return
        if not active():
            return
        data, error_code = api.read(read_handle, base + ROOT_TEXT_RVA, ROOT_TEXT_BYTES)
        okay = data is not None and len(data) == ROOT_TEXT_BYTES
        emit("STATIC_EMBEDDED_ROOT_TEXT_DIGEST", observed=okay, requested_bytes=ROOT_TEXT_BYTES,
             win32_error=error_code, sha256=hashlib.sha256(data).hexdigest() if okay else None,
             raw_bytes_saved=False, runtime_store_contents_proven=False)
    finally:
        if read_handle:
            api.close(read_handle)


class WindowsReadOnly:
    def __init__(self):
        if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
            raise RuntimeError("64-bit Windows required")
        from ctypes import wintypes as w
        class Module(ctypes.Structure):
            _fields_ = [("dwSize", w.DWORD), ("th32ModuleID", w.DWORD), ("th32ProcessID", w.DWORD),
                        ("GlblcntUsage", w.DWORD), ("ProccntUsage", w.DWORD),
                        ("modBaseAddr", ctypes.c_void_p), ("modBaseSize", w.DWORD),
                        ("hModule", w.HMODULE), ("szModule", w.WCHAR * 256), ("szExePath", w.WCHAR * 260)]
        self.Module = Module
        self.k = ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "OpenProcess": ([w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
            "CloseHandle": ([w.HANDLE], w.BOOL),
            "GetProcessTimes": ([w.HANDLE] + [ctypes.POINTER(ctypes.c_uint64)] * 4, w.BOOL),
            "QueryFullProcessImageNameW": ([w.HANDLE, w.DWORD, w.LPWSTR, ctypes.POINTER(w.DWORD)], w.BOOL),
            "CreateToolhelp32Snapshot": ([w.DWORD, w.DWORD], w.HANDLE),
            "Module32FirstW": ([w.HANDLE, ctypes.POINTER(Module)], w.BOOL),
            "Module32NextW": ([w.HANDLE, ctypes.POINTER(Module)], w.BOOL),
            "ReadProcessMemory": ([w.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                   ctypes.POINTER(ctypes.c_size_t)], w.BOOL),
        }
        for name, (arguments, returns) in signatures.items():
            function = getattr(self.k, name)
            function.argtypes, function.restype = arguments, returns

    def open(self, rights, process_id):
        handle = self.k.OpenProcess(rights, False, process_id)
        return handle, 0 if handle else ctypes.get_last_error()

    def close(self, handle):
        self.k.CloseHandle(handle)

    def created(self, handle):
        values = [ctypes.c_uint64() for _ in range(4)]
        okay = self.k.GetProcessTimes(handle, *(ctypes.byref(value) for value in values))
        return (values[0].value, 0) if okay else (None, ctypes.get_last_error())

    def path(self, handle):
        value = ctypes.create_unicode_buffer(32768)
        size = ctypes.c_uint32(len(value))
        okay = self.k.QueryFullProcessImageNameW(handle, 0, value, ctypes.byref(size))
        return (value.value, 0) if okay else (None, ctypes.get_last_error())

    def module(self, process_id):
        snapshot = self.k.CreateToolhelp32Snapshot(8, process_id)
        if snapshot in (None, ctypes.c_void_p(-1).value):
            return None, ctypes.get_last_error()
        try:
            entry = self.Module()
            entry.dwSize = ctypes.sizeof(entry)
            if not self.k.Module32FirstW(snapshot, ctypes.byref(entry)):
                return None, ctypes.get_last_error()
            found = []
            for _ in range(MAX_MODULES):
                if entry.th32ProcessID != process_id:
                    return None, 87
                if entry.szModule.lower() == "newworld.exe":
                    if os.path.normcase(entry.szExePath) != os.path.normcase(str(CLIENT)):
                        return None, 87
                    found.append((entry.modBaseAddr, entry.modBaseSize))
                if not self.k.Module32NextW(snapshot, ctypes.byref(entry)):
                    error_code = ctypes.get_last_error()
                    return (found[0], 0) if error_code == 18 and len(found) == 1 else (None, error_code or 87)
            return None, 122
        finally:
            self.close(snapshot)

    def read(self, handle, address, count):
        value = ctypes.create_string_buffer(count)
        received = ctypes.c_size_t()
        okay = self.k.ReadProcessMemory(handle, address, value, count, ctypes.byref(received))
        if not okay:
            return None, ctypes.get_last_error()
        return (value.raw, 0) if received.value == count else (None, 299)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-directory", required=True, type=Path)
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    run, process_id, expected_start, bindings = load_owner(arguments.run_directory, root)
    output = run / "rep-readonly-observation.jsonl"
    with output.open("x", encoding="utf-8") as stream:
        def emit(state, **metadata):
            record = dict(schema=1, timestamp_utc=datetime.now(timezone.utc).isoformat(), state=state,
                          process_id=process_id, metadata=metadata)
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        emit("READONLY_OBSERVATION_START", source_sha256=digest(Path(__file__)),
             manifest_bindings=bindings, process_memory_writes=False, raw_dump=False,
             debug_attach=False, privilege_adjustment=False, current_client_version="1.400.6031.6004151")
        try:
            observe(WindowsReadOnly(), process_id, expected_start, emit,
                    active=lambda: not (run / "stop.request").exists())
        except Exception as exc:
            emit("READONLY_OBSERVATION_FAILED", exception_type=type(exc).__name__, raw_exception_saved=False)
            raise
        finally:
            emit("READONLY_OBSERVATION_STOPPED", handle_cleanup="CloseHandle attempted in finally; helper exit releases remaining handles",
                 no_system_cleanup_needed=True)


if __name__ == "__main__":
    main()
