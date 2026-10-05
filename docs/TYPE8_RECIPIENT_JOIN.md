# Current type8 recipient and member parser join

Actionable **#207**, under **workItemId 164**. The bounded outcome is an exact
conditional **static join** from the current type8 decoder to a concrete recipient
and member parser. It does not establish runtime delivery or a valid player payload.
Current task status and aggregate Milestone 1 acceptance remain in
[ROADMAP](ROADMAP.md). Original metadata and private evidence hashes are in the
[receipt](../research/evidence/current-type8-recipient-join.json).

## Contract recorded before work

The pre-work contract was saved to #207 before analysis or edits. Its outcome was
to identify the actual descriptor/key, registration/recipient and member parser,
or document each exact missing edge with its blocker and handoff.

| Check | Acceptance |
|---|---|
| C1 | Pin the current owned image, type mapping and relevant dirty inputs. |
| C2 | Trace or falsify decoder → descriptor/key → registration/recipient → member parser. A generic queue shape is insufficient. |
| C3 | Record original sanitized evidence, exact unknowns, rejection checks and handoff without substituting a weaker result. |
| C4 | Verify source attribution and changed documents/receipts, run the complete workspace offline profile, preserve unrelated work and commit only #207 changes locally. |

Permitted operations were read-only pinned-image/private static analysis, narrowly
needed read-only pinned reference inspection, original evidence/documents and
focused offline validation. The primary owns this report, its receipt and minimal
#207 additions to TASK_BRIEFS, ROADMAP, EVIDENCE_LEDGER and the evidence catalog.
Unique ignored scratch directories contain all instruction output and helpers.

Excluded work: #208 player/entity construction and PlayerRegistry; #209 identity,
readiness and local-player designation; other Actionables or task/dependency
changes; codecs, guessed member formats, new payloads or replay; game launches,
process reads/hooks/captures, game endpoints, hosts/trust/EAC changes; upstream
edits, pushing, publication or contributor contact. Each additional inspection
below served C1, C2 or C3. No other task was started.

## Input identity

- Checkout: `85becb68f5df661415e4a8642984145ce5e8bb06`, branch `main`, plus 16
  modified tracked and eight untracked files. All 24 pre-existing files were saved
  byte-for-byte before analysis. Their baseline hashes are in the receipt; the
  task's shared-file additions are independently removable and staged separately.
- Owned image: SHA256
  `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`, file
  version `1.400.6031.6004151`, Steam app/build `1063730/22469132`. This identifies
  on-disk input, not a running process.
- Private type mapping: SHA256
  `f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75`. The
  null-first mapping contains bundle UUID `8a40aec2-ae07-4f92-9bf3-78fc0cc94fdf`
  exactly once, at index `8`.
- Existing dirty player source map: SHA256
  `07cb671ac79d30ab0137dcb0c16c3f31272aac0dffc1281bf99fd74ad8239bcd`.
- Static tools: Python `3.11.9`, Capstone `5.0.7`, validated PowerShell `7.6.6`
  and the shared private runtime. Clean reference commits remained First Light
  `63756a3f7ff0ae41752dcc7c80267802c3fa7548` and Aeternum
  `820156dbc44c86c9436af81aa0dba72e94cb636b`; neither supplies a current schema.

## Exact selected route

The addresses below are fixed endpoints in that image. Every edge is source
inference; literal/table controls are synthetic checks. Conditions at the handler
remain part of the result.

| Edge | Exact source and result |
|---|---|
| J207-1: descriptor → decoder | Getter `0x146437070` identifies the bundle UUID. Its descriptor `+0x48` stores an allocated factory object whose first qword is table `0x148502a48`. Factory virtual `+0x28` is wrapper `0x14646c2b0`, which calls body decoder `0x146b07870` at `0x14646c343`. |
| J207-2: decoded object identity | Wrapper writes the caller's `R8` object, installs table `0x1484ff1d8` and clears object `+0x10`. Object virtual `+0x30` is `0x14643a240`, returning the same bundle descriptor. The wrapper's return is the supplied result/status pointer, not the decoded object. |
| J207-3: actual dispatch selection | `0x14643e7b0` is the GameMessagePort table `0x1484fc680` slot `+8`. Initial cast through virtual `+0x28` expects getter `0x14179a4d0`; its UUID `2964f3ae-4da5-48f0-942b-3f428f8c9cd2` differs from the default object's base UUID `7f4b41c6-06ae-47a1-a144-5f8ba048b0ef`. Under ordinary initialization and the inspected default table, the cast is null and selects `0x14643e9af` after the handler's readiness/owner gates. |
| J207-4: descriptor → concrete recipient | That dedicated branch calls `0x146437070`, obtains incoming virtual `+0x30` and compares descriptors through `0x146158ba0` at `0x14643e9e1`. Pointer equality or both UUID qwords can match. It forwards the same incoming object directly to owner consumer `0x14175ccc0` at `0x14643eb15` or `0x14643eb83`, after context/sequence or ordering gates respectively. The owner is the instance recovered through the port's lazy accessor from its holder `-0x2c0`, separately constructed by `0x141613a10/0x141614e30`. |
| J207-5: decoder storage → recipient view | Body decoder passes the declared tail pointer/count to buffer helper `0x146470df0` with owner `message+0x110` at `0x146b07a24..0x146b07a32`. Constructor `0x1463fb250` places inline and heap children at owner `+8/+0x838`, hence message `+0x118/+0x948`. Consumer helper `0x146adf6a0` selects those same children and exposes their data/length. Their fixed data/length targets were checked. Buffer writes retain capacity/error/migration gates. `0x146adfc80` instead returns the consumed-byte counter at message `+0x988`. |
| J207-6: recipient → record parser | Consumer `0x14175ccc0` creates a stream over that view at `0x14175d1a0`, invokes `0x146af20d0` at `0x14175d21b`, and iterates using the consumed-byte result and remaining view. The record parser reads a compact record value, stores its low 16 bits, reads an 8-bit member count and calls `0x146af2340` for each member at `0x146af22da`. Failure returns zero consumed bytes. These observations do not define a valid gameplay record. |
| J207-7: concrete member parser | `0x146af2340` reads a compact member index, resolves a descriptor through `0x1461ad130` at `0x146af2474`, obtains descriptor `+0x48` via `0x1406d97d0`, invokes that factory object's virtual `+8`, then the returned member object's virtual `+0x90` decoder at `0x146af2649`. Successful decoding gates a 24-byte vector-entry append at `0x146af2754..0x146af2772`. This is generic member machinery; no concrete player class was selected or constructed in this investigation. |
| J207-8: exact handoff boundary | Resolver `0x1461ad130` calls class-descriptor accessor `0x146162150`, identifier reader `0x1461acfe0` and resolver `0x1461650e0`, and writes the resolved pointer to its output at `0x1461ad276`. Consumer passes the parsed record/member vector to `0x141717fc0` at `0x14175d28b`. Investigation stops before that downstream application call and before concrete class implementations. |

The selected type8 branch uses a descriptor comparison and a direct owner call.
It has no subscriber-key lookup or map insertion prerequisite. The separate
generic route hashes incoming object `+0x10`, looks up entry `+0x18` and enqueues
to recipient `+0x130`; that route's writer/drainer remains unjoined. The numeric
wire index `8` must not be substituted for its unknown data key.

The initial cast and the inner generic cast use different descriptor getters.
The inner getter `0x141759df0` initializes UUID
`164473fb-fa8f-4a8d-8957-ace50bac1b66`, also distinct from the default bundle base.
Its mismatch does not exclude the dedicated bundle branch. The previous generic
queue-only limitation in K179/K181 is historical; K182–K184 close this static route.

## Rejections and counter-evidence retained

- The first-pass hypothesis that an unknown generic subscriber registration was
  the required missing join was falsified by the handler's separate bundle branch.
  Independent recipient work remains useful for the generic route, with its
  original limits preserved in private reports.
- Adversarial review found that first-return extraction of `0x146158ba0` omitted
  its second success leaf at `0x146158bbc`. Extraction was repaired and rerun with
  explicit complete bounds ending at `0x146158bbf`; an escaping conditional branch
  now rejects a leaf slice. The complete success leaf and descriptor match passed.
- The factory table itself is not descriptor `+0x48`; that field holds its object.
  The reported pointer chain was corrected and checked against exact table slots.
- The body decoder's selected tail block does not directly iterate payload
  members. Its optional pre-tail helper has a separate two-byte collection walk.
  No transitive claim of absent collection parsing or unconditional copy is made.
- Fixed UUIDs were checked through this image's initializer character/nibble
  tables, with identical-input positives and distinct first-qword negatives. The
  adversary separately modeled initializer/compare branches, including invalid
  input and a differing second qword. No client code was executed by these models.

## Verification and limits

The [receipt](../research/evidence/current-type8-recipient-join.json) records exact
commands, run identities and hashes. The final source seal contains 37 unique
fixed-function slices with zero undecoded bytes in the selected ranges, eight
literal/table controls, the complete comparator success leaf and the unchanged
24-file baseline before owned edits. The adversary confirmed the revised direct
route, buffer aliases and member-parser dispatch; primary verification separately
closed the resolver and descriptor `+0x48` getter attribution.

Focused checks bind the report, catalog and evidence to those inputs, and check
that removing the task's additions exactly restores all original file bytes.
The complete workspace offline profile is required by C4. Its result and owned
loopback cleanup are recorded in the receipt; offline success cannot establish
game-client acceptance. Raw instruction output remains ignored. No live game
resources were created or touched by source analysis.

Runtime entry into the handler, descriptor registration, actual decoded contents,
port readiness, context/sequence/order gates and class-specific decoder success
remain unmeasured. This source join has no missing static prerequisite. It does
not unlock a candidate member encoding or Milestone 1 acceptance.

## Deferred notes and handoff

| Owner | Exact remaining question; no work started here |
|---|---|
| #208 | Starting at `0x141717fc0` and the concrete descriptor/member class selected by the parser, join application to fresh player construction and PlayerRegistry. Exact current class layout, factory implementation, IDs, ownership and valid creation payload remain unknown. |
| #209 | Independently join identity, asynchronous readiness and designation to the guarded live local-player result. The parser dispatch proves none of those conditions. |
| Deferred generic route | Concrete subscriber-map writer/key and ring drainer are still unknown. They are not prerequisites for the dedicated type8 branch shown here. Revisit only when a separately authorized outcome actually requires them. |

The next bounded owner should consume the pinned endpoint/hash record and preserve
the runtime limits. Further analysis or implementation requires that owner's
existing task scope; no weaker payload, guessed message or historical actor replay
is a substitute for a missing class or creation contract. #207 changes documents
and original evidence only, with a local task-only commit and no push.
