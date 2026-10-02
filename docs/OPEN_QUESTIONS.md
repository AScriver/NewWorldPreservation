# Open questions

Unknowns are explicit work inputs, not invented protocol behavior. Source profiles and executed test boundaries are in [ledger](EVIDENCE_LEDGER.md). The offline environment task is complete; no live-client compatibility is established.

## Questions that gate real-client progress

| Question | Current evidence / limit | Smallest resolution |
|---|---|---|
| Which legitimate PC client build is the target? | First Light response defaults to `[RETAIL].Javelin.1.365.6031.6006993`; newer Aeternum research targets `v1.400.6031.40375`. No game install found in discovered Steam libraries, not an exhaustive scan. | Record owned installation's Steam build ID, executable version/hash and normal launch/config identity. Do not transfer indices across builds. |
| How can that client select an entirely private bootstrap endpoint? | Public source describes historical redirection/instrumentation; no current supported configuration path proved. | Read legitimate local configuration/startup behavior; observe normal session metadata; test only a deliberate endpoint on a host/service we control. No hidden machine-wide hosts/proxy/cert changes. |
| Can the stock executable trust a private world-service certificate? | Historical responder comment mentions trust-bypass instrumentation. Our DTLS-context construction says nothing about client trust. | Establish certificate/endpoint validation requirements for this build; prove private handshake without Amazon keys or official auth bypass. If client adaptation is unavoidable, document that concrete decision before any implementation; do not claim unmodified compatibility. |
| Can it still launch after game-service and platform dependencies disappear? | Owning/installing the client is not proof Steam/offline-launch/session behavior survives shutdown. | Preserve normal documented launch/offline-mode observations and local dependency metadata while available; do not emulate Amazon/Steam ownership or distribute clients. |
| What identity/session contract must private auth supply? | Shared global `Ctx` plus synthetic responses; current schemas unverified. | Own normal-session schema observations with secrets removed, then two isolated private-account tests and a ticket-to-peer binding proof. |

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

Game binaries/assets, Amazon server source, leaked code, credentials, local/private keys, proprietary decompilations or new live captures. External references/private test output are ignored. No invented packet implementation or claim that friends can already play.
