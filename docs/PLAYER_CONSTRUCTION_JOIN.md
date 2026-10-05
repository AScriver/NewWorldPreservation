# Current player construction and registry join — #208

Task: M1-06A.2, Actionable208 under workItemId164 (coordination parent177).
This closes the bounded static research question with precise missing joins.
It establishes two source-supported paths: replication-member construction and
application, and concrete PlayerComponent construction/facet/registry handling.
Their connecting implementation, fresh gameplay entity binding and authoritative
lifetime ownership remain unknown. No current player wire schema is established.
Current progress belongs to [ROADMAP](ROADMAP.md); claims K186-K190 and the original
[evidence receipt](../research/evidence/current-player-construction-join.json)
retain the input identities, source references and executed verification.

## Contract recorded before analysis

Only208 was claimed and moved to Researching before investigation. Its pre-work
Research note recorded the exact outcome: join #207's application endpoint through
the concrete member/class factory to fresh entity/player construction, general
PlayerRegistry registration and ownership, with required fields/lifetimes; or
document each precise missing join. Generic allocation, class names and defaults
do not satisfy the positive construction contract.

Permitted work was pinned-image static analysis, necessary read-only reference
inspection, ignored private analysis output, original sanitized documents/evidence
and offline verification. Primary edit ownership was this report/receipt and
minimal208 additions to TASK_BRIEFS, ROADMAP, EVIDENCE_LEDGER and the evidence catalog.
All24 pre-existing pending files were snapshotted before reuse. The four shared
documents retain their original bytes underneath the208 insertions.

Completion checks: C1 refresh image/build/mapping and relevant dirty-source/report
identities; C2 exact construction/registration/field/lifetime joins or precise
missing boundaries; C3 independent forward/backward evidence and adversarial
checks for aliases, generic allocation and ownership; C4 source/document and full
workspace offline verification, preservation and a task-only local commit;
C5 reconcile208 validation/status/claim release and stop.

Excluded:209 designation/asynchronous readiness; the generic subscriber route
unless necessary here; any other task/dependency or implementation; codecs,
guessed payloads/replay, clients, process reads, hooks/capture/live trials/endpoints,
hosts/certificates/EAC changes, upstream edits, publication/push or contributor
messages. Nothing in this result admits encoding or dependent game work.

## Refreshed identity and evidence method

Analysis checkout: main at `be1a1d2e2c129e85c3d6506146e6b6bb3a606838`, plus the24
pending paths/hashes in the receipt. Initial index was empty. Source seals bind
that working state rather than relying on the commit alone.

- Owned image SHA256: `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`;
  version1.400.6031.6004151, Steam app1063730/build22469132,179204176 bytes.
- Private typeindex SHA256: `f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75`.
  Null-first mapping and unique bundle index8 were rechecked.
- #207 report SHA256: `3419498faccba24c59799bcf395beb6512056fdedf656298d6c1df5a9e4807f4`;
  its finalized receipt: `83b55f90333ea2603d5b692203909702ec9b355163bdaf6b78953f0d2561d7d5`.
- Dirty player source map SHA256: `07cb671ac79d30ab0137dcb0c16c3f31272aac0dffc1281bf99fd74ad8239bcd`.
  It supplies candidates; current fixed reads validate the selected endpoints.
- Read-only references: First Light63756a3f7ff0ae41752dcc7c80267802c3fa7548 and
  Aeternum820156dbc44c86c9436af81aa0dba72e94cb636b, both clean at fresh preflight.
  Historical reference behavior supplies no current construction schema here.

Independent investigator and architect passes started in fresh contexts with
separate scratch ownership; the primary adjudicated their claims before an
adversarial pass. PE/Capstone5.0.7 reads used Python3.11.9 and selected complete
PDATA/chained-unwind ranges. PowerShell7.6.6 wrappers passed parser and automatic
variable validation. Raw instruction/decompilation output stays ignored. All
code-flow claims below are static inference; no current client code was executed.

## Exact joined paths and limits

| Claim | Source-supported relationship | Exact boundary / limit |
|---|---|---|
| J208-1 / K186 | Record parser146af20d0 calls member parser146af2340. The member index is read separately from class descriptor selection via1461ad130/1461acfe0. Nonzero bounded class index selects a UUID; index0 reads16 UUID bytes. TypeRegistryInstance resolver1461650e0 returns the descriptor, whose+48 getter1406d97d0 yields a factory object. | No concrete player replication-member descriptor, selected class identifier or schema recovered. TypeRegistryInstance is distinct from PlayerRegistry. Mapping absence is file-specific. |
| J208-2 / K186 | Parser calls factory virtual+8, obtains member R12, decodes that same object through virtual+90 and retains it in a24-byte entry: member index at0, pointer at8, control at10. Consumer14175ccc0 calls application141717fc0 at14175d28b; application uses that entry's pointer for member virtual+60. Reconciler14172ce70 calls member+38/+48/+60. | Concrete factory/vtable/callback implementations remain unknown. State+608 is a separate inline16-byte-slot table, not the immediate member callback receiver. Indirect construction remains possible but unjoined. |
| J208-3 / K187 | PlayerComponent getter1467d0250 miss branch creates a0x18 factory object and installs final table148537160. Its slot0 is1467ca760: allocation0x580, alignment0x10, default constructor146711440. Primary component table148536b70. | Cached branch returns an existing object without this installation proof. Factory slot8 is name getter146824820, unlike the member parser's create slot8; an adapter or other class may be needed. Fresh component allocation is not fresh gameplay entity allocation. |
| J208-4 / K187 | Component virtual+B8 selects1467c7140, allocating0xb20/alignment0x10 and calling facet constructor146711870. It stores component+80=facet and setter1406ec930 stores facet+8=component. Facet table148535728. | Raw facet back-reference establishes no separate retention. Component disposal reaches facet virtual+30; callback ordering and activation are unmeasured. |
| J208-5 / K188 | Base constructor1416184e0 clears+40/+48/+50 and+60/+68/+70; key+58 becomes0x00000000ffffffff. Lazy reference resolver1417da5a0 checks cached pointer/guard/live byte, then this same sentinel. Non-sentinel invalid cache resolves through separate-owner14100a290/map getter1416aecc0 and caches object/guard/control. | Defaults return null before owner lookup. Entity/context key producer, owner-map writer, guard-byte allocator and invalidation authority are unknown. |
| J208-6 / K189 | Facet lifecycle1468760d0 passes its existing component to general PlayerRegistry virtual+20=146769980 at146876d30. Registration calls the resolver but ignores its result; copies raw component,+48 guard,+50 control and retains control. Helper1466c82a0 stores that tuple in registry+20; a new insertion updates secondary collection+b0 and notification. | Storage does not enforce a live guard, resolved identity or strong ownership of component memory. Actual lifecycle dispatch/order is not proved. Local designation+10=146928d80 is separate and belongs to209. |
| J208-7 / K189 | General removal14690b000, local tuple clear146916bc0, component reference reset1417abef0 and component/facet disposal are distinct operations. Facet cleanup14686fac0 conditionally clears local designation and calls registry general removal+28 at14686fe21. | Guard invalidation versus membership removal/disposal order, compensating reindex and authoritative allocation ownership are unknown. |
| J208-8 / K188-K190 | The paths above stop at four precise construction/ownership joins listed below. | No valid field values, actual registration, player creation or Milestone1 acceptance follow from these static paths. |

PlayerComponent UUID `{D50340CF-A082-4B90-9933-8C42387C0C77}` comes from1465827c0
through141048fe0. PlayerComponentClientFacet UUID
`{68AF28ED-E426-49C1-9502-B1E97F6EA047}` comes from1469480d0.
Both names and UUIDs were independently checked in fixed literals/tables. Neither
UUID appears in the pinned typeindex file. The reader's raw UUID branch, another
registry, an adapter or transitive construction is still possible; none is proved.

## Fields and lifetime contract

Offsets are hexadecimal source offsets, not admitted wire fields or payloads.

| Object / fields | Observed source use or default | Required provenance / lifetime still unknown |
|---|---|---|
| Member entry0/8/10 | Separate parsed member index, same factory-created member pointer, retained control; stride0x18. | Concrete class identifier/descriptor, member factory and decoder/application field schema; control's complete ownership semantics. |
| Component40/48/50 | Cached entity-reference object, guard pointer, retained control; all initially zero. Resolver requires pointer/guard/live byte to use cache. | Fresh entity allocation, tuple binding writer, object allocation owner and guard authority. Registry storage does not enforce these validity checks. |
| Component58 | Key defaults to00000000ffffffff; resolver compares the same zero-extended value. | Valid entity/context key, uniqueness and writer. Defaults are not valid gameplay identity. |
| Separate owner map230/280/288 | Getter1416aecc0 searches keyed entries; matching node20/28/30/38 supplies object/guard/control/key. | Map insertion, correct owner/context, guard creation/invalidation and relation to newly constructed entity/component. |
| Component60/68/70 and78 | Second reference tuple and additional field initially zero; reset clears/releases these references. | Actual role and producer. It is not established as gameplay owner/authority merely from its position. |
| Component80; facet8 | Component stores its constructed facet; facet stores raw component back-reference. | Facet activation/callback order; back-reference lifetime beyond the observed disposal chain. |
| Component198/1f0 | Empty strings at default construction. | Replicated setters and required gameplay meanings/values are not recovered. No209 designation/character-id investigation here. |
| Facet318 and31c..31f | Initial318=0;31c/31d/31e=0,31f=1. | Activation-state meanings and transitions remain unknown; defaults are not readiness proof. |
| Registry20 andb0 | General collections retain component/guard/control tuple and secondary membership. Local8/10/18 is a separate guarded tuple. | Component-memory owner, guard-byte lifetime, registration/removal/invalidation order. Control retention alone does not own the component allocation. |

The registry helper hashes `live ? rawComponent : null` but stores the original
raw tuple; removal uses the same conditional hash then compares the raw pointer.
Hash1414a0fa0 and synthetic pointer0x1000/mask7 give live bucket5 versus dead bucket0.
This is an executed arithmetic counterexample to treating guard retention as a
sufficient removal guarantee. Correct ordering or compensating reindex/removal is
required; no actual guard transition, runtime bucket or failed removal was observed.

## Precise missing joins and prerequisites

1. **Concrete replication member → PlayerComponent create operation.** The missing
   selection is the separate class identifier/descriptor, descriptor+48 factory,
   factory create+8 and resulting member vtable's decode+90/application+38/+48/+60.
   A source-supported implementation or adapter must connect those callbacks to
   PlayerComponent factory1467ca760. The member index alone cannot select that class.
2. **Fresh gameplay entity → component entity/context binding.** PlayerComponent
   construction is known; fresh entity allocation is not. The valid key+58 and
   tuple+40/+48/+50 producer, separate owner-map insertion and context relation must
   be joined. No allocator, valid identity or field value is inferred from defaults.
3. **Component memory and lifetime guard authority.** Identify the allocation owner,
   control block semantics, guard-byte creator and invalidation writer. A registry
   retaining a control pointer does not establish ownership of component memory.
4. **Construction/registration/removal/disposal order.** Join the callbacks that
   bind entity, construct/activate facet, register general membership, invalidate
   guard, remove membership, reset references and dispose allocations, or identify
   compensating reindex/removal. Existing routines do not establish their order.

These are prerequisites to a positive construction contract, not a reason to begin
209, live discovery or payload guessing. The bounded missing-join alternative in
208's acceptance is satisfied; parent177/164 gameplay acceptance remains open.

## Counter-evidence, failed approaches and verification

- The first forward report used local designation as general registration and
  conflated inline state slots with the member receiver. Final forward evidence
  and primary adjudication retain the corrected general endpoint and pointer chain.
  Its final paragraph also conflated member index with class selection; fixed
  descriptor-reader evidence above supersedes that clause. A source-map hash typo
  in that report is superseded by independently refreshed input identity.
- An early consumer-call mismatch was a read selection error. Fresh complete call
  listing and the primary exact call check confirm14175d28b→141717fc0 from207.
- Initial sentinel wording treated a32-bit register write as UINT64_MAX. Both
  writes zero-extend to00000000ffffffff. Original reports/seals remain historical;
  a seven-check repair, independent challenge and primary exact-byte check correct
  the claim. This does not add a valid identity.
- Adversarial checks narrowed factory identity to the fresh branch, rejected
  validity/strong-memory-ownership from insertion and retained the conditional-hash
  ordering counterexample. UUID absence remains limited to the pinned file.
- Whole-image Ghidra analysis did not finish and yielded no decompilation used here.
  A narrow exact-project-path helper query verified zero matching Java/headless
  processes. A broader query's self-match was excluded. The private partial database
  is retained. A broad field-candidate scan was nondiagnostic and supplies no absence
  claim. Metadata script/output drift was repaired before the final source seal.

Executed source verification:79 unique selected functions, zero undecoded selected
bytes,127 sealed private artifacts,43 primary literal/synthetic/preservation checks,
15 adversarial table/literal/mapping/agreement checks and seven sentinel repair
checks. The final source seal rehashes forward corrections,207 inputs and the lock.
All24 pending files matched their baseline before public edits. Document links,
claim/catalog consistency and reversible removal of208 insertions are checked
separately. Fresh workspace verification ran20:01:07-20:02:09 UTC on October5:
445 Python cases/32 files with no failures/errors/skips, three PowerShell suites,
and an owned127.0.0.1 HTTPS child with HTTP200, exit0 and closed listener. No selected
input changed during the run. The receipt records the exact command, run identity,
hash and subsequent validation-metadata finalization. These checks validate source
attribution and the repository harness, not an executed New World construction.

Resources: unique ignored primary/member/registry/challenge scratch paths only;
read-only reference checkouts; no game, shared database/service or fixed port. Static
helpers exited; the separately verified Ghidra helper is absent. Workspace validation
owns its isolated temp resources and loopback child. Private raw output remains
ignored; only original metadata/documentation is committed. No push is authorized.

Deferred notes:209 owns local designation/identity/readiness; the separate generic
subscriber writer/drainer remains deferred because the selected type8 branch needs
no such join. Cached factory registration, other UUID catalogs and broader field
semantics remain unknown beyond this bounded contract. Conditional-hash lifecycle
order is retained above because it affects this task's ownership correctness; it
is not a separately opened bug. No other Actionable was claimed or begun.

Any later construction investigation starts with one of the four precise joins,
fresh input hashes and its own authorized scope. This task stops at this handoff.
