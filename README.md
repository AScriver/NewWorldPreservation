# New World: Aeternum preservation research

Preserve the legitimately owned PC client and replace only the backend it needs. Initial objective: **two private accounts, one Aeternum map, mutual player movement**. This is a research/engineering workspace, **not a playable server release**.

## Start here

- [First Light / OpenWorld findings](docs/FIRST_LIGHT_ANALYSIS.md)
- [Architecture and diagram](docs/ARCHITECTURE.md)
- [Protocol notes and Capture Before Shutdown](docs/PROTOCOL_NOTES.md)
- [Client connection flow](docs/CLIENT_FLOW.md)
- [Current-client connectivity result and probe procedure](docs/CURRENT_CLIENT_CONNECTIVITY.md)
- [Current private queue-to-game handoff and next DTLS gate](docs/PRIVATE_GAME_HANDOFF.md)
- [Current DTLS trust result and gated Carrier/V3 registration](docs/DTLS_REGISTRATION.md)
- [Current-build trust-store, verifier and expected-peer evidence](docs/REP_TRUST_POLICY.md)
- [Spawn-sequence evidence and remaining gates](docs/SPAWN_SEQUENCE.md)
- [Milestone 1 tasks and exact next blockers](docs/ROADMAP.md)
- [Open questions](docs/OPEN_QUESTIONS.md)
- [Evidence ledger](docs/EVIDENCE_LEDGER.md)

## Completed first task

Reproduced pinned First Light on Windows with an isolated Python environment and existing public redacted fixture. **455 upstream tests passed, one deliberate skip; 9 original validation-gate tests passed.** DTLS context/memory-BIO construction works with an ephemeral self-generated certificate; **no game DTLS handshake, private account, spawn or multiplayer behavior tested**. The later private HTTPS result is separate below.

Source stays clean/external at `63756a3`; no packet guesses or upstream rewrites. Newer Aeternum-World source (`820156d`) was inspected too. All eight visible First Light fork heads match the historical source. Current community lead: [Open World Discord](https://discord.gg/projectopenworld); no public current server source established. See analysis for limits and provenance.

## Current connectivity slice

**Stock New World `1.400.6031.6004151` / Steam build22469132 reached our private HTTPS server.** Exact accepted-socket owner matched our recorded ordinary Steam launch. The client sent HTTP/1.1 `GET /STEAM_APP_ID.1063730.json` over TLS1.2 to IPv6 localhost443; probe returned deliberate501. Local CurrentUserRoot CA + correct hostname works; absent CA or wrong-name same-CA leaf prevents HTTP; restoration restores HTTP. No memory inspection, binary patch or EAC change. Both temporary CAs removed, hosts restored byte-exact, owned probes/client closed.

**Latest live checkpoint:** the certificate-data-only candidate was refused at launch by intact EAC (“Unrecognized game client” / “Unknown file version”). Exact stock bytes/signature restored; this route is retired, not bypassed. The matched elevated stock/original-launcher control completed five private HTTP requests and reached DTLS, then returned two **fatal unknown_ca** alerts. Eight alerts across four stock runs; **no completed private game DTLS, Carrier/V3, world loading, actor or Milestone1**. [Comparison](docs/PRIVATE_REP_ANCHOR_TRIAL.md), [hash-pinned live receipt](research/evidence/private-rep-anchor-eac-control.json). The static embedded-anchor/standard-verifier map is established, but an unchanged-client private-CA configuration route remains unknown. [Trust policy](docs/REP_TRUST_POLICY.md). Prior285 workspace/14 interval/9 lifecycle and455 upstream/skip1 checks remain historical; no protocol changes or new test execution. Final stockValid/originalhosts/zero temporary resources verified; approved CA retained. No secure private account/ticket validation yet.

```powershell
C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Inspect-CurrentClient.ps1 -Execute
C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Test-ConnectivityProbe.ps1 -Execute
```

See [CURRENT_CLIENT_CONNECTIVITY](docs/CURRENT_CLIENT_CONNECTIVITY.md) for exact build, attribution limits, certificate controls, failures and live reproduction/cleanup procedure. Safe receipts: [real-client result](research/evidence/current-client-connectivity.json), [probe controls](research/evidence/connectivity-validation.json), [instrumentation](research/evidence/instrumentation-validation.json), [CLI control](research/evidence/connectivity-cli-control.json). [SPAWN_SEQUENCE](docs/SPAWN_SEQUENCE.md) maps the historical candidate flow without inventing current packets. No spawn implementation follows from synthetic or HTTPS-only success.

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
- Own-session bootstrap HTTPS controls executed; authentication/REP/world/spawn/movement captures remain outstanding. Official announced shutdown: [January31, 2027](https://www.newworld.com/en-us/news/articles/the-future-of-new-world-aeternum-what-to-expect).

## Next step

Establish a private-anchor loading boundary that preserves verification, then prove an actual current-client handshake and observe/answer Carrier/V3 registration. The REP wrapper/interface source join is complete; live branch/store readback is not. Two isolated CA-verified DTLS controls already exchange data. Actor work remains gated. See [trust evidence](docs/REP_TRUST_POLICY.md) and [roadmap](docs/ROADMAP.md).

All work is local. No remote/public repository, contributor messages or Actionables were created/updated; no governing Actionables work-item ID was supplied.
