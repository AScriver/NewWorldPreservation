"""Public Git-object checks use isolated repositories, never a client or endpoint."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish_hygiene as hygiene


def git(repo, *arguments, input=None):
    result = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *arguments],
                            input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
                            timeout=15)
    return result.stdout


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.name", "Synthetic fixture")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "core.autocrlf", "false")
    return tmp_path


def stage(repo, path, data=b"original synthetic control\n"):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    git(repo, "add", "--", path)
    return target


def index_entry(repo, path, data=b"original synthetic control\n", mode="100644", oid=None):
    oid = oid or git(repo, "hash-object", "-w", "--stdin", input=data).strip().decode()
    git(repo, "update-index", "--add", "--cacheinfo", f"{mode},{oid},{path}")
    return oid


def rules(report):
    return {item["rule"] for item in report["findings"]}


def cli(repo, *arguments):
    result = subprocess.run([sys.executable, "-B", str(Path(hygiene.__file__)), "--repo", str(repo), *arguments],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    return result, json.loads(result.stdout)


def test_clean_tree_allows_source_metadata_and_original_synthetic_fixtures(repo):
    stage(repo, "scripts/control.py", b"address = 0x146b70af0\n# FUN_123; DAT_456; SHA256: 8654f01d\n")
    stage(repo, "tests/fixtures/control.bin", b"original synthetic fixture\x00\x01")
    stage(repo, ".env.example", b"SERVICE_TOKEN=replace-me\n")
    stage(repo, "docs/space and \u03c0.md")
    result, report = cli(repo)
    assert result.returncode == 0 and report["status"] == "passed"
    assert report["complete"] and report["files"] == report["blobsScanned"] == 4
    assert not result.stderr


@pytest.mark.parametrize("path", [
    ".scratch/control.txt", "private/control.txt", ".venv/control.txt", "research/upstream/control.txt",
    "PRIVATE/control.txt", "nested/private/control.txt", ".env", "nested/.env.local",
    "capture.pcap", "CAPTURE.PCAPNG", "trust.pem", "secret.key", "client.exe", "client.dll",
    "assets.pak", "game.xex", "archive.zip", "archive.7z", "archive.rar",
])
def test_forbidden_candidate_paths_reject_without_blob_reads(repo, path):
    index_entry(repo, path, b"unpublished synthetic content")
    report = hygiene.scan(repo)
    assert report["status"] == "rejected" and report["complete"]
    assert report["blobsScanned"] == report["bytesScanned"] == 0
    assert report["findings"][0]["path"] == path


@pytest.mark.parametrize("blob, expected", [
    (b"-----BEGIN " + b"PRIVATE KEY-----\nsynthetic\n", "private-key"),
    (b"-----BEGIN " + b"RSA PRIVATE KEY-----\nsynthetic\n", "private-key"),
    (b"AKIA" + b"A" * 16, "credential-token"),
    (b"ASIA" + b"B" * 16, "credential-token"),
    (b"ghp_" + b"A" * 36, "credential-token"),
    (b"github_pat_" + b"A" * 70, "credential-token"),
    (b"MZsynthetic", "binary-artifact"),
    (b"\x7fELFsynthetic", "binary-artifact"),
    (b"PK\x03\x04synthetic", "binary-artifact"),
    (b"\xd4\xc3\xb2\xa1synthetic", "packet-capture"),
    (b"\x0a\x0d\x0d\x0asynthetic", "packet-capture"),
])
def test_signatures_reject_and_cli_never_emits_blob_contents(repo, blob, expected):
    stage(repo, "candidate.txt", blob)
    result, report = cli(repo)
    assert result.returncode == 1 and expected in rules(report)
    assert blob not in result.stdout and blob not in result.stderr
    assert report["blobsScanned"] == 1 and report["bytesScanned"] == len(blob)


def test_environment_example_does_not_exempt_credential_content(repo):
    stage(repo, ".env.example", b"TOKEN=" + b"ghp_" + b"A" * 36)
    assert "credential-token" in rules(hygiene.scan(repo))


@pytest.mark.parametrize("variation", ["exact", "changed-path", "changed-bytes"])
def test_reviewed_negative_marker_requires_the_exact_path_and_blob(repo, variation):
    fixture_path = "tests/test_rep_anchor_candidate.py"
    fixture = (Path(__file__).parent / "test_rep_anchor_candidate.py").read_bytes().replace(b"\r\n", b"\n")
    if variation == "changed-path":
        fixture_path = "tests/copied_marker.py"
    elif variation == "changed-bytes":
        fixture += b"\n# Any edit requires a new review.\n"
    stage(repo, fixture_path, fixture)
    report = hygiene.scan(repo)
    if variation == "exact":
        assert report["status"] == "passed"
        assert report["reviewedMarkers"] == [{"rule": "private-key", "path": fixture_path}]
    else:
        assert report["status"] == "rejected" and "private-key" in rules(report)
        assert report["reviewedMarkers"] == []


def test_staged_content_is_independent_of_working_files(repo):
    target = stage(repo, "control.txt")
    secret = b"ghp_" + b"A" * 36
    target.write_bytes(secret)
    assert hygiene.scan(repo)["status"] == "passed"
    git(repo, "add", "--", "control.txt")
    target.write_bytes(b"repaired only in working tree")
    assert hygiene.scan(repo)["status"] == "rejected"


def test_committed_mode_uses_pinned_head_not_staged_changes(repo):
    target = stage(repo, "control.txt")
    git(repo, "commit", "-qm", "fixture")
    expected_commit = git(repo, "rev-parse", "HEAD").strip().decode()
    target.write_bytes(b"ghp_" + b"A" * 36)
    git(repo, "add", "--", "control.txt")
    report = hygiene.scan(repo, "committed")
    assert report["status"] == "passed" and report["commit"] == expected_commit
    assert hygiene.scan(repo)["status"] == "rejected"


@pytest.mark.parametrize("mode, expected", [("120000", "symlink"), ("160000", "unsupported-mode")])
def test_symlinks_and_gitlinks_are_refused_without_target_access(repo, mode, expected):
    if mode == "160000":
        stage(repo, "ordinary.txt")
        git(repo, "commit", "-qm", "fixture")
        oid = git(repo, "rev-parse", "HEAD").strip().decode()
        git(repo, "rm", "--cached", "ordinary.txt")
    else:
        oid = git(repo, "hash-object", "-w", "--stdin", input=b"C:/private/never-read").strip().decode()
    index_entry(repo, "link", mode=mode, oid=oid)
    report = hygiene.scan(repo)
    assert expected in rules(report) and report["blobsScanned"] == 0


def test_renamed_unicode_paths_follow_the_index(repo):
    oid = index_entry(repo, "old name.txt", b"ghp_" + b"A" * 36)
    git(repo, "update-index", "--force-remove", "old name.txt")
    unusual_path = 'docs/\u03c0 renamed, spaces.txt'
    index_entry(repo, unusual_path, oid=oid)
    result, report = cli(repo)
    assert result.returncode == 1
    assert report["findings"] == [{"rule": "credential-token", "path": unusual_path}]
    assert len(result.stdout.splitlines()) == 1


def test_escaped_inventory_paths_are_parsed_and_reported_without_line_splitting(repo, monkeypatch, capsys):
    # Windows Git refuses these names. Model its NUL-delimited inventory bytes,
    # while retaining real Git object reads, to exercise the parser boundary.
    oid = index_entry(repo, "control.txt", b"ghp_" + b"A" * 36)
    unusual_path = 'docs/\u03c0 tab\tline\n"quoted".txt'
    raw = b"100644 " + oid.encode() + b" 0\t" + unusual_path.encode() + b"\0"
    original_git_output = hygiene.git_output

    def modeled_inventory(root, arguments, limit):
        if arguments[0] == "ls-files":
            return raw
        return original_git_output(root, arguments, limit)

    monkeypatch.setattr(hygiene, "git_output", modeled_inventory)
    assert hygiene.main(["--repo", str(repo)]) == 1
    output = capsys.readouterr()
    assert json.loads(output.out)["findings"] == [{"rule": "credential-token", "path": unusual_path}]
    assert len(output.out.splitlines()) == 1 and not output.err


def test_known_token_in_candidate_path_is_redacted(repo):
    sensitive_name = "ghp_" + "A" * 36
    index_entry(repo, f"private/{sensitive_name}.txt")
    result, report = cli(repo)
    assert result.returncode == 1
    assert report["findings"] == [{"rule": "forbidden-path", "path": "[redacted-path]"}]
    assert sensitive_name.encode() not in result.stdout + result.stderr


def test_missing_object_never_passes_and_git_stderr_is_redacted(repo):
    index_entry(repo, "control.txt", oid="f" * 40)
    result, report = cli(repo)
    assert result.returncode == 2 and report["status"] == "incomplete"
    assert "git-command" in rules(report) and not result.stderr


def test_missing_repository_does_not_echo_sensitive_git_error_path(tmp_path):
    sensitive_name = "ghp_" + "A" * 36
    result, report = cli(tmp_path / sensitive_name)
    assert result.returncode == 2 and report["status"] == "incomplete"
    assert sensitive_name.encode() not in result.stdout + result.stderr


@pytest.mark.parametrize("mode", ["staged", "committed"])
def test_subdirectory_is_not_silently_scanned_as_the_whole_repository(repo, mode):
    stage(repo, "docs/control.txt")
    git(repo, "commit", "-qm", "fixture")
    assert "repository-root" in rules(hygiene.scan(repo / "docs", mode))


def test_unborn_committed_tree_is_incomplete_but_empty_index_is_valid(repo):
    assert hygiene.scan(repo)["status"] == "passed"
    assert hygiene.scan(repo, "committed")["status"] == "incomplete"


@pytest.mark.parametrize("limits, expected", [
    ({"max_file_bytes": 3}, "file-byte-cap"),
    ({"max_total_bytes": 5}, "total-byte-cap"),
    ({"max_files": 1}, "file-count-cap"),
])
def test_caps_fail_closed_before_reading_beyond_budget(repo, limits, expected):
    stage(repo, "a.txt", b"abcd")
    stage(repo, "b.txt", b"efgh")
    report = hygiene.scan(repo, **limits)
    assert not report["complete"] and expected in rules(report)
    assert report["bytesScanned"] <= limits.get("max_total_bytes", 8)


def test_inventory_and_finding_caps_do_not_claim_a_complete_scan(repo, monkeypatch):
    stage(repo, "control.txt")
    monkeypatch.setattr(hygiene, "MAX_INVENTORY_BYTES", 8)
    assert "git-output-cap" in rules(hygiene.scan(repo))
    monkeypatch.setattr(hygiene, "MAX_INVENTORY_BYTES", 2 * 1024 * 1024)
    monkeypatch.setattr(hygiene, "MAX_FINDINGS", 3)
    for number in range(4):
        index_entry(repo, f"private/{number}.txt")
    report = hygiene.scan(repo)
    assert "finding-cap" in rules(report) and not report["complete"]
    assert len(report["findings"]) == 3


@pytest.mark.parametrize("raw", [
    b"missing-terminator", b"100644 " + b"a" * 40 + b" 0 path\0",
    b"100644 bad-oid 0\tpath\0", b"100644 " + b"a" * 40 + b" 0 extra\tpath\0",
])
def test_malformed_inventory_cannot_pass(repo, monkeypatch, raw):
    original_git_output = hygiene.git_output

    def malformed_inventory(root, arguments, limit):
        return raw if arguments[0] == "ls-files" else original_git_output(root, arguments, limit)

    monkeypatch.setattr(hygiene, "git_output", malformed_inventory)
    report = hygiene.scan(repo)
    assert not report["complete"] and "git-inventory" in rules(report)


def test_object_bytes_must_match_the_indexed_hash(repo, monkeypatch):
    stage(repo, "control.txt", b"abcd")
    original_git_output = hygiene.git_output

    def altered_object(root, arguments, limit):
        return b"efgh" if arguments[:2] == ["cat-file", "blob"] else original_git_output(root, arguments, limit)

    monkeypatch.setattr(hygiene, "git_output", altered_object)
    report = hygiene.scan(repo)
    assert not report["complete"] and "git-object" in rules(report)


def test_unavailable_git_is_incomplete_without_exception_text(repo, monkeypatch):
    def unavailable(*arguments, **options):
        raise OSError("unpublished diagnostic")

    monkeypatch.setattr(hygiene.subprocess, "Popen", unavailable)
    report = hygiene.scan(repo)
    assert not report["complete"] and "git-unavailable" in rules(report)
    assert "unpublished diagnostic" not in json.dumps(report)


def test_changed_index_during_scan_is_not_a_pass(repo, monkeypatch):
    stage(repo, "a.txt")
    original_git_output = hygiene.git_output
    changed = False

    def interleaved_git_output(root, arguments, limit):
        nonlocal changed
        if arguments[:2] == ["cat-file", "blob"] and not changed:
            changed = True
            stage(repo, "new.txt")
        return original_git_output(root, arguments, limit)

    monkeypatch.setattr(hygiene, "git_output", interleaved_git_output)
    report = hygiene.scan(repo)
    assert not report["complete"] and "index-changed" in rules(report)


def test_timeout_kills_only_owned_git_child(repo, monkeypatch):
    original_popen = subprocess.Popen
    children = []

    def slow_owned_child(*arguments, **options):
        child = original_popen([sys.executable, "-c", "import time; time.sleep(10)"],
                               stdin=options["stdin"], stdout=options["stdout"], stderr=options["stderr"])
        children.append(child)
        return child

    monkeypatch.setattr(hygiene.subprocess, "Popen", slow_owned_child)
    monkeypatch.setattr(hygiene, "GIT_TIMEOUT", 0.05)
    report = hygiene.scan(repo)
    assert report["status"] == "incomplete" and "git-timeout" in rules(report)
    assert children and all(child.poll() is not None for child in children)


def test_caller_selected_index_and_repository_are_not_used(repo, tmp_path, monkeypatch):
    stage(repo, "control.txt")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    git(foreign, "init", "-q")
    stage(foreign, "unsafe.txt", b"ghp_" + b"A" * 36)
    monkeypatch.setenv("GIT_INDEX_FILE", str(foreign / ".git/index"))
    monkeypatch.setenv("GIT_DIR", str(foreign / ".git"))
    assert hygiene.scan(repo)["status"] == "passed"


def test_scan_leaves_candidate_index_and_working_files_unchanged(repo):
    target = stage(repo, "control.txt")
    index_before = (repo / ".git/index").read_bytes()
    object_before = target.read_bytes()
    assert hygiene.scan(repo)["status"] == "passed"
    assert (repo / ".git/index").read_bytes() == index_before and target.read_bytes() == object_before
