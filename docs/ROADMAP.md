# Milestone 1 roadmap

## Acceptance boundary

Two legitimate PC clients, distinct **private** accounts and characters, same Aeternum world/map, two distinct visible players and bilateral position/movement updates. Test both roles, stop/turn/reverse direction, logout and reconnect. For acceptance, record at least ten minutes together and one reconnect without a duplicate/stale actor. Ten minutes is **our test criterion**, not a discovered protocol timeout.

No Amazon service, credentials or asset redistribution should be necessary for the final private backend. Existing local client assets remain with their legitimate owners. Ignore the Trading Post/MMO-scale systems listed in [architecture](ARCHITECTURE.md).

## Current status

- Research completed for the publicly accessible pinned First Light/Aeternum sources and visible forks. Private OpenWorld implementation remains uninspectable.
- **M1-00 completed:** reproducible development/reference/test environment. Original scripts pin source and redacted fixture, hash-lock dependencies, guard verification and log test transitions.
- **455 upstream tests passed, one deliberate skip; 9 original gate tests passed.** Certificate-backed DTLS context/memory BIO constructed; no handshake/client tested.
- No New World install found in discovered local Steam libraries. No game launched, live packets observed, account created, host mapping changed or trust hook enabled.
- **Milestone 1 not achieved.** No private account system, world entry, actor spawning or mutual movement implemented by this workspace.

## Small independently testable tasks

Tasks are bounded outcomes, not assignments to layers. Dependencies identify actual prerequisites; independent offline checks can proceed separately. No Actionables scope was supplied, so this Markdown is the task record.

| ID | Outcome / scope | Depends on | Independent verification / completion criterion |
|---|---|---|---|
| M1-00 **Done** | Reproduce strongest public Python implementation; retain unchanged source and existing fixtures externally | None | Pinned clean source/hash-verified fixture; hash-pinned venv; explicit 11-module profile: 455 pass / 1 intentional skip; 9 gate tests; DTLS context constructor |
| M1-01 Next, time-sensitive | Pin actual owned target client and collect minimal normal-session bootstrap/entry/movement/reconnect evidence | Access to legitimate installed client/session, not M1-00 | Version/hash/build metadata + consented scenario manifests; actual transitions distinguished from unknown/encrypted data; no secrets in tracked output |
| M1-02 | Resolve controlled private bootstrap and certificate trust for target build | M1-01 | One legitimate client deliberately reaches only our loopback auth/DTLS endpoints; prove negotiation or precisely identify trust failure; no official auth bypass or machine-wide mutation hidden in a launcher |
| M1-03 | Exercise actual responder transport with two locally controlled protocol endpoints | M1-00 | Actual loopback DTLS handshake/send/receive for two independent peers; no sequence/key/session cross-talk; deterministic disconnect/idle cleanup; these endpoints are **not** New World clients |
| M1-04 | Implement two private account/character selections with client-compatible response schemas | M1-01's schema evidence; M1-02 for client acceptance | Two logins return disjoint character ownership; wrong/expired credentials rejected locally; changing one identity cannot rewrite another; cold restart behavior explicitly defined |
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

The first local development blocker—missing fixtures/unpinned environment—is resolved. The **next live-client gate** is identifying the actual target build and proving how it can use our private bootstrap and trusted DTLS endpoint. This host has no identified game install; public source cannot establish that behavior for the latest legitimate executable.

The next **world-entry protocol blocker** after that gate is establishing/generated actor/replica creation and its self-identification/level/replication dependencies. First Light's proposed three-message minimum is not established. Do not jump straight to movement fan-out or describe current OpenWorld community claims as solving it.

M1-03 is the next independent offline slice if live client access is not available. No broad language/framework redesign is needed.

## After Milestone 1

Incrementally add durable private accounts/characters/positions, authoritative combat and health, NPC spawn/AI, equipment/inventory, gathering/refining/crafting, quest state/dialogue, then expeditions. Choose vertical slices with private-fixture proof, not complete-system scaffolds. Item/world content needed on the server must come from lawful local inspection or independently produced definitions; do not assume the client contains Amazon's backend logic.

## Verification and handoff

Run the scripts in [README](../README.md). Current original receipt: `research/evidence/latest-validation.json`; historical sparse and fixture-enabled receipts remain separate. Raw output stays ignored in `.scratch/`.

Every future packet change must record: upstream/source dirty-state identity, exact client build, fixture hash, direction/state/channel/type, input/output relationships, positive and rejection cases, and remaining unknowns. Relevant edits stale affected evidence only. Add structured transition logs when implementing connection behavior; no tokens/keys/raw bodies in normal logs.

Repository history is local-only; no remote was created and no code/asset/capture was published. Actionables was not updated because no governing `workItemId` was supplied.
