# Evidence ledger

Research date: 2026-10-01 America/Phoenix (2026-10-02 UTC). Initial evidence below concerns offline source review, public metadata and isolated Python tests. The subsequent connectivity slice is recorded separately below. No game clients, hooks, Amazon game endpoints, hosts entries or certificate stores were touched; local Python TLS control services were exercised.

## Evidence identities

- First Light: clean source at `63756a3f7ff0ae41752dcc7c80267802c3fa7548`, external ignored checkout. Initially sparse without `info/`; subsequently restored only the public redacted May 2 reference fixture. See `research/upstreams.json` and `research/evidence/fixture-summary.json` for identity/hash. Relevant source unchanged between profiles; only fixture-dependent checks needed revalidation.
- Aeternum-World: clean external source at `820156dbc44c86c9436af81aa0dba72e94cb636b`. Packet decoder/documentation inspected, capture hooks not run.
- Test runtime: Windows, CPython 3.11.9, pytest 9.1.1, pyOpenSSL 26.4.0, cryptography 50.0.2. Hash-pinned `requirements-dev.lock`.
- No own New World installation was found through the locally discovered Steam libraries (`client-install-summary.json`); this is not an exhaustive disk scan or an ownership judgment. Current client compatibility is unknown.

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

Starting checkout `main` at `c77b3c962fd9eaf28b7b2ba25217e0e34ef23903`, clean; original scripts/tests subsequently uncommitted during experiments. [Probe receipt](../research/evidence/connectivity-validation.json) hashes the exact tested source, runner, tests and independently written synthetic fixture. [CLI receipt](../research/evidence/connectivity-cli-control.json) pins probe and generated certificate fingerprints. First Light remains clean/unchanged at its existing pin. Runtime: isolated Python 3.11.9 / OpenSSL 3.0.13; no current New World runtime exists in this evidence.

| ID | Claim | Status / limits | Evidence |
|---|---|---|---|
| C01 | No client identified by registered libraries/conventional paths/config directories; no matching process running | Observed **bounded absence**, not exhaustive machine absence. Install-path question pending. | [Discovery](../research/evidence/current-client-discovery.json); `Inspect-CurrentClient.ps1` |
| C02 | Python loopback TLS 1.2/1.3 clients validate expected CA+SAN; reject missing CA and mismatched hostname | Reproduced control behavior; not game compatibility, Windows user-store or DTLS proof. | 19-test control receipt, `test_connectivity_probe.py` |
| C03 | Original probe binds only explicit IPv4/IPv6 loopback, records sanitized metadata, implements no auth/forwarding/game transport | Strongly source-supported; malformed/secret/absolute-URL controls produced no leak or forwarding in tested cases. Not exhaustive all-input verification. | `connectivity_probe.py`; tests; independent private tester report |
| C04 | TLS-success/decrypted HTTP logs do not prove peer certificate verification or executable identity | Reproduced ambiguity with a permissive **Python-only negative control**; logs deliberately retain `unattributed`. No game bypass. | `test_permissive_control_does_not_turn_server_logs_into_validation_proof`; [connectivity doc](CURRENT_CLIENT_CONNECTIVITY.md) |
| C05 | Historical auth/queue route requests + HTTP 501 are diagnostic rejection, not successful auth/world selection | Reproduced synthetic requests; current route semantics unknown. | Synthetic fixture privacy test; no `GAME_SESSION_SELECTED`/transport-complete events |
| C06 | Probe CLI genuinely starts, receives CA-validated health HTTP200, stops and releases listener | Reproduced on ephemeral IPv4 loopback; child ownership/cleanup confirmed. Not real game startup or port443/firewall verification. | `verify_probe_cli.py`; CLI receipt |
| C07 | Own-client observer would record matched executable metadata and sampled TCP four-tuples; does not see DNS/TLS/payloads | Source-supported + PowerShell syntax/analyzer validation only; unexecuted with legitimate game. Sampling may miss short sockets. | `Observe-CurrentClient.ps1`; connectivity procedure |
| C08 | First Light's redirection uses fixed hosts list + local CA/SAN certificate; REP/DTLS trust is separate | Strongly source-supported. Old flow dated 2025-12-27; historical unknown-ca/patch report unverified on current build. No supported current override proven. | `setup_hosts.py:28-59,69-81`; `generate_auth_certs.py:95-147`; `auth_mock.py:1547-1564`; `docs/dtls-trust-bypass.md:7-14` in external reference |
| C09 | Current-client endpoint/config, resolver, SNI, certificates/pinning, auth schemas and private-world entry | **Unknown.** Game not found/launched; synthetic controls cannot settle any of these. Spawn cannot begin. | Missing executable and current capture; no `SPAWN_SEQUENCE.md` until required gate |

A failed intermediate control run (18 pass/1 fail) showed client certificate error versus server reset in TLS1.3; an assertion incorrectly required the server CA-alert mnemonic. Test now checks exact client validation error + absent HTTP and retains server's actual reason. This counter-evidence is documented rather than diagnosing all resets as pinning. Existing 455-pass/one-deliberate-skip and 9-gate-test profile was revalidated without upstream/codecs changes; only local control instrumentation is newly proven.
