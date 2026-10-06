# Concrete creation member and BODY contract

Work item 164, parent 177; source #236 and offline codec #237. This is a
conditional current-image source join for UUID
`203dc8c7-0c60-454b-a46f-566114314b84`. Its friendly class name is unknown.
The image/build, exact spans, finite windows and private artifact seals are in
[the original source receipt](../research/evidence/current-creation-member-contract.json).
No native client code ran.

## Selector, descriptor and factory

Parser `146af2340` calls selector `1461acfe0`: zero reads raw UUID16; a nonzero
value indexes the bounds-checked registry UUID table. Resolver `1461ad130` and
lookup `1461650e0` compare both UUID qwords. Getter `1416cfb20` parses this
candidate's UUID literal, builds its descriptor through `1407de270` and installs
factory table `14801d4b0` at descriptor `+48`. Registration wrapper `141547380`
passes that same descriptor pair to registrar `1461a9740`.

Factory virtual `+8`, `141513e30`, constructs member `14161c070` and returns its
raw/control pair. Its primary table `148041178` supplies decoder `+90` at
`1417b4110`, writer `+88` at `141727cc0` and truthy predicate `+60` at
`14029f880`. This matches the parser's actual member interface. The outer type8
bundle factory, NullType's empty factory and PlayerComponent's module descriptor
have different roles.

Registration callback invocation, registry population and actual selection are
unobserved. The retained mapping-file position 10 is no proved runtime selector.
Descriptor caching, allocation and registry lookup remain conditions.

## Fresh factory schema

Base constructor `14162f3e0` creates one group through `141677dd0` and
`1416196c0`. Constructor `14161c070` appends exactly two ordinary fields to that
initially empty group: AssetId, then GdeRef. Separate auxiliary entries
(ExplicitClientTargets, DefaultBits and ReplicationCategory) are outside this
decoder's ordinary group vector.

| BODY component | Supported bytes | Exact source |
|---|---|---|
| Group mask | One byte; bit0 selects the sole fresh group | `1417b4110`, byte reader `14087a190` |
| Field mask | One byte; bit0 AssetId, bit1 GdeRef, in that order | `1417b43c0`, writer `141728100` |
| AssetId | Raw16 followed by opaque uint32 in big endian | Reader `1417b3670`, writer `141727250`; raw `140878610`, BE32 `14087a220`/`140876cd0` |
| GdeRef | Raw16 only | Reader `1417b3ae0`, bounded writer entry `141727450` |

Canonical explicit selections are `00` (absent), or `01` followed by field mask
`01`, `02` or `03` and their fields. Sizes are 1, 22, 18 and 38 bytes respectively.
`01 00` is an accepted empty-selection alias and can canonicalize to `00`.
Native dirty/revision/peer selection is separate from explicit offline presence.

Native readers tolerate unused mask bits and inner continuation pages. The
bounded offline domain rejects outer bits 1–7, inner bits 2–7 and continuation;
that refusal is deliberately stronger than the native reader. Native aliases
`02`, `01 04` and `01 80 01` remain counterevidence to any claim of native
rejection. Masks are not a guessed general member format.

On success, native fields set revision/dirty state. AssetId's raw16 can already
be changed when its later scalar read fails. The pure codec supplies values and
consumed offsets, without emulating native mutations or inventing error codes.
GdeRef stores the complete raw16 and separately derives its first little-endian
qword through the ten-byte leaf `140870c50`; this is not a hash or unique identity.

## Conditional application

GdeRef's interface value at member `+860` contains raw16 at `+870` and derived
qword at `+880`. That layout matches `14178db00`'s actual value input. Successful
decode retains the pair; the established nonempty 1–32 ordering/empty-slot route
can install it because its virtual predicate is truthy. Separate guarded dispatch
then reaches GDEStreamer and builder `141747c60`.

[Application](PLAYER_MEMBER_APPLICATION.md), [owned vector](PLAYER_ENTITY_VECTOR.md),
[clone](PLAYER_ENTITY_CLONE.md) and [binding](PLAYER_ENTITY_BINDING.md) retain
active-handler/interception/map misses, deferred state2, weak locks, resources,
reflection, source-key and designation conditions. Factory creation is not
successful Entity/PlayerComponent creation. No valid field values, runtime class
choice or authenticated gameplay follow from this source closure.

## Remaining #210 dependency

Later #218–#230 evidence closes selected registration request/response BODY,
physical sender stream and identifier placement. It does not close the actual
receive inverse/outer replication record boundary and Carrier placement,
runtime class/index/fallback choice, exact resend/ACK retirement, historical860
discriminator or authenticated authority. These do not block an inert BODY-only
fixture. They still prevent calling it a complete world-entry datagram or closing
#212. Parent #177, the #232 aggregate and Milestone 1 acceptance remain open.

## Verification boundary

Initial registry and backward member passes were isolated; the primary accumulated
ledger joined them before targeted challenges. Material decompiler claims were
checked against instructions. No-PDATA leaf queries failed and were replaced by
finite instruction windows; RTTI naming failed; an interrupted broad query supplies
no evidence. The receipt preserves those failures, historical source refreshes and
executed file-only checks. The original codec and fixture are verified in
[the offline receipt](../research/evidence/current-creation-member-body-validation.json).

## Offline API and executed checks

[`current_creation_member_body.py`](../scripts/current_creation_member_body.py)
exposes immutable `AssetIdField(raw16, field_20)` and
`CreationMemberBody(asset_id=None, gde_ref=None)`. `None` omits a field; explicit
zero bytes/scalar remain present. Raw values require exactly 16 immutable bytes;
the opaque scalar requires a true uint32 integer without narrowing.

`encode_body(record)` returns canonical BODY bytes. `decode_body(data,
member_uuid=MEMBER_UUID)` requires the exact external UUID guard before parsing
and returns `(record, consumed_bytes)`. It accepts contiguous bytes, bytearrays
and memoryviews, owns immutable decoded values and leaves caller suffix bytes
untouched. `DecodeError` reports the BODY-relative field/cursor; it represents
the strict offline policy and supplies no native error-code equivalence.

The five [original synthetic vectors](../tests/fixtures/replication/current-creation-member-original.json)
exercise all four presence shapes, zero and upper-bound scalars and distinct raw
values. The focused suite passed 34 codec cases plus 17 runner cases. Independent
Tester checks passed 168 assertions, including a separate literal/truncation-cursor
oracle. Required workspace passed 988 Python cases across 37 modules, three
PowerShell suites and the synthetic 127.0.0.1 lifecycle; its listener closed and
child exited 0. Inputs stayed unchanged during the run. Tooling rerun passed 81
after correcting a missing fixture-catalog entry; the failed receipt remains.
No native/client code or game endpoint was exercised.
