# Protocol notes

Evidence profiles: First Light `63756a3`, historical May2 redacted reference (hash in `research/evidence/fixture-summary.json`); Aeternum-World `820156d`, documentation targets `v1.400.6031.40375`. The actual installed current client is **not identified**. All application-wire interpretations below are scoped to those sources, not promises about the final client.

## Transport, framing and serialization

| Layer | Established implementation/evidence | Missing or uncertain |
|---|---|---|
| Bootstrap/auth | Python TLS HTTP server with JSON mock responses; route table in `auth_mock.py:1340-1400` | Exact current-client HTTP sequence/required schema; `/Javelin.RPC.*` is not a working gRPC implementation |
| Game transport | UDP; configurable port, default23971; pyOpenSSL DTLS memory BIO per source address (`rep_responder.py:167-175,286-287,316-382`) | Actual two-client handshake not tested; stock-client trust and supported private endpoint selection unknown |
| Encryption | DTLS1.2 context with `ECDHE-RSA-AES256-GCM-SHA384` configured (`rep_responder.py:70,167-175`) | Cipher comment describes an old capture. No current negotiation or private-certificate acceptance proved |
| Carrier envelope | Four bytes: mode0x80/0x81, protocol0x01, BEu16 datagram sequence (`frame.py:142-161`) | 0x81 is **compression**, not another encryption layer |
| Compression | Bit0 signals LZ4. First Light strips envelope then directly parses body (`rep_responder.py:425-432`) | No inflate in that runtime. Aeternum `decode_dtls_ledger.py:207-228` actually inflates raw LZ4 blocks; empirical correctness not tested here |
| Carrier records | Flag/conditional length/channel/chunk count/sequence fields, then payload; `parse_datagram`/`marshal_datagram`; BE fixed integers and per-datagram sequence compression | Not all flag/channel/truncation/sequence-wrap combinations verified; enum presence is not runtime support |
| Application | Typed binary forms, VLQ/LEB128 helpers and bitstream IO; responder prefixes outgoing typed bodies with VLQ32 length | Not a generic protobuf assumption. Some C->S forms carry CRC32 + BE length +16-byte correlation UUID (`wire.py:101-134`); helper does **not** validate CRC or declared size |
| State replication | Type0x08 codec parses some header forms and preserves opaque data | Actor/component identity, baselines, ownership, member decoding and movement semantics missing |

Source links: [Carrier frame code](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/server/javelin/frame.py), [wire helpers](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/server/javelin/wire.py), [newer LZ4 decoder](https://github.com/Coldzer0/Aeternum-World/blob/820156dbc44c86c9436af81aa0dba72e94cb636b/Tools/nw_capture/decode_dtls_ledger.py#L199).

Record flag values in First Light: reliable0x01; chunks0x04; sequential ID0x08; sequential reliable ID0x10; explicit channel0x20; special no-length0x40; connecting0x80 (`frame.py:40-52`). The no-length registration form is First Light's documented New World extension; the newer generic frame diagram does not describe every such case. Do not combine their diagrams into a new universal packet specification.

## Message namespaces and IDs

**Do not conflate Carrier system IDs, AZ type indices, class UUIDs, replica component IDs, internal EBus event hashes or captured sequence numbers.** `analysis/message_inventory.md` contains internal as well as candidate wire classes. Names alone do not give movement packet formats. Numeric type stability across different builds is not verified.

### Carrier system messages

Channel3 payload's **last byte** is message ID (`frame.py:55-63,95-99`):

| ID | Enum name | Responder status |
|---|---|---|
| 1 | SM_CONNECT_REQUEST | Recognized; connect-ACK path |
| 2 | SM_CONNECT_ACK | Emitted with selectable historical variants |
| 3 | SM_DISCONNECT | Enum known; game/actor cleanup handler not implemented |
| 4 | SM_CLOCK_SYNC | Enum known; full behavior unestablished |
| 5 | SM_CT_FIRST | Enum known; not an application world message |
| 6 | SM_CT_ACKS | Continuous ACK builder/piggyback exists; no complete resend window |
| 7 | SM_CT_CONN_CONTROL | Enum known; full behavior unestablished |
| 8 | SM_CT_BANDWIDTH | Enum known; full behavior unestablished |

### Typed codec inventory

These are **code dispatch bindings/codec labels**, not fully established semantics. The executable tables are `server/javelin/dispatch.py:92-124,180-212`.

| Hex type | Codec/module label | Evidence limit |
|---|---|---|
| 0x03 | V3RegistrationResponse | Encoder only; old captured/default fields |
| 0x08 | chunked_stream / StateBundle | Opaque tails, not decoded actor state |
| 0x13 | V3RegistrationRequest | Strict old832-byte shape plus lenient identity extraction |
| 0xa4 | session_message_a4 | Label does not establish all session semantics |
| 0x14f | session_clock_beacon | Clock/nonce interpreted from old reference |
| 0x15d | heartbeat | Direction-sensitive ping/ack forms |
| 0x1be, 0x40a | handshake_blob_76 | Shared blob codec; meaning not fully resolved |
| 0x5b2 | identity_fingerprint | Reference-shaped |
| 0x635 | action_history | Not a implemented combat/input system |
| 0x651 | empty_marker | Marker shape only |
| 0x65c | world_data_blob | Blob codec, not world-streaming implementation |
| 0x663 | level_descriptor | Distinct from candidate LevelInfoChanged |
| 0x8e6 | identity_blob | Identity meaning/substitution not fully resolved |
| 0x9fc | receipt_handshake | Reference-shaped |
| 0xa95 | permission_bitmap | Not account authorization |
| 0xca4 | asset_count_table | Not redistributed assets |
| 0x1033 | opaque_blob | Semantics explicitly opaque |
| 0x1067 | vivox_config | Voice service not required for Milestone1 |
| 0x1096 | frame_config | Reference-shaped |
| 0x1097, 0x136a | result_token | Not a real private-account/session validator |
| 0x12f6 | keybinding_config | Reference-shaped |
| 0x16a0 | asset_blob | Opaque/reference data, not asset delivery |
| 0x18a6 | init_message | Initialization shape, not complete spawn |
| 0x1a59 | session_subkey | Semantic/key role needs evidence; never log real secrets |
| 0x1b88 | session_identity_beacon | Reference-shaped |
| 0x5d1 | candidate SelfIdentification | Synthetic binding; body/header-only and build-index conflicts remain |

Aeternum documentation calls PositionInTheWorldReplicatedState **decimal13 (hex0x0d)**, not First Light's hex0x13 registration. It gives a class UUID and bitmap/quantized-position layout (`packet_system.md:305-374`), but no checked-in executable component decoder. Its StateBundle member grammar (`242-301`) is a promising research lead, not a proven serializer or actor-spawn contract.

## Handshake, request/response and authority

- DTLS negotiation precedes decrypted Carrier traffic. A configured DTLS context existing does not prove the client accepts its certificate.
- Carrier connect request -> connect ACK; reliable inbound sequence -> optional continuous ACK. Carrier acknowledgement is not application registration or actor acknowledgement.
- V3 request -> registration response + ACK. Source extracts persona/session identity, uses UUID-derived/stub token and old build/clock/nonce defaults (`rep_responder.py:649-694,765-785`; `v3_response.py:39,57-58,101-127`). No validated local-account ticket binding exists.
- Registration response -> optional timed replay/heartbeat. Replay advancement is time-driven, not proven client-state or receipt driven (`rep_responder.py:830-866`). Retry count is not a character/spawn state.
- Candidate SelfIdent -> wrapper10->11; automatic11->12; level info ->12->13; replica/player readiness ->13->14 are **historical hypotheses**, not a verified minimal three-message handshake.
- Client-authoritative input/position and server-authoritative replication policy remain **unknown**. No actual input acceptance, position mutation, actor ownership or fan-out is implemented. Never infer authority from a replicated-state name or a replay direction alone.

Reliability gaps: inbound reassembly, outbound resend/ACK window, duplicate/order handling and sequence wrap. Identity substitution currently uses redaction-span length defaults/empty overrides; a16-byte span is not necessarily a persona UUID (`replay_substitution.py:76-97,199-205,241-244`).

## Capture Before Shutdown

The official [January15 announcement](https://www.newworld.com/en-us/news/articles/the-future-of-new-world-aeternum-what-to-expect) says servers go offline **January31, 2027**. It does not specify a shutdown hour/time zone. First Light's approximate December2026 date is stale. Preserve observations early rather than treating the final day as a guaranteed capture window.

This is an **observation plan, not executed work**. Restrict observations to our own legitimate clients/accounts and consenting friends, normal game actions and ordinary locally available logs/config/metadata. Do not intercept another user's traffic, MITM official endpoints, bypass uncontrolled authentication, scrape credentials, attack infrastructure or induce abnormal service failures. If a message body is not available through an allowed observation, label it unknown; an encrypted capture is not a decoded protocol fixture.

### Priority0: irreplaceable entry and multiplayer evidence

| Normal scenario / metadata | Specific information to preserve | Why it matters |
|---|---|---|
| Installed client before each update | Steam build ID, executable version/hash, launch mode, platform, region/world and timestamps; names/hashes of required local configuration files | Prevent incompatible-build/type-index comparisons; document legitimate launch dependencies without copying assets here |
| Cold startup and normal auth | Order of bootstrap/config discovery, endpoint host/path/method, HTTP/content type, redirects, status/result categories, local log events; **no tokens/tickets/headers containing credentials** | Separate mandatory identity/discovery services from optional content/telemetry after shutdown |
| Discovery and character screen | World/region identifiers, response schema shape, status fields, character-list ownership and selection behavior, allowed initial world/character choices | Make a minimal offline world selectable with two independent private identities |
| Existing character -> enter world | Queue-ticket schema/expiry categories (redacted), REP host/port/protocol metadata, selection-to-connect timing, client transition/log sequence | Establish ticket/session/world association rather than guessing from fixed mock values |
| DTLS and Carrier startup | Negotiated version/cipher and certificate-chain/public-fingerprint metadata if normally available; connect/ACK ordering, sequence/channel/retry timing | Distinguish trust, transport, reliability and application failures. No private keys or key-log secrets in this repository |
| Registration -> visible local player | Direction/type/channel/sequence/length/timing, correlation/identity field roles where locally exposed, client readiness/load/spawn events, first world/level/replica messages | This is the major unsolved First Light boundary; old replay/state53 is not a general spawn recipe |
| Same consenting friend enters/leaves view | Actor/interest/component identity lifecycle, spawn/despawn ordering, full baseline versus deltas, mapping of two private observations to the two players | Prevent duplicating one captured actor or broadcasting updates with the wrong replica identity |
| One player stationary; the other walks, turns, stops, jumps | Sender/receiver direction; message type/component; tick cadence, sequences, position/rotation presence/quantization if observable; update-to-render timing | Identify position versus input authority and transform dependencies with controlled normal actions |
| Swap roles and repeat movement | Same scenario with A/B interchanged and independently logged timestamps | Cross-check directional assumptions and avoid learning only one character/camera's behavior |
| Logout then relog; ordinary involuntary disconnect if it occurs | Close/disconnect reason categories, heartbeat/timeout cadence, session/address change, ticket reuse/new issue, actor removal and replacement order | Recover reconnect/duplicate-actor handling and distinguish transport timeout from game logout |

Observe failed-login/queue/service-unavailable behavior only when normally encountered or through supported ordinary UI—not by probing credentials, forcing official requests, adding load or taking services down.

### Priority1: dependencies and later gameplay

- Repeat a successful world entry with a fresh/low-complexity and established character; compare schema/member presence, not private identity values. Record empty versus populated inventory/equipment/quest state if it changes spawn dependencies.
- Normal zone boundary/fast travel: record level/interest changes and whether actor/session identity persists. It may reveal streaming needs before a small-group walk test succeeds.
- Small controlled equip/unequip, gather, craft, NPC dialogue, single combat action, quest accept/complete and expedition entry/exit: keep one action/timestamp per observation. These are future-system leads, not Milestone1 implementation scope.
- Preserve publicly accessible upstream protocol/version documentation and Git commit identities. Licensed components stay attributed; privately archived owned client files remain outside this repository and are never redistributed.

### Fixture record format (ours, not a wire format)

Each private observation should have a manifest recording scenario ID, collector/consent scope, UTC and monotonic timing, executable/Steam build identity, environment/region/world, exact normal actions, expected visible behavior, observed logs/transitions, source-file hashes, message metadata where available, redaction process and remaining unknowns. State whether material is encrypted metadata, decoded locally accessible data, a historical upstream capture or synthetic test input.

Use private storage outside tracked docs; keep a redaction-span map so masked bytes are not mistaken for zeros. Replace account/character/session IDs consistently in shareable notes; remove auth tokens, cookies, bearer/Steam tickets, keys, third-party identifiers and bodies that have not been reviewed. Never call a fixture deterministic proof of behavior merely because round-tripping opaque bytes succeeds. One fixture per isolated question is more useful than a long unlabeled dump.

Current availability: **one old public redacted reference** loaded only from ignored upstream, plus a new [own current-client bootstrap metadata fixture](../tests/fixtures/connectivity/current-client-bootstrap.json). The actual legitimate stock client reached private HTTPS with local trust; no current auth/DTLS/actor/movement wire fixture exists. The new fixture is metadata, not raw packets or response schemas. See [connectivity](CURRENT_CLIENT_CONNECTIVITY.md).
