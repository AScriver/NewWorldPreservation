"""Exercise the real guarded script against synthetic hosts files only."""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = Path(r"C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1")
ENDPOINT = b"d2c74t4zimux3r.cloudfront.net"


@pytest.fixture
def target():
    scratch = ROOT / ".scratch"
    scratch.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="hosts-test-", dir=scratch))
    hosts = directory / "hosts"
    journal = directory / "journal"
    yield hosts, journal
    assert directory.parent == scratch and directory.name.startswith("hosts-test-")
    shutil.rmtree(directory)


def invoke(action, target, success=True, profile="BootstrapOnly"):
    hosts, journal = target
    # All mutations remain behind the full parser/automatic-variable validator.
    expression = "& $args[0] -Path $args[1] -Execute -ArgumentList @('-Action',$args[2],'-JournalDirectory',$args[3],'-HostsPath',$args[4],'-EndpointProfile',$args[5])"
    script = ROOT / ".scratch" / "hosts-test-invoke.ps1"
    # No shared ports/processes/services; this stable wrapper contains no fixture data.
    script.write_text(expression, encoding="utf-8")
    result = subprocess.run([
        "pwsh", "-NoProfile", "-NonInteractive", "-File", str(script), str(WRAPPER),
        str(ROOT / "scripts/Set-ConnectivityHosts.ps1"), action, str(journal), str(hosts), profile
    ], capture_output=True, text=True, timeout=20)
    if success:
        assert result.returncode == 0, result.stdout + result.stderr
    else:
        assert result.returncode != 0
    return result


@pytest.mark.parametrize("original", [b"", b"127.0.0.1 localhost", b"\xef\xbb\xbf# original\r\n127.0.0.1 localhost\r\n"])
def test_apply_idempotent_restore_byte_exact(target, original):
    hosts, journal = target
    hosts.write_bytes(original)
    invoke("Prepare", target)
    assert hosts.read_bytes() == original
    invoke("Apply", target)
    applied = hosts.read_bytes()
    assert applied.startswith(original) and applied.count(ENDPOINT) == 2
    invoke("Apply", target)
    assert hosts.read_bytes() == applied
    invoke("Restore", target)
    invoke("Restore", target)
    assert hosts.read_bytes() == original
    events = [json.loads(line) for line in (journal / "events.jsonl").read_text().splitlines()]
    assert all(event["timestamp_utc"] for event in events)
    assert events[-1]["state"] == "HOSTS_REDIRECT_ALREADY_RESTORED"


def test_refuses_changed_target_on_apply(target):
    hosts, _ = target
    hosts.write_bytes(b"# original\n")
    invoke("Prepare", target)
    hosts.write_bytes(b"# concurrent\n")
    invoke("Apply", target, success=False)
    assert hosts.read_bytes() == b"# concurrent\n"


def test_restore_preserves_concurrent_unrelated_edits(target):
    hosts, _ = target
    original = b"# original\r\n"
    hosts.write_bytes(original)
    invoke("Prepare", target)
    invoke("Apply", target)
    hosts.write_bytes(hosts.read_bytes() + b"192.0.2.1 unrelated.example\r\n")
    invoke("Restore", target)
    assert hosts.read_bytes() == original + b"192.0.2.1 unrelated.example\r\n"


def test_refuses_conflicting_mapping_and_ambiguous_cleanup(target):
    hosts, journal = target
    original = b"192.0.2.1 " + ENDPOINT + b"\n"
    hosts.write_bytes(original)
    invoke("Prepare", target, success=False)
    assert hosts.read_bytes() == original and not journal.exists()
    hosts.write_bytes(b"# original\n")
    invoke("Prepare", target)
    invoke("Apply", target)
    applied = hosts.read_bytes()
    hosts.write_bytes(applied + applied[len(b"# original\n"):])
    invoke("Restore", target, success=False)
    assert hosts.read_bytes() == applied + applied[len(b"# original\n"):]


def test_token_profile_is_explicit_complete_and_restores_unrelated_edits(target):
    hosts, _ = target
    original = b"# original\n"
    hosts.write_bytes(original)
    invoke("Prepare", target, profile="TokenServices")
    invoke("Apply", target, success=False)  # Wrong profile cannot use that journal.
    assert hosts.read_bytes() == original
    invoke("Apply", target, profile="TokenServices")
    applied = hosts.read_bytes()
    for name in (ENDPOINT, b"tokenservice.amazongames.com", b"prod.newworld.com"):
        assert applied.count(name) == 2
    invoke("Apply", target, profile="TokenServices")
    assert hosts.read_bytes() == applied
    unrelated = b"192.0.2.1 unrelated.example\n"
    hosts.write_bytes(applied + unrelated)
    invoke("Restore", target, profile="TokenServices")
    assert hosts.read_bytes() == original + unrelated


def test_token_profile_refuses_existing_token_host_mapping(target):
    hosts, journal = target
    original = b"192.0.2.1 tokenservice.amazongames.com\n"
    hosts.write_bytes(original)
    invoke("Prepare", target, success=False, profile="TokenServices")
    assert hosts.read_bytes() == original and not journal.exists()


def test_tampered_endpoint_list_cannot_expand_mutation_scope(target):
    hosts, journal = target
    hosts.write_bytes(b"# original\n")
    invoke("Prepare", target, profile="TokenServices")
    plan_path = journal / "plan.json"
    plan = json.loads(plan_path.read_text())
    plan["hostnames"].append("arbitrary.invalid")
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    invoke("Apply", target, success=False, profile="TokenServices")
    assert hosts.read_bytes() == b"# original\n"
