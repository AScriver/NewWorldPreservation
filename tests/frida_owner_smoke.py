"""Explicit-only Windows process/job smoke; excluded from default pytest collection."""
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import frida_client_trial as trial


def test_windows_owner_inert_sleeper_lifecycle():
    if sys.platform != "win32":
        raise RuntimeError("Windows only")
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    owner = trial.WindowsOwner()
    try:
        created = owner.claim(sleeper.pid, Path(sys.executable).resolve())
        assert created > 0 and owner.assigned and not owner.exited()
    finally:
        try:
            owner.close()
        finally:
            if sleeper.poll() is None:
                sleeper.terminate()
            sleeper.wait(timeout=5)
    assert sleeper.returncode is not None
