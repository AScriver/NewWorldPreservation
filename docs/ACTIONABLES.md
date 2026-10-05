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

The next source task is **#177**, the fresh player creation/designation contract.
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
[TASK_BRIEFS template](TASK_BRIEFS.md#task-brief-template) before execution.

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
