# Publication hygiene

[Test-PublishHygiene](../scripts/Test-PublishHygiene.ps1) runs the original,
standard-library-only [scanner](../scripts/publish_hygiene.py) against exact Git
objects. It is an offline commit/publication check. It neither publishes nor
authorizes publication; the existing provenance, licensing and client boundaries
in [AGENTS](../AGENTS.md) still apply.

## Run the check

Use the existing development environment and a Git version supporting
`--no-lazy-fetch`. Run from the repository root in PowerShell7:

```powershell
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-PublishHygiene.ps1 -Execute
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-PublishHygiene.ps1 -Execute -ArgumentList '-Mode','committed'
```

Stage and review only task-owned changes before the first command. `staged`
checks the **entire index**, including unchanged tracked files, against its pinned
object IDs. Unstaged and untracked bytes do not affect this candidate.
`committed` resolves `HEAD` once and checks that commit's entire tree; staged and
working-tree changes do not affect it. Its report identifies the commit. An index
inventory hash identifies the staged candidate; a changed inventory at the end
makes the result incomplete. Recheck after changing the candidate. Serialize
staging/committing with this check; it does not lock out other writers.

Valid invocations emit one JSON report containing status, completeness, candidate
identity, counters and findings. Findings contain rule IDs and escaped paths;
matched blob contents and Git error text are suppressed. Paths containing a
recognized credential or private-key marker are redacted too. `reviewedMarkers`
reports any exact fixture exception applied.

| Python exit | Report | Meaning |
| --- | --- | --- |
| 0 | `passed` | The exact candidate passed the declared checks. |
| 1 | `rejected` | Candidate entries violate one or more rules. |
| 2 | `incomplete` | A read, identity, concurrency, timeout or budget check failed. |

The PowerShell wrapper treats either nonzero Python result as failure. Resolve the
identified candidate issue or incomplete check; never treat an incomplete result
as a clean scan. The scanner makes no deletions or repairs.

## Declared checks and budgets

| Boundary | Rules |
| --- | --- |
| Paths | Reject `.scratch`, `private`, `.venv`, `.git` segments; root `research/upstream`; unsafe paths; `.env` and `.env.*` except `.env.example`. |
| Modes | Reject symlinks, gitlinks, unmerged entries and unsupported modes before blob reads. Targets are not followed. |
| Artifacts | Reject capture, key, executable, client package and archive extensions declared in the scanner; detect PE/ELF, ZIP/7z/RAR and pcap/pcapng prefixes even after renaming. |
| Contents | Detect private-key markers and the declared AWS/GitHub credential formats. `.env.example` has no content exemption. |
| Integrity | Bound reads and verify Git blob hashes; reject missing objects and changed staged inventories. Disable lazy fetch, object replacement and filesystem-monitor hooks; suppress Git stderr. |

Defaults are 5,000 entries, 2MiB per public blob, 32MiB total public blob bytes,
2MiB inventory output and 64 findings including the terminal incomplete finding.
Each owned Git child has a 15-second command deadline and bounded cleanup waits.
Byte/count caps can be reduced through the Python CLI for controlled checks; any
increase needs a concrete reason and a reviewed candidate scope. Forbidden entries
are rejected without reading their blobs. Git commands use argument arrays and
read only local index/tree/object metadata and selected blobs; no network fetch,
game process, hook execution or repository writes are requested.

Addresses, hashes and decompiler names remain valid evidence. Original synthetic
fixtures and public metadata are permitted unless they match a declared rule.
Do not add broad exceptions to accommodate genuine client artifacts or secrets.
The scanner contains one reviewed exception: the private-key rule for the exact
`tests/test_rep_anchor_candidate.py` blob with SHA256
`416787834d1c909b7e7e3ad66ff7687c8ba76dfc8dc06dbdea0261902d40d702`.
That original negative test appends a deliberately invalid `AA==` marker, with no
key material. A different path or any changed bytes lose the exception; all other
rules remain enforced. Retain this rejection test rather than weakening the rule
for all tests.

## Limits and verification

This is a narrow detector, not proof of ownership, licensing, absence of every
secret or absence of proprietary data. Undeclared credential formats, opaque
client-derived bytes and other archive formats can escape these signatures.
Review provenance and the diff separately. A clean `HEAD` does not scan earlier
commits: before an explicitly authorized push, also review the outgoing history
for material removed from the final tree.

The [tooling profile](../scripts/offline-test-profiles.json) includes
[isolated Git regression tests](../tests/test_publish_hygiene.py). They cover
snapshot selection, path/mode/content rejection, output redaction, budgets,
missing objects, index changes and owned-child timeout cleanup. Windows Git
refuses tab/newline/quote names; that parser boundary uses modeled NUL-delimited
inventory bytes with real Git object reads and is labeled accordingly.
