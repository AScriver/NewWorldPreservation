"""Read-only readiness and public evidence bindings; never imports client/probe code."""
from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path, PureWindowsPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = "research/agent-evidence-index.json"
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
PUBLIC_AREAS = ("scripts/", "tests/", "docs/", "research/evidence/")
PUBLIC_FILES = {"AGENTS.md", "README.md", ".gitignore", ".gitattributes",
                "requirements-dev.in", "requirements-dev.lock", "research/upstreams.json", INDEX,
                "scripts/offline-test-profiles.json"}
MAX_JSON_BYTES = 2_000_000


def public_path(root: Path, name: str) -> Path | None:
    """Reject external/private paths and symlinks escaping the public workspace."""
    if not isinstance(name, str):
        return None
    normalized = name.replace("\\", "/")
    if PureWindowsPath(name).is_absolute() or normalized.startswith("/"):
        return None
    if ".." in normalized.split("/"):
        return None
    if normalized not in PUBLIC_FILES and not normalized.startswith(PUBLIC_AREAS):
        return None
    candidate = root / normalized
    if not candidate.resolve().is_relative_to(root.resolve()):
        return None
    resolved_name = candidate.resolve().relative_to(root.resolve()).as_posix()
    if resolved_name not in PUBLIC_FILES and not resolved_name.startswith(PUBLIC_AREAS):
        return None
    return candidate


def read_json(path: Path) -> dict:
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("metadata exceeds size limit")
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(result, dict):
        raise ValueError("metadata must be an object")
    return result


def file_hash(path: Path) -> str:
    before = path.stat()
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("file changed during read")
    return digest


def git_read(root: Path, *arguments: str) -> str:
    return subprocess.run(["git", "-C", str(root), *arguments], capture_output=True,
                          text=True, encoding="utf-8", check=True, timeout=20).stdout.strip()


def git_state(root: Path) -> dict:
    try:
        # Do not strip NUL records: status/path whitespace is significant.
        output = subprocess.run(["git", "-C", str(root), "status", "--porcelain=v1", "-z",
                                 "--untracked-files=all"], capture_output=True, text=True,
                                encoding="utf-8", check=True, timeout=20).stdout
        records = iter(output.split("\0"))
        changes = []
        for record in records:
            if not record:
                continue
            entry = {"status": record[:2], "path": record[3:].replace("\\", "/")}
            if "R" in record[:2] or "C" in record[:2]:
                entry["originalPath"] = next(records).replace("\\", "/")
            target = public_path(root, entry["path"])
            if target and target.is_file():
                try:
                    entry["sha256"] = file_hash(target)
                except (OSError, ValueError):
                    entry["sha256"] = "unavailable-or-changing"
            changes.append(entry)
        return {"status": "observed", "head": git_read(root, "rev-parse", "HEAD"),
                "branch": git_read(root, "branch", "--show-current"),
                "totalChanges": len(changes), "changes": changes[:25], "truncated": len(changes) > 25}
    except (OSError, subprocess.SubprocessError, StopIteration):
        return {"status": "unavailable"}


def locked_packages(path: Path) -> dict[str, str]:
    """Accept the repository's generated exact-pin/sha256 lock syntax, fail closed."""
    pins = {}
    hashed = set()
    current = None
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        pin = re.fullmatch(r"([A-Za-z0-9_.-]+)==([0-9][A-Za-z0-9_.+!-]*)\s*\\?", line)
        if pin:
            name, version = pin.groups()
            if name.lower().replace("_", "-") in {entry.lower().replace("_", "-") for entry in pins}:
                raise ValueError(f"duplicate dependency pin at line {number}")
            pins[name] = version
            current = name
        elif current and re.fullmatch(r"--hash=sha256:[0-9a-fA-F]{64}\s*\\?", line):
            hashed.add(current)
        else:
            raise ValueError(f"malformed dependency lock at line {number}")
    if not pins or set(pins) != hashed:
        raise ValueError("dependency pins must each include sha256 hashes")
    return pins


def environment_report(root: Path) -> dict:
    packages = {}
    problems = []
    lock = root / "requirements-dev.lock"
    try:
        pinned = locked_packages(lock)
        if not {"pytest", "pyopenssl", "cryptography"}.issubset(pinned):
            problems.append("dependency lock incomplete")
        for name, expected in pinned.items():
            try:
                installed = metadata.version(name)
            except metadata.PackageNotFoundError:
                installed = None
            packages[name] = {"expected": expected, "installed": installed, "matches": installed == expected}
            if installed != expected:
                problems.append(f"package mismatch: {name}")
        lock_hash = file_hash(lock)
    except (OSError, ValueError):
        lock_hash = None
        problems.append("dependency lock unavailable or malformed")
    if sys.version_info[:2] not in ((3, 11), (3, 12)):
        problems.append("supported Python is 3.11 or 3.12")
    isolated = Path(sys.prefix).resolve() == (root / ".venv").resolve()
    if not isolated:
        problems.append("run with the workspace .venv interpreter")
    return {"ready": not problems, "python": sys.version.split()[0], "isolatedVenv": isolated,
            "lockSha256": lock_hash, "packages": packages, "problems": problems}


def upstream_report(root: Path) -> list[dict]:
    try:
        pins = read_json(root / "research/upstreams.json")
    except (OSError, ValueError):
        return [{"name": "pins", "status": "unavailable"}]
    reports = []
    for name, pin in pins.items():
        entry = {"name": name, "expectedCommit": pin.get("commit"), "status": "missing"}
        directory = pin.get("directory", "").replace("\\", "/")
        reference = root / directory
        if (not directory.startswith("research/upstream/") or ".." in directory.split("/")
                or not reference.resolve().is_relative_to((root / "research/upstream").resolve())):
            entry["status"] = "invalid-reference-path"
        elif reference.is_dir():
            try:
                entry["commit"] = git_read(reference, "rev-parse", "HEAD")
                entry["commitMatches"] = entry["commit"] == pin["commit"]
                entry["originMatches"] = git_read(reference, "remote", "get-url", "origin") == pin["url"]
                entry["clean"] = not git_read(reference, "status", "--porcelain")
                entry["status"] = "ready" if all(entry[key] for key in ("commitMatches", "originMatches", "clean")) else "mismatch"
                if "fixture" in pin:
                    fixture_name = pin["fixture"].replace("\\", "/")
                    fixture = reference / fixture_name
                    if (PureWindowsPath(fixture_name).is_absolute() or ".." in fixture_name.split("/")
                            or not fixture.resolve().is_relative_to(reference.resolve())):
                        raise ValueError("invalid fixture path")
                    actual = file_hash(fixture)
                    entry["fixture"] = {"path": fixture_name, "expectedSha256": pin["fixtureSha256"],
                                        "sha256": actual, "matches": actual == pin["fixtureSha256"]}
                    if not entry["fixture"]["matches"]:
                        entry["status"] = "mismatch"
            except (OSError, ValueError, KeyError, subprocess.SubprocessError):
                entry["status"] = "unavailable-or-incomplete"
        reports.append(entry)
    return reports


def hash_bindings(value, prefix=""):
    """Legacy receipts use several names; recognize hashes bound to explicit paths."""
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and "sha256" in value:
            yield value["path"], value["sha256"], prefix
        for key, item in value.items():
            field = f"{prefix}.{key}" if prefix else key
            path_key = "/" in key or "\\" in key
            hash_map = "sha" in prefix.lower() or prefix.lower().endswith("sources")
            if path_key and ((isinstance(item, str) and SHA256.fullmatch(item)) or hash_map):
                yield key, item, field
            elif isinstance(item, (dict, list)):
                yield from hash_bindings(item, field)
    elif isinstance(value, list):
        for number, item in enumerate(value):
            yield from hash_bindings(item, f"{prefix}[{number}]")


def receipt_report(root: Path, name: str, *, runtime: dict | None = None) -> dict:
    report = {"path": name, "freshness": "unknown", "checkedBindings": 0,
              "uncheckedBindings": 0, "mismatches": [], "missing": [], "malformedBindings": []}
    target = public_path(root, name)
    # The caller may explicitly inspect a new offline run's metadata, never arbitrary scratch files.
    if target is None and re.fullmatch(r"\.scratch/offline-validation/run-[A-Za-z0-9_-]+/receipt\.json", name):
        candidate = root / name
        if candidate.resolve().is_relative_to((root / ".scratch/offline-validation").resolve()):
            target = candidate
    if target is None:
        report["reason"] = "receipt outside public metadata/offline-run scope"
        return report
    try:
        value = read_json(target)
        report["recordedStatus"] = value.get("status", value.get("state", "not-recorded"))
        mismatches = set()
        missing = set()
        malformed = set()
        for path_name, expected, _field in hash_bindings(value):
            candidate = public_path(root, path_name)
            if candidate is None:
                report["uncheckedBindings"] += 1
                continue
            if not isinstance(expected, str) or not SHA256.fullmatch(expected):
                malformed.add(path_name)
                continue
            report["checkedBindings"] += 1
            if not candidate.is_file():
                missing.add(path_name)
            elif file_hash(candidate) != expected.lower():
                mismatches.add(path_name)
        # Older CLI receipt pins one named script without a path map.
        if SHA256.fullmatch(str(value.get("probeSha256", ""))):
            report["checkedBindings"] += 1
            if file_hash(root / "scripts/connectivity_probe.py") != value["probeSha256"]:
                mismatches.add("scripts/connectivity_probe.py")
        recorded_runtime = value.get("runtime", {})
        if runtime and isinstance(recorded_runtime, dict):
            if recorded_runtime.get("lockSha256") and recorded_runtime["lockSha256"] != runtime.get("lockSha256"):
                mismatches.add("requirements-dev.lock")
            if recorded_runtime.get("python") and recorded_runtime["python"] != runtime.get("python"):
                mismatches.add("runtime:python")
            for package, version in recorded_runtime.get("packages", {}).items():
                if isinstance(version, dict):
                    version = version.get("installed")
                current = runtime.get("packages", {}).get(package, {}).get("installed")
                if current != version:
                    mismatches.add(f"runtime:package:{package}")
        reference = value.get("reference") or value.get("upstream", {}).get("reference")
        if isinstance(reference, dict) and reference.get("commit"):
            for upstream in upstream_report(root):
                if upstream["name"] == "firstLight":
                    report["checkedBindings"] += 1
                    if upstream["status"] != "ready" or upstream.get("commit") != reference["commit"]:
                        mismatches.add("upstream:firstLight")
                    if reference.get("fixtureSha256") != upstream.get("fixture", {}).get("sha256"):
                        mismatches.add("upstream:firstLight:fixture")
        report["mismatches"] = sorted(mismatches)[:8]
        report["missing"] = sorted(missing)[:8]
        report["mismatchCount"] = len(mismatches)
        report["missingCount"] = len(missing)
        report["malformedBindings"] = sorted(malformed)[:8]
        report["malformedCount"] = len(malformed)
        report["detailsTruncated"] = len(mismatches) > 8 or len(missing) > 8 or len(malformed) > 8
        if mismatches or missing:
            report["freshness"] = "stale-local-inputs"
        elif malformed:
            report["reason"] = "malformed public hash bindings prevent a complete freshness check"
        elif report["checkedBindings"]:
            report["freshness"] = "local-bindings-match"
        else:
            report["reason"] = "no checkable public source/runtime bindings"
        report["scope"] = "local bindings only; historical observations retained; private artifacts and real client unverified"
    except (OSError, ValueError, TypeError, AttributeError):
        report["reason"] = "metadata or bound file unavailable, malformed or changing"
    return report


def index_report(root: Path) -> dict:
    errors = []
    fixtures = []
    try:
        index = read_json(root / INDEX)
        claims = set(re.findall(r"\|\s*((?:K|C|E)\d+)\s*\|", (root / "docs/EVIDENCE_LEDGER.md").read_text(encoding="utf-8")))
        ids = set()
        for boundary in index["boundaries"]:
            if boundary["id"] in ids:
                errors.append(f"duplicate boundary: {boundary['id']}")
            ids.add(boundary["id"])
            for claim in boundary["claimIds"]:
                if claim not in claims:
                    errors.append(f"unknown claim: {claim}")
            for name in boundary["docs"] + boundary["scripts"] + boundary["tests"]:
                candidate = public_path(root, name)
                if candidate is None or not candidate.is_file():
                    errors.append(f"missing/out-of-scope indexed file: {name}")
            for evidence in boundary["evidence"]:
                candidate = public_path(root, evidence["path"])
                if candidate is None or not candidate.is_file():
                    errors.append(f"missing evidence: {evidence['path']}")
        for fixture in index["fixtures"]:
            candidate = public_path(root, fixture["path"])
            actual = file_hash(candidate) if candidate and candidate.is_file() else None
            matches = actual == fixture["sha256"]
            fixtures.append({"path": fixture["path"], "classification": fixture["classification"],
                             "expectedSha256": fixture["sha256"], "sha256": actual, "matches": matches})
            if not matches:
                errors.append(f"fixture hash mismatch/missing: {fixture['path']}")
        known = {fixture["path"] for fixture in fixtures}
        existing = {path.relative_to(root).as_posix() for path in (root / "tests/fixtures").rglob("*.json")}
        for name in sorted(existing - known):
            errors.append(f"fixture not indexed: {name}")
        roadmap = (root / "docs/ROADMAP.md").read_text(encoding="utf-8")
        tasks = set(re.findall(r"\| (M1-[A-Z0-9]+)\b", roadmap))
        indexed_tasks = {task for boundary in index["boundaries"] for task in boundary["roadmapTasks"]}
        for task in sorted(tasks - indexed_tasks):
            errors.append(f"roadmap task not indexed: {task}")
        return {"ready": not errors, "errors": errors, "fixtures": fixtures,
                "boundaryCount": len(ids), "roadmapTaskCount": len(tasks)}
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return {"ready": False, "errors": ["evidence index unavailable/malformed"], "fixtures": fixtures}


def collect(root: Path, *, powershell: dict | None = None, extra_receipts: tuple[str, ...] = ()) -> dict:
    runtime = environment_report(root)
    index = index_report(root)
    try:
        names = read_json(root / INDEX)["receipts"]
    except (OSError, ValueError, KeyError):
        names = []
    receipts = [receipt_report(root, name, runtime=runtime) for name in dict.fromkeys([*names, *extra_receipts])]
    result = {"mode": "read-only-project-preflight", "newWorldClientTested": False,
              "workspaceReady": runtime["ready"] and index["ready"],
              "runtime": runtime, "powershell": powershell or {"status": "not-checked-use-wrapper"},
              "git": git_state(root), "upstreams": upstream_report(root), "index": index,
              "receipts": receipts,
              "limits": ["No private/raw artifacts or installed-client bytes read",
                         "Hash matches do not rerun tests or prove real-client acceptance",
                         "Missing optional references do not block workspace-only profiles",
                         "Git/files are sequential observations; concurrent edits can stale checks"]}
    if powershell is not None:
        result["workspaceReady"] = result["workspaceReady"] and powershell.get("ready", False)
    return result


def text_report(report: dict) -> str:
    lines = [f"Workspace offline readiness: {'ready' if report['workspaceReady'] else 'attention required'}",
             f"Python {report['runtime']['python']}; isolated venv: {report['runtime']['isolatedVenv']}"]
    lines += [f"  {problem}" for problem in report["runtime"]["problems"]]
    lines.append(f"PowerShell: {report['powershell'].get('version', report['powershell'].get('status', 'unknown'))}; analyzer: {report['powershell'].get('analyzerVersion', 'unknown')}")
    state = report["git"]
    lines.append(f"Git: {state.get('head', 'unavailable')} ({state.get('branch', '?')}); {state.get('totalChanges', '?')} dirty/untracked paths")
    lines += [f"  {entry['status']} {entry['path']}" for entry in state.get("changes", [])]
    if state.get("truncated"):
        lines.append("  Git detail truncated at 25 paths; inspect git status for all paths")
    lines += [f"Reference {item['name']}: {item['status']} (pin {item.get('expectedCommit', '?')})" for item in report["upstreams"]]
    lines.append(f"Evidence index: {report['index'].get('boundaryCount', 0)} boundaries; {len(report['index']['fixtures'])} fixture hashes")
    lines += [f"  {problem}" for problem in report["index"]["errors"]]
    for item in report["receipts"]:
        lines.append(f"Receipt {item['path']}: {item['freshness']} ({item['checkedBindings']} public bindings; {item['uncheckedBindings']} unchecked)")
        lines += [f"  changed: {path}" for path in item["mismatches"]]
        lines += [f"  missing: {path}" for path in item["missing"]]
        lines += [f"  malformed hash: {path}" for path in item["malformedBindings"]]
        if item.get("reason"):
            lines.append(f"  {item['reason']}")
    lines.append("Local freshness preserves historical evidence; it does not establish current gameplay or verify private artifacts.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--receipt", action="append", default=[])
    parser.add_argument("--powershell-version")
    parser.add_argument("--analyzer-version")
    options = parser.parse_args()
    powershell = None
    if options.powershell_version is not None:
        major = options.powershell_version.split(".")[0]
        powershell = {"version": options.powershell_version, "analyzerVersion": options.analyzer_version,
                      "ready": major.isdigit() and int(major) >= 7 and bool(options.analyzer_version)}
    report = collect(ROOT, powershell=powershell, extra_receipts=tuple(options.receipt))
    print(json.dumps(report, indent=2) if options.format == "json" else text_report(report))
    return 0 if report["workspaceReady"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
