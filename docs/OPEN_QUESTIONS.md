# Open questions

Unknowns are explicit work inputs, not invented protocol behavior. [Ledger](EVIDENCE_LEDGER.md) separates tests from live evidence. Environment and current bootstrap HTTPS are established; private authentication/REP/world/spawn/movement are not.

Latest [selection checkpoint](LOGIN_INFO_CONTRACT.md): accepted synthetic token/credentials ->login-info200 ->selectable Preservation/world/frontend avatar ->Play ->queue-v2 POST501. Remaining: queue response/readiness/refresh/cancel/ticket/REP-address and DTLS acceptance. Query presence is observed; actual query names/values are not captured. No world or actor. Earlier501-login-info/credentials/token controls remain historical evidence.

## Questions that gate real-client progress

| Question | Current evidence / limit | Smallest resolution |
|---|---|---|
| Which legitimate PC client build is the target? | **Answered here:** Steam22469132 / file and own-log1.400.6031.6004151 / SHA8654f01d…; [receipt](../research/evidence/current-client-connectivity.json). | Repin updates; disclose inaccessible live image path and launch/name/PID/start-time/socket correlation. Do not transfer old indices across builds. |
| How can that client select an entirely private bootstrap endpoint? | **Answered:** temporary one-host dual-stack hosts mapping, owned loopback443; current game used IPv6. No supported config/CLI override found in bounded inspection. Hosts restored. | Accepted HTTP200 descriptor must select further private services. DNS/cache/fallback internals remain unknown; no hidden global proxy/DNS mutation. |
| Can the stock executable trust a private world-service certificate? | **Bootstrap and observed token HTTPS answered:** CurrentUserRoot CA + correct SAN; bootstrap noCA/wrong-name reversals and token-positive HTTP. No EAC/binary change. Later game-auth and **REP/DTLS unknown.** | Preserve separate trust gates; token-negative controls remain unrun. Do not infer all endpoints lack pinning or that server-side handshake proves client validation. |
| Can it still launch after game-service and platform dependencies disappear? | Owning/installing the client is not proof Steam/offline-launch/session behavior survives shutdown. | Preserve normal documented launch/offline-mode observations and local dependency metadata while available; do not emulate Amazon/Steam ownership or distribute clients. |
| What identity/session contract must private auth supply? | Current token envelope accepted with synthetic local IDs/opaque markers, without top-level account. SDK0 and credentials GET are not a private account/character ownership proof. Old shared `Ctx` is unsuitable. | Establish current credentials response/handoff first, then two isolated private-account tests and ticket-to-peer binding. Later token validation, refresh/expiry and disconnected launch remain unknown. |

## World entry and movement contracts

1. **Which registration fields are mandatory and which are capture artifacts?** Strict parser assumes one old832-byte shape; lenient parsing extracts identity. Clock/nonce/default build/token and error interpretation need multiple legitimate, version-matched observations. CRC/length acceptance and retries require private controlled tests, not permissive parsing guesses.
2. **What ends V3 retries and moves into actual world readiness?** Historical reports differ: ~30s destruction vs replay-held black screen. Transport ACK, application response, heartbeat, ordering and state dependencies remain competing explanations.
3. **Is candidate SelfIdentification header-only or structured, and what is its actual current index?** Source explicitly retains both forms and possible build-dependent sub-ID. Byte round trips of synthetic forms do not choose one.
4. **What constitutes a level/world-loaded notification?** Candidate LevelInfoChanged's fields are inferred; nonempty extended encoding unsupported. It is not necessarily interchangeable with type0x663 level descriptor.
5. **What creates the local player and remote actors?** Replica creation/NewProxy is a hypothesis. Determine actor/interest/component identifiers, baselines, initialization ordering and selected character association. Do not label an unknown packet NewProxy just because public GridMate has that concept.
6. **How are StateBundle members delimited and updated?** Newer docs describe interest/member/class nesting, but executable public decoder stops at Carrier payload. Unknown-class skipping, body lengths, full/delta state and component disappearance require bounded fixtures.
7. **Does the client send input, position, both, or differently in each state?** The public position-component diagram does not establish direction, ownership, reconciliation, world coordinates or collision authority. Compare stationary/walking/stopping observations from two consenting clients.
8. **Which ancillary messages are actually required for load?** Equipment/inventory permissions/time/asset counts may be prerequisites despite deferred gameplay. Prove minimal omission behavior only on our controlled service; don't implement every seasonal/economy system.
9. **How does disconnect/reconnect affect actor, ticket and peer identity?** Source expires peers after idle120s but has no world actor owner/reconstruction. Need logout, ordinary connection loss and relog observations, then duplicate/stale-peer tests.

## Reuse and environment unknowns

- Is a licensed, publicly reviewable current OpenWorld implementation available? A live invite is not source access/progress proof; current team continuity is unverified. No contributors were messaged or Discord joined.
- Why did First Light move? Only the move/defunct notice is supported; deeper reasons remain unknown. Do not inherit allegations from other projects.
- Can First Light maintainers supply a redistribution license? No detected license at the pinned commit. **This blocks vendoring/distribution, not local read-only research or our original harness.** Aeternum-World's AGPL terms need review before reuse.
- Will actual two-peer DTLS exchange and prolonged traffic expose the sequence-wrap/channel/scheduling issues noted in source? Context construction and helper tests cannot answer. This is the next available offline experiment, with entirely controlled endpoints.
- Do target traffic paths require LZ4, resend windows or inbound reassembly before world load? Source limitations are known; prioritize by actual current-build observation rather than speculative general transport work.

## Not blocking Milestone 1 now

Cloud hosting, large-scale shards, server economy, territories/wars, transfers, seasons, cash shop, leaderboard services and complete combat/NPC/quest content. Do not spend effort choosing infrastructure or another language before the client/world-entry contract is established.

## What this workspace intentionally does not contain

Game binaries/assets, Amazon server source, leaked code, credentials, local/private keys, proprietary decompilations or raw live captures. External references/private output are ignored. A sanitized own-client bootstrap metadata fixture is tracked, not raw wire or a server schema. No invented packet implementation or claim friends can already play.
