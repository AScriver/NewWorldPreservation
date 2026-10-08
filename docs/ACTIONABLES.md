# Pending work in Actionables

Created October 5, 2026 at the user's request from the unfinished
[ROADMAP](ROADMAP.md#small-independently-testable-tasks) outcomes and current
[TASK_BRIEFS](TASK_BRIEFS.md). This is a creation snapshot, not a second progress
ledger: ROADMAP retains current technical evidence, progress and milestone acceptance.

## Scope and hierarchy

Milestone 1's top-level Actionable is **#164**:
**Milestone 1 — two private clients in one world with bilateral movement**.
Use `workItemId: 164` for its exact authorized task; its eleven immediate children
and three nested registration slices are listed below.

| Roadmap outcome | Actionable | Pending outcome |
|---|---|---|
| M1-01 | #166 | complete build-bound entry, movement and reconnect evidence |
| M1-03 | #167 | verify prolonged transport, idle recovery and reconnect |
| M1-04 | #168 | isolate two private accounts and character selections |
| M1-05 | #169 | bind a private world ticket to one authorized peer |
| M1-06 | #170 | establish the current registration-to-world-entry contract |
| M1-07 | #171 | spawn one fresh generated private character |
| M1-08 | #172 | establish current actor baseline and transform delta codecs |
| M1-09 | #173 | spawn two distinct players in one private world |
| M1-10 | #174 | apply and replicate movement in both directions |
| M1-11 | #175 | preserve actor identity across disconnect and reconnect |
| M1-12 | #176 | run complete two-client acceptance and hosting handoff |

The registration/world-entry coordinator **#170** contains these three children;
their top-level `workItemId` remains **164**, not 170.

| Research slice | Actionable | Bounded outcome |
|---|---|---|
| M1-06A | #177 | join bundle decoding to fresh player creation and designation |
| M1-06B | #178 | identify initial registration type and authentication semantics |
| M1-06C | #179 | validate current world-entry fixtures and phase transitions |

Fresh player creation/designation is coordinated by **#177**; its next
bounded source task is **#207**, the current type8 decoder/member-recipient join.
It investigates the actual current type8 decoder/subscriber/member/entity/registry
joins before any new payload trial. **#178** separately resolves initial request
and authentication semantics. **#179** turns established joins into current
fixtures and phase checks. The unsent maintainer question is a documentation
source; no contributor message was authorized.

The independent parked alternative is **#165**:
**M1-02C — establish supported unchanged-client private REP trust**.
It has its own `workItemId: 165`, remains parked pending concrete new evidence,
and is outside #164's hierarchy so it cannot become an artificial prerequisite
for the admitted isolated-client route.

Completed M1-00 and M1-02A/B/B1/B2/B3/H were not recreated. M1-01 and M1-03 cover
only their unfinished evidence/lifetime portions. Later gameplay ideas in
[After Milestone 1](ROADMAP.md#after-milestone-1) were not expanded into speculative
implementation tasks.

## Prerequisites and acceptance

Prerequisites are written in task descriptions. **No persisted blocking edges**
were created: this creation-only request leaves tasks unclaimed in Inbox.

- #166 assembles actual entry, movement and reconnect evidence from #170/#171/#173/#174/#175 as those slices finish; it does not duplicate implementation.
- #167 closes the remaining prolonged/idle/reconnect transport contracts; #168 implements isolated private accounts using already evidenced response schemas.
- #169 requires #168's identities, #167's transport/lifetime evidence and #178's registration/authentication contract.
- #170 coordinates #177/#178/#179. Static contract work can proceed before real authenticated acceptance; #169 additionally gates the latter.
- #171 requires #170's accepted current player/world-entry contract and an admitted live procedure.
- #172's current codec work uses established build-bound #170/#177/#179 evidence and can proceed offline before visible #171 spawn when its inputs are established.
- #173 requires #169/#171/#172; #174 requires #173/#172; #175 requires established #173/#174 behavior.
- #176 consolidates #166 through #175 for complete actual-client acceptance. Ten-minute coexistence, bilateral movement and reconnect remain live gates.
- #179 requires source-backed #177/#178 inputs; real authenticated trials also require #169 and an explicitly admitted procedure.

Every task includes deliberate priority, estimated effort, meaningful tags, an
intended outcome, completion/rejection boundaries, planned checks and evidence
references in its description. Research may finish with a precise bounded answer
or missing-contract report; that does not make the gameplay condition true.
Implementation owners must refresh exact files/input identities and fill the
[task brief template](TASK_BRIEF_TEMPLATE.md) before execution.

Creation starts no implementation, game process, hook, endpoint contact or system
change. Existing [AGENTS](../AGENTS.md), owned-copy/loopback procedures, private-output
and cleanup boundaries remain authoritative. Task membership does not extend
live-operation or contributor-message authorization.

## Creation identity and verification

Baseline HEAD: `c4b98ee66da69bed54b45845703370914de8ff87`. The checkout already contained unrelated dirty
and untracked protocol/trial/documentation changes. Creation used the following
working-tree bytes; the associated docs edits necessarily change their later
hashes. Refresh relevant identities before technical work.

| Baseline input | SHA-256 |
|---|---|
| AGENTS.md | `83c3f03c49da4b923155d99d5fb5ed2b7981845d3d75a5e0d8c884c1ddb16810` |
| docs/ROADMAP.md | `3f9669606a9be21a05be6d3e6c3a27826f46595b0e11ebef88ea38904ccb755c` |
| docs/TASK_BRIEFS.md | `0fcd535b2bb30952887c66e72ef5f78448a737d5b645ad3cfa6bbf8ce58e2a2d` |
| docs/AGENT_START.md | `e5682522bfca505a60133cbd635e6b86543638379c2f318112801165272c7c33` |
| research/evidence/current-player-spawn-source-map.json | `07cb671ac79d30ab0137dcb0c16c3f31272aac0dffc1281bf99fd74ad8239bcd` |
| research/evidence/current-self-length-prefix-trial.json | `16615564497c82f6b8f3fa1ab766d7145cce7236869335b515cc5cbd18925cf9` |
| research/evidence/current-self-length-prefix-validation.json | `d965463569871ca9fd5c2eaf8ac740940e72dd97ee046ececd45b5dfc88299d7` |

The validated creation plan checked sixteen unique task keys/UUIDs, two roots,
eleven immediate Milestone 1 children, three nested slices, seven unchanged source
identities and twenty-four existing file references. All three ordered bulk
batches passed preview before apply; every per-item result reported creation.

Read-only scoped inspection then verified all **#164–#179** in the
**NewWorldPreservation / NewWorldPreservation / Default** scope, the exact
parent/root relationships, titles, priorities, efforts and tags, **Inbox** status,
and **no claims**. #164's complete inventory contained fourteen descendants with
no next page; #165 had no children. No lifecycle transition, completion or
dependency mutation occurred.

Original creation plan, per-batch receipts and final readback stay in ignored
`.scratch/actionables-20261005T1806Z/`; no credentials or claim tokens were created.
The tracking-only validation checks source links, mapping coverage, lifecycle
readback and the scoped staged diff; it makes no new protocol/runtime claim.

## Effort breakdown — October 5

The user requested that every M–L-or-larger task be broken into smaller subtasks.
All original large tasks are now coordination parents; their estimates still
describe aggregate work. Every executable leaf is **M or smaller**. Keep this
rule when creating or refining future tasks: if a leaf grows above M, divide its
complete outcome into independently verifiable children before execution.

The existing #164 milestone and #170 registration hierarchy was preserved.
Thirteen previously large leaves gained **35 subtasks (#180–#214)**. #166 was
already M and remains a leaf. Creation-only readback confirmed **51 total tasks**,
**36 leaves**, **Inbox** status and **no claims** throughout both scoped trees.
There are no unsplit M–L/L/L–XL/XL leaves.

| Coordination parent | New subtask | Effort | Bounded outcome |
|---|---|---|---|
| #165 | #180 | M | trace a new supported root input into the actual REP store |
| #165 | #181 | M | verify supported stock-client trust with positive and negative controls |
| #167 | #182 | M | verify prolonged transport and idle recovery |
| #167 | #183 | M | verify transport reconnect, peer budgets and clean shutdown |
| #168 | #184 | M | return disjoint character selections for two private accounts |
| #168 | #185 | M | reject invalid private credentials and cross-account selection |
| #168 | #186 | S–M | define and verify private account session restart behavior |
| #169 | #187 | M | issue and consume one correctly bound private world ticket |
| #169 | #188 | M | reject expired, replayed and wrongly bound world tickets |
| #169 | #189 | S–M | bind accepted registration to the authorized peer lifetime |
| #171 | #190 | M | construct one fresh source-backed player spawn payload |
| #171 | #191 | M | register and designate the generated player for its private character |
| #171 | #192 | M | verify one visible player with usable camera and map |
| #172 | #193 | M | encode and decode the current actor identity baseline |
| #172 | #194 | M | encode and apply verified transform deltas |
| #172 | #195 | S–M | handle malformed and unknown actor members safely |
| #173 | #196 | M | admit two distinct authorized players into one world |
| #173 | #197 | M | replicate each fresh actor baseline to the other player |
| #173 | #198 | S–M | reject wrong-world and duplicate-identity player joins |
| #174 | #199 | M | apply authorized movement to the correct actor |
| #174 | #200 | M | replicate accepted movement in both directions |
| #174 | #201 | M | preserve stationary, turn and stop behavior during movement |
| #175 | #202 | M | remove departed actors without disrupting the remaining player |
| #175 | #203 | M | restore the authorized character on a fresh peer connection |
| #175 | #204 | S–M | reject stale peer input after player reconnect |
| #176 | #205 | M | document and verify the bounded hosting start/stop procedure |
| #176 | #206 | M | verify the full ten-minute two-client milestone |
| #177 | #207 | M | join the current type8 decoder to its member recipient |
| #177 | #208 | M | join replication members to fresh entity and player construction |
| #177 | #209 | M | join fresh character identity and readiness to player designation |
| #178 | #210 | M | identify initial registration framing, type and retry contract |
| #178 | #211 | M | establish registration authentication and peer binding semantics |
| #179 | #212 | M | validate original current world-entry member fixtures |
| #179 | #213 | M | validate transport, context and actor prerequisite ordering |
| #179 | #214 | M | observe admitted current contract phase transitions |

The next bounded static task is **#207** under #177, with `workItemId: 164`.
Its siblings #208/#209 close the fresh constructor/registry and
identity/readiness/designation joins. #180/#181 stay within the separate parked
stock-client root, `workItemId: 165`.

Each child retains its parent's original outcome and authorization limits, with
its own completion/rejection boundary, prerequisite notes, planned checks and
source references. Outcomes include their own implementation/research and
verification; the split is not a separation into code and test layers.
Parent prerequisite names refer to established evidence within the parent;
do not invent an all-parent-Done cycle where static source/fixture work can
proceed before separately admitted actual-client acceptance. Persisted blocking
edges still have not been created.

The baseline was HEAD `5ffc867646647fe557c560d673c020f08ef1a092` plus the existing
dirty protocol/trial/documentation state. Split-plan validation checked thirteen
explicit parents, thirty-five unique keys/UUIDs, five unchanged baseline inputs,
twenty existing file references and leaf effort at most M. Both batches passed
preview before ordered apply. Final scoped inspection exhausted two pages under
#164 (47 descendants) and one under #165 (2 descendants), verifying exact task
titles, hierarchy/root, priorities, tags, effort, lifecycle and claim state.

The plan, applied receipts and complete readback are ignored under
`.scratch/actionables-split-20261005T1823Z/`. No task was claimed, prepared,
advanced or completed; no dependency mutation, implementation, client trial,
game/system operation or contributor contact occurred.
