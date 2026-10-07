"""User-stop lifetime for existing private trial processes; no game inspection."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import re
import stat

PRIVATE = Path(__file__).resolve().parents[1] / "private" / "frida-trials"
CONTROLLER_PID_ENV = "NWP_TRIAL_CONTROLLER_PID"
CONTROLLER_CREATED_ENV = "NWP_TRIAL_CONTROLLER_CREATED_FILETIME"


def add_lifetime_options(parser, *, timed_flag="--duration", dest="duration"):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(timed_flag, dest=dest, type=int)
    group.add_argument("--until-stopped", type=Path, metavar="STOP_FILE",
                       help="no session deadline; stop on the owned run's stop.request or controller exit")


def resolve_lifetime_options(parser, options, *, default_seconds, maximum=600, dest="duration"):
    seconds = getattr(options, dest)
    if options.until_stopped is None:
        seconds = default_seconds if seconds is None else seconds
        if not 1 <= seconds <= maximum:
            parser.error(f"{dest} must be 1..{maximum}")
    setattr(options, dest, seconds)


def admit_stop_file(path: Path, *, private: Path = PRIVATE) -> Path:
    """Only the selected direct private run may receive the durable stop signal."""
    path = Path(path).absolute()
    run = path.parent
    private = private.resolve(strict=True)
    if (path.name != "stop.request" or run.parent.resolve(strict=True) != private or
            not re.fullmatch(r"run-[A-Za-z0-9_-]+", run.name)):
        raise ValueError("stop file must be one direct private/frida-trials/run-*/stop.request")
    for component in (run, path):
        try:
            details = component.lstat()
        except FileNotFoundError:
            if component == run:
                raise
            continue
        if (component.is_symlink() or getattr(details, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)):
            raise ValueError("stop path must not redirect")
    if path.exists():
        raise ValueError("stop already requested")
    return run.resolve(strict=True) / "stop.request"


class WindowsController:
    """A retained, creation-verified controller handle cannot follow PID reuse."""

    def __init__(self, process_id: int, created_filetime: int, *, api=None):
        if (type(process_id) is not int or not 1 <= process_id <= 0xffffffff or
                type(created_filetime) is not int or not 1 <= created_filetime <= 0xffffffffffffffff):
            raise ValueError("exact controller PID and creation FILETIME required")
        if api is None:
            if os.name != "nt":
                raise RuntimeError("user-stop controller ownership is Windows only")
            api = ctypes.WinDLL("kernel32", use_last_error=True)
            api.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
            api.OpenProcess.restype = wintypes.HANDLE
            api.GetProcessTimes.argtypes = (wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                           ctypes.c_void_p, ctypes.c_void_p)
            api.GetProcessTimes.restype = wintypes.BOOL
            api.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
            api.WaitForSingleObject.restype = wintypes.DWORD
            api.CloseHandle.argtypes = (wintypes.HANDLE,)
            api.CloseHandle.restype = wintypes.BOOL
        self.api = api
        self.handle = api.OpenProcess(0x00100000 | 0x1000, False, process_id)
        if not self.handle:
            raise OSError("controller handle unavailable")
        try:
            times = [wintypes.FILETIME() for _ in range(4)]
            if not api.GetProcessTimes(self.handle, *(ctypes.byref(value) for value in times)):
                raise OSError("controller creation identity unavailable")
            actual = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
            if actual != created_filetime or self.exited():
                raise ValueError("controller creation identity mismatch or exited controller")
        except BaseException:
            self.close()
            raise

    @classmethod
    def from_environment(cls):
        values = [os.environ.get(key, "") for key in (CONTROLLER_PID_ENV, CONTROLLER_CREATED_ENV)]
        if any(not re.fullmatch(r"[0-9]{1,20}", value) for value in values):
            raise ValueError("user-stop mode requires the owning controller identity")
        return cls(*(int(value) for value in values))

    def exited(self) -> bool:
        result = self.api.WaitForSingleObject(self.handle, 0)
        if result not in (0, 258):
            raise OSError("controller liveness unavailable")
        return result == 0

    def close(self):
        if self.handle:
            handle, self.handle = self.handle, None
            if not self.api.CloseHandle(handle):
                raise OSError("controller handle close failed")


class UserStop:
    def __init__(self, path: Path, *, controller=None, private: Path = PRIVATE):
        self.path = admit_stop_file(path, private=private)
        self.controller = controller if controller is not None else WindowsController.from_environment()
        self.reason = None

    def is_set(self) -> bool:
        if self.reason is None:
            if self.path.exists() or self.path.is_symlink():
                self.reason = "stop_requested"
            else:
                try:
                    if self.controller.exited():
                        self.reason = "controller_exited"
                except OSError:
                    self.reason = "controller_unavailable"
        return self.reason is not None

    def close(self):
        self.controller.close()

    def __enter__(self):
        return self

    def __exit__(self, *_exception):
        self.close()
