# Task brief template

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
Expected next owner: <agent | user | external | none; one bounded action and reason>
Required authorization: <existing task/live scope; specific missing grant; or none additional>
```

The brief identifies expected responsibility; the handoff records the actual slice
result and next owner. These fields do not change Actionables lifecycle states or
native/gameplay acceptance. Use agent when authorized independent work remains;
reserve user for a required decision, authorization or manual observation, and
external for an identified outside dependency. No next owner is needed only when
the requested bounded outcome and closure are complete.

## Shared operating contract

The [bounded task briefs](TASK_BRIEFS.md) permit original integration code, lawful sanitized
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
