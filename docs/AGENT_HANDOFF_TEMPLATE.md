# Agent handoff template

Use this format at a task boundary. Keep current task status in [ROADMAP](ROADMAP.md)
and substantive factual claims in [EVIDENCE_LEDGER](EVIDENCE_LEDGER.md). A handoff
links those records rather than creating another current-status document.

```markdown
Task: <ROADMAP ID and bounded outcome>
Owner / edit scope: <agent and exact files; independently owned files preserved>
Checkout: <HEAD, relevant dirty/untracked paths and hashes; runtime/lock identity>
Evidence inputs: <claim IDs; build, upstream commit/dirty state, fixture hashes>
Slice result: <complete | partial; result for this bounded outcome>
Next owner: <agent | user | external | none>
Next action / reason: <one bounded action and why that owner must perform it>
Required authorization: <existing task/live scope; specific missing grant; or none additional>

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

A completed offline slice can coexist with an open native or gameplay milestone.
Use agent when authorized independent work remains; use user for a required
decision, grant or manual observation; identify the actual outside dependency
for external. Use none only when the requested bounded outcome and closure are
complete. These fields describe responsibility, not new Actionables states or
permission to extend a live procedure. Preserve historical handoffs unchanged.

For offline tooling, identify the unique run receipt and the input hashes in it.
Do not paste private stdout, raw packets, secrets, client assets or decoded
proprietary material into the handoff. Store a hash/reference when a private
artifact is necessary; disclose that another agent has not verified its contents.

Preflight labels matching **public local bindings**, stale local inputs and unknown
bindings separately. A stale source receipt remains historical evidence; a fresh
hash does not rerun its experiment. Do not report a local synthetic DTLS peer as a
New World client or a frontend preview as an in-world actor.
