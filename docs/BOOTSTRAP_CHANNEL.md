# Current bootstrap HTTP200 checkpoint

## Observed result (2026-10-02, UTC)

Stock Steam build **22469132**, client **1.400.6031.6004151**, executable SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e` parsed our original local channel response. It did **not** authenticate, enter Aeternum or create an actor.

Evidence: [metadata-only receipt](../research/evidence/current-client-channel.json), [observed result fixture](../tests/fixtures/connectivity/current-client-channel-result.json). Raw owned logs, certificate material and the public original descriptor remain ignored; the user's screenshot is not copied into this repository.

1. Ordinary Steam launch requested16:56:46.596Z; exclusive fresh client PID41196/start16:56:50.4958785Z. Live executable path inaccessible: this is launch/name/PID/start-time correlation, not a verified live-image hash.
2. Accept-time native TCP owner41196 matched that launch. At16:56:57.841Z, current client sent HTTP/1.1 `GET /STEAM_APP_ID.1063730.json`, empty body, no Authorization/Cookie, over IPv6`::1:443`. SNI/bootstrap hostname `d2c74t4zimux3r.cloudfront.net`, TLS1.2, `ECDHE-RSA-AES256-GCM-SHA384`, no selectedALPN.
3. Our server returned HTTP200/application-octet-stream, canonical3825bytes/SHA256`69075e7a7487b9ac6269db8df865decd56ea6a8190f7adacd9798c1bd7a1cbae`.
4. Own fresh Game.log contains all five deliberately unique `NWPLocalBootstrap` region names at lines279/288/297/306/317. This corroborates **parsing our substituted descriptor**, not merely receiving200. Front-end `NW_Frontend_NightHaven` markers at331/332 are not an Aeternum world load.
5. `Omni CreateSession` / Steam session failure records report **204**, four attempts/two log records per attempt. Stable owned log30131bytes/SHA256`bfc518da3c87f64689c5c0c0f496ba74549e0e4e5bb2f49cc71cde8f325defd4`. Extraction timestamps are explicitly not client event timestamps.
6. User supplied a screenshot: `CONNECTION FAILED` / `Failed to authenticate. Failed to create session. Please try again.` They reported OK dismisses it but it returns. No cursor/keyboard control was used. Screenshot alone cannot identify an endpoint or error-code meaning.
7. **Exactly one private HTTP request** was observed: discovery. No token/session/credential request reached either listener. No auth success, character/world selection or REP/DTLS handshake occurred. Result204's meaning on this build is **unknown**; historical notes about203 cannot explain it.

## Current schema and substitutions

Public account-independent resource: `https://d2c74t4zimux3r.cloudfront.net/STEAM_APP_ID.1063730.json`; successful read16:39:50.990626Z, HTTP200, `application/octet-stream`,5404bytes/SHA256`a09098b6c061de4499fc2b7e666c5f1c48ff60016c4bc95958aea271312ba4a9`. Read-only normal public retrieval; no authentication, query or credentials. Two preceding retrievals were discarded by too-strict local MIME/key guards, not demonstrated server failures. This source is **not a wire capture from NewWorld.exe**.

Observed layout: `channelName`; five regions `fra-prod/gru-prod/iad-prod/pdx-prod/syd-prod`; `platformMetadata`. Regions contain `displayName`, `localizedName`, `poolId`, `publicApis`. Four API tags: `authStack`, `loginGateway`, `JavelinGatewayServiceV2`, `JavelinGatewayService-CF`, each with region/version/hostname/tag; stage`prod` exceptCF. `iad-prod` lists loginGateway beforeauthStack. Platform contains Steam entitlement app and Omni's `omniTokenUrl`, **`nwTokenUrl`**, stage/gamealias. Requiredness of every field is not established by successful full-shape parsing.

Original [local template](../tests/fixtures/connectivity/local-channel.json) preserves these observed fields/types/tag order/constants. It deliberately replaces display/localized names with local markers, pool identifiers with regional zero UUIDs, every API hostname with the redirected bootstrap name, and both token URLs with that same origin. These are **controlled local substitutions**, not captured official values. Every advertised destination must pass the strict validator before binding. No private-account, JWT or auth response format is invented.

First Light `63756a3` builder (`server/auth_mock.py:197-233`) returns an existing captured descriptor unchanged; absent it, its synthetic fallback has only two API tags and lacks current `nwTokenUrl`/entitlement metadata. It does not rewrite endpoints. It was not reused verbatim.

## Reproduce this exact stopping point

Only our legitimate client/owned infrastructure; perform live actions separately from offline validation.

1. Run `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_channel_descriptor.py tests/test_bootstrap_probe.py tests/test_bootstrap_log_metadata.py` (48checks); run validated `scripts/Test-ConnectivityProbe.ps1` for original19/26, CLI and observer controls.
2. Require no running NewWorld/test listener. Generate a fresh private CA/leaf for the one bootstrap hostname and IP SANs using `scripts/connectivity_probe.py certificates`; copy the original local template to that ignored run directory. Validate every PowerShell helper using `Invoke-CodexPowerShell.ps1` before execution.
3. Prepare a fresh hosts journal via `scripts/Set-ConnectivityHosts.ps1 -Action Prepare`. Start `scripts/bootstrap_probe.py` once per `127.0.0.1` and `::1`, port443, duration600, supplied certificates/descriptor/private JSONL path, `--observe-local-socket-owner`. Verify the real Python listener child PIDs/parentage, not only venv launcher PIDs.
4. Run validated/elevated `scripts/Invoke-BootstrapTrialWindow.ps1 -RunDirectory <ignored-run> -IPv4ListenerProcessId <actual-v4-owner> -IPv6ListenerProcessId <actual-v6-owner> -Seconds 300`. It installs only an owned **NewWorld.exe** outbound rule, checks all-profile/all-protocol IPv4/IPv6 ActiveStore scope, maps/resolves bootstrap toloopback and logs ready. Microsoft documents [program/address filtering](https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule). This is policy readback, **not a packet-level proof of blocking**; Steam/EAC/other helper processes are not filtered. No global proxy/DNS/driver changes.
5. Import only the fresh CA into CurrentUserRoot via validated `scripts/Use-ConnectivityTrust.ps1`; require readback1. Ordinary `steam.exe -applaunch 1063730` after pinning installed hash and confirming zero existing clients. Record exclusive fresh name/PID/UTC-start-time and launch boundary in `<run>/owned-client.json` (keys`process_id/start_time_utc/launch_boundary_utc`). It is required for cleanup. If live Path is available, it must match the installed target. No assetprocessor/game flags, memory/hook/binary/EAC changes.
6. Observe private requests. Extract only safe markers/numeric codes with `scripts/bootstrap_log_metadata.py --source <our-Game.log> --output <ignored-exclusive-json>`. Tie output to fresh process, private response hash, replaced session log and local markers. Actual marker times remain unknown. Do not describe HTTP200 alone as acceptance or raw generic loading as world entry.
7. Signal `<run>/stop.request` or let the300-second deadline expire. Guard stops **only recorded PID/start-time** and verifies no client remains **before** hosts restoration and owned-rule removal. On ambiguous identity, it retains containment and records cleanupblocked; do not remove protection while a client survives. Ordinaryfinally handles errors/deadline, not forced OS termination. Reconcile ownership journals after interruption.
8. Verify byte-exact hosts restore, owned rule absent, exact CA removed/readback0, owned listenersclosed. Only recorded listener children may be stopped; trial used guarded controller termination rather than a graceful `BOOTSTRAP_STOPPED` event. Preserve unrelated processes/trust/hosts/editor files.

Executed cleanup: client stopped17:00:33.2356299Z; hosts/rule restored17:00:34.3381375Z; CA removed17:03:14.5970578Z; listeners absent17:03:16.4419132Z. Hosts SHA256`7c0d9bdf4d52255a757f4e1fa235c39a65701b26ec7b2c5aae8975539a4cc708` matches before.

## Exact next blocker / capture before shutdown

**Observe current Omni CreateSession's actual destination/handshake on our infrastructure.** Collapsing advertised token hostnames into bootstrap did not produce a session request; hardcoded/provider-derived hostname, local validation, helper behavior, pool substitution, and transport/trust differences remain hypotheses. Result204 is not enough to choose one.

Next controlled hypothesis: preserve the two **observed original token URL hostnames** (`tokenservice.amazongames.com`, `prod.newworld.com`) while redirecting both to owned loopback with correct certificate SANs and program-specific containment. They appear in the public descriptor; that does not prove this build actually contacts them. No official request forwarding or auth-success fixture will be used. If an HTTP request reaches us, retain only method/fixed-route/header-presence/body-length/handshake metadata, not Steam tickets, cached fallback tokens, cookies or identities. Private auth response schema/validation is a separate later task.

Capture normal own-session route order and numeric successful/failure transitions while official services exist; do not harvest successful tokens for replay. Own DNS/connection/SNI observations would discriminate hardcoded/default endpoint selection from ignored metadata; process-scoped instrumentation must not capture another user's traffic. Actor/spawn implementation remains blocked by private session selection and separate REP/DTLS trust.
