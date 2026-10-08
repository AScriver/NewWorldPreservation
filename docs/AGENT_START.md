# Agent start guide

Current progress, blockers and acceptance belong to [ROADMAP](ROADMAP.md).
The immediate priority is the [one-player spawn-and-control checkpoint](ONE_PLAYER_MILESTONE.md).
The separate shutdown-observation lane uses [its preservation packet](SHUTDOWN_PRESERVATION.md)
under #166/workItem164. Preserve the broader two-client milestone and existing grants.

## Read in this order

1. [AGENTS](../AGENTS.md): client, provenance, offline, live-trial and publication boundaries.
2. [The exact next blocker](ROADMAP.md#exact-next-blocker), its task table and acceptance.
   A dependency's name does not establish completion.
3. Run read-only preflight below; inspect dirty/untracked files before choosing ownership.
4. Find the boundary in the [evidence index](EVIDENCE_INDEX.md) or
   [JSON catalog](../research/agent-evidence-index.json), read its slice document and
   the referenced [ledger](EVIDENCE_LEDGER.md) claims.
5. Fill the [task brief template](TASK_BRIEF_TEMPLATE.md), including exact inputs,
   permitted operations, resource ownership and rejection checks. Bounded native
   questions use the [function-scoped Ghidra procedure](TOOLS.md#function-scoped-ghidra-default).
6. Run the focused offline profile; use the complete workspace profile before handoff.
   Reuse unaffected validation and recheck changed inputs under
   [completion and continuation](../AGENTS.md#completion-and-continuation).
7. Use the [handoff template](AGENT_HANDOFF_TEMPLATE.md): record the bounded result,
   next owner/action, authorization, evidence limits and cleanup. Update ROADMAP and
   ledger with small edits that preserve concurrent work; continue authorized work.
   Review temporary scaffolding introduced by the task and record its disposition;
   preserve useful tests, reusable diagnostics and evidence receipts. Before a
   commit, check the staged candidate with [publication hygiene](PUBLISH_HYGIENE.md).

## Safe commands

Run from the repository root in PowerShell 7. The wrapper validates each entire
script before execution. These offline commands do not start a game, read game
memory, change routing/trust or contact game endpoints.

```powershell
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Get-ProjectPreflight.ps1 -Execute
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-Offline.ps1 -Execute
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-Offline.ps1 -Execute -ArgumentList '-Profile','tooling'
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-Offline.ps1 -Execute -ArgumentList '-ListProfiles'
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-PublishHygiene.ps1 -Execute
```

The [profile manifest](../scripts/offline-test-profiles.json) owns the exact selected
tests and upstream helper exceptions. `workspace` includes reviewed offline
controls and an owned loopback CLI lifecycle check; `upstream` and `all` additionally
require the existing clean pinned First Light checkout and redacted fixture.
Read-only/fake-API profiles authorize no live process observation. Native trials
follow the [Frida](FRIDA_PRIVATE_DTLS_TRIAL.md), [Carrier](CARRIER_REGISTRATION_TRIAL.md)
or other specifically admitted runbook. Function-slice tooling tests use synthetic
inputs; actual static queries follow TOOLS. If dependencies are missing, use
[local setup](../README.md#reproduce-locally); preflight downloads nothing.

## Shared work and evidence

Claim exact edit paths in the brief. Inspect latest bytes before shared-document
edits; a dirty file is not yours to revert. Use unique ignored `.scratch/` run
directories. Serialize shared hosts, certificates, clients, databases or fixed
ports with their actual owner; preserve unrelated resources and receipts.

Offline validation writes a unique `.scratch/offline-validation/run-*/receipt.json`,
keeps stdout/JUnit private, binds selected input hashes and fails if they change
during a run. Its result proves its named offline scope; real clients and bilateral
movement remain the two-client milestone acceptance.

Tracking uses top-level `workItemId: 164`; the separate parked unchanged-client
trust alternative uses `165`. Resolve the exact task in [ACTIONABLES](ACTIONABLES.md).
ROADMAP owns technical status; task creation changes no implementation or trial authority.
