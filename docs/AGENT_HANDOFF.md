# Agent handoff

October6 #234: [clone/Id contract](PLAYER_ENTITY_CLONE.md), K281–K286 and
[receipt](../research/evidence/current-player-entity-clone.json) close conditional
nested allocation/copy/custom mapping. Initial generic-only Id pass, pointer
correction, partial/no-PDATA queries and null/skip/error cases remain retained.
Private file-only helper resources exited; offline runner receipts record owned
loopback cleanup. Local commit only; next permitted #164 leaf follows release.
Parent232 aggregate, concrete member/schema, #212 and bilateral movement stay open.

Use this format at a task boundary. Keep current task status in [ROADMAP](ROADMAP.md)
and substantive factual claims in [EVIDENCE_LEDGER](EVIDENCE_LEDGER.md). A handoff
links those records rather than creating another current-status document.

```markdown
Task: <ROADMAP ID and bounded outcome>
Owner / edit scope: <agent and exact files; independently owned files preserved>
Checkout: <HEAD, relevant dirty/untracked paths and hashes; runtime/lock identity>
Evidence inputs: <claim IDs; build, upstream commit/dirty state, fixture hashes>

Changes:
- <concrete behavior changed, why, and affected files>

Executed verification:
- <exact command/profile; start/end; counts and outcomes; receipt path + SHA256>
- <selected inputs unchanged or changed during run; cleanup observed>

Evidence limits:
- Observed/reproduced: <what actually ran, with references>
- Source inference: <bounded conclusions, with references>
- Historical upstream: <prior results and their input/config identity>
- Synthetic: <controls/fixtures and what they cannot prove>
- Unrun/unknown: <missing acceptance checks and material uncertainty>

Failed approaches / counter-evidence:
- <conditions actually tested, result, and why not to repeat blindly>

Resources / cleanup:
- <owned temp data, child processes, ports, trust/routing if separately authorized>
- <executed readback or explicit unresolved cleanup; retained diagnostics>

Next concrete action:
- <one bounded step, required evidence/authorization and verification command>
ROADMAP / ledger updates: <links to the preserved task and claim records>
```

For offline tooling, identify the unique run receipt and the input hashes in it.
Do not paste private stdout, raw packets, secrets, client assets or decoded
proprietary material into the handoff. Store a hash/reference when a private
artifact is necessary; disclose that another agent has not verified its contents.

Preflight labels matching **public local bindings**, stale local inputs and unknown
bindings separately. A stale source receipt remains historical evidence; a fresh
hash does not rerun its experiment. Do not report a local synthetic DTLS peer as a
New World client or a frontend preview as an in-world actor.
