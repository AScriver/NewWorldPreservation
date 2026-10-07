"""Bounded, owned-copy Frida trial. Never run from offline validation.

The caller owns isolation, firewall, bootstrap and any private DTLS endpoint.
This runner only spawns its admitted staged executable and loads the pinned,
unmodified upstream trust hook plus an original observation listener.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import threading
import time

from private_trial_lifetime import UserStop, add_lifetime_options, resolve_lifetime_options

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "private" / "frida-trials"
HOOK = ROOT / "research" / "upstream" / "first-light" / "tools" / "client-hooks" / "frida_dtls_trust_patch.js"
OBSERVER = ROOT / "scripts" / "frida_trial_observer.js"
EXE_SHA256 = "8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e"
HOOK_SHA256 = "42ebaa8fe9804588a5c41a26cd1d2bbf7c0492845a114dfbb4e15c16d236811d"
RVA = 0x5DCE750
CONTEXT_GATE_TARGETS = (
    ("self_identification", 0x6454C00, 0x990),
    ("level_info", 0x6446800, 0x990),
    ("context_load", 0x6448CD0, 0),
)
CONTEXT_GATE_FLAGS = (
    "self_identified", "activation_latched", "context_ready", "level_pending",
    "jav_context_present", "client_sdk_present", "game_present",
)
CONTEXT_GATE_EVENT_LIMIT = 96
PROCESS_TERMINATE = 0x0001
PROCESS_SET_QUOTA = 0x0100
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SYNCHRONIZE = 0x00100000
JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def file_offset_for_rva(data: bytes, rva: int) -> int:
    if data[:2] != b"MZ":
        raise ValueError("not a PE image")
    pe = int.from_bytes(data[0x3C:0x40], "little")
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("invalid PE header")
    count = int.from_bytes(data[pe + 6:pe + 8], "little")
    optional_size = int.from_bytes(data[pe + 20:pe + 22], "little")
    sections = pe + 24 + optional_size
    for index in range(count):
        section = sections + index * 40
        virtual_size = int.from_bytes(data[section + 8:section + 12], "little")
        virtual_address = int.from_bytes(data[section + 12:section + 16], "little")
        raw_size = int.from_bytes(data[section + 16:section + 20], "little")
        raw_pointer = int.from_bytes(data[section + 20:section + 24], "little")
        if virtual_address <= rva < virtual_address + min(virtual_size, raw_size):
            return raw_pointer + rva - virtual_address
    raise ValueError("initializer RVA not in a file-backed section")


def selected_copy(run: Path, exe: Path, admission: Path) -> tuple[Path, Path]:
    """Resolve the one physical copy named by this run's admission file."""
    run = run.resolve(strict=True)
    private = PRIVATE.resolve(strict=True)
    if run.parent != private or not re.fullmatch(r"run-[A-Za-z0-9_-]+", run.name):
        raise ValueError("run must be one direct ignored private/frida-trials/run-* directory")
    admission_real = (run / "admission.json").resolve(strict=True)
    if admission_real.parent != run or admission.resolve(strict=True) != admission_real:
        raise ValueError("admission must be this run's admission.json")
    if (run / "stop.request").exists():
        raise ValueError("stop already requested")
    metadata = json.loads(admission.read_text(encoding="utf-8"))
    source_name = metadata.get("staged_copy_run")
    if source_name is None:
        source_run = run
    else:
        if not isinstance(source_name, str) or not re.fullmatch(r"run-[A-Za-z0-9_-]+", source_name):
            raise ValueError("staged_copy_run must name one direct private run")
        source_run = private / source_name
        if source_run == run or source_run.resolve(strict=True).parent != private:
            raise ValueError("staged_copy_run must be a different direct private run")
        if not (source_run / "stop.request").is_file():
            raise ValueError("source copy run is still live: stop.request missing")
        cleanup_path = source_run / "cleanup-reconciled.json"
        if not cleanup_path.is_file():
            raise ValueError("source copy cleanup receipt missing")
        cleanup = json.loads(cleanup_path.read_text(encoding="utf-8"))
        required = ("game_absent", "ports_closed", "firewall_rules_absent", "hosts_byte_exact")
        if any(cleanup.get(field) is not True for field in required):
            raise ValueError("source copy cleanup is not reconciled")
    staged_path = source_run / "client" / "Bin64" / "NewWorld.exe"
    for component in (source_run, source_run / "client", source_run / "client" / "Bin64", staged_path):
        details = component.lstat()
        if component.is_symlink() or (getattr(details, "st_file_attributes", 0) &
                                      getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)):
            raise ValueError("source copy path contains a symlink or junction")
    staged_real = staged_path.resolve(strict=True)
    if source_run.resolve(strict=True) not in staged_real.parents or exe.resolve(strict=True) != staged_real:
        raise ValueError("staged executable path mismatch")
    return staged_real, source_run


@contextmanager
def hold_copy_use(source_run: Path):
    """A nonblocking byte-range lock prevents concurrent trials of one copy."""
    import msvcrt

    lock_path = source_run / "copy-use.lock"
    if lock_path.is_symlink():
        raise ValueError("copy-use.lock must not be a symlink")
    with lock_path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        try:
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as error:
            raise RuntimeError("selected client copy is already in use") from error
        try:
            yield
        finally:
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def admit(run: Path, exe: Path, admission: Path, *, context_gate_observer=False) -> dict:
    staged_real, _ = selected_copy(run, exe, admission)
    if sha256(staged_real) != EXE_SHA256 or sha256(HOOK) != HOOK_SHA256:
        raise ValueError("executable or upstream hook hash mismatch")
    metadata = json.loads(admission.read_text(encoding="utf-8"))
    if metadata.get("exe_sha256") != EXE_SHA256 or metadata.get("rva") != RVA:
        raise ValueError("admission hash/RVA mismatch")
    entry_hex = metadata.get("expected_entry_hex", "")
    if not isinstance(entry_hex, str) or not re.fullmatch(r"[0-9a-fA-F]{32,128}", entry_hex) or len(entry_hex) % 2:
        raise ValueError("expected_entry_hex must contain 16-64 bytes")
    expected = bytes.fromhex(entry_hex)
    image = staged_real.read_bytes()
    offset = file_offset_for_rva(image, RVA)
    if image[offset:offset + len(expected)] != expected:
        raise ValueError("disk initializer entry bytes mismatch")
    result = {"path": str(staged_real), "hex": entry_hex.lower(), "bytes": list(expected)}
    if context_gate_observer:
        targets = []
        for site, rva, adjustment in CONTEXT_GATE_TARGETS:
            offset = file_offset_for_rva(image, rva)
            prefix = image[offset:offset + 16]
            if len(prefix) != 16:
                raise ValueError("context-gate entry bytes unavailable")
            targets.append({"site": site, "rva": rva, "adjustment": adjustment,
                            "hex": prefix.hex(), "bytes": list(prefix)})
        result["context_gate_targets"] = targets
    return result


def context_gate_metadata(payload: dict) -> dict | None:
    """Accept only fixed site/phase enums, ephemeral tags and boolean state."""
    keys = {"type", "site", "phase", "port_tag", *CONTEXT_GATE_FLAGS}
    if set(payload) != keys or payload.get("type") != "context-gate":
        return None
    if (type(payload["site"]) is not str or
            payload["site"] not in {site for site, _, _ in CONTEXT_GATE_TARGETS}):
        return None
    if type(payload["phase"]) is not str or payload["phase"] not in ("entry", "return"):
        return None
    tag = payload["port_tag"]
    if type(tag) is not int or not 1 <= tag <= 16:
        return None
    if any(payload[key] is not None and type(payload[key]) is not bool
           for key in CONTEXT_GATE_FLAGS):
        return None
    return {key: payload[key] for key in ("site", "phase", "port_tag", *CONTEXT_GATE_FLAGS)}


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD)]


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in
                ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                 "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo", IO_COUNTERS), ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t)]


class WindowsOwner:
    """The job and process handles remain live from suspended spawn through cleanup."""

    def __init__(self):
        if os.name != "nt":
            raise RuntimeError("Windows only")
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        self.api.OpenProcess.restype = wintypes.HANDLE
        self.api.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        self.api.CreateJobObjectW.restype = wintypes.HANDLE
        self.api.SetInformationJobObject.argtypes = (wintypes.HANDLE, wintypes.INT, ctypes.c_void_p, wintypes.DWORD)
        self.api.SetInformationJobObject.restype = wintypes.BOOL
        self.api.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        self.api.AssignProcessToJobObject.restype = wintypes.BOOL
        self.api.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
        self.api.TerminateJobObject.restype = wintypes.BOOL
        self.api.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
        self.api.TerminateProcess.restype = wintypes.BOOL
        self.api.GetProcessTimes.argtypes = (wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                             ctypes.c_void_p, ctypes.c_void_p)
        self.api.GetProcessTimes.restype = wintypes.BOOL
        self.api.QueryFullProcessImageNameW.argtypes = (wintypes.HANDLE, wintypes.DWORD,
                                                        wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD))
        self.api.QueryFullProcessImageNameW.restype = wintypes.BOOL
        self.api.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        self.api.WaitForSingleObject.restype = wintypes.DWORD
        self.api.CloseHandle.argtypes = (wintypes.HANDLE,)
        self.api.CloseHandle.restype = wintypes.BOOL
        self.process = None
        self.job = None
        self.assigned = False
        self.created = None
        self._lock = threading.RLock()

    def _check(self, result, operation):
        if not result:
            raise OSError(ctypes.get_last_error(), operation)
        return result

    def claim(self, pid: int, exe: Path) -> int:
        self.process = self._check(self.api.OpenProcess(PROCESS_TERMINATE | PROCESS_SET_QUOTA |
                                                       PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE,
                                                       False, pid), "OpenProcess")
        creation = wintypes.FILETIME()
        exit_time, kernel_time, user_time = (wintypes.FILETIME() for _ in range(3))
        self._check(self.api.GetProcessTimes(self.process, ctypes.byref(creation), ctypes.byref(exit_time),
                                             ctypes.byref(kernel_time), ctypes.byref(user_time)), "GetProcessTimes")
        self.created = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        size = wintypes.DWORD(32768)
        path = ctypes.create_unicode_buffer(size.value)
        self._check(self.api.QueryFullProcessImageNameW(self.process, 0, path, ctypes.byref(size)),
                    "QueryFullProcessImageNameW")
        if os.path.normcase(path.value) != os.path.normcase(str(exe)):
            raise ValueError("spawned process image path mismatch")
        self.job = self._check(self.api.CreateJobObjectW(None, None), "CreateJobObjectW")
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_ACTIVE_PROCESS
        info.BasicLimitInformation.ActiveProcessLimit = 1
        self._check(self.api.SetInformationJobObject(self.job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                                                     ctypes.byref(info), ctypes.sizeof(info)), "SetInformationJobObject")
        self._check(self.api.AssignProcessToJobObject(self.job, self.process), "AssignProcessToJobObject")
        self.assigned = True
        return self.created

    def exited(self) -> bool:
        if self.process is None:
            return False
        result = self.api.WaitForSingleObject(self.process, 0)
        if result == 0:
            return True
        if result == 258:  # WAIT_TIMEOUT
            return False
        raise OSError(ctypes.get_last_error(), "WaitForSingleObject(process)")

    def close(self):
        with self._lock:
            failure = None
            try:
                if self.job and self.assigned:
                    if not self.api.TerminateJobObject(self.job, 1):
                        failure = OSError(ctypes.get_last_error(), "TerminateJobObject")
                elif self.process:
                    try:
                        running = not self.exited()
                    except Exception as error:
                        failure = error
                        running = True
                    if running and not self.api.TerminateProcess(self.process, 1) and failure is None:
                        failure = OSError(ctypes.get_last_error(), "TerminateProcess")
            finally:
                if self.job:
                    if not self.api.CloseHandle(self.job) and failure is None:
                        failure = OSError(ctypes.get_last_error(), "CloseHandle(job)")
                    self.job = None
                if self.process:
                    if self.api.WaitForSingleObject(self.process, 5000) != 0 and failure is None:
                        failure = RuntimeError("owned process did not exit within five seconds")
                    if not self.api.CloseHandle(self.process) and failure is None:
                        failure = OSError(ctypes.get_last_error(), "CloseHandle(process)")
                    self.process = None
            if failure is not None:
                raise failure


def execute(device, owner, run: Path, exe: Path, admission: dict, seconds: int | None, record,
            *, stop=None) -> None:
    """Injectable Frida/device and owner facades permit failure tests without a client."""
    if seconds is None and stop is None:
        raise ValueError("user-stop lifetime requires an owned stop guard")
    pid = None
    session = None
    opened_process = False
    state = {"observer": None, "upstream": None, "child_error": None, "detached": None,
             "cleanup_started": False, "context_gate_events": 0}
    condition = threading.Condition()

    def on_child(child):
        if pid is None or child.parent_pid != pid:
            return  # Device events for unrelated processes are never ours.
        try:
            device.kill(child.pid)  # Frida child gating holds it suspended.
            record("child_rejected", pid=child.pid)
        except Exception as error:
            state["child_error"] = type(error).__name__
            try:
                record("child_rejection_failed", error=state["child_error"])
            finally:
                owner.close()  # Fail closed even if the main loop is waiting.

    def on_message(source):
        def receive(message, _data):
            payload = message.get("payload") if message.get("type") == "send" else None
            if message.get("type") == "error":
                with condition:
                    state[source] = False
                    condition.notify_all()
                record("script_error", script=source)
            elif isinstance(payload, dict):
                kind = payload.get("type")
                if source == "observer" and kind == "observer-status":
                    with condition:
                        state[source] = payload.get("ok") is True
                        condition.notify_all()
                    record("observer_status", ok=state[source], observer_event=payload.get("event"),
                           error=payload.get("error"))
                elif source == "upstream" and kind == "status":
                    with condition:
                        state[source] = payload.get("ok") is True
                        condition.notify_all()
                    record("upstream_hook_status", installed=state[source])
                elif source == "upstream" and kind == "log":
                    upstream_text = payload.get("text")
                    if isinstance(upstream_text, str):
                        if upstream_text.startswith("[trust-bypass] zeroed verifyField ctx="):
                            record("trust_write_result", success=True)
                        elif upstream_text.startswith("[trust-bypass] FAILED to null verifyField ctx="):
                            record("trust_write_result", success=False)
                elif source == "observer" and kind == "hook-invocation":
                    record("hook_invocation", before_read=payload.get("before_read"),
                           before_nonzero=payload.get("before_nonzero"),
                           after_zero_at_return=payload.get("after_zero_at_return"),
                           retval_hex=payload.get("retval_hex"),
                           retval_zero=payload.get("retval_zero"))
                elif (source == "observer" and kind == "context-gate" and
                      "context_gate_targets" in admission):
                    fields = context_gate_metadata(payload)
                    if fields is not None and state["context_gate_events"] < CONTEXT_GATE_EVENT_LIMIT:
                        state["context_gate_events"] += 1
                        record("context_gate", **fields)
        return receive

    def on_detached(reason, _crash):
        if state["cleanup_started"]:
            return
        state["detached"] = reason
        try:
            record("session_detached", reason=reason)
        finally:
            owner.close()

    def wait_status(source):
        with condition:
            if state[source] is None:
                condition.wait_for(lambda: state[source] is not None or state["child_error"], timeout=10)
        if state[source] is not True or state["child_error"]:
            raise RuntimeError(source + " script admission/registration failed")

    try:
        device.on("child-added", on_child)
        environment = {"SteamAppId": "1063730", "SteamGameId": "1063730"}
        if (run / "stop.request").exists() or (stop is not None and stop.is_set()):
            raise RuntimeError("stop requested before spawn")
        pid = device.spawn(str(exe), env=environment, cwd=str(exe.parent))
        record("spawn_suspended", pid=pid)
        try:
            created = owner.claim(pid, exe)
        finally:
            opened_process = owner.process is not None
        record("owner_claimed", pid=pid, creation_filetime=created, job_active_limit=1)
        if stop is not None and stop.is_set():
            raise RuntimeError("stop requested before attach")
        if owner.exited():
            raise RuntimeError("spawned process exited before attach")
        session = device.attach(pid)
        session.on("detached", on_detached)
        record("attached")
        session.enable_child_gating()
        record("child_gating_enabled")
        observer_source = OBSERVER.read_text(encoding="utf-8").replace("__ADMISSION__", json.dumps(admission))
        observer = session.create_script(observer_source, name="bounded-trial-observer")
        observer.on("message", on_message("observer"))
        observer.load()
        wait_status("observer")
        upstream = session.create_script(HOOK.read_text(encoding="utf-8"), name="pinned-upstream-trust")
        upstream.on("message", on_message("upstream"))
        upstream.load()
        wait_status("upstream")
        if ((run / "stop.request").exists() or (stop is not None and stop.is_set()) or
                state["child_error"] or state["detached"] or
                state["observer"] is not True or state["upstream"] is not True):
            raise RuntimeError("stop/child/session/script failure before resume")
        if owner.exited():
            raise RuntimeError("spawned process exited before resume")
        device.resume(pid)
        record("resumed")
        deadline = time.monotonic() + seconds if seconds is not None else None
        while deadline is None or time.monotonic() < deadline:
            if state["child_error"]:
                raise RuntimeError("child rejection failed")
            if state["observer"] is not True or state["upstream"] is not True:
                raise RuntimeError("Frida script failed after resume")
            if state["detached"]:
                if state["detached"] == "process-terminated":
                    record("client_exited", via="frida_session")
                    break
                raise RuntimeError("Frida session detached after resume: " + state["detached"])
            if (stop is not None and stop.is_set()) or (run / "stop.request").exists():
                record("stop_requested", reason=getattr(stop, "reason", None) or "stop_requested")
                break
            if owner.exited():
                record("client_exited")
                break
            time.sleep(0.25)
        else:
            record("lifetime_expired")
    finally:
        # Job termination, not Frida detach, is the cleanup boundary.
        state["cleanup_started"] = True
        try:
            owner.close()
        finally:
            try:
                if pid is not None and not opened_process:
                    device.kill(pid)  # newly spawned, still suspended; handle claim failed
            finally:
                if session is not None:
                    try:
                        session.detach()
                    except Exception:
                        pass
                try:
                    device.off("child-added", on_child)
                except Exception:
                    pass


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    add_lifetime_options(parser, timed_flag="--seconds", dest="seconds")
    parser.add_argument("--context-gate-observer", action="store_true",
                        help="observe only three pinned callback/gate sites and boolean state")
    args = parser.parse_args(argv)
    resolve_lifetime_options(parser, args, default_seconds=120, maximum=300, dest="seconds")
    run = args.run_dir.resolve(strict=True)
    private = PRIVATE.resolve(strict=True)
    if run.parent != private or not re.fullmatch(r"run-[A-Za-z0-9_-]+", run.name):
        parser.error("run must be one direct ignored private/frida-trials/run-* directory")
    lock_path = run / "runner.lock"
    if lock_path.is_symlink():
        parser.error("runner.lock must be a regular file in the run directory")
    # The controller's exclusive open cannot succeed while this handle is live.
    # Keep it through every admission, spawn, publication, and cleanup path.
    with ExitStack() as resources:
        resources.enter_context(lock_path.open("a+b"))
        stop = None
        if args.until_stopped is not None:
            if args.until_stopped.absolute() != run / "stop.request":
                parser.error("user-stop file must belong to the selected run")
            stop = resources.enter_context(UserStop(args.until_stopped))
        staged_real, source_run = selected_copy(run, args.exe, args.admission)
        with hold_copy_use(source_run):
            admission = admit(run, staged_real, args.admission,
                              context_gate_observer=args.context_gate_observer)
            events = run / "frida-events.jsonl"
            with events.open("x", encoding="utf-8") as stream:
                event_lock = threading.Lock()

                def record(event, **fields):
                    with event_lock:
                        stream.write(json.dumps({"event": event, "time_ns": time.time_ns(), **fields}) + "\n")
                        stream.flush()

                try:
                    record("selected_copy", source_run=source_run.name)
                    import frida  # Only load for an explicitly admitted live trial.
                    execute(frida.get_local_device(), WindowsOwner(), run, staged_real,
                            admission, args.seconds, record, stop=stop)
                    record("trial_complete")
                    return 0
                except Exception as error:
                    record("trial_failed", error_type=type(error).__name__, error=str(error)[:240])
                    return 1


if __name__ == "__main__":
    sys.exit(main())
