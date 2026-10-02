# New World: Aeternum preservation research

Preserve the legitimately owned PC client and replace only the backend it needs. Initial objective: **two private accounts, one Aeternum map, mutual player movement**. This is a research/engineering workspace, **not a playable server release**.

## Start here

- [First Light / OpenWorld findings](docs/FIRST_LIGHT_ANALYSIS.md)
- [Architecture and diagram](docs/ARCHITECTURE.md)
- [Protocol notes and Capture Before Shutdown](docs/PROTOCOL_NOTES.md)
- [Client connection flow](docs/CLIENT_FLOW.md)
- [Current-client connectivity gate and probe procedure](docs/CURRENT_CLIENT_CONNECTIVITY.md)
- [Milestone 1 tasks and exact next blockers](docs/ROADMAP.md)
- [Open questions](docs/OPEN_QUESTIONS.md)
- [Evidence ledger](docs/EVIDENCE_LEDGER.md)

## Completed first task

Reproduced pinned First Light on Windows with an isolated Python environment and existing public redacted fixture. **455 upstream tests passed, one deliberate skip; 9 original validation-gate tests passed.** DTLS context/memory-BIO construction works with an ephemeral self-generated certificate; **no handshake, game client, private account, spawn or multiplayer behavior tested**.

Source stays clean/external at `63756a3`; no packet guesses or upstream rewrites. Newer Aeternum-World source (`820156d`) was inspected too. All eight visible First Light fork heads match the historical source. Current community lead: [Open World Discord](https://discord.gg/projectopenworld); no public current server source established. See analysis for limits and provenance.

## Current connectivity slice

Added an original **loopback-only HTTPS/SNI diagnostic**, secret-minimizing structured logs, client executable discovery and a bounded own-process TCP observer. **19 control tests pass**, and a separate CLI lifecycle control receives CA-validated HTTP 200 then verifies listener cleanup. These use Python, **not New World**. Discovery found no current installed client in the checked locations; the exact executable path is required for the live gate. No game was launched, hosts/trust stores changed, binary patched, auth completed or actor spawned. HTTPS and REP/DTLS trust remain separate unproven current-client requirements.

```powershell
C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Inspect-CurrentClient.ps1 -Execute
C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-ConnectivityProbe.ps1 -Execute
```

See [CURRENT_CLIENT_CONNECTIVITY](docs/CURRENT_CLIENT_CONNECTIVITY.md) for exact controls, historical endpoint sources, failure observations, redirection options **not yet tested on the game**, and the gated live procedure. Safe receipts: [test profile](research/evidence/connectivity-validation.json), [CLI control](research/evidence/connectivity-cli-control.json), [client discovery](research/evidence/current-client-discovery.json). Observer was syntax-validated only; it cannot see DNS/payloads and may miss short-lived connections. No spawn work begins from synthetic success.

## Reproduce locally

Requires Windows PowerShell7, Git, Python3.11 (or explicitly supplied3.12) and `uv`. No game install, admin rights, hosts changes, certificate-store changes, Frida, python3-dtls or external game services are required for these offline checks.

From this workspace:

```powershell
C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Get-FirstLightReference.ps1 -Execute
C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Initialize-DevEnvironment.ps1 -Execute
C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-FirstLight.ps1 -Execute
```

The wrapper validates each entire PowerShell script before running it in `pwsh -NoProfile`. `Get-FirstLightReference` downloads public reference code and a redacted fixture into ignored `research/upstream/`; it checks origin, commit, cleanliness and fixture hash and does not overwrite a changed checkout. New references explicitly use Windows CRLF conversion; the fixture pin identifies those checkout bytes, not the canonical Git blob. `Initialize-DevEnvironment` syncs hash-pinned packages **only in this workspace's .venv**. It does not re-resolve the lock or alter global Python packages.

`Test-FirstLight` runs our verification-gate tests and an explicit11-module upstream profile. It refuses wrong source/dependency/fixture identities, unexpected skips, zero/changed test coverage, failures or errors. Avoid bare upstream `pytest`: `server/test_client.py` is a CLI with import-time exit behavior. Site/dashboard test profiles are not included in this protocol/runtime profile.

Current local test receipt: [latest-validation.json](research/evidence/latest-validation.json). Full stdout/JUnit stays private in `.scratch/validation/run-*/`; no captured packet bytes are printed by our runner. Keep these outputs private even if a failed test prints packet data. The reference dump itself is **not committed or redistributed here**.

## Source and data boundaries

- [Upstream pins](research/upstreams.json), [ecosystem receipt](research/evidence/ecosystem-summary.json), [fixture hash](research/evidence/fixture-summary.json), and separate before/after-fixture test receipts identify the evidence.
- First Light has no detected license at the pinned revision: no vendoring. Aeternum-World declares AGPL-3.0: inspected externally, not integrated.
- Do not commit clients, assets, raw captures, credentials, keys, leaked/proprietary server code or decompiled Amazon material. Do not contact game endpoints or run capture/trust-patch tooling through these scripts.
- Own-session observation priorities are documented, not executed. Official announced shutdown: [January31, 2027](https://www.newworld.com/en-us/news/articles/the-future-of-new-world-aeternum-what-to-expect).

## Next step

Pin a legitimate current client and prove controlled private bootstrap/DTLS trust; then establish registration-to-actor-spawn behavior. Without client access, the next independent offline slice is a real two-peer loopback DTLS exchange—not another invented gameplay codec. See [roadmap](docs/ROADMAP.md).

All work is local. No remote/public repository, contributor messages or Actionables were created/updated; no governing Actionables work-item ID was supplied.
