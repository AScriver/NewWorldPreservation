# Open questions

Newest [private anchor checkpoint](PRIVATE_REP_ANCHOR_TRIAL.md): the admitted certificate-data trial hit an observed EAC launch refusal, with zero HTTP/DTLS traffic. Exact stock restoration was verified before routing release. A matched elevated stock/original-launcher control then reached private queue200 and returned two fatal `unknown_ca` alerts. The on-disk substitution route is retired, not bypassed. Next discriminator: identify an unchanged-client private REP trust/configuration input compatible with intact EAC, if one exists. [New live receipt](../research/evidence/private-rep-anchor-eac-control.json). Earlier metadata/elevation failures remain historical; nine lifecycle tests are inert controls, not game acceptance.

Unknowns are explicit work inputs, not invented protocol behavior. [Ledger](EVIDENCE_LEDGER.md) separates tests from live evidence. Environment and current bootstrap HTTPS are established; private authentication/REP/world/spawn/movement are not.

Latest [live DTLS checkpoint](DTLS_REGISTRATION.md): synthetic selection/queue200 ->our loopback responder's full-chain flight ->**incoming fatal unknown_ca**, with matching secure-connection error(2), six attempts across three runs. CurrentUserRoot trust works for private HTTPS but is insufficient here. [New static trust map](REP_TRUST_POLICY.md) establishes embedded-certificate loading, standard-verifier/identity inputs and same-object transport setup; actual session context/private-root override remain unproven. No completed DTLS, Carrier/V3, world loading or actor. Secure private accounts/tickets, queue follow-ups and cold-cache equivalence remain open; no request/query values retained. Earlier501/receive-only stops are historical.

## Questions that gate real-client progress

| Question | Current evidence / limit | Smallest resolution |
|---|---|---|
| Which legitimate PC client build is the target? | **Answered here:** Steam22469132 / file and own-log1.400.6031.6004151 / SHA8654f01d…; [receipt](../research/evidence/current-client-connectivity.json). | Repin updates; disclose inaccessible live image path and launch/name/PID/start-time/socket correlation. Do not transfer old indices across builds. |
| How can that client select an entirely private bootstrap endpoint? | **Answered:** temporary one-host dual-stack hosts mapping, owned loopback443; current game used IPv6. No supported config/CLI override found in bounded inspection. Hosts restored. | Accepted HTTP200 descriptor must select further private services. DNS/cache/fallback internals remain unknown; no hidden global proxy/DNS mutation. |
| Can the stock executable trust a private world-service certificate? | Private HTTPS succeeds; stock REP rejects our full-chain leaf/root. Embedded-certificate/store/standard-verifier path mapped; no expected DNS/IP or separate pin configured in inspected lifecycle. The later data-only interval substitution was refused by intact EAC and restored. | Trace the shared settings manager/providers for a normal unchanged-client CA/transport control, without assuming one exists. Prove actual game DTLS/application data and unrelated-root rejection only after a viable route is identified. Carrier/V3 stays gated. |
| Did a certificate-file override solve REP trust? | Original-launcher default and child SSL_CERT_FILE=retainedCA both give two fatal unknown_ca/no app. Parent verified, environment consumption unknown. Mapped secure initializer uses descriptor text, with no default-path loader found in its complete body. | Do not repeat blind env overrides as a descriptor setting. Establish the actual private-anchor path; do not infer global pinning or reuse the old memory hook. |
| Can it still launch after game-service and platform dependencies disappear? | Owning/installing the client is not proof Steam/offline-launch/session behavior survives shutdown. | Preserve normal documented launch/offline-mode observations and local dependency metadata while available; do not emulate Amazon/Steam ownership or distribute clients. |
| What identity/session contract must private auth supply? | Compatible synthetic token/credentials/selection/queue envelopes advance to owned UDP. No secure private account, ticket issue/consume or cryptographic validation. Old shared `Ctx` is unsuitable. | Two isolated private-account tests and ticket-to-peer binding after current transport evidence. Queue request schema, clock units/expiry, JWT/signature enforcement, refresh/cancel and disconnected launch remain unknown. |

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
- Two isolated DTLS peers now exchange CA-verified inert data (normal/reversed order);7 original responder controls pass. Prolonged/current-game traffic and Carrier wrap/channel/scheduling behavior remain untested.
- Do target traffic paths require LZ4, resend windows or inbound reassembly before world load? Source limitations are known; prioritize by actual current-build observation rather than speculative general transport work.

## Not blocking Milestone 1 now

Cloud hosting, large-scale shards, server economy, territories/wars, transfers, seasons, cash shop, leaderboard services and complete combat/NPC/quest content. Do not spend effort choosing infrastructure or another language before the client/world-entry contract is established.

## What this workspace intentionally does not contain

Game binaries/assets, Amazon server source, leaked code, credentials, local/private keys, proprietary decompilations or raw live captures. External references/private output are ignored. A sanitized own-client bootstrap metadata fixture is tracked, not raw wire or a server schema. No invented packet implementation or claim friends can already play.
