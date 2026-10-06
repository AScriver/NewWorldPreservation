# Current Entity clone and Id treatment

October 6, #234 under #232 / #177 / workItemId164. The current source now joins
the Entities pointer adapter to nested allocation, destination storage, original
Id copying and the producer's two remapping passes. **Fresh allocation does not
imply a freshly generated Id:** the actual producer supplies XOR or identity
mapping, overriding the reflected default generator.

This is instruction-supported source inference at clean main
`2097ac60bcebd03433b3acb74e64330c12df7010`, owned build22469132/version1.400.6031.6004151.
The [receipt](../research/evidence/current-player-entity-clone.json) pins current
inputs, exact spans, bounded windows, private source seals and offline checks.
No client or native client code was executed. Addresses and offsets are hexadecimal.

## Nested allocation — J234-1 / K281

InstantiatedContainer's Entities metadata embeds adapter `147f22da8` through
`14053bbc0`. Its `1406b8a30` enumerator steps eight-byte pointer slots and forwards
the slot, UUID and descriptor through `1414a7a40` to `1413f8cf0`. Runtime RTTI
helper `1402edc00` asks the source object's virtual slot0 for its dynamic UUID.
Null pointers or missing classdata can skip entries; a derived UUID can select
different metadata. Declared Entity pointers do not force one factory.

With exact AZ::Entity UUID75651658-8663-478D-9090-2432DFCAFA44 and the shown
classdata/factory registration selected, `141382420` invokes factory
`149e8b150` → `147fe7a88`+8 → `1411b0990` at `1413824f6..500`.
The result reaches the reserved pointer slot at `141382733`. Adapter reserve
`14075bb40` advances the vector before allocation; exit hook `140294860` is a
no-op. A null result can be stored. Duplicate class registration retains earlier
metadata; successful allocation, complete counts and atomic rollback do not follow.
The returned container joins the [existing holder/binding route](PLAYER_ENTITY_VECTOR.md).

## Original Id copy — J234-2 / K282

Factory initialization gives Entity+8 the zero-extended `00000000ffffffff`.
Normal reflected traversal then visits Entity.`Id` at offset8, EntityId.`id`
at offset0, and the AZ::u64 serializer `149e8b510` / table `147fe6200`.
Save `1411a5430` and load `1411a5340` copy the original qword through the same
temporary eight-byte buffer into cloned Entity+8; both endian flags are zero.
This overwrites the sentinel before clone return under successful traversal.

The supplied context must contain the shown registrations, including primitive
registration enabled by `141300240`'s third argument. Save/load return values are
ignored by the worker; failed allocation, stream or traversal is not error-atomic
success. The temporary buffer is local serialization storage, not a network message.

## Field attribute and actual policy — J234-3–4 / K283–K284

Under reflection context byte+8==0, `141451ee3` points the builder at the Id
attribute vector; `1411c44b0` appends callback `141425760` with key `149e8affc`.
The helper repeats that context guard before attachment. Type getters `14147baf0`
and `140788e80` share the EntityId cache/literal UUID6383F1D3-BB27-4E6B-A49A-6409B2059EAA.
The remapping walker matches that type, attribute key and typed vtable.
Default adapter `1407a2280` → attribute virtual+38 → `141419e10` invokes the stored
generator. Successful typed attribute construction is required; a null attribute
can instead classify the field as unattributed.

Actual producer `14171e370` supplies its own nonempty callback:

| Source condition | Actual result |
|---|---|
| source+138==`00000000ffffffff` | Null return before holder allocation, cloning or either pass |
| Non-sentinel, source+15e bit4 clear | `oldId XOR (source+138 XOR requested_key)` |
| Non-sentinel, bit4 set | Unchanged `oldId` |

The custom callbacks are `1417e5a20` and `1417e5a30`; they take precedence over
the default generator. Both passes share the cloned container and one local map.
The true pass handles generator-bearing fields; the false pass handles other
matching references. Its explicit presence/selector filter skips primary Ids
already changed by the first pass, including when a new key equals another old key.
Duplicate old keys retain the first stored mapping; absent references remain
unchanged. No source uniqueness, reserved-value safety, cross-clone uniqueness,
valid requested key, coverage of every reference or gameplay identity is established.

## Role and failure corrections — J234-5 / K285

The separate `MakeEntityId` registration uses another cast context and a named
callable registry at context+F0. Exact LEA `141452612` points to full name
`147feb8a0`; the earlier `147feb8a7` was an interior substring. This registry and
the Id field attribute independently use the same generator; they are distinct
registrations. No unverified context name or sole-role claim is needed.

The source-key sentinel route at `14171ef14` returns null, without dereferencing
the requested key or constructing an empty/borrowed holder. Common cleanup acts
on the original resource. Runtime source values and branch selection remain unknown.

## Verification and remaining acceptance — J234-6 / K286

Independent allocation and Id reviews survived with dynamic-type, registry,
typed-attribute, allocation and traversal conditions. Rejected no-PDATA/broad
queries, partial initial Id work, pointer correction and null/skip/error cases
remain preserved privately. Exact spans and finite windows are distinguished.
The receipt records focused and required workspace checks separately from source
inference. #232 aggregate review, concrete replication-member/schema joins,
#212, parent177/164 and bilateral movement remain open.
