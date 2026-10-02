# Current-client connectivity gate

## Result and acceptance boundary

**Current New World client connectivity has NOT been demonstrated. No current client build was tested.** No legitimate executable was found in the discovered Steam libraries, no matching process was running, and the checked conventional config directories were absent. This is a bounded search, not proof that no copy exists anywhere. The explicit installation-path question is pending. See [discovery receipt](../research/evidence/current-client-discovery.json) and `scripts/Inspect-CurrentClient.ps1`.

The new original HTTPS probe works with **Python control clients** on IPv4/IPv6 loopback. Its tests prove that the measurement apparatus distinguishes validated requests, untrusted CA and hostname mismatch. They do **not** establish New World's endpoints, trust provider, pinning, authentication, world loading or game transport. See [control receipt](../research/evidence/connectivity-validation.json).

**Installation follow-up (October 2 UTC):** User authorized downloading their library copy. The existing, validly signed Valve Steam client was sent `steam://install/1063730` at 06:59:07 UTC. At 07:04:10 UTC the configured library still had neither the app manifest nor a partial-download directory, so only request dispatch—not download/entitlement/install success—is established. Native Steam-window control is unavailable in this session; the browser account page was signed out. A precise user handoff to complete Steam's Install dialog is pending. No credentials were read or entered. See [install-attempt receipt](../research/evidence/steam-install-attempt.json). This does not alter the current-client TLS/spawn gate.

To pass this gate, pin the actual owned client build/hash, associate its process/socket with the probe's connection, and demonstrate a decrypted request. To additionally claim **certificate validation solved**, inspect the unmodified client's validation outcome and exercise negative CA/hostname controls against our endpoint. Even decrypted HTTP cannot tell the server whether the peer verified its certificate: a deliberately permissive **Python-only negative control** also reaches HTTP 200. No such bypass was applied to the game. HTTPS acceptance alone also does not solve the separate REP/DTLS trust gate. Spawn work remains gated on the required current-client connectivity; no spawn protocol or gameplay implementation was added.

## Evidence identities

| Evidence | Identity / scope |
|---|---|
| Starting workspace | Local `main`, `c77b3c962fd9eaf28b7b2ba25217e0e34ef23903`, clean before this connectivity slice. New scripts/tests are original; control receipt hashes their exact tested bytes. |
| Existing First Light | Clean external source `63756a3f7ff0ae41752dcc7c80267802c3fa7548`; unchanged. Source references below are paths inside `research/upstream/first-light`, not our redistributable code. |
| Client discovery | October 2, 2026 UTC receipt; registered Steam libraries + existing conventional C/D Steam roots + eight config-directory existence checks. No client files/logs copied and no launch. Additional bounded filename searches in discovered Steam/common and conventional D locations found no executable. `D:\Code\NewWorld` contains a small JavaScript/data project, not the client. |
| Probe runtime | Isolated workspace Python 3.11.9; exact OpenSSL runtime and source/fixture hashes in control receipt. Generated CA/leaf and request logs stay in ignored temporary directories. |
| Fixtures | `tests/fixtures/connectivity/requests.json` is independently written synthetic HTTP, **not a game capture or current response schema**. No New World request/handshake fixture exists. |

Existing ecosystem findings remain in [First Light analysis](FIRST_LIGHT_ANALYSIS.md); they were not repeated. The previously passing upstream protocol profile is unchanged.

## Observed endpoint flow

### Current client: unknown

| Stage | Current observation / evidence |
|---|---|
| Startup | No executable/build identified, no running `NewWorld` process; discovery receipt. No launch. |
| Endpoint selection/configuration | Unknown; current client files and local config were unavailable. No supported CLI parameter has been established. |
| Hostnames / DNS | No current-client DNS query or endpoint observed. An operator `.NET Dns.GetHostAddresses('localhost')` control returned `::1` and `127.0.0.1`; it does not establish the game's resolver, cache or IPv6 policy. |
| Connection attempt | No current-client-owned socket observed. Probe accepts control sockets only. |
| TLS / SNI / certificate | Unknown for current client. Python controls provide SNI `localhost` with hostname connections, and no SNI for literal IP SAN connections. |
| HTTP/bootstrap/API | No current client request received; exact method/order/schema unknown. |
| Authentication request/response | Not observed. Probe does not authenticate. A synthetic historical-route request receives diagnostic HTTP 501. |
| Character/world/session selection | Not observed or implemented by probe. |
| REP game transport | Not observed; probe is TCP HTTPS, **not** a UDP DTLS responder. |

### Historical First Light path: source-supported leads, not current observations

`docs/connection-flow.md:1` explicitly attributes its flow to **Game.log 2025-12-27**. `server/auth_mock.py:10-40` attributes its host list to channel configuration and a game log. The hardcoded redirection/certificate lists are manually maintained, not live discovery (`tools/setup_hosts.py:28-59`; `tools/generate_auth_certs.py:26-82`).

| Historical stage | Endpoint / behavior | Evidence |
|---|---|---|
| Channel discovery | `https://d2c74t4zimux3r.cloudfront.net/STEAM_APP_ID.1063730.json` | `docs/connection-flow.md:6-19`; mock route `auth_mock.py:1343` |
| Regional service choice | JSON supplies regional auth/API/gateway hosts. Mock loads `capture/channel_config.json` if present; otherwise synthetic US-East auth/US-West gateway fallback. | `auth_mock.py:197-233,761-763` |
| Credentials | `/prod/credentials/omni` on historical regional gateway, e.g. `d3bj4csovi1fe8.cloudfront.net` | `docs/connection-flow.md:28-43`; `auth_mock.py:1346-1347` |
| Login information | `/prod/game/getlogininfo` returns world/character information in historical mock | `auth_mock.py:895-993,1359-1360` |
| Queue/session ticket | `/prod/game/login/queue...` / older `/prod/users/login_queue...`; ready-ticket response contains REP address | `auth_mock.py:258-314,547-589,777-892,1353-1354` |
| Ancillary HTTP | Entitlement, remote-config, content, token-service/JWKS/OpenID routes | `auth_mock.py:1377-1399`; HTTP route handlers are not proof of actual HTTP/2/gRPC support |
| Game connection | Separate UDP REP endpoint, historically `127.0.0.1:23971` when redirected by the mock | `auth_mock.py:78-81,1561-1564`; `server/rep_responder.py:167-175,316-382` |

Historical regional gateway names from `docs/connection-flow.md:12-18`: `d1w0bfy6smo4d1.cloudfront.net` (EU), `d1cjlmzk0xrm0z.cloudfront.net` (SA), `d2oeuvxi3kfsrw.cloudfront.net` (US-East), `d3bj4csovi1fe8.cloudfront.net` (US-West), `de4mfzk9wkelz.cloudfront.net` (AP). Historical auth endpoints are API Gateway names listed in that document. **None has been contacted or identified as current here.** Avoid treating this list as a safe shotgun redirect recipe.

## TLS/certificate observations

| Claim | Status / source |
|---|---|
| Probe leaf has local CA signature, explicit DNS SAN(s), loopback IP SANs and server-auth EKU | Generated independently by `connectivity_probe.py::generate_certificates`; seven-day lifetime; CA private key not saved. No Amazon subject impersonation. |
| Python trusts correct CA + SAN and rejects untrusted CA / wrong SAN | Executed control tests, TLS 1.2 and 1.3; actual socket handshakes/requests, not context construction alone. Wrong-host control verifies X509 hostname-mismatch result. |
| Current New World accepts local/self-signed certificates | **Unknown.** Controls load the CA in a Python SSL context only; no Windows trust store was modified. CA-signed leaf control does not test a self-signed game certificate. |
| HTTPS uses Windows trust store | **Unknown for current game.** Historical certificate generator merely prints `certutil` instructions (`generate_auth_certs.py:9-13,146-147`). |
| Current game has certificate pinning | **Unknown.** A fatal `unknown ca` would indicate trust failure but by itself would not distinguish bundled roots, missing local trust, pinning, hostname policy or other validation. |
| Historical REP certificate failure | `docs/dtls-trust-bypass.md:7-14` reports local DTLS `unknown ca` and game transport-security error. Later runtime-patch claims are historical and unexecuted here, not proof about stock/current executable behavior. |
| HTTPS and DTLS are the same trust path | **Unsupported.** Separate TCP/UDP implementations; installing an HTTPS CA does not establish REP trust. |
| SNI is equivalent to DNS redirection | **No.** Probe controls connect to loopback while supplying a separate hostname for TLS validation/SNI; DNS selection and TLS identity must be measured separately. Current game behavior remains unknown. |

The probe uses standard [Python SSL contexts/SNI callbacks](https://docs.python.org/3.11/library/ssl.html), not a custom TLS implementation. SNI identifies a requested hostname during TLS negotiation, independent of the address reached ([RFC 6066, section 3](https://www.rfc-editor.org/rfc/rfc6066#section-3)). TLS failures may precede any HTTP request; record the phase and OpenSSL alert mnemonic, not a guessed game state ([RFC 8446, section 6](https://www.rfc-editor.org/rfc/rfc8446#section-6)).

## Redirection options and failed approaches

| Option | Tested? / conclusion |
|---|---|
| Explicit loopback socket + separate TLS hostname | **Python controls only:** works with matching trusted CA/SAN; rejects wrong hostname and unknown CA. No game endpoint override proven. |
| Current client configuration / CLI endpoint override | Not tested: executable/config unavailable; no evidenced supported override in inspected First Light tools. Do not invent command-line switches. |
| Single observed-host Windows hosts mapping | Not applied. Historical tool adds IPv4 and IPv6 mappings; current applicability unknown. Requires exact observed host, guarded backup/readback/revert and ensuring only our own client is affected. |
| Local DNS override | Not tested; no current client resolver/caching behavior observed. Mapping to an IP does not solve certificate identity. |
| Local CA in user trust store | Not installed/tested. Prefer scoped/current-user trust if the identified stack uses it; record exact certificate thumbprint and remove only the certificate we introduced. No blanket CA-store edits. |
| HTTP(S) proxy | Not configured/tested. Current client proxy support and HTTP/2 requirements unknown. Probe never proxies or forwards traffic. |
| UDP redirect / DTLS responder | Not run in this slice. Requires authenticated game's actual REP address/handshake evidence, separate from HTTPS. |
| Binary/hook modification | Not performed or justified by current evidence. Missing client access is not a reason to bypass trust. Historical patches are not part of this test procedure. |

**Executed failures:** untrusted-CA and wrong-hostname **control** handshakes; cleartext sent to the TLS listener; ambiguous/unsupported HTTP body framing. The service records alert/rejection metadata without secret contents. **No failed New World redirection experiment has occurred.**

An added control run also exposed a Windows timing difference: an untrusted TLS 1.3 client reported certificate verification failure, while the server saw `ConnectionResetError` rather than `unknown ca`. The original overly specific test assertion failed (18 passed / 1 failed), and was corrected to require the exact **client** issuer-validation error and no HTTP, while preserving the actual server failure reason. A reset alone must not be diagnosed as certificate pinning or CA failure. Historical failed-run diagnostics remain ignored/private.

## Minimum service and structured transitions

The implemented service is sufficient to answer a narrower measurement question: *does an identified client reach our loopback TLS server, validate its certificate, and send an HTTP request?* It is **not** sufficient to advance authentication or world loading. The minimum current-client bootstrap service set remains unknown until that client can be observed.

Every probe event has UTC timestamp, schema, run ID, connection UUID and sequence. Events flush as JSONL; no raw URI/query, account ID, headers, tokens, cookies or bodies are exported. Only allowlisted hostnames and route classes are retained. Unknown paths/hosts are redacted. One request per connection, bounded body discard, short socket timeout, loopback-only binds and bounded process lifetime. HTTP/1.1 only; offered ALPN list, full ClientHello extensions and game protocol are not decoded. A client requiring HTTP/2 would need an evidence-led extension, not a fabricated gRPC response.

| Requested transition | Instrumentation / truthful limitation |
|---|---|
| `CLIENT START` | `Observe-CurrentClient.ps1`: matched executable process, PID, actual start timestamp and executable hash. Does not launch game. Syntax validated; no actual game run yet. |
| Endpoint resolution | **Not observable by TLS listener.** Own-process DNS tracing / sanitized own-client config/log evidence is still required. Operator DNS control must be labelled as such. |
| Connection attempt | Observer samples only matched PID's TCP table, with local/remote four-tuple and TCP state. Probe records accepted socket separately; absence may mean a missed short-lived attempt, not proof of no attempt. |
| TLS/session establishment | `TLS_CLIENT_HELLO` from OpenSSL SNI callback; `TLS_ESTABLISHED` with negotiated version/cipher/ALPN; `TLS_FAILED` with phase/reason. Callback is not a full handshake capture. |
| Authentication request | `HTTP_REQUEST` plus `AUTHENTICATION_REQUEST` for allowlisted historical credentials route. Route label is historical inference, not validation of current semantics. |
| Authentication response | HTTP 501 + `AUTHENTICATION_RESPONSE`, explicitly `authentication_success:false`; no fake successful login. |
| Game-server/session selection | Historical queue/login-info request is logged as `GAME_SESSION_SELECTION_REQUEST`. No selection response or `GAME_SESSION_SELECTED` is emitted. |
| Game transport connection | **Not instrumented/observed by this HTTPS-only slice.** Requires subsequent owned REP/DTLS test; no success event is fabricated. |

The observer polls at 500 ms, cannot see payloads/TLS or UDP remote peers and cannot attribute DNS. Match observer/probe four-tuples and timing before attributing a request to NewWorld.exe; `client_identity:"unattributed"` is deliberately the probe default. Do not equate a browser/curl/Python request with game success.

## Exact reproducible procedure

### A. Verified local controls, no installed game required

From `C:\Code\NewWorldPreservation`, using the existing pinned `.venv`:

```powershell
& 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1' -Path .\scripts\Inspect-CurrentClient.ps1 -Execute
& 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1' -Path .\scripts\Test-ConnectivityProbe.ps1 -Execute
& 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1' -Path .\scripts\Test-FirstLight.ps1 -Execute
```

The probe profile runs 19 scoped tests, then `scripts/verify_probe_cli.py`: generate a fresh local CA/SAN leaf, start a hidden child probe on an ephemeral loopback port, use explicit CA+hostname validation to send `GET /__probe/health`, require HTTP 200, wait for automatic stop, verify child exit 0 and closed listener. The test runner emits safe summary counts only; raw diagnostics/JUnit stay ignored. [CLI receipt](../research/evidence/connectivity-cli-control.json) records request, certificate fingerprint, script hash, progression and cleanup. No hostname redirect, Windows certificate import, game launch or external service is involved.

### B. Standalone diagnostic listener

Generate once in a **new** ignored directory; reuse that exact certificate directory across trust/hostname controls. Existing certificate directories and logs are refused rather than overwritten:

```powershell
& .\.venv\Scripts\python.exe @('scripts/connectivity_probe.py', 'certificates', '--directory', 'private/connectivity/manual-01/certificates', '--hostname', 'localhost')
& .\.venv\Scripts\python.exe @('scripts/connectivity_probe.py', 'serve', '--certificates', 'private/connectivity/manual-01/certificates', '--log', 'private/connectivity/manual-01/events-v4.jsonl', '--bind', '127.0.0.1', '--port', '8443', '--duration', '60')
```

For IPv6 use `--bind ::1` and a distinct log. Two listeners may run in separate terminals on their respective loopback addresses with the same certificate directory. Binding an all-interface/remote address is refused. Port collision fails without stopping any existing process. The probe supports a specified port, including 443, but **443 was not tested** and should only be used once the actual client URL/port is known and the listener is free. DNS mapping cannot change a URL's port.

`--hostname` is repeatable to issue SANs for **observed** client hostnames in a future controlled redirect. No arbitrary upstream host list is installed, resolved or contacted by certificate generation. Logs and private keys must stay private, even if future client traffic arrives. The listener is intentionally not an auth mock; HTTP 501 is its application-path stopping point.

### C. Resume with the actual legitimate client: pending, not executed

1. Supply/locate the actual `NewWorld.exe`, then pin it with the script's explicit-path parameter. Steam build ID is recorded when available; file version/hash is recorded regardless. Verify the path belongs to the legitimate current install. **Do not substitute First Light's historical build string.**
2. Start the bounded observer before an ordinary user-owned launch. It does not read Steam account configuration, game logs, credentials, request payloads or other processes' connections:

```powershell
& 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1' -Path .\scripts\Inspect-CurrentClient.ps1 -Execute -ArgumentList @('-ClientExecutable', 'ACTUAL_FULL_PATH_TO_NewWorld.exe')
& 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1' -Path .\scripts\Observe-CurrentClient.ps1 -Execute -ArgumentList @('-ClientExecutable', 'ACTUAL_FULL_PATH_TO_NewWorld.exe', '-LogPath', 'C:\Code\NewWorldPreservation\private\connectivity\owned-client-01.jsonl', '-Seconds', '60')
```

3. Establish the attempted hostname/config source using only this client's safe metadata. TCP-table IPs are not hostnames. Process-attributed DNS tracing and a whitelist extractor for this build's own log/config are **not yet implemented/validated**; do not use an unfiltered machine-wide packet capture or copy raw credential-bearing logs into the repository.
4. Prefer an evidenced supported endpoint configuration/CLI option. If none exists, redirect **one observed** bootstrap hostname to the matching loopback listener(s), with a separately guarded script preserving unrelated hosts entries and a documented restoration. No broad historical-host mapping has been prepared/applied. Keep default official access unchanged outside the controlled experiment.
5. Test the local leaf without importing trust first. Record exact game failure + server alert/reset. If the identified TLS stack uses the Windows user store, test the same CA after a narrowly scoped import; verify that exact fingerprint and later remove only the introduced certificate. If it uses bundled roots/pinning, record that evidence before considering narrower interoperability work. This conditional step has no tested current-client recipe yet.
6. Correlate matched process PID/hash and TCP four-tuple with probe request events. Compare correct-CA/SAN, untrusted CA and wrong-name controls **against our endpoint**, preserving the client's executable. A request proves application connectivity; validation policy requires these additional observations. Export only sanitized current-build request/handshake metadata with provenance into fixtures.
7. Only after this gate is truly met, identify the minimum bootstrap/selection replies and separate REP handshake. Do not turn 501, SNI alone or an old replay into successful authentication. If world-loading/actor existence is reached later, stop expansion and document it. No spawn work may start from the Python control result.

Steps C3-C6 cannot be made precise for the current client until its installation/build exists locally; this is the exact remaining prerequisite, not an inferred pinning failure.

## Current-client differences from First Light

Actual wire/build differences are **unknown**. The known differences are our evidence and tooling: current build unpinned/unrun; historical flow dated; HTTPS probe loopback-only and secret-minimizing; no success-synthesizing auth mock; no broad hosts/CA edits or trust hook; separate HTTPS and DTLS acceptance gates. The historical `omnisdk-notes.md:102-108` claim of 34 certificate SANs disagrees with 28 entries in the pinned generator (`generate_auth_certs.py:28-82`), further reason not to trust old setup counts blindly.

## Verification review / unresolved questions

- Independent tester at starting HEAD + probe SHA-256 `bfddc360269c7d2756b0d2a85cc9a5c9657eadd9439ada40950afdda34e0532a` exercised wrong CA/SAN, malformed/error-path secret markers, absolute-form URL with a loopback no-forwarding sentinel, failed auth/queue responses and IPv6. No secret leak or forwarding reproduced in those cases; this is bounded evidence, not exhaustive proof. Server event ambiguity was reproduced by a deliberately unverified **Python-only** control. Two useful falsifiers were promoted into tracked tests; the probe source stayed unchanged.
- Base Python HTTP parsing accepts some malformed header shapes; this diagnostic does not claim complete strict HTTP validation. Ambiguous body framing is explicitly rejected. No HTTP/2, game-specific parser, actor or gameplay codec was modified.
- CLI lifecycle control verifies real process start/stop and listener closure; observer is syntax-validated only, not tested with a legitimate client. Existing upstream tests must remain green; exact current receipts are linked above.
- **Missing:** installed client's exact build/hash, live endpoint/config chain, resolver/cache/IPv6 behavior, SNI and offered TLS/ALPN, trust provider and pinning evidence, acceptable bootstrap/auth schemas, session-selection response and REP trust behavior.
- **Exact next blocker:** access to the legitimate installed current executable (installation path or installation), then its first process-attributed controlled HTTPS attempt. There is no evidence-based reason to modify a binary or diagnose hardcoded trust yet.
- **Actor/spawn work can begin? No.** `SPAWN_SEQUENCE.md` is deliberately not created before the user-required connectivity gate. Milestone 1 and world-loading remain unachieved.

## Capture Before Shutdown: connectivity-specific priorities

Only our own normal legitimate sessions; no credential acquisition or traffic from others. After a client is available, prioritize: exact executable/build identity; startup configuration URL/source and regional selection; normal endpoint names/ports/fallback order; DNS vs cached resolution and IPv4/IPv6 choices; SNI/TLS/ALPN and public certificate chain identity; redirects/HTTP status/content types and sanitized route ordering; account-independent channel metadata; queue/world selection dependencies and REP address handoff; observed failure/retry/timing/state transitions. Store secrets neither as fixtures nor ordinary logs. Own encrypted traffic may show timing/length but does not establish plaintext schemas. These items are requested future observations, **not captures already made**.
