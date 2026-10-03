# Current REP DTLS trust and Carrier/V3 registration

> Latest October 3 comparison: the certificate-data candidate was refused at launch by intact EAC (“Unrecognized game client” / “Unknown file version”). After exact stock restoration, a matched elevated original-launcher control reached private queue200 and returned two more fatal `unknown_ca` alerts. Eight alerts across four stock runs; **no private game DTLS, Carrier/V3 or actor**. Final stock hash/signature/hosts verified, temporary resources absent, same CA retained. [Live receipt](../research/evidence/private-rep-anchor-eac-control.json). Earlier metadata failure/canceled elevation remain separate historical outcomes, not explanations for this refusal. The on-disk substitution route is retired; investigate unchanged-client configuration instead.

## Scope and current evidence boundary

Continuation of [private queue handoff](PRIVATE_GAME_HANDOFF.md), clean parent HEAD `4bf6511468fa66d3935fca5859b2657c3ca3183b`. Target unchanged stock Steam22469132 / version1.400.6031.6004151 / installed SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`. Prior own client reached selected127.0.0.1:64003 and sent ClientHello-header observations; prior observer sent no replies. This alone did not test certificate trust.

Work in this slice: verified local DTLS peers, owned current-client handshake/trust, then current Carrier/V3 **only if transport succeeds**. No actor/gameplay implementation, memory writes, executable/EAC change, other-user traffic, official-system authentication bypass, remote publication or mouse/keyboard control.

**Newer static checkpoint:** [REP_TRUST_POLICY](REP_TRUST_POLICY.md) identifies current embedded-certificate transport→store initialization, the actual linked verifier/identity inputs and the same-object factory→connection→secure-setup path. This supersedes the initial unlinked-candidate findings below, not the live rejection. Actual REP context attribution/private-root configuration remain unproven. No additional game trial, bypass or protocol implementation;39 previously validated artifact hashes unchanged.

## Evidence ledger for this slice

| ID | Claim | Classification / limit | Evidence |
|---|---|---|---|
| D36 | Two isolated local DTLS clients verify the retained CA and exchange distinct payloads | Executed with normal and reversed completion order; presented-leaf-as-anchor control raises certificate verify failed and sends no application data. Not New World trust or hostname verification | Ignored `.scratch/dtls-local-exchange/probe.py`, results.json, experiment-report.md and validated run.ps1; fresh ephemeral127.0.0.1 sockets all closed |
| D37 | Existing Python DTLS BIO setup is a reusable integration boundary | Source-supported, clean First Light63756a3: per-source-tuple SSL.Connection/accept/feed/handshake/drain; server VERIFY_NONE means no client-certificate authentication, **not** a client trust bypass | `server/rep_responder.py:167–177,275–283,316–364,1308–1334`; no source vendored |
| D38 | Historical responder does not explicitly drive DTLS timers and emits unsafe raw logs for this task | Source-supported: no DTLSv1_handle_timeout call; record/parse-error/V3 payload dumps and identity/token logging. Do not run this responder unchanged | `rep_responder.py:433,451,601–613,631,673,768,771,1138`; old dtls_bridge one-client/WIP |
| D39 | Current-client REP trust differs from the successful private HTTPS result | **Observed rejection:** full configured leaf+retained-root flight followed by incoming fatal unknown_ca on both current-game attempts. CurrentUserRoot trust alone is insufficient for this tested path; exact active roots/pinning still unknown | [Current trust receipt](../research/evidence/current-dtls-trust-rejection.json); no trust/binary/memory changes |
| D40 | Original responder and portable controls preserve workspace regression | Executed268 pass/no failures/errors/skips;7 new actual-local/mock-error tests. Independent retained-CA experiment remains separate; no game acceptance | [Validation receipt](../research/evidence/dtls-local-validation.json),23explicit modules/36source hashes |
| D41 | Current game and owned responder exchange DTLS handshake/alert traffic | Observed two159byte ClientHello-header datagrams, two2516byte server flights and two15byte incoming fatal-unknown_ca records; both SNI callbacks report present=false; no completed handshake/application data | [Sanitized metadata fixture](../tests/fixtures/connectivity/current-dtls-trust-rejection.json), responder SHA13e73462791543f65bd0b328dc5f8d2d52c729e629df65f7d0cd244f204b8611 |
| D42 | `(2)` popup correlates with the incoming alerts | User report plus owned Game.log fixed mm_csdkerr_transport_security_error(2) at lines464,465,474,476. Log extraction timestamps are not source event times | Game.log SHA0742fcc46d9c5334d22be9d4d268eb7f46d24997e4ca110ce9e37135c376cd6d; receipt/parser tests |
| D43 | Certificate-file/directory environment handling exists in linked client code | Source-supported inference from current hash-pinned PE keys/callers/fallbacks; **no REP invocation established** | Bounded static map below; ignored original inspector hashes in controls receipt |
| D44 | A parsed embedded certificate has an indirect data reference | Static X.509v1/self-issued/other-CN candidate, no BasicConstraints; use by one function established, **DTLS/trust role not established** | Region/pointer/function map below; no PEM/name/client code exported |
| D45 | Launcher CA-file candidate did not establish DTLS | Two comparable vendor-launcher cases each receive two read/fatal/unknown_ca alerts/no app. Game parent is launcher; runtime environment was **not** read back, so not proof the setting was consumed/ignored | [Controls receipt](../research/evidence/current-dtls-trust-controls.json) |
| D46 | Public Lumberyard trust-descriptor code is not linked to this current build by the tested discriminator | Exact three supplied diagnostic-name strings absent in ASCII/UTF16LE scan. Not proof the engine code is globally absent | Public source link and failed discriminator below; current binary hash unchanged |

The original local experiment uses Python3.11.9 / pyOpenSSL26.4.0 / cryptography50.0.2, the same installed dependency lock as the workspace. Both clients negotiated First Light's `ECDHE-RSA-AES256-GCM-SHA384` with separate server states. Test CA/leaf PEM-file hashes differ from DER fingerprints; compare like formats. No certificate/private key was copied into the test scratch folder. Its negative trust source was the presented leaf itself, not an unrelated CA; failure is scoped to those verification flags. The separate portable responder tests use temporary certificates, not game sessions or installed trust.

## Owned responder design and observability

Use existing pyOpenSSL memory-BIO boundaries in an original loopback-only diagnostic, not First Light's raw-logging responder or an OpenSSL subprocess bridge. Each source tuple owns an independent connection/state and outbound encrypted BIO route. OpenSSL, not a speculative New World codec, implements the handshake and encryption. Explicit public timeout handling covers timer-driven handshake retransmission; actual loss behavior must be tested separately.

Reuse `private/connectivity/retained-test-ca.json` certificate_directory, `server.pem`, `server.key`, `ca.pem`; never print key/PEM bytes. Startup leaf/root DER fingerprints describe **configured** material, not a wire capture or proof of certificate transmission. Record whether the root chain is supplied separately from actual output/peer evidence. Same CurrentUserRoot thumbprint `1AEE2B69AD82A5C6F2CF52A80127D22A4487CECA`, expiry2026-10-09T18:58:22Z; no import/removal/new approval. Configurations differ only where explicitly documented.

Required timestamped evidence: fresh Steam/PID/start identity; queue HTTP200/hash; received UDP bind-owner readback (not exact flow); handshake state changes; outgoing encrypted byte counts; optional SNI presence/class with unknown values discarded; SSL alert direction/level/description; negotiated version/cipher on server completion; decrypted application **length only**; timeout/close and client-first cleanup. Server completion alone must not be promoted to gameplay/authentication or a final client trust decision. A no-response timeout is not pinning proof.

Protocol/library references: [RFC6347](https://www.rfc-editor.org/rfc/rfc6347.html) for DTLS framing/handshake flights, and [pyOpenSSL SSL API](https://www.pyopenssl.org/en/stable/api/ssl.html) for BIO, info callbacks and DTLS timeout methods. These describe standard DTLS/library behavior, not New World packet schemas.

## Current-game outcome: full-chain trial

Clean exercised HEAD880662a829eb3f941426e322882d32d9e4a4c29b; no source edits during live execution. Same legitimate installed build/hash and retained CA as above. Fresh normal Steam launch21:44:35.558Z, owned PID34940/start21:44:39.910Z. IPv6 HTTPS443 receives queue-v2/omni, returns the unchanged synthetic829byte200 at21:45:12.584Z. Selected game destination remains127.0.0.1:64003.

First DTLS input21:45:12.758Z; OpenSSL writes server_hello/certificate/key_exchange states and emits2516bytes. At21:45:12.759Z, an incoming epoch0 alert record (15byte datagram,2byte record body) is decoded by OpenSSL as **read/fatal/unknown_ca**. Peer closes without establishment. A second ClientHello at21:45:12.778Z gets the same flight and explicit alert. IPv4 bound-port owner is the fresh game PID; this is not an exact-flow trace or live executable hash. No SNI is present in either callback. DTLS1.2 record version is a header observation, **not a negotiated session version**. Leaf/root fingerprints identify configured material; no separate DER-on-wire comparison was performed.

User-visible result: **“A secure connection could not be made. Please restart or update the game and try again. (2)”**. Our extractor exports only the matching fixed SDK code/value and line numbers, never raw error text or account/session values. No application/Carrier/V3 record was received. This differs from the old receive-only timeout: our server answered; the game rejected the presented chain. It does **not** alone prove leaf pinning, a particular embedded CA, hostname validation behavior, or that Windows roots are globally ignored.

```mermaid
stateDiagram-v2
    [*] --> SyntheticSelection
    SyntheticSelection --> PrivateQueue200: user Play
    PrivateQueue200 --> ClientHello: selected127.0.0.1:64003
    ClientHello --> ServerCertificateFlight: original local responder
    ServerCertificateFlight --> TrustRejected: incoming fatal unknown_ca (observed twice)
    TrustRejected --> SecurityError2: owned log and user popup
    ServerCertificateFlight --> DTLSReady: NOT reached
    DTLSReady --> CarrierConnect: gated
    CarrierConnect --> V3Registration: gated
```

Cleanup verified: client stopped21:46:13.420Z **before** hosts/firewall restoration21:46:14.520Z; HTTPS absent21:46:26.341Z; DTLS64003 absent21:46:32.653Z. Final readback21:46:39.750Z: original hosts SHA7c0d9bdf4d52255a757f4e1fa235c39a65701b26ec7b2c5aae8975539a4cc708, owned rule absent, no game/443, same CA Root count1. CA intentionally retained. No attachment, memory access, cursor/keyboard control, executable/EAC modification or raw capture export.

## Exact current-workspace reproduction

1. Require no running NewWorld and no443/64003 listeners. Verify pinned installed SHA/build, clean checkout and unchanged candidate file/canonical response hashes in the prior handoff document. Retained CA must have the exact Root entry and be unexpired; do not reimport it.
2. Validate/run `.scratch/prepare-dtls-run.ps1 -Chain full` through `Invoke-CodexPowerShell.ps1`. It creates a **fresh ignored run**, not reuse of this immutable receipt. `active-channel-trial.json` records source identities and journal paths.
3. Validate/run `start-queue-listeners.ps1`, then `start-dtls-responder.ps1`. Verify child-parent/PID/start ownership and loopback443/127.0.0.1:64003. Neither service forwards traffic.
4. Validate/run `dispatch-channel-trial.ps1`. User approves elevation with their own inputs if prompted. Require BOOTSTRAP_TRIAL_READY, exact three-name loopback resolutions and game-only nonloopback firewall ActiveStore readback **before** launch. Helpers/Steam/EAC are not filtered; this is configuration evidence, not packet-enforcement proof.
5. Validate/run `start-owned-baseline.ps1`, then immediately `record-channel-client.ps1`. Normal Steam launch, no attach/inject. User manually advances Continue, selects Preservation and clicks Play once.
6. Inspect structured `bootstrap-v4/v6.jsonl` and `dtls-transport.jsonl`. Require queue200/candidatehash, actual outgoing flight and the **incoming** fatal alert before concluding rejection. Server completion alone is not client trust acceptance. Record user screen independently. Default responder discards application bytes and cannot register/load a world.
7. Validate/run `stop-channel-trial.ps1`; require client stopped/trial closed before `close-channel-listeners.ps1`, `close-dtls-responder.ps1`, then `verify-credentials-cleanup.ps1`. Record separate UDP absence. Retain same CA; restore hosts/rule state. Never overwrite earlier run/receipt/fixture outputs.

Helpers are ignored local operator tooling, not portable deployment services. Wrapper: `C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path <full-script-path> -Execute`. Tracked responder, extractor and immutable metadata fixture are the reviewable artifacts. This fixture is **sanitized metadata, not a raw handshake replay**. Local control tests exercise real DTLS without game/OS trust changes. Current explicit regression:273 pass, no failures/errors/skips; five new fixed-code/privacy tests were added after live capture, with an expected failing pre-change test followed by14 passing focused checks. [Current validation receipt](../research/evidence/current-dtls-trust-rejection-validation.json) pins39 source/fixture hashes; unaffected268-test source hashes remain unchanged.

## Historical Carrier/V3 map — not yet current-client proof

| Boundary | Existing reference implementation | Current limitation |
|---|---|---|
| DTLS → Carrier | `parse_envelope` then `parse_datagram`; envelope plaintext0x80/proto0x01/BE16sequence | Only apply to actual decrypted current data; lengths/flags may differ |
| Connect request | Channel3, system-msg trailing ID1 | Current request not yet observed |
| Connect ACK | Historical default reliable ch3 flag0x21, body00 00 00 05 02 plus inline ACK | Envelope-sequence echo is a historical hypothesis; ack-variant CLI is ignored by sender |
| V3 request | Historical flags0xe0/0xf0 and no-length framing; strict old832bytes plus lenient identity extraction | Responder's generic flags&0x40 heuristic is too broad for a current semantic claim; real auth blob/identities must not be logged |
| V3 response | Existing 88byte codec, VLQ-length framing, default reliable ch0, optional piggyback ACK | Help says mirror request but implementation defaults ch0; success/current dependencies untested |

Sources: clean ignored First Light `server/javelin/frame.py:40–94,142–225`, `v3_request.py:111–169,295–347`, `v3_response.py:149–175`, `rep_responder.py:425–480,639–765,1069–1140`. No payloads, proprietary client code or upstream source are copied here. Parser round-trips and field names do not prove registration acceptance.

## Reproduction and gates

Offline responder checks completed:7 focused tests and full268-test regression, with temporary unrelated-CA rejection/read-fatal-unknown_ca, separate local peers, timer retransmission and socket-error controls. Corrected startup fingerprint labels and historical negative-anchor identity after targeted review. Live outcomes will be recorded separately with exact exercised source hashes. Live routing uses the prior TokenServices profile, owned HTTPS443 and selected UDP64003; only our game executable is blocked from nonloopback destinations. ActiveStore readback is configuration evidence, not whole-machine/helper packet enforcement proof.

Responder CLI: `.venv\Scripts\python.exe scripts/dtls_transport_probe.py --certificates <same-retained-directory> --log <fresh-private-jsonl> --port 64003 --duration 600 --chain full`. Bind is fixed127.0.0.1. `--chain leaf` changes the presented chain only; it does not regenerate certificates or alter trust. Default decrypted application handling records length then discards bytes, with no Carrier response. The optional callback is for later evidence-constrained integration, not enabled by this CLI.

No already-running client/listener is replaced. All helper scripts require full PowerShell validation, fresh ignored run journals and explicit process/start/parent/script ownership. Normal Steam launch; user advances Continue/Preservation/Play manually. Stop owned game before restoring hosts/firewall; stop owned responder/listeners and verify original hosts bytes/hash, rule absence and same retained CA.

Next decisions must follow evidence: local configuration/root/chain behavior first; if current private trust rejects, preserve the exact error and narrowly inspect the **current** transport trust path. Never apply an old memory hook, manufacture a certificate/signature, modify the running game's memory, or mislabel a generic popup as pinning. Actor work waits for transport/registration/private identity and current spawn evidence. Milestone1 remains unachieved.

Targeted independent review checked receipt-pinned hashes,273-test JUnit and same-peer output/read-alert ordering. The rejection/privacy claims survived. Corrected “absent callback” to “both callbacks report no SNI value.” No SNI does **not** prove endpoint-name verification is disabled. The reviewer did not rerun the game or recheck live OS state; cleanup remains the primary's executed readback.

## Non-destructive trust controls after the first rejection

Both later trials exercised clean HEADf8c9b7f150c4afe8442875753792891e32a4370d, unchanged responder/candidates and retained full chain. Started the **original installed NewWorldLauncher.exe**, not a modified executable/direct EAC bypass. Launcher SHA5a9217fafb5656c0b72b516583287ca362c3e1a87e1b5b515ad64a6402b292ec. Steam already running with legitimate installation; child-scoped SteamAppId/SteamGameId both1063730 in both cases, no Steam restart/global environment mutation. User manually advances/selects/plays. Game parent PID matches launcher in each case, but no remote environment/memory readback was attempted.

| Case | Owned launch/game | Configuration | Observed result |
|---|---|---|---|
| Original launcher/default control |22:08:10.516Z; game26168/start22:08:12.895Z, parent14364 | Child SSL_CERT_FILE and SSL_CERT_DIR unset | Queue200; two2516byte flights; read/fatal/unknown_ca at22:08:45.981Z and22:08:46.000Z; user same error(2) |
| Original launcher/retained CA file |22:12:18.545Z; game35112/start22:12:20.902Z, parent28296 | Child SSL_CERT_FILE points to same retained ca.pem; SSL_CERT_DIR unset. CA PEM-file SHA30bba23f8800ddad69f199c96746aec5eed7e5ce405e130206c630d516573b19 (not DER fingerprint) | Queue200; two2516byte flights; read/fatal/unknown_ca at22:12:56.404Z and22:12:56.424Z; user same error(2) |

This tested launch configuration did **not** solve REP trust. It does not prove the game read the variable, that the DTLS context calls a default loader, or that all CA-file configurations fail. The user additionally reported disabling NordVPN; exact change time/state were not independently captured. No VPN causal isolation is claimed. Loopback bidirectional traffic and explicit alerts identify the demonstrated failure without attributing it to a missing route.

Both cases stop the owned game before restoring hosts/rule, then stop443/64003. Default final readback22:09:55.041Z, CA-file final readback22:16:08.312Z: game/listeners/rule absent, original hosts SHA unchanged, same Root count1. Separate UDP absence receipts present. No certificate regeneration/import/removal, executable/EAC/configuration or global environment change, memory access, input takeover or proprietary/raw-payload export.

Reproduction delta to the seven-step procedure above: after a fresh prepared/responder/ready window, validate/run `.scratch/start-owned-launcher-trust.ps1` with `-ArgumentList @('-TrustSource','Default')`, then `.scratch/record-launcher-trust-client.ps1` immediately. Repeat in a **new cleaned run** using `-ArgumentList @('-TrustSource','RetainedCaFile')`. `-ArgumentList` belongs to the wrapper; each full helper is validated before execution. Both require ready-window age<=60seconds and pinned client/launcher. Normal user inputs/cleanup unchanged. Preserve `launch-manifest.json`, `trust-case-metadata.json`, filtered own Game.log hash/error codes and all structured trial/source/cleanup hashes. Do not equate child launch configuration with verified game environment consumption.

## Initial bounded current-build trust-path inspection (historical)

Reason for binary inspection: current REP explicitly rejected our approved local full chain despite private HTTPS success. Static read-only inspection of the pinned installed PE was warranted to identify configuration/trust loading, not to remove verification. No proprietary disassembly, PEM, subject name or game file is included here; original analysis-only scripts and local output remain ignored under `.scratch/current-dtls-trust-path/`.

The initial findings below retain the failed discriminator and its limits. Later positive argument/object/context analysis is documented in [REP_TRUST_POLICY](REP_TRUST_POLICY.md); the embedded certificate now has a concrete static secure-driver store relationship. The initial string-based inability to join it is not the latest result.

| Static finding | Evidence / limit |
|---|---|
| Generic environment keys |0x1477d7ed0 returns SSL_CERT_DIR;0x1477d7ef0 returns SSL_CERT_FILE. `.pdata` callers0x147bceaf0–0x147bceb80 and0x147bcf3f0–0x147bcf4b3 pass keys to0x1477aba20, select compiled fallback if null, then call0x147bcf100/0x147bcf4d0. Supports linked path handling, not its use by REP |
| Fallback strings | cert.pem,/certs,OPENSSL_CONF and build-time vcpkg certificate directory occur in PE. Actual path existence/use not established; do not create files in guessed build directories |
| Embedded certificate candidate | VA0x148590460/fileoffset0x858ec60/1349byte PEM region parses as X.509v1. DER SHA62880372376f5d9b4e63e453c7eaaf906a9b3d11bf8e3e9e2c8cbdd98c28ffe3. CN class other, actual name discarded; subject==issuer, BasicConstraints absent. A second PEM-shaped region fails parse. Neither proves REP anchor |
| Indirect data use | Pointer at0x149f80d90/fileoffset0x9f7eb90; reads0x146b6a52c/0x146b6a5d6 inside function0x146b6a270–0x146b6a9a3 pass candidate to0x146b34780. No SSL/DTLS/X509_STORE relationship established. A v1 explicit trust role cannot be excluded merely for missing BasicConstraints |
| Package/loose-file scan |79 PAK central directories read without extraction;14 cert/CA/trust filename matches had texture/audio-related extensions. Only loose certificate found under EAC; it was not changed. DER/indirect/other stores remain possible |

OpenSSL documents SSL_CERT_FILE/SSL_CERT_DIR overrides **for contexts using default verification paths**; that condition matters and is not established for REP. [Official default-path API](https://docs.openssl.org/3.0/man3/SSL_CTX_load_verify_locations/).

The public Lumberyard SecureSocketDriver initializer uses an explicit descriptor PEM to populate its context certificate store, or another verifier when absent. This suggests a useful initialization discriminator, **not a current-client recipe**. Exact selected diagnostics and GridMateSecure were absent in current PE ASCII/UTF16LE scan; no function/caller link was obtained. Stripped/different code remains possible. No public-engine code was copied or substituted. [Public source, initialization lines1398–1429](https://github.com/aws/lumberyard/blob/master/dev/Code/Framework/GridMate/GridMate/Carrier/SecureSocketDriver.cpp#L1398).

Ignored discriminator artifacts: vendor-source-check.py SHA7c2d5134050de25c855f49e4af11ce17a27e5277084c993d152de1b5a7d18e94; metadata-only vendor-source-check.json SHA35656f55991cbac2375c73faa33ae126c9e5a9f2431387654bb16ab1d69f34e7; validated run-vendor-check.ps1 SHA89b6c758661d5d5979839f8b6e8dc00c9107eb2edbbba8651ef9bad22ce62edc. These pin the bounded negative check, not absence of the implementation.

## Exact remaining blocker and Carrier/V3 gate

Current REP wrapper/interface→factory→UDP trust-store initialization, verifier dispatch and expected-peer inputs are now mapped in [REP_TRUST_POLICY](REP_TRUST_POLICY.md). Both known SDK connect branches converge before UDP selection. **Remaining:** determine an evidence-backed private-anchor loading boundary preserving validation and prove the actual game handshake. Live enum/context/store contents remain unread. Tested CurrentUserRoot/full-chain and launcher-scoped CA-file configurations do not establish the handshake. No supported override, global no-pinning result, broad bypass or memory write follows from static code or old Frida reports.

No current decrypted application/Carrier/V3 input was received in any of these six handshake attempts. Therefore the historical connectACK/V3 codecs were mapped but **not speculatively connected to the stock client**. Next transport-positive checkpoint must prove handshake plus genuine client application data; only then parse the actual Carrier connect and registration request with secret-minimizing metadata, reuse pinned codecs, and verify response-driven state transitions. Actor/spawn remains gated; no world-loading/player actor or Milestone1.
