# Agent start guide

Use this page to choose a bounded task and reproduce its checks. Current progress,
blockers and Milestone 1 acceptance belong to [ROADMAP](ROADMAP.md), not this guide.
The current priority is the [one-player spawn-and-control checkpoint](ONE_PLAYER_MILESTONE.md);
preserve the broader two-client roadmap and existing approvals.

## Read in this order

1. [AGENTS](../AGENTS.md): client, provenance, offline and publishing boundaries.
2. [ROADMAP — exact next blocker](ROADMAP.md#exact-next-blocker), then the task table
   and acceptance boundary. Do not infer that a dependency is complete from its name.
3. Run the read-only preflight below. Inspect dirty/untracked files before choosing
   edit ownership; another agent may be working in the same checkout.
4. Find your boundary in the [evidence index](EVIDENCE_INDEX.md) or
   [JSON catalog](../research/agent-evidence-index.json). Read its specific slice doc,
   then the referenced claim rows in [EVIDENCE_LEDGER](EVIDENCE_LEDGER.md).
5. For bounded native-function questions, use the [function-scoped Ghidra procedure](TOOLS.md#function-scoped-ghidra-default)
   with exact entries, current hash and instruction checks; whole-image automatic
   analysis is not the default. Fill the [task brief](TASK_BRIEFS.md#task-brief-template), including exact files,
   permitted operations, input identity and rejection checks. Run the matching
   focused profile; use the complete workspace profile before handing off.
6. Finish with the [handoff format](AGENT_HANDOFF.md). Record the task/verification
   in ROADMAP with a small edit that preserves any concurrent work.
   Follow [completion and continuation](../AGENTS.md#completion-and-continuation):
   preserve required checks and material corrections, reuse unaffected validation,
   and finish or continue authorized work once closure is verified, without time caps.

## Safe commands

Run from the repository root in PowerShell 7. Each invocation validates the entire
PowerShell script before execution. These commands do not launch a game, inspect
its memory, edit hosts/trust stores, or contact game endpoints.

```powershell
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Get-ProjectPreflight.ps1 -Execute
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-Offline.ps1 -Execute
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-Offline.ps1 -Execute -ArgumentList '-Profile','tooling'
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-Offline.ps1 -Execute -ArgumentList '-ListProfiles'
```

The default `workspace` profile explicitly selects reviewed Python tests, three
mock/synthetic PowerShell suites and an owned loopback HTTPS child lifecycle check.
Focused profiles are listed in [offline-test-profiles.json](../scripts/offline-test-profiles.json).
`upstream` and `all` additionally require the existing clean, pinned external First
Light checkout and redacted fixture. The focused `rep-readonly` profile exercises
the now-reviewed fake-API tests, which are also included in the complete workspace
profile. The probe's live process-observation CLI remains separately gated.
The `frida-trial` profile runs original fake-API ownership/failure/privacy tests and
is included in `workspace`; it never imports Frida's live backend or starts a game.
The explicit-only inert Windows owner smoke is outside default test collection.
Live startup/runtime trust work follows [its own procedure](FRIDA_PRIVATE_DTLS_TRIAL.md).
The pinned upstream profile selects eleven files; `server/test_loopback.py` is a
helper with zero pytest cases. Its explicit exception is recorded in the manifest
and receipt; the profile still requires all 456 cases and its one exact deliberate skip.

```powershell
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-Offline.ps1 -Execute -ArgumentList '-Profile','all'
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Get-ProjectPreflight.ps1 -Execute -ArgumentList '-OutputFormat','Json'
```

When the environment/reference is missing, follow [README setup](../README.md#reproduce-locally)
using the existing scripts. Setup downloads public code and syncs only the local
venv; preflight performs neither operation. The old `Test-FirstLight -PreflightOnly`
constructs a DTLS context and writes its old receipt: use `Get-ProjectPreflight` for
read-only inspection.

## Where to work and test

| Boundary | Original scripts / test entry | Navigation |
|---|---|---|
| Original player creation candidate | `current_player_creation_candidate`; `test_current_player_creation_candidate` | [Two-member composition and explicit gates](PLAYER_CREATION_CANDIDATE.md) |
| Owned player delivery index | `owned_player_delivery_index`; `test_owned_player_delivery_index` | [Asset field, mode and offline reader](PLAYER_DELIVERY_INDEX.md) |
| Player identity BODY | `current_player_identity_body`; `test_current_player_identity_body` | [Identity fields and delivery limits](PLAYER_IDENTITY_BODY.md) |
| Reference/dependencies | `Get-FirstLightReference`, `Initialize-DevEnvironment`, `validate_first_light`; `test_validation_gate` | [First Light analysis](FIRST_LIGHT_ANALYSIS.md) |
| Bootstrap HTTPS and ownership | `connectivity_probe`, `game_log_metadata`, `windows_tcp_owner`; `test_connectivity_probe`, metadata/owner/observer tests | [Connectivity](CURRENT_CLIENT_CONNECTIVITY.md) |
| Channel/token request | `channel_descriptor`, `bootstrap_probe`, `bootstrap_log_metadata`; descriptor/bootstrap/flow tests | [Channel](BOOTSTRAP_CHANNEL.md) |
| Token/credentials/login-info | `token_contract_probe`, `credentials_contract_probe`, `session_handoff_probe`; contract/fixture tests | [Token](TOKEN_SESSION_CONTRACT.md), [credentials](CREDENTIALS_SESSION_HANDOFF.md), [login-info](LOGIN_INFO_CONTRACT.md) |
| Queue/UDP handoff | `queue_contract_probe`, `udp_handoff_probe`, `windows_udp_owner`; queue/handoff/owner tests | [Game handoff](PRIVATE_GAME_HANDOFF.md) |
| Local DTLS / current REP trust | `dtls_transport_probe`; DTLS controls; synthetic candidate/transaction/lifecycle tests | [DTLS](DTLS_REGISTRATION.md), [trust](REP_TRUST_POLICY.md) |
| Carrier, spawn, actor replication | `carrier_registration_probe` metadata/privacy tests; live scoped trial is separate from offline validation | [Carrier trial](CARRIER_REGISTRATION_TRIAL.md), [spawn](SPAWN_SEQUENCE.md), [architecture](ARCHITECTURE.md) |
| Agent tooling | `project_preflight`, `validate_offline`, `client_config_archive_metadata`, `ghidra_function_slice`; four offline tooling test modules | [Catalog](EVIDENCE_INDEX.md), [tools](TOOLS.md), [handoff](AGENT_HANDOFF.md) |

The tooling profile includes synthetic function-slice safety tests; it never
starts Ghidra or reads a client image. Explicit static queries follow
[TOOLS](TOOLS.md#function-scoped-ghidra-default).

The catalog carries exact filenames; the table above is a reading map, not an
invocation list for live procedures. Existing redirect/trust/client/anchor scripts
require separately authorized resource ownership and their own runbooks.

## Parallel work and evidence

Claim an exact file scope in the brief; a dirty file is not yours to revert. Inspect
latest bytes immediately before shared documentation edits. Keep scripts/logs in
unique task/run directories under ignored `.scratch/`; never reuse another trial's
resources or overwrite its receipt. Serialize work that shares hosts, certificates,
client processes, databases or fixed ports with the actual owner.

The new runner creates a unique `.scratch/offline-validation/run-*/receipt.json`,
captures input hashes before/after and fails when selected inputs change during a
run. Raw stdout/JUnit stays private in that run directory. Passing tests establish
the named offline scope only; two actual clients and bilateral movement remain the
Milestone 1 acceptance boundary. Pending Milestone 1 work uses Actionables
`workItemId: 164`; the separate parked stock-client trust task uses
`workItemId: 165`. Resolve the exact task in [ACTIONABLES](ACTIONABLES.md),
then follow the scoped workflow. ROADMAP retains current technical progress and
acceptance; task creation alone does not authorize implementation or a live trial.
