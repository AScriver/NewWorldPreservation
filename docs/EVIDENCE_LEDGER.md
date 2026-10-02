# Evidence ledger

Research date: 2026-10-01 America/Phoenix (2026-10-02 UTC). Initial evidence was offline source review/public metadata/isolated tests; no game/hosts/trust mutations occurred **then**. The actual current-client slice is at the end, with cleanup verified. No hooks, process-memory inspection or EAC/binary changes.

## Evidence identities

- First Light: clean source at `63756a3f7ff0ae41752dcc7c80267802c3fa7548`, external ignored checkout. Initially sparse without `info/`; subsequently restored only the public redacted May 2 reference fixture. See `research/upstreams.json` and `research/evidence/fixture-summary.json` for identity/hash. Relevant source unchanged between profiles; only fixture-dependent checks needed revalidation.
- Aeternum-World: clean external source at `820156dbc44c86c9436af81aa0dba72e94cb636b`. Packet decoder/documentation inspected, capture hooks not run.
- Test runtime: Windows, CPython 3.11.9, pytest 9.1.1, pyOpenSSL 26.4.0, cryptography 50.0.2. Hash-pinned `requirements-dev.lock`.
- Historical initial bounded discovery found no installation, not an ownership judgment. Superseded by installed Steam22469132 / version1.400.6031.6004151 and actual bootstrap HTTPS evidence below; downstream compatibility is unknown.

## Material claims

| ID | Claim | Classification and limit | Exact evidence |
|---|---|---|---|
| E01 | Official announced shutdown is January 31, 2027, not the old README's approximate December 2026. | Observed public primary announcement; recheck before deadline decisions. | [Official January 15 announcement](https://www.newworld.com/en-us/news/articles/the-future-of-new-world-aeternum-what-to-expect) |
| E02 | First Light stopped accepting development in this repository and directed it to OpenWorld. A deeper cause is not established. | Observed Git history/notice, not proof Discord development remains active. | `git show 63756a3 -- README.md`; `README.md:1-5` |
| E03 | All eight visible fork branches are the same First Light commit. A public playable successor was not found in the bounded search. | Observed API refs; private/deleted/unindexed repositories remain unknown. | `successor-inspection.json` (private raw metadata), forthcoming compact ecosystem receipt |
| E04 | New invite `projectopenworld` resolves to Open World; old `5XzwZHFv` returns 404. Public invite does not expose source or validate progress. | Observed public invite API, 2026-10-02 UTC; continuity with the historical team not authenticated. | Current invite metadata and October 1 public community link; no join or messaging |
| E05 | Auth process shares one persona/character/world/ticket Ctx across HTTP request threads; there is no independent private-account backend here. | Strongly source-supported; no two-client HTTP runtime observed. | `auth_mock.py:416-493,1183-1208,1408-1416,1554-1606` |
| E06 | REP has per-address DTLS sessions/counters/ACKs, despite older single-peer/no-ACK wording. This is not shared-world multiplayer. | Strongly source-supported; named multi-peer tests exercise only logging/idle helpers, not concurrent sessions or full construction. | `rep_responder.py:91-131,179-312,1280-1328`; `test_multi_peer.py:1-127` |
| E07 | Typed inbound decode is log-only; there is no authoritative shared actor/movement owner/fan-out in responder. SessionState is unused. | Strongly source-supported for inspected runtime, not an assertion about private OpenWorld code. | `rep_responder.py:476-527`; `javelin/session_state.py:1-29`; `chunked_stream_08.py:19-20,48-54` |
| E08 | DTLS owns encryption; Carrier bit0 indicates LZ4 compression. First Light responder does not inflate it; newer ledger decoder does. | Strongly source-supported; newer decoder has not been empirically exercised here. | `frame.py:122-161`; `rep_responder.py:425-432`; Aeternum `decode_dtls_ledger.py:199-228` |
| E09 | SelfIdent, LevelInfoChanged and replica creation are spawn hypotheses, not a verified three-packet recipe. | Historical static RE with explicit counter-evidence; unknown live sufficiency and current-build IDs. | `self_ident.py:34-64`; `level_info_changed.py:31-35,133-138`; `autonomous_worklog_through_253.md:2385-2402`; responder does not emit these codecs |
| E10 | Old reports conflict: ~30s V3 retry/destruction vs later replay-held connection still black-screened at state10. | Historical reports under different configurations; neither repeated in this workspace. | `README.md:43-48`; `docs/next-session.md:112-127,286-294` |
| E11 | Newer public Aeternum-World is analysis/capture/decoder tooling, not a checked-in private game server. Position type13 and bundle layouts are documented but not supplied as an executable component decoder there. | Observed full Git tree + inspected decoder; don't turn diagrams into proven packet semantics. | Aeternum full `git ls-tree`; `packet_system.md:242-374`; `decode_dtls_ledger.py:118-234` |
| E12 | First Light has no detected license/file in inspected full tree; Aeternum-World declares AGPL-3.0. | Observed provenance constraint, not legal advice. References remain external; no vendoring. | Git full tree search / GitHub `license:null`; Aeternum `LICENSE` |
| E13 | Before fixtures: 402 passed, 50 skipped, 4 failed of456, all failed CLI cases depend on omitted replay. Ephemeral DTLS context/memory BIO creation passed, not handshake. | Observed historical sparse-profile result; preserved, not current acceptance evidence. | `research/evidence/baseline-summary.json`; private JUnit |
| E14 | Same profile with restored pinned fixture: 455 passed, 1 deliberate skip, 0 failed. All four old failures passed. Our original runner repeated this successfully. | Observed offline tests only; no semantic actor/spawn/movement or real handshake proof. | `fixture-enabled-summary.json`, `latest-validation.json`; current fixture hash in `fixture-summary.json` |

## Unresolved constraints

Stock current-client private-endpoint selection and DTLS certificate trust; independent local account/session contract; exact current-build registration/spawn protocol; full StateBundle/replica identity and movement semantics; reliable resend/reassembly/decompression; private OpenWorld development access. No credentials or proprietary server implementation are needed or assumed.

## Verification review

Targeted read-only review found:

| Challenge | Result | Consequence |
|---|---|---|
| Does the multi-peer test instantiate concurrent peers? | Falsified that inference: `test_multi_peer.py:98-103` bypasses SSL construction; helper tests only. Source ownership E06 survives. | No claim of multi-peer transport validation. |
| Do byte-preserving codec tests establish spawn/movement semantics? | No: opaque tails retained (`chunked_stream_08.py:48-54`); SelfIdent tests use synthetic forms (`test_codecs.py:4395-4442`). E07/E09 survive. | Offline green is a development prerequisite, not Milestone1 acceptance. |
| Is newer documented position replication implemented publicly? | No component decoder/server in pinned full tree; Carrier decoder stops at payload (`decode_dtls_ledger.py:118-234`). E11 survives within that tree. | Treat diagrams as research leads; private work still unknown. |

The original validation harness and its current gate tests are recorded in README and roadmap. No upstream source changed. Only fixture-dependent historical checks were revalidated; transport/auth/spawn runtime claims remain unverified.

## Current-client connectivity slice

Historical instrumentation preparation started at clean `main`c77b3c9; no game existed **in that slice**. C01/C07/C09 are superseded where affected by K01–K07 below. Current control receipts hash exercised source/fixtures but remain offline evidence. First Light unchanged; runtime Python3.11.9 / builtin OpenSSL3.0.13.

| ID | Claim | Status / limits | Evidence |
|---|---|---|---|
| C01 | Initial bounded search found no client | Historical, **superseded** by K01; no longer a blocker. | Discovery at Git2206da7; latest discovery now records installed client. |
| C02 | Python loopback TLS 1.2/1.3 clients validate expected CA+SAN; reject missing CA and mismatched hostname | Reproduced control behavior; not game compatibility, Windows user-store or DTLS proof. | 19-test control receipt, `test_connectivity_probe.py` |
| C03 | Original probe binds only explicit IPv4/IPv6 loopback, records sanitized metadata, implements no auth/forwarding/game transport | Strongly source-supported; malformed/secret/absolute-URL controls produced no leak or forwarding in tested cases. Not exhaustive all-input verification. | `connectivity_probe.py`; tests; independent private tester report |
| C04 | TLS-success/decrypted HTTP logs do not prove peer certificate verification or executable identity | Reproduced ambiguity with a permissive **Python-only negative control**; logs deliberately retain `unattributed`. No game bypass. | `test_permissive_control_does_not_turn_server_logs_into_validation_proof`; [connectivity doc](CURRENT_CLIENT_CONNECTIVITY.md) |
| C05 | Historical auth/queue route requests + HTTP 501 are diagnostic rejection, not successful auth/world selection | Reproduced synthetic requests; current route semantics unknown. | Synthetic fixture privacy test; no `GAME_SESSION_SELECTED`/transport-complete events |
| C06 | Probe CLI genuinely starts, receives CA-validated health HTTP200, stops and releases listener | Reproduced on ephemeral IPv4 loopback; child ownership/cleanup confirmed. Not real game startup or port443/firewall verification. | `verify_probe_cli.py`; CLI receipt |
| C07 | Original observer required readable exact process path | Historical proposal; actual path-inaccessible process falsified coverage. Corrected explicit launch correlation plus accept-time tuple lookup covers observed sockets; not live-image proof. | Current observer/native-owner tests and K03; old source at2206da7. |
| C08 | First Light's redirection uses fixed hosts list + local CA/SAN certificate; REP/DTLS trust is separate | Strongly source-supported. Old flow dated 2025-12-27; historical unknown-ca/patch report unverified on current build. No supported current override proven. | `setup_hosts.py:28-59,69-81`; `generate_auth_certs.py:95-147`; `auth_mock.py:1547-1564`; `docs/dtls-trust-bypass.md:7-14` in external reference |
| C09 | Current endpoint/trust and downstream contracts were unknown | Partly **superseded**: bootstrap/SNI/HTTPS trust answered K02–K04. Auth/world/REP/spawn still unknown; spawn analysis may begin, implementation waits. | K01–K07 and [spawn evidence](SPAWN_SEQUENCE.md). |

A failed intermediate control run (18 pass/1 fail) showed client certificate error versus server reset in TLS1.3; an assertion incorrectly required the server CA-alert mnemonic. Test now checks exact client validation error + absent HTTP and retains server's actual reason. This is counter-evidence to diagnosing resets as pinning, not game evidence.

## Actual owned current-client slice

Started clean `main`2206da7; original files dirty during trials. [Live receipt](../research/evidence/current-client-connectivity.json) pins installed client, relevant source bytes, ignored evidence hashes, phase/PID/start-time correlation and cleanup. ExperimentA probe SHA`bfddc360269c7d2756b0d2a85cc9a5c9657eadd9439ada40950afdda34e0532a`; experimentB instrumented SHA`3231f78d32920e893494120570206f4c6b2cae74b92ec5bf9ee0189b0cb4c17c`. Unaffected First Light evidence remains current; no codec changed.

| ID | Claim | Classification / limit | Evidence |
|---|---|---|---|
| K01 | Current install Steam22469132 / file and own-log1.400.6031.6004151 | Observed file/hash/log; live image path unavailable, not live-hash proof. | Discovery/live receipt and ordinary launch records. |
| K02 | Historical bootstrap host/path still works for current redirection | Observed own log plus game-owned IPv6-loopback GET; operator resolver/readback, not client DNS trace. | Receipt bootstrap/log/window metadata. |
| K03 | ExperimentB sockets belong to recorded game PIDs | Observed exact Windows client-side tuple owner + name/PID/start-time launch match; not live image bytes. | PIDs38624/42316/40672; native IPv4/IPv6 controls. |
| K04 | Correct CA/SAN permits bootstrap HTTP; absent trust/wrong name do not | Reproduced game differential0/3/0/3/0/3, CA reversal and same-CA/same-key SAN restoration. Active trust API and other HTTPS/DTLS unknown. | Fingerprints/phases in receipt; connectivity procedure. |
| K05 | Reached HTTP bootstrap, not auth/world/REP | Observed HTTP1.1/TLS1.2 GET + deliberate501. Generic loader marker is not world entry. | Current metadata fixture and receipt. |
| K06 | Temporary trust/routing cleaned up | Hosts original SHA7c0d9bdf…; exact introduced CA counts0; no owned443 listener/game left. No memory/EAC/binary change. | Restoration/readback/stop events and final OS checks. |
| K07 | Existing codecs/replay do not establish current actor flow | Strong old-source support, not current runtime: unwired SelfIdent, unknown LevelInfo ID, opaque actor/transform. | SPAWN_SEQUENCE and pinned clean source. |

Historical environment profiles:455 upstream passes/1deliberate skip;9 gates. Original19 probe controls,26 instrumentation checks,CLI and observer reran successfully17:09–17:10UTC. Added48 descriptor/HTTPS/safe-log checks passed17:08UTC. No test count establishes private authentication or Milestone1.

## Channel HTTP200 evidence (later, same current build)

Scope: main starting1f094ac; preexisting untracked`.vscode/` preserved; original new modules/fixture dirty during trial, exact SHA256s recorded in [channel receipt](../research/evidence/current-client-channel.json). Original probe SHA3231f78d… unchanged. Public original configuration/raw owned logs stay ignored. See [checkpoint/procedure](BOOTSTRAP_CHANNEL.md).

| ID | Claim | Classification / limit | Evidence |
|---|---|---|---|
| K08 | Current public descriptor has five regions/four API tags plus nwTokenUrl/entitlement metadata | Observed unauthenticated public read, not game wire capture; full-shape presence not field-requiredness proof. | Public5404byte/SHAa09098b6… receipt; original local fixture intentionally substituted. |
| K09 | Current owned client parsed local HTTP200 descriptor | Observed own PID41196/UTCstart/accept-time owner; server200SHA69075e7a… plus five unique local display markers in fresh own log. Not proof every API/tag/token URL consumed. | Channel receipt/fixture; own stable logSHA bfc518da…, markers279/288/297/306/317. |
| K10 | Earlier collapsed-token trial reached frontend plus Omni session failure204 | Historical observed generic frontend markers and numeric204; superseded as furthest state byK13. Its204cause remains unknown; no sessionHTTP in that trial. | Exactly one private HTTP request; owned-log352/353 etc; user screenshot not redistributed. |
| K11 | Trial's own resources restored after client exit | Observed stop17:00:33 before hosts/firewall removal17:00:34, CAcount0 then listenersabsent. Rule scope ActiveStore-readback, not packet trace/helper containment. | Ownership/window/trust receipt hashes plus root OS readbacks; no memory/EAC/input control. |

K05's501-bootstrap andK10's204/no-session stopping points remain historical; only state progress is superseded, not their recorded observations or trust controls.

## Token-origin HTTPS evidence (latest, same current build)

Scope: token-profile code was dirty during live trials; exercised hashes and observed checkout state in [token receipt](../research/evidence/current-client-token.json). Preserve the user's separate local ignore-config commit719af6e. No upstream/codec/gameplay edits. Fixture is metadata only, not an authentication payload.

| ID | Claim | Classification / limit | Evidence |
|---|---|---|---|
| K12 | First original-hostname comparison was invalid because trust arrived after client exit | Observed import-complete17:26:57 after PID8200 exit17:26:55; bootstrap-only noHTTP is not evidence about token endpoint selection or pinning. | Prior private run/trust hashes retained in token receipt; failed-control procedure. |
| K13 | Stock client reaches our token origin over trusted local HTTPS | Observed fresh owned PID31396/start17:35:29, exact tuple owners for bootstrap + three token requests. TLS1.3/SNI tokenservice, HTTP1.1 POST/games/new-world/tokens; stub501. No request bodies retained. | Token fixture/receipt; local200SHA68bf491a…, firsttoken17:35:43.026Z. |
| K14 | Original-token-hostname profile advances beyond collapsed-token trial, without login success | Observed tokenHTTP and SDK201 versus earlier204/no-tokenHTTP; meanings unknown. Matching URL/default, descriptor-field requiredness and follow-on response validation unresolved. No prod.newworld.com request, selection, REP, world or actor proof. | Five local log markers; stable logSHA55ee6f31…; user again reported failed authentication. |
| K15 | Latest trial's owned routing, client, listeners and trust are removed | Observed client exit before host/rule restoration; exact CA removal17:54:40/readback0; final18:07:17 readback game/listeners/rule absent and original hostsSHA. Earlier pending cleanup is superseded, not erased. Native CLI fallback refused before mutation because CA absent. | Completed token cleanup/trust receipt and private source hashes; no input control. |

Next blocker at that historical token-HTTPS checkpoint: **current token/session response contract**. This is superseded by K16–K21 below, not erased. Token-specific negative trust controls and later endpoints remain unknown; no green offline test establishes login or Milestone1.

## Current token response contract — controlled live comparisons

Scope: checkout started clean at `b18861c8498a8f43a8df5f6cb132b9026b564745`; original contract probe/fixture were dirty during trials. [Receipt](../research/evidence/current-token-contract.json) pins exercised source and private metadata hashes. Initial control did not record source hashes at preparation; its exact2-byte response was independently logged, and added model cases did not change its loaded control. Installed SHA/build unchanged; external First Light remains63756a3. No codec, game binary, EAC or process-memory edits/reads.

| ID | Claim | Adjudication / scope | Evidence |
|---|---|---|---|
| K16 | Current platformAccount object requires four members and a recognized identity type; account root can be absent | Strongly static-supported from SHA-pinned installed PE; member presence is not type validation; root account absence sets nested307 without automatic root failure. Static findings are not runtime proof alone | [Contract exact VA anchors](TOKEN_SESSION_CONTRACT.md#exact-static-anchors); private annotations/helper hashes in receipt |
| K17 | HTTP200 empty object produces SDK203 without credentials handoff | Observed fresh PID860, owned token TLS1.3/HTTP2002bytes, fresh own stable log203. Static missing-platform path explains this rejection;203 also used for invalid JSON, so not syntax-only | [Observed fixture](../tests/fixtures/connectivity/current-token-contract-result.json), control sources/cleanup hashes |
| K18 | Synthetic account-present token model advances client to credentials API | Observed PID32416, SDK0; response461bytesSHA660b1029…; owned credentials GET7ms later with Authorization present, TLS1.2, intentional501. No successful game login/actor | Fixture; own logSHA7b6e94c4…; exact accept-time OS owners |
| K19 | Top-level account can be omitted for the observed handoff; opaque unsigned token markers suffice at this step | Observed fresh PID42280 SDK0; model minus account311bytesSHAd5c7d093… ->owned credentials GET5ms later. platform/limitedUseToken also omitted. Fresh process, not cleared per-user state; request719bytes vs2941. Cause/equivalence unknown. Pristine-first-login, missing/empty tokens and later validation remain untested | Fixture; own logSHA2bc9439a…; separate fresh positively verified CA/profile recorded |
| K20 | Current CA intentionally retained; routing/owned processes/rules restored | Observed exact currentRoot1/thumbprint1AEE2B69…, expiryOct9, user explicitly requested reuse. EarlierCA A7AFB2CE… removed/root0 before instruction. No memory/input control | Retention receipt, final hostsSHA7c0d9bdf…, absent game/listeners/three owned rules; certificate ownership journals |
| K21 | Failed elevation is not a protocol failure; focused/workspace regressions pass | Observed canceled RunAs ->no client/routing, unused listeners stopped; user requested successful repeat.88 focused =existing58 +30 new checks; full workspace145 pass/no skips includes9 gates. Unchanged upstream455/skip1 not rerun | Canceled-comparison receipt; [validation receipt](../research/evidence/current-token-contract-validation.json); source hashes |

Exact next blocker: **current GET `/prod/credentials/omni` response and private game-session handoff**. Token-envelope acceptance to that request is solved for this build, not exhaustive authentication semantics. Actor implementation still waits for private auth/selection, REP trust and current spawn fixtures. Milestone1 remains unachieved.

Read-only adversarial review: K18/K19 survived within the recorded handoff; all exercised/private-source/fixture hashes matched. Universal2941-byte request summary was falsified and corrected to2941/719, with cached-state equivalence unknown. Fresh-CA reproduction wording was corrected to reuse retained trust. Missing public test provenance was resolved with the validation receipt above. K16's binary interpretation was outside that review's assigned scope; it remains source-supported, not independently re-disassembled by the reviewer. No review agent changed runtime resources.
