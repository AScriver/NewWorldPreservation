# Current PlayerComponent entity-reference binding — #231

Task231 under workItem164/parent177 closes a specific #208 prerequisite: the
current-image operation and caller that bind an existing PlayerComponent to an
owner-map reference. It establishes no fresh entity allocation or wire schema.
K271–K274 and the [original receipt](../research/evidence/current-player-entity-binding.json)
record exact source ranges, private artifact seals and executed checks.

Input: clean main `7b344d46552710568466a8fcfc38f24a17abe0ce`, owned image
SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`,
version1.400.6031.6004151/build22469132, pinned type mapping and clean reference
checkouts. All behavior below is bounded static source inference. No native
client code or gameplay ran. Independent initial passes, narrow adjudication
and targeted counterchecks remain separately identified in the receipt.

## Concrete binding operation

J231-1: batch `14167bdc0` takes supplied objects and an owner. For each object,
it copies object+8 as lookup key and calls writer `1417758d0`; a later pass gets
that owner/key through `1416aecc0`. It visits the object's +10/+18 entry range,
queries each nonnull entry through virtual+20 using selector `141798ed0`, and
passes a nonnull cast result to binder `14167bb50` with owner, collection and
the returned reference. Exact call sites: `14167be50..70`, `14167bf03..4f`.

Applicability is concrete: PlayerComponent constructor `146711440` installs
table `148536b70`; its +20 target `1468b4fb0` delegates to `14174c220`, which
recognizes the same selector and returns unchanged `this`. Actual batch contents
and runtime invocation remain unknown. The selector's normal initializer is
source-supported; returned writable static storage is not an immutable fixture.

Binder writes are explicit (`14167bc50..69`): reference+8 becomes component+40,
reference+10/+18 becomes guard/control at +48/+50 via `14056d1f0`, and
reference+20 becomes key+58. Pair assignment retains incoming control before
replacing/releasing old control. This is the non-default key/cache producer;
constructor defaults and registry insertion alone did not supply it.

The binder also stores owner at component+78 and a separate collection reference at
component+60/+68/+70. That separate reference is not the entity key at +58;
#209's readiness/designation contract remains separate.

## Map membership and guard ownership

J231-2: writer `1417758d0` constructs a separate 0x28-byte guard control through
`14162d460` and inserts through `1415e94c0` at owner+228. Node+10 is external
lookup key; +20 raw object, +28 guard, +30 retained control, +38 embedded
object+8 key. Node+40/+48 separately holds the guard-invalidation owner pair.
Getter `1416aecc0` matches node+10 and returns/retains node+20/+28/+30/+38.
The map's sentinel/count/mask/buckets are owner+230/+240/+280/+288.

Remover `1417b47a0` supplies node+18 to destructor `141641df0`. The destructor
zeros the guard through node+40 before releasing node+48 and node+30 controls;
the remover then frees the node and decrements membership. Retained references
can keep guard storage alive after membership invalidates it. The control's
bounded disposal prefixes support guard-storage ownership, not ownership of
the supplied object's allocation, exclusive write authority or concurrent safety.

## Conditions and aftereffects

J231-3: the caller makes external/embedded keys equal under stable inputs;
the generic writer does not enforce equality. The batch ignores insertion
success and later looks up by key. A duplicate-key supplied object can therefore
receive the pre-existing object's reference if the error path returns normally.
Exact supplied-object identity requires successful unique insertion and stable
keys. A missing token can still be copied; a hit/live guard is required for a
live bound object, not visibly for binder invocation.

After the cache copy, `14167bc6d..7b` resolves the source token and updates
component+8/+10 through `141464610`. A source-token refresh does not recopy the
component's +40/+48/+50 cache here. These are distinct steps, not one atomic
binding event. Owner virtual predicate slots+48/+50 gate component virtual
B8/B0 and facet+80/+88 creation/disposal paths. #208 already resolves the
PlayerComponent B8 allocating facet path; it is not fresh entity allocation.
Backpointer assignment and `14167b950` aftereffects prevent an assignment-only
description. Their broader runtime/callback semantics remain outside this join.

Batch insertion/binding and teardown are resumable phases. `1417abfc0` clears
eligible component references before map removal after its callback phase
completes, but time-budget branch `1417ac0a1→1417ac311` returns before either.
Registration has an analogous partial-binding exit. Function return does not
prove completion, and no all-or-nothing, exception or cancellation contract follows.

## Verification and remaining boundary

J231-4: source ranges/instruction claims and private artifacts were rehashed
against the pinned image. Counterchecks preserved duplicate-key and partial-phase
qualifications and corrected the owner predicate terminology. Original illustrative
dataflow controls and repository regression are separate from native execution;
the receipt supplies actual focused/workspace commands, outcomes and cleanup.

`14100a290` caches an MB::ClientContext service slot; resolver `1417da5a0`
dereferences it and adjusts -0x2c0 before map access. Actual concrete service
installation/replacement/lifetime remains unknown. Fresh supplied-object allocation,
valid world/key identity, replication-member application/schema and live player
creation remain open; #212, parent177/164 and Milestone1 acceptance are unchanged.
Failed capped scans, rejected PDATA/RTTI queries and an unbacked returned-GUID
storage query are retained privately. Static helpers exited without live resources.
