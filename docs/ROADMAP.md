# Milestone 1 roadmap

## Acceptance boundary

Two legitimate PC clients, distinct **private** accounts and characters, same Aeternum world/map, two distinct visible players and bilateral position/movement updates. Test both roles, stop/turn/reverse direction, logout and reconnect. For acceptance, record at least ten minutes together and one reconnect without a duplicate/stale actor. Ten minutes is **our test criterion**, not a discovered protocol timeout.

No Amazon service, credentials or asset redistribution should be necessary for the final private backend. Existing local client assets remain with their legitimate owners. Ignore the Trading Post/MMO-scale systems listed in [architecture](ARCHITECTURE.md).

## Current status

- Research completed for the publicly accessible pinned First Light/Aeternum sources and visible forks. Private OpenWorld implementation remains uninspectable.
- **M1-00 completed:** reproducible development/reference/test environment. Original scripts pin source and redacted fixture, hash-lock dependencies, guard verification and log test transitions.
- **455 upstream tests passed, one deliberate skip; 9 original gate tests passed.** Certificate-backed DTLS context/memory BIO constructed; no game DTLS handshake tested.
- **Actual current client pinned and private bootstrap HTTPS proven:** version1.400.6031.6004151 / Steam22469132; exact socket owner correlated with ordinary Steam launch. GET channel over TLS1.2/HTTP1.1; response501 is the deliberate stop. Correct user-store CA/SAN works, absent CA/wrong SAN do not; restores to working. [Live evidence](../research/evidence/current-client-connectivity.json).
- **Instrumentation validated:** original19 controls +26 new instrumentation/fixture tests + CLI lifecycle + mocked observer. Both CAs removed, hosts restored byte-exact, owned game/probes stopped. No EAC/binary/memory/trust bypass. [Connectivity](CURRENT_CLIENT_CONNECTIVITY.md) and [spawn evidence](SPAWN_SEQUENCE.md).
- **Milestone 1 not achieved.** No private account system, world entry, actor spawning or mutual movement implemented by this workspace.
- **Latest connection checkpoint:** stock build22469132 accepts synthetic token/credentials/login-info; Play sends queue-v2 POST, our original829byte200 response hands off to owned127.0.0.1:64003. Ten owned-client DTLS ClientHello-header datagrams observed; receive-only observer sends no replies. No handshake, game trust, world loading or actor. [Handoff](PRIVATE_GAME_HANDOFF.md), [receipt](../research/evidence/current-queue-handoff.json). Full explicit workspace regression261 pass including9 gates and48 new queue/UDP/evidence tests; upstream455/skip1 historical and unchanged.
- **Trust policy:** fresh short-lived test CA intentionally retained at the user's request through October9; routine trials must reuse it. Hosts/firewall/processes still restored/stopped after each run. Retention is documented, not failed cleanup.
- **New current-game DTLS checkpoint:** original responder answers the stock client's selected loopback endpoint; two configured full-chain flights receive explicit incoming fatal unknown_ca. User/log secure-connection error(2) agrees. No DTLS completion/application/Carrier/V3; not pinning proof. Original responder/local controls268pass; post-capture fixed-error/privacy checks raise current regression to273pass. [Evidence/reproduction](DTLS_REGISTRATION.md). Earlier receive-only result above remains historical.
- **New static trust checkpoint:** current UDP factory passes embedded certificate text through the same transport/connection object into secure setup; context/store creation, ordinary chain verifier and expected-identity parameters are mapped. No expected DNS/IP or separate pin is installed by the inspected lifecycle; global/runtime policy remains bounded. Actual REP context attribution and a supported private-anchor configuration are still gates. [Policy/coverage/receipt](REP_TRUST_POLICY.md). All39 validated artifact hashes, prior JUnit/runner and installed EXE/launcher rechecked; no new tests/live trial or executable/runtime mutation.

## Small independently testable tasks

Tasks are bounded outcomes, not assignments to layers. Dependencies identify actual prerequisites; independent offline checks can proceed separately. No Actionables scope was supplied, so this Markdown is the task record.

| ID | Outcome / scope | Depends on | Independent verification / completion criterion |
|---|---|---|---|
| M1-00 **Done** | Reproduce strongest public Python implementation; retain unchanged source and existing fixtures externally | None | Pinned clean source/hash-verified fixture; hash-pinned venv; explicit 11-module profile: 455 pass / 1 intentional skip; 9 gate tests; DTLS context constructor |
| M1-01 **Partial** | Pin target client; own-session bootstrap evidence done, entry/movement/reconnect still missing | Owned installation/session | Build/hash + launch/owner correlation + safe schema/state fixtures; no secrets |
| M1-02A **Done** | Stock current client reaches private bootstrap HTTPS with local trust | M1-01 bootstrap | Actual attributed GET; CA absent/present/removed and same-CA correct/wrong/restored-name controls; all routing/trust restored |
| M1-02B **Done: discovery only** | Current local channel HTTP200 parsed; original token hostnames preserved and locally mapped | M1-02A + current descriptor schema | Five local names parsed; token request reached owned service. Not proof every descriptor field is consumed or authentication succeeds |
| M1-02B1 **Done** | Observe Omni CreateSession token request on owned endpoint | M1-02B parsed descriptor | Three attributed POSTs, correct token SNI/Host, TLS1.3, deliberate501; metadata-only fixture, no credential replay |
| M1-02B2 **Done: compatible envelope** | Establish a current-build token response that advances to the credentials API | M1-02B1 | Static parser checks; empty-model203 control; synthetic account-present and account-absent models bothSDK0/credentials GET; deterministic response/transition fixtures. Exhaustive error/refresh/optional-field validation remains open |
| M1-02B3 **Done: compatible handoff only** | Establish current credentials/selection/queue response and selected private game endpoint | M1-02B2 | Numeric credentials200 ->synthetic character/world preview ->queue200 ->owned UDP attempt. No secure private accounts/ticket issue/validation, handshake or gameplay proof |
| M1-02C **Partial: rejection and static policy mapped** | Separate current game REP/DTLS trust | M1-02B3 selected address + M1-03 transport | Six fatal unknown_ca attempts; same-object embedded-certificate→store/standard-verifier path mapped statically. Actual session context/private-root configuration and game acceptance remain; no global no-pinning inference |
| M1-03 **Partial: local exchange proven** | Exercise actual responder transport with two locally controlled protocol endpoints | M1-00 | Original responder7tests: two CA-verified independent peers/inert exchange, unrelated-CA alert, timer retransmission, capacity/socket-error/stop cleanup. Independent retained-CA normal/reversed control also passes. Full268test regression. These endpoints are **not** New World clients; prolonged/idle/reconnect contracts remain |
| M1-04 | Implement two private account/character selections with client-compatible response schemas | M1-01's schema evidence; M1-02B3 game-auth handoff | Two logins return disjoint character ownership; wrong/expired credentials rejected locally; changing one identity cannot rewrite another; cold restart behavior explicitly defined |
| M1-05 | Bind private world ticket to one authorized game peer/character/world | M1-03, M1-04 | Deterministic issue/consume/expiry/replay/wrong-account tests; registration logs identify a private character, not guessed identity from span length |
| M1-06 | Establish evidence-backed current-build registration -> world-entry contract | M1-01; M1-02/05 for real private acceptance | Versioned fixtures and exact type/body/dependency ordering; separate retry, transport-ready, level-ready and actor-ready observations; controlled private omission tests where justified |
| M1-07 | One real character spawns in a generated minimal world session | M1-06 | Actual visible local actor and usable camera/map; server-generated identity/state, not old-session impersonation or a black loading screen; log proven spawn transition |
| M1-08 | Decode and serialize the minimal actor/position baseline+delta contract | M1-01/06's build-bound evidence; may run offline before M1-07 | Exact-boundary/truncation/unknown-type/round-trip captured fixtures; member/actor IDs and transform encoding verified; unknown tails rejected or explicitly retained, never guessed |
| M1-09 | Spawn two distinct real players in the same private world | M1-05, M1-07, M1-08 | Each sees the other's correct identity/actor baseline; isolation and visibility proved; no duplication of one replayed persona |
| M1-10 | Apply one player's accepted movement and replicate it to the other | M1-09 | A moves/B sees, then B moves/A sees; stationary/turn/stop/jump as supported; validate sender ownership/finite transforms according to established contract; no new packet guesses |
| M1-11 | Remove/reconstruct actors across logout/disconnect/reconnect | M1-10 | Other client sees departure; reconnect creates/reuses identity according to proven contract; old peer cannot mutate new session; no duplicate/stale actor |
| M1-12 | Document/run complete friend-hosted acceptance | M1-11 | Two-client ten-minute/reconnect scenario, then optional2-8private peers; ports/interface/start/stop/runbook; clean stop with no unrelated process changes; no claim based solely on unit tests |

Compression/reliability/reassembly fixes are narrowly pulled into M1-03/06/08 **when required by observed target traffic**, not a speculative rewrite. The known wrap/channel/scheduling limits in [First Light analysis](FIRST_LIGHT_ANALYSIS.md) deserve targeted falsification before they affect long-running sessions. A TCP/UDP socket count is not an actor count.

## Exact next blocker

**Private-anchor loading boundary preserving verification, followed by actual game acceptance.** Local CA-verified DTLS peers exchange data; the stock client still rejects our owned configured full-chain response with fatal unknown_ca. Current REP wrapper/interface source joining is complete; both known connect branches converge on the factory, whose UDP cases have an embedded-certificate→transport→connection→secure-driver→store path, standard verifier and parameter-gated identity checks. This does not establish live context contents, all aliases/callbacks or a supported override. [REP_TRUST_POLICY](REP_TRUST_POLICY.md). Carrier/V3 waits for actual current-client transport acceptance.

Two subsequent original-launcher cases (default versus child SSL_CERT_FILE=retainedCA) also each reject with two explicit unknown_ca alerts. No verified game-environment readback; do not label the variable consumed/ignored. Initial discriminator inspection could not join the initializer; the newer positive source/object/verifier map supersedes that gap. Six current-game attempts total across three runs; no Carrier/V3 or actor. No tested code changed after273-pass regression; all39 receipt artifact hashes remain current. Local analysis/receipts/documents added separately, not a new live test.

Next small checks in order: (1) prove a private-anchor loading boundary without broad validation bypass, retaining wrong-root rejection; (2) observe owned context/transport/verification metadata if runtime attribution is needed, then record actual game handshake completion and first genuine application input; (3) parse/respond to that current Carrier/V3 input with versioned sanitized fixtures. The static source/object attribution step is complete. Do not substitute generic local-peer success for game acceptance or invent registration bodies.

M1-02B3 is complete only as a compatible synthetic response/address handoff; M1-04/05 still own secure private identities/ticket-to-peer binding. Incoming signatures and queue bodies were not validated. No world-loading screen, actor or multiplayer. Current full workspace273 pass/no skips; prior261-test queue and268-test local-DTLS receipts remain historical. Previous token/credentials/login-info checkpoints are preserved separately. No current spawn packet is validated.

The next **world-entry protocol blocker** after that gate is establishing/generated actor/replica creation and its self-identification/level/replication dependencies. First Light's proposed three-message minimum is not established. Do not jump straight to movement fan-out or describe current OpenWorld community claims as solving it.

M1-03's isolated DTLS exchange slice is complete; prolonged/current-game transport and registration remain. No broad language/framework redesign is needed.

## After Milestone 1

Incrementally add durable private accounts/characters/positions, authoritative combat and health, NPC spawn/AI, equipment/inventory, gathering/refining/crafting, quest state/dialogue, then expeditions. Choose vertical slices with private-fixture proof, not complete-system scaffolds. Item/world content needed on the server must come from lawful local inspection or independently produced definitions; do not assume the client contains Amazon's backend logic.

## Verification and handoff

Run the scripts in [README](../README.md). Current original receipt: `research/evidence/latest-validation.json`; historical sparse and fixture-enabled receipts remain separate. Fresh isolated bootstrap validation is recorded in `research/evidence/fresh-reference-summary.json`. Raw output stays ignored in `.scratch/`.

Every future packet change must record: upstream/source dirty-state identity, exact client build, fixture hash, direction/state/channel/type, input/output relationships, positive and rejection cases, and remaining unknowns. Relevant edits stale affected evidence only. Add structured transition logs when implementing connection behavior; no tokens/keys/raw bodies in normal logs.

Repository history is local-only; no remote was created and no code/asset/capture was published. Actionables was not updated because no governing `workItemId` was supplied.
