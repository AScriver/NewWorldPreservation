# Bounded task briefs

These are starting questions and candidate scopes, not current task status or an
automatic assignment. [ROADMAP](ROADMAP.md) owns progress, dependencies and acceptance.
Before work, select one ID, check its gates, and fill the template with exact files
and verified input identities. Future module names are decided when evidence makes
implementation possible; no speculative server scaffold is implied here.

## Task brief template

```markdown
Task / bounded question: <ROADMAP ID and one answerable outcome>
Input identity: <HEAD, relevant dirty/untracked hashes; runtime/lock; client build;
                 upstream commit/dirty state; fixture hashes; execution config/data>
Evidence: <ledger claim IDs and exact public docs/receipts/fixtures; known limits>
Owner / files: <exact owned edit paths; other owners; read-only references>
Permitted operations: <read-only/offline edits/tests; separately authorized live scope>
Resource contract: <unique temp data/ports/processes; owner; isolation; serialization>
Completion: <positive observable result and exact verification command/profile>
Rejection checks: <negative cases; evidence that would falsify the proposed result>
Failed approaches: <conditions/results to retain; no blind repetition>
Cleanup: <owned resources/readback; private diagnostics/receipt locations>
Handoff: <AGENT_HANDOFF format; ROADMAP/ledger updates; next bounded step>
```

## Shared operating contract

The candidate scopes below permit original integration code, lawful sanitized
fixtures, documentation and explicitly selected offline tests with temporary data
and loopback-only listeners. They do not authorize game launches, process-memory
observation, routing/trust changes, capture hooks, endpoint contact, upstream
vendoring or publication. Apply an existing explicit user authorization to a live
step only within its actual scope; identify the runbook and resource owner first.

For every brief, cleanup means release the listeners/child processes it created,
preserve unrelated resources, keep raw diagnostics private in a unique ignored run
directory, and record executed cleanup versus unknown cleanup. Shared hosts, trust,
clients or fixed ports require serialization with the actual owner. A source review
is not an experiment, and an offline test does not unlock real-client acceptance.

## M1-00 — reference and environment

- Question: Can the named pinned public implementation/profile be reproduced?
- Evidence: E02/E03/E12/E13/E14; [reference catalog](EVIDENCE_INDEX.md).
- Candidate files: original setup/verification scripts, lock, upstream pin metadata,
  `test_validation_gate.py`; external source is read-only.
- Complete/reject: exact origin/commit/clean fixture, lock match, 455 passes and the
  one named skip; reject changed references, unexpected skips or empty coverage.
- Check: `upstream`; existing setup scripts only when setup is required.
- Prior failures: sparse checkout omitted the replay fixture; retain E13.
- Cleanup: ephemeral context certificate/key removed; upstream remains unchanged.

## M1-01 — build-bound client observations

- Question: Which build, ownership and sanitized observations support this slice?
- Evidence: K01–K07; [connectivity](CURRENT_CLIENT_CONNECTIVITY.md).
- Candidate files: inspection/observer metadata code, build-bound fixtures/tests/docs.
- Complete/reject: build/hash and exact launch/owner attribution with disclosed image
  limits; reject reused PID/start-time or treating installed bytes as live-image proof.
- Check: `fixtures-static`, `windows-native`, `powershell`; own-session observation
  is a separately authorized procedure.
- Prior failures: inaccessible image paths weakened exact-process attribution.
- Cleanup: record owned observation resources separately from retained metadata.

## M1-02A — private bootstrap HTTPS

- Question: Does the recorded stock client reach the owned endpoint with valid trust?
- Evidence: C02–C08/K02–K07; [connectivity](CURRENT_CLIENT_CONNECTIVITY.md).
- Candidate files: connectivity probe/metadata/owner controls and sanitized fixtures.
- Complete/reject: attributed live GET plus positive/absent-CA/wrong-name/reversal
  comparisons; reject permissive synthetic TLS as client verification evidence.
- Check: `protocol-loopback`, `windows-native`, `powershell`; live routing/trust work
  requires its own runbook and approval already covering those resources.
- Prior failures: resets alone did not establish pinning or verifier semantics.
- Cleanup: any authorized live routing/trust/client resources need exact readback.

## M1-02B — channel descriptor

- Question: Which descriptor schema selects the client's next private services?
- Evidence: K08–K12; [channel](BOOTSTRAP_CHANNEL.md).
- Candidate files: channel descriptor, bootstrap probe/log code, descriptor fixtures/tests.
- Complete/reject: observed parsing/next request with original required hostname
  semantics; reject assuming every supplied field was consumed.
- Check: `fixtures-static`, `protocol-loopback`; live progression separately gated.
- Prior failures: preserving service/token hostname semantics mattered to selection.
- Cleanup: isolated fixture listeners; live resources under their separate owner.

## M1-02B1 — token request

- Question: What method/route/host metadata identifies the owned token request?
- Evidence: K13–K15; [token](TOKEN_SESSION_CONTRACT.md).
- Candidate files: bootstrap/flow metadata code and sanitized request/result fixtures.
- Complete/reject: attributed token POST/host transition; deliberate 501 is a stop,
  and neither logged authorization presence nor TLS alone proves authentication.
- Check: `fixtures-static`, `protocol-loopback`.
- Prior failures: retain deliberate endpoint stops and their actual conditions.
- Cleanup: discard credential/body values; preserve only approved safe metadata.

## M1-02B2 — token envelope

- Question: Which evidenced response envelope advances the current parser?
- Evidence: K16–K21; [token contract](TOKEN_SESSION_CONTRACT.md).
- Candidate files: token contract builder, candidate/result fixtures and tests.
- Complete/reject: compatible positive/control comparisons and deterministic builder
  cases; reject inferring requiredness, refresh or private auth from one accepted model.
- Check: `fixtures-static`, `protocol-loopback`.
- Prior failures: empty-model control remains separate from accepted synthetic models.
- Cleanup: synthetic identities only; never persist/replay official credentials.

## M1-02B3 — credentials, preview and queue handoff

- Question: Which responses select the private game endpoint on the recorded build?
- Evidence: K22–K35; [credentials](CREDENTIALS_SESSION_HANDOFF.md),
  [login-info](LOGIN_INFO_CONTRACT.md), [game handoff](PRIVATE_GAME_HANDOFF.md).
- Candidate files: credentials/session/queue/UDP builders, metadata and fixtures/tests.
- Complete/reject: observed selection/queue-to-owned-address chain; reject frontend
  preview as world entry or synthetic token acceptance as secure ticket validation.
- Check: `fixtures-static`, `protocol-loopback`, `windows-native`.
- Prior failures: raw-target matching failed on a query; preserve K27 and guard tests.
- Cleanup: discard incoming signatures/bodies; release owned loopback services.

## M1-02C — unchanged-client REP trust

- Question: Is there an evidenced normal private-anchor input preserving verification?
- Evidence: K36–K48 and later ledger updates; [trust policy](REP_TRUST_POLICY.md).
- Candidate files: original safe metadata/DTLS/fake-API controls and docs; private
  client analysis remains ignored and independently owned.
- Complete/reject: identify actual input/consumption before a separately authorized
  real-client positive/unrelated-root comparison. Reject guessing settings keys,
  treating descriptor construction as loading, or claiming acceptance from local peers.
- Check: `protocol-loopback`, `rep-readonly`, `powershell`; no live probe CLI here.
- Prior failures: intact EAC refused disk anchor substitution (K41/K45); route retired.
  SSL_CERT_FILE comparisons rejected; environment consumption remains unproved.
- Cleanup: honor retained CA policy; any live trial has its own strict ownership/readback.

## M1-03 — responder transport

- Question: Can independently controlled verified peers exchange data and recover
  according to the transport evidence?
- Evidence: E06/C08/K33; [DTLS](DTLS_REGISTRATION.md) and local control receipts.
- Candidate files: original DTLS transport and isolated transport/lifecycle tests.
- Complete/reject: verified independent peers, unrelated-root rejection, timers,
  capacity/error/stop behavior; reject calling these peers real game clients.
- Check: `protocol-loopback`, then opt-in `upstream` for unchanged reference checks.
- Prior failures: stock `unknown_ca` is a separate real-client gate, not local exchange.
- Cleanup: close each created socket/peer and remove ephemeral cert/key files.

## M1-04 — private identities and selections

- Question: Can two private accounts select only their own characters using evidenced schemas?
- Evidence: E05/K22–K30; [authority constraints](ARCHITECTURE.md#authority-and-lifetime-decisions).
- Candidate files: original private identity/selection modules chosen in the brief,
  existing evidenced response builders, new isolation/security tests.
- Complete/reject: disjoint ownership, wrong/expired credentials rejected and defined
  cold-restart behavior; reject shared mutable personas as private account storage.
- Check: new named offline security tests after profile review; existing contract profiles.
- Prior failures: accepted synthetic envelopes proved compatibility, not account security.
- Cleanup: isolate account/test data; do not alter another agent's database/session.

## M1-05 — ticket-to-peer binding

- Question: Can one authorized private identity/world ticket bind exactly one game peer?
- Evidence: E05/K31–K35; [handoff limits](PRIVATE_GAME_HANDOFF.md).
- Candidate files: original issue/consume binding code and deterministic security tests;
  current queue schema changes require their own wire evidence.
- Complete/reject: issue/consume/expiry/replay/wrong-account cases; reject identity inferred
  from byte span length or unchecked synthetic queue bodies.
- Check: reviewed new offline ticket tests and evidenced contract profiles.
- Prior failures: queue200/owned UDP was not secure ticket/signature/JWT acceptance.
- Cleanup: isolated ticket store and fake peers; expire only the test's own identities.

## M1-06 — current registration/world-entry contract

- Question: What accepted current-build types/body order connect transport to world readiness?
- Evidence: E07/E09/E10/E11/K33/K45; [spawn sequence](SPAWN_SEQUENCE.md).
- Candidate files: independently original parsers/serializers, lawful sanitized fixtures,
  type/order/retry rejection tests and state-transition logs.
- Complete/reject: versioned evidence for each boundary and positive/omission controls;
  reject a historical guessed three-message recipe or unvalidated registration body.
- Check: new fixture-driven profiles; actual Carrier/V3 observation waits for REP acceptance.
- Prior failures: historical retries/black screens had different configurations (E10).
- Cleanup: isolate replay data; keep raw/proprietary observations private and ignored.

## M1-07 — one generated actor

- Question: Can a real client visibly spawn one server-generated private character?
- Evidence: E07/E09 and M1-06's accepted current contract; [spawn](SPAWN_SEQUENCE.md).
- Candidate files: original session/actor state and evidenced spawn responses/tests.
- Complete/reject: visible actor and usable camera/map with proven transition; reject
  frontend preview, black loading screen or impersonation of one replayed persona.
- Check: deterministic generation/identity tests plus separately authorized real-client run.
- Prior failures: historical replay-held connections did not prove successful world entry.
- Cleanup: remove the run's actor/peer and record owned client/service shutdown.

## M1-08 — actor baseline and delta encoding

- Question: Which current byte contracts identify actors and encode verified transforms?
- Evidence: E07/E08/E09/E11 and build-bound M1-06 inputs; [protocol](PROTOCOL_NOTES.md).
- Candidate files: original codecs, approved fixtures and exact-boundary/round-trip tests.
- Complete/reject: observed actor/member IDs and transforms, truncation/unknown-type
  cases; retain explicit unknown tails or reject them, never infer layout from a name.
- Check: new named fixture/codec tests; historical upstream tests remain a separate scope.
- Prior failures: historical position type/bundle documentation was not an executable
  current-build component decoder.
- Cleanup: no copyrighted asset/raw secret redistribution; retain fixture provenance.

## M1-09 — two players in one world

- Question: Do two distinct private identities produce two mutually visible real actors?
- Evidence: M1-05/07/08 accepted evidence, E05/E06/E07; [architecture](ARCHITECTURE.md).
- Candidate files: original world/actor authority and visibility/isolation tests.
- Complete/reject: each client sees the other's correct identity/baseline; reject two
  sockets, two frontend previews or duplicated replay identity as two-player proof.
- Check: deterministic isolation tests and separately authorized bilateral live acceptance.
- Prior failures: per-address responder peers did not implement shared-world authority.
- Cleanup: remove each owned peer/actor and prove the other session remains independent.

## M1-10 — bilateral movement

- Question: Does each accepted movement update reach the other real player correctly?
- Evidence: M1-09 plus current M1-08 transform contract; E07/E08; [authority](ARCHITECTURE.md).
- Candidate files: original movement acceptance/replication and identity/value tests.
- Complete/reject: A moves/B sees then reverse, stop/turn/direction cases; reject guessed
  input packets or an authority/prediction policy inferred from a class name.
- Check: codec/ownership/finite-value tests consistent with the evidenced protocol;
  real bilateral movement is a separate acceptance gate.
- Prior failures: logging typed inbound decode alone supplied no authoritative fan-out.
- Cleanup: reset only owned test world state and release its replication peers.

## M1-11 — disconnect and reconnect

- Question: Does departure/reconnect preserve identity without stale or duplicate actors?
- Evidence: established M1-09/10 behavior; E06/E07 and [lifetime constraints](ARCHITECTURE.md).
- Candidate files: original peer/session/actor lifecycle and reconnect rejection tests.
- Complete/reject: remaining client observes departure and reconnect; old peer cannot
  mutate the new session. Actor reuse versus replacement follows the proven contract.
- Check: deterministic expiry/disconnect/replay tests and separately authorized reconnect.
- Prior failures: socket/idle helper tests did not exercise a full client/world lifetime.
- Cleanup: expire only owned peers and verify no duplicate/stale actor remains.

## M1-12 — complete acceptance and hosting handoff

- Question: Can two legitimate private clients satisfy every ROADMAP acceptance condition?
- Evidence: accepted M1-01 through 11 slices; [acceptance](ROADMAP.md#acceptance-boundary).
- Candidate files: original start/stop/hosting runbook and safe acceptance receipts.
- Complete/reject: distinct accounts/characters, same world, bilateral movement,
  at least ten minutes together and one reconnect with no stale actor; reject offline
  tests as proof. Optional 2–8 peers follow the two-client gate.
- Check: named offline regression and the separately authorized complete live scenario.
- Prior failures: HTTPS, synthetic DTLS, frontend/queue handoff and transport counts
  each stopped short of this acceptance boundary.
- Cleanup: owned services/clients/ports stopped with readback; unrelated resources intact.

## Evidence and handoff maintenance

Use [EVIDENCE_INDEX](EVIDENCE_INDEX.md) to locate the exact files/fixtures behind the
claim IDs; classification and scope stay in the ledger and receipts. Extend this
page when ROADMAP adds a task. Do not copy changing Done/Partial/Blocked labels here.
The owner fills exact runtime/data identity and resource scope in each assignment,
then returns [AGENT_HANDOFF](AGENT_HANDOFF.md) with executed checks and counter-evidence.
