# Current creation replication record codec

October 6, #238 under #177 / workItemId 164. This original codec combines the
established record reader grammar with a paired per-member writer. The native
outer slot/count writer remains unjoined. All fixtures are synthetic; no client
or native client code ran. [Source receipt](../research/evidence/current-creation-record-contract.json)
pins the current owned image, exact spans, private artifacts and retained failures.

## Record and member boundary — R238-1/4

Reader `146af20d0` consumes a compact uint32, narrows it to a uint16 application
slot, reads one byte of member count, then calls `146af2340` exactly that many
times. Zero members are structurally allowed. Consumer `14175ccc0` forwards the
same zero-extended slot to applier `141717fc0`. The slot, member key and class
selector have separate roles.

| Component | Supported bytes | Source |
|---|---|---|
| Application slot | Current compact32; reader retains low16 | `146af20d0`, `14087b5c0` |
| Member count | One byte, structural 0–255 | `146af20d0`, `14087a190` |
| Each member key | Current compact32 | Writer `146b0f140`, reader `146af2340` |
| Each member class | Compact32 index; index0 adds raw UUID16 | `1461673b0`, `1461acfe0` |
| Selected creation BODY | Existing fresh one-group/two-field BODY | Writer `141727cc0`, decoder `1417b4110` |

The member writer receives DWORD key, member, context, stream and result pointer
in RCX/RDX/R8/R9/stack. It gets that member's UUID through virtual+8, writes the
selector, then invokes its writer+88. The reader retains its compact key at
entry DWORD+0 and decoded raw/control pair at+8/+10 in a 24-byte entry after
decoder+90 succeeds. The current candidate table joins those writer/decoder slots.
The record contains no per-member byte length or extra presence byte on this path.
Member order is retained by the offline codec; later native sorting/application
conditions, including the reviewed 1–32-entry route, remain separate.

## Selection and ownership — R238-2

Registry `146162150` owns the UUID descriptor map and two different vectors.
Registrar `1461a9740` assigns descriptor+50 from local registration order.
Writer `1461673b0` uses cached descriptor+54, while reader `1461acfe0` indexes
the configured UUID table at registry+40/+48. These positions are distinct.

Installer `14615f720` calls loader `1461661c0` for `typeindex.json` and its
`generationTime`/nonempty `typeIndex` keys. On a fresh successful load it appends
reserved nil0, skips file element0 only when nil, then installs matching indices
1 onward into descriptor+54. Duplicate UUIDs can leave the last matching index
cached. A supplied file position is conditional on this load and registration;
it is no observed runtime index. GenerationTime is no proved compatibility check.

Normal load failure clears the table's length but leaves cached indices. Success
appends without first clearing. Reload reachability, recovery, shutdown and live
cache validity remain unproved. The codec therefore requires an explicit immutable
UUID table with reserved nil0 and explicit indices. Nonzero indices must be below
table length and resolve to the creation UUID. Out-of-range values have no raw
fallback. Index0 writes the exact textual-order UUID16; no GUID byte swapping.

## API, aliases and rejection policy

[`current_creation_replication_record.py`](../scripts/current_creation_replication_record.py)
exposes frozen `CreationRecordMember(key, class_index, body)` and
`CreationReplicationRecord(slot, members)`. Keys/indices require true uint32;
constructor slots require uint16, and members require a tuple of at most255.
`encode_record(record, class_table=...)` emits canonical compact bytes.
`decode_record(data, class_table=...)` returns `(record, consumed)` for one prefix,
owns decoded raw values and preserves suffix bytes and duplicate keys.

The established compact32 helper is not LEB128: widths1–5 have7/6/5/4/3 prefix
payload bits followed by little-order payload bytes. Decoding preserves native
nonminimal encodings, f8–ff aliases and uint32 wrapping; record slot then narrows
to16 bits. Decoding and re-encoding can therefore canonicalize bytes. The existing
[BODY codec](CREATION_MEMBER_BODY.md) retains its stronger unsupported-mask and
continuation gates. The later [player candidate](PLAYER_CREATION_CANDIDATE.md)
extends exact class selection to the separately proved identity BODY; arbitrary
classes remain refused. Existing creation-only literal bytes stay unchanged.

An unknown class cannot be skipped safely without its schema. Native member
failure calls `140873220`/`140879590` to drain the current supplied stream before
returning false; the enclosing record returns zero and can retain partial native
state. The pure codec returns no partial record and does not drain/mutate input.
Its `DecodeError.field/cursor` is a diagnostic offset relative to the supplied
record view, with no native error-code or final-cursor equivalence.

## Verification and exact remaining boundary

Seven original [literal fixtures](../tests/fixtures/replication/current-creation-record-original.json)
cover raw/indexed selectors, empty records/BODY, wide selector/key widths, all
BODY fields, order and duplicate keys/table positions. Focused checks passed60
record cases plus34 BODY and17 runner cases. They exercise every proper fixture
truncation, compact widths/aliases/wrapping, slots, structural counts through255,
unknown-class/out-of-range gates, sliced buffers, suffixes and owned values.
Independent verification passed87 literal/cursor assertions and94 record/BODY
cases. Required workspace passed1048 Python cases/38 modules, three PowerShell
suites and the synthetic127.0.0.1 lifecycle; listener closed, child exit0, inputs
unchanged. [Validation receipt](../research/evidence/current-creation-record-validation.json).
These checks do not establish native acceptance.

The current direct caller chain `146b0bb60 → 146ab5dc0 → 146b0f140` conditionally
serializes one member; it has no joined outer slot/count assembly. Exact-address
data searches expose no table route for those helper addresses. Other indirect
routes remain possible. Generic selector callers `146ae6860`/`146ae6a80` emit
presence plus descriptor+20 bodies and are a different serialization path.
The offline outer encoder is an inverse of the established reader grammar.

## Serializer input checkpoint — October7, #240

The new bounded caller trace reaches generic whole-message serializer `146ae79b0`
through `146ab4d20`/`146ab4f20`, then `146ab5600`/`146afc090` and upstream
`146afa350`/`146afd420`/`146afbfd0`. Exact instructions confirm the two wrappers
move one qword from machine argument7/6, clear its source and pass a local slot
address. They do not copy a two-qword shared handle at that boundary.

`146afa350` moves its incoming argument4 pointee. The other routes supply incoming
two-qword pairs through `146153e70`, then forward its return or an allocation-failure
zero. Independent review falsified the apparent TLS fallback in `146afd420`: that
branch exits before the serializer-reaching call. The successful route uses both
argument3 slots, not its second slot alone.

[Original partial receipt](../research/evidence/current-creation-record-publication-inputs.json),
K356, pins seven function slices, direct-call scans, instruction review and exact
query state. The wrapper query overlapped only a milestone documentation edit;
native spans and output hashes matched. Three overlapping-global decompiler
warnings are retained; global names and inferred types are not proof.

The concrete incoming object, helper ownership semantics and association with the
retained type8 payload remain unknown. An absent explicit context+418/+420 access
does not prove no alias. This narrows the supplier paths without joining the native
outer slot/count writer or changing the original codec/candidate. No native trial
or creation acceptance follows from this static query.

## Wrapper and queue suppliers — October7, #240

The next bounded trace places an incoming pair in wrapper+60/+68 through
`146153e70`. This wrapper is separate from its carried object. The one-qword
supplier reaches `146afa350` from queue drain `146abae10`/`146b04560`.
Feeder `146aecdf0` processes0xb8-byte pending entries and supplies pointer slots
to one of two queues under an unjoined virtual predicate. Its optional callback
can affect selection; selection is fetched again before that branch. Queue-helper
durability and network transmission are not established by these calls.

Entry conversion `146aba5d0` moves cached entry+a8 directly, or calls
`146b085d0` when the cache is absent. The latter separately allocates storage and
initializes an empty carried pair through `146154030`. Zero stored-stream length
retains this default wrapper without reconstruction. Nonempty entry+58 stream
passes through `1461ac8d0`, requiring result byte+1 and a second stream predicate
to retain output. Nonnull output therefore does not prove reconstruction, valid
message contents or native creation.

The new callee passes wrapper+60 plus stream to `1417b2430`; reconstruction is
supported inference while lower byte operations remain unjoined. Cached-pointer
and stored-stream producers, concrete type8 alias and payload/outer writer remain
unknown. [Original partial receipt](../research/evidence/current-creation-record-supplier-path.json),
K357, pins seven new primary functions and two reviewed callees, exact instructions,
hashes, conditional gates and warnings. The original codec and prepared candidate
are unchanged; no native trial was executed.

Remaining #210 joins: native outer writer and enclosing receive/Carrier placement,
actual runtime mapping/index/fallback choice, exact resend/ACK retirement,
historical860 discriminator and authenticated authority. Bundle extent/framing,
valid creation inputs, conditional source/resource/clone/binding/designation,
#212, #232/#177 aggregate and bilateral movement remain open. This record is
not a complete datagram. No launch, hook, capture, endpoint, credentials, replay,
upstream edit, push or publication occurred.
