# Current entity vector and binding receiver

October6 follow-up #234 now joins conditional nested Entity allocation, original
Id copying and actual XOR/identity remapping. See [the clone contract](PLAYER_ENTITY_CLONE.md).
The #233 input and limits below remain its historical source scope.

October 6, #233 under #232 / #177 / workItemId 164. The current image supports a
concrete owned-vector producer and a guarded deferred-job path that supplies the
same factory-created receiver to its setter and binding batch. The earlier direct
queue-to-setter claim is falsified for its shown caller. Per-Entity clone factory
selection and `Id` treatment remain #234; parent #232's aggregate acceptance is open.

This is instruction-supported source inference. Input was clean main
`2ca3201d70d806a12ef44f218bac7fd1b87720b7`, image version 1.400.6031.6004151,
build 22469132. The [original receipt](../research/evidence/current-player-entity-vector.json)
pins image/map/reference/tool identities, exact source spans, bounded windows,
private seals, counterevidence and repository verification separately. No client
or native client code was executed; runtime invocation and Milestone 1 were untested.
Addresses and structure offsets below are hexadecimal; allocation sizes use `0x`.

## Same receiver through the deferred job — J233-1

1. Factory `1410563d0` initializes through `141619850` and installs table
   `147fd6b28`, whose slot 0 is `14167b790` → batch `14167bdc0`.
   Caller `141747c60` retains that precise raw/control pair in operation+0x18 via
   `14056d1f0` at `141748543..54a`. The operation records its manager at+0xD8;
   its self weak pair is initialized at `1415edd4a` within `1415edba0`.
2. Scheduler `1417b94f0` queues that operation in manager+0x190; processor
   `1417b53e0` passes it to `14178df50` with sixth argument **zero**. In the
   admitted state 2 / operation+0x64==0 branch, that zero selects construction of a
   deferred job. `141609730` copies the operation's self weak pair;
   `141585400` stores it at job+0x48 and installs table `148042780`.
3. The constructed job is supplied to `141438500` when the old counter's low 24
   bits equal 1; bit 30 must be clear. Its configured parent/context chooses
   execution or queuing. Executor `14143fe10` invokes job virtual+0x40 only when
   its executor gate permits it. Table+0x40 → exact nine-byte thunk `141740bb0`
   adds `0x48` and enters `1416631d0` with the captured weak pair.
4. The callback locks the same operation and requires nonnull operation+0x18,
   state+0x50==2, and compared values at+0x30 and+0x88/+0x90 differing from helpers'
   defaults (`14053eb60`, `1407f7d80`). It passes operation+0x18 to setter
   `1417898f0` at `141663286..28a`. The guard values' wider identity meaning is
   unproved; they are caller-provided, not constructor-forced passing values.

The operation strongly retains the receiver; the job captures the operation
**weakly**. Expiry can prevent callback execution. Operation initially has state 1;
reaching state 2 is unverified. Initial job counter is `0x80000001`, with bit 29 clear:
the executor therefore needs context flag+0x10==0 unless that bit later changes.
Scheduling, live context, weak-lock success and guard values remain conditions.

## Stored vector and deletion authority — J233-2

Setter `1417898f0` calls `14171e370` and installs its returned holder at receiver+0xC0.
The `0x20`-byte holder retains the source resource at+0x8; clone wrapper `1413d0aa0` /
visitor `1413d0b00` supplies holder+0x10. Getter `1416b8a90` returns that exact+0x10
pointer, which the actual batch enumerates. The batch's object+0x8 key/component
query/binder path is [already joined](PLAYER_ENTITY_BINDING.md).

The exact clone type is **InstantiatedContainer**, UUID 05038EF7-9EF7-40D8-A29B-503D85B85AF8:
`1411d66e0` / `14148afb0`, registered by `141456800`. Its field 0 `Entities` uses
the same `1407774f0` element-type getter as AZ::Entity reflection. Its factory
`149e8b578` → table `147fe7aa0`+0x8 → `1411b0b70` allocates `0x28` bytes and initializes
own-elements+0x20=1. This factory is evidenced by an explicitly bounded window.

Holder disposal `141664000` → `1405c9e40` → `14133a470` checks the container's
current+0x20 flag before reverse-deleting nonnull elements through virtual+0x30/flag 1.
It releases vector storage, the retained resource and holder storage. The stack
temporary passed to cloning initializes+0x20=0, so its cleanup does not delete the
borrowed elements. Neither exclusive ownership nor deletion-versus-map ordering
follows; #231's guard controls protect guard storage separately.

## Corrections and construction limits — J233-3

- The direct queue route is falsified: `1417b562d` writes sixth argument 0,
  while state 2's direct setter branch `14178e2dc/2e0` requires it to be nonzero.
  Exact stack-offset and jump-table checks preserve that counterexample.
- Nearby SerializableEntityContainer has a different UUID. Another object's+0xC0
  holds SIMD transform data. Neither type nor receiver identity follows from an
  offset, nearby name or allocator; the deferred-job capture supplies the join.
- AZ::Entity factory `1411b0990` allocates `0x68` bytes and defaults+0x8 to zero-extended
  `00000000ffffffff`. Separate constructors accept, copy or generate keys. These
  are concrete prerequisites, not the actual nested clone's selected key path.
- Normal Entity flag 1 deletion destroys contained components; ordinary Entity
  copying duplicates component-pointer bytes via `memcpy`. Flag 4's target returns
  without freeing. Exclusive ownership, hazardous copy execution and concurrency
  are unproved. The separate fresh outer wrapper is not the enumerated entity.
- Holder replacement/disposal can precede a later null/root check. Binding has
  duplicate-key and partial-phase qualifications from #231. No atomic success,
  failure-preserves-state, fresh valid identity or complete construction claim follows.

## Verification — J233-4

The primary source refresh checked 108 exact spans, 37 bounded data/prefix windows
and 322 private artifact seals. Final callback-source and selected challenge
artifacts matched after the source report was sealed. Failed/partial queries,
the corrected receiver assumption and falsified queue route remain retained.
Bounded factory/helper windows are not full PDATA/unwind evidence. Repository
checks are recorded in the receipt; they do not establish native/gameplay acceptance.
#234, #232, #212, parent 177/164 and bilateral movement remain open.
