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

Final offline profiles:455 upstream passes/1deliberate skip;9 gates;19 original probe controls;26 instrumentation/metadata-fixture tests;CLI lifecycle and mocked observer scenarios pass. None promotes501 to auth or Milestone1. Exact next blocker: accepted current channel descriptor, private auth/session, separate REP/DTLS gate, then current actor fixture.
