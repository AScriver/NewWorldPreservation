# First Light / OpenWorld analysis

Investigated October 1, 2026 Arizona / October 2 UTC. **Actual source was inspected**, not just README claims. Source identities: [First Light `63756a3`](https://github.com/nw-private-server/first-light/tree/63756a3f7ff0ae41752dcc7c80267802c3fa7548), [Aeternum-World `820156d`](https://github.com/Coldzer0/Aeternum-World/tree/820156dbc44c86c9436af81aa0dba72e94cb636b). Both reference checkouts remain clean and ignored. All file/line references below refer to those revisions.

## Findings at a glance

**First Light is useful protocol research and a Python mock/replay/transport scaffold, not a demonstrated playable multiplayer server.** Its testable framing/codecs are worth retaining. Authentication needs real private account isolation; post-registration requires evidence-backed world/actor state rather than per-peer captured replay.

### 1. What First Light actually implemented

| Component | Verified in source | Important limitation |
|---|---|---|
| `server/auth_mock.py` | HTTPS request routing, channel configuration, Omni-shaped tokens/JWKS/OpenID responses, synthetic entitlements, login info, character creation/validation, world list and immediately-ready queue tickets | One process-wide mutable persona/character/ticket `Ctx`; permissive unknown-route `{}` responses; not an independent private-account service |
| `server/rep_responder.py` | pyOpenSSL DTLS memory BIO per source tuple; Carrier handshake ACK; V3 parsing/response; piggyback continuous ACK; sequence counters; paced replay/chunking; optional heartbeat; idle eviction and peer-tagged logs | No live shared actors/world, no movement application/fan-out, no complete resend/reassembly/decompression; private certificate acceptance not established |
| `server/javelin/` | Bitstream/frame parser/marshaler, VLQ/CRC helpers, registration codecs, numeric codec dispatcher, replay parser/redaction spans and substitution | Some fields are opaque; some codecs are explicitly hypothesized; byte preservation is not gameplay semantics |
| `tools/decode_message.py`, build/reference tools | Local inspection/decoder CLI, API/site catalog tools | Dashboard coverage percentages count recognized/captured forms, not complete world behavior |
| Analysis/capture tooling | Historical static RE, type catalogs and one public redacted login/spawn-sequence reference | Historical reports and offsets may not match today's client; hooks/capture tools were not run |

Source anchors: [auth context](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/server/auth_mock.py#L416), [routes](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/server/auth_mock.py#L1340), [per-peer sessions](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/server/rep_responder.py#L1280), [log-only decode](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/server/rep_responder.py#L483).

### 2. Existing protocol/RE documentation

- `docs/protocol.md`, `docs/gridmate-reference.md`: transport/framing and public Lumberyard GridMate comparison. The engine reference is useful context, not proof New World has no custom extensions.
- `docs/post-v3-sequence.md`, `analysis/replay_message_inventory.md`: captured post-registration phases and message ordering.
- `analysis/v3_request/BODY_DECODE.md`, `HEADER_DECODE.md`: strict registration layout and special Carrier header.
- `analysis/message_inventory.md`: 2,025 recovered class pairs across namespaces; includes probable internal/bus messages. **Not 2,025 decoded network packet schemas.**
- `analysis/typeregistry_vs_replay.md`, `typename_unblock_spec.md`: gaps between indices, names and capture interpretations.
- `analysis/state_machine_summary.md`, `state_13_14_writer_investigation.md`: candidate spawn gates, including an indirect-call static-RE wall.
- `self_ident.py:34-64`, `level_info_changed.py:31-38`: crucial caveats in executable codecs, even where later narrative claims sound confident.
- Aeternum-World's [packet-system reference](https://github.com/Coldzer0/Aeternum-World/blob/820156dbc44c86c9436af81aa0dba72e94cb636b/docs/Network/packet_system.md) is newer (June 2026), describes StateBundle members and a position component, and gives a different target version (`v1.400.6031.40375`). Treat diagrams/examples as hypotheses until supported by executable decoders plus versioned fixtures.

### 3. Why it became defunct

The May 15 local-time / May 16 UTC commits `8b4151f`, `fa3729c`, `63756a3` changed the README to redirect development to OpenWorld Discord and declare the repository historical/unmonitored. The GitHub `archived` flag is false; **defunct is its maintainer notice, not GitHub archival**.

No inspected commit, source or public maintainer evidence explains a deeper organizational, funding or legal reason. Do not attribute it to a takedown, scam, failed technical effort or the shutdown itself. Third-party allegations about other named projects do not establish this repository's cause.

### 4. Where OpenWorld currently lives

The README's `https://discord.gg/5XzwZHFv` returned HTTP404 from the public invite API. A current [community-linked invite](https://www.reddit.com/r/newworldgame/comments/1wulcxs/modded_singleplayer/) is [Open World: `projectopenworld`](https://discord.gg/projectopenworld), which returned HTTP200 with guild name Open World and a description about hosting NW servers.

That establishes a publicly accessible community location, **not a publicly reviewable server implementation or authenticated continuity with the historical team**. No Discord membership, messaging, private-channel access or progress claims were obtained. Public claims that development is far ahead remain unverified without source/fixtures/client acceptance evidence.

### 5. Forks and successors

The eight visible forks were queried for branch refs, not compared merely by push dates:

| Fork owner | Visible branch/head |
|---|---|
| dragoso | main / `63756a3` |
| itsOwen | main / `63756a3` |
| zkulle | main / `63756a3` |
| Commando501 | main / `63756a3` |
| Realystic1 | main / `63756a3` |
| lemmcode | main / `63756a3` |
| ryanmcadams | main / `63756a3` |
| jeremylcarter | main / `63756a3` |

No fork provides a newer visible branch. See [compact metadata receipt](../research/evidence/ecosystem-summary.json). This bounded search is not proof that no differently named/private/unindexed successor exists.

**Coldzer0/Aeternum-World:** full tracked tree contains 17 files: catalog, packet diagrams, capture hooks, HTTPS pairing, Carrier ledger decoder, license and a log. Actual [decoder code](https://github.com/Coldzer0/Aeternum-World/blob/820156dbc44c86c9436af81aa0dba72e94cb636b/Tools/nw_capture/decode_dtls_ledger.py#L176) does LZ4-aware Carrier extraction. It does not implement the position-component decoder pictured in the documentation, world entry or a game server. It is newer adjacent RE, not an established First Light successor. Capture logs were not read/exported and hooks were not executed.

`nw-buddy` is an asset/data/viewer lead, not evidence of an emulator. Aeternum Legacy donation/marketing claims were not used to select code or conclude anything about OpenWorld.

### 6. Reusable portions and condition of abandoned components

| Candidate | Decision |
|---|---|
| Pure bitstream, Carrier frame/marshal, wire helpers, covered codecs | Retain/test through external pinned checkout; resolve redistribution license before vendoring |
| pyOpenSSL responder transport/session container | Prefer as transport starting point; test actual DTLS exchange separately; do not inherit all-interface defaults or byte-dump logging |
| Auth response shapes / endpoint router | Reuse schema evidence, not shared-persona account ownership or catch-all success behavior |
| ReplayStore and public redacted reference | Keep as private deterministic byte-shape oracle; never publish original fixture here; redaction placeholders are not real identity/state |
| Aeternum LZ4/Carrier decoder | Useful comparison/possible reuse subject to AGPL and verification; not a complete replacement transport |
| `server/dtls_bridge.py` | Earlier WIP OpenSSL-subprocess bridge; recorded Windows pipe-handshake failure and no guaranteed pipe datagram boundaries. Do not choose over memory-BIO responder |
| python3-dtls route | Historical compatibility dead end on newer Python; not installed or required by our reproduced runtime |
| `server/javelin/session_state.py` | Unused sketch, not an implemented state machine/persistence layer |
| SelfIdent/LevelInfo candidate codecs | Preserve uncertainties; no speculative three-message spawn implementation |
| Runtime hooks/certificate patches | Historical experiments only, not enabled, redistributed, or required by this workspace's offline tests |

Source-supported defects/limits worth separate future tests: ACK cursor uses ordinary comparison across wrapping u16 values (`rep_responder.py:111-118`); frame channel validation permits4 while sequence arrays have four slots (`frame.py:174-175,200-229`); periodic replay/heartbeats run on socket timeout, potentially deferred by continuous traffic (`rep_responder.py:1283-1305`). These were **not reproduced as defects** in the chosen suite and are not a justification for unrelated edits now.

### 7. Gap from connecting to two moving players

1. Current legitimate-client bootstrap/private trust is unproven; there is no installed client build identified on this host.
2. Mock auth has no separate accounts and no validated ticket-to-peer-to-character binding.
3. DTLS/registration may produce `rep.ready` historically without world load. Historical retry/destruction and later replay-held black-screen reports conflict under different configurations.
4. Candidate self-identification/level/replica messages are not a proven generation sequence; opaque StateBundle replay does not instantiate independently identified authoritative actors.
5. Movement payload/authority, replica IDs, interest ownership, sequencing/baselines and actor create/update/remove must be established.
6. The server must apply A's accepted update and serialize it for B, and vice versa, with no shared session counters or cross-account state contamination.
7. Disconnect/reconnect must remove/reconstruct actors without duplicates and stale updates.

## First implementation task and executed verification

The source had no conventional application build; the first task was **reproduce its Python development/test environment**. Original reference/bootstrap/validation scripts now pin the commit, lock dependency versions/hashes, verify the public redacted fixture hash, construct an ephemeral DTLS context/memory BIO and run an explicit offline test profile. No upstream server/source changes were needed.

| Experiment | Actual result | What it establishes |
|---|---|---|
| Sparse profile without public reference fixture | 402 passed /50 skipped /4 failed, 456 total | Missing-fixture environment failures reproduced; not protocol defects |
| Same profile with pinned public redacted fixture restored | **455 passed /1 deliberate skip /0 failed** | Four CLI failures disappeared; covered parser/serializer/replay behavior reproducible |
| Original verification-gate tests | **9 passed** | Missing coverage, nonzero exit, failures/errors and unexpected fixture skips cannot silently produce a green receipt |
| Ephemeral cert + actual responder DTLS context/memory BIO | Constructed successfully; temporary key deleted | Installed TLS API usable at construction seam; **no handshake or client trust tested** |

Current receipts: [latest validation](../research/evidence/latest-validation.json), [fixture-enabled baseline](../research/evidence/fixture-enabled-summary.json), [historical sparse baseline](../research/evidence/baseline-summary.json). Raw test/JUnit output is private/ignored. `test_multi_peer.py` tests logger/idle helpers and bypasses connection construction; it does **not** test concurrent clients. Round-trip tests preserve opaque data and cannot prove spawn/movement semantics.

**Exact next technical gate:** identify/pin a current legitimately installed PC client and a controlled private endpoint/trust path; then reproduce one registration-to-world-entry sequence with explicit state observations. The unresolved post-registration blocker is actor/replica creation and its exact dependencies, not merely writing a movement broadcast function. See [roadmap](ROADMAP.md).
