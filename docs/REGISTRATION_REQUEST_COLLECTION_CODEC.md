# Current V3 sequence and field+0x10 collection — #221

October 6, 2026; workItemId164 / parent178. The selected V3 body writer and
decoder now join the aggregate field order and the complete first collection:
a compact count, repeated BE32 keys and compact-counted raw byte strings.
Duplicate keys retain the first value. The larger nested fields remain separate
source prerequisites; no complete request fixture or body implementation follows.

Clean input main `29b570950380785e202f3ffd91c655a80348a428`, owned build22469132,
version1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
[Original receipt](../research/evidence/current-registration-request-collection-codec.json)
pins image/map/references, exact code/data seals, dirty report state and checks.
All native claims below are instruction-supported source inference. No client or
native client code ran. #215–#220 findings retain their original scope.

## Selected sequence — J221-1

Writer `0x1407ce860` emits field+8 through BE32 helper `0x140876cd0` at
`0x1407ce88b`, then calls aggregate `0x1407d54a0` at `0x1407ce8c9`.
Decoder `0x1407ce8e0` constructs a fresh placement object (`0x1407e37d0`),
then calls `0x1407d9620` at `0x1407ce955`. The reader stops on each failure.

| Field | Writer edge | Complementary reader edge | Scope |
|---|---|---|---|
| +8 | `0x140876cd0` | `0x14087a220` | Four-byte BE32 bits |
| +0x10 | `0x1407d62b0` at `0x1407d54c1` | `0x1407da980` at `0x1407d9676` | Complete collection below |
| +0xa0 | Inline compact length/raw bytes | `0x1407fc670` at `0x1407d9690` | Adjacent string bounds/cursor below |
| +0xc0 | `0x1407d5f30` at `0x1407d5509` | `0x1407db350` at `0x1407d96a6` | Nested schema still unjoined |
| +0x2c8 | Inline prefix, then `0x1407d4540` at `0x1407d5607` | Inline prefix, then `0x1407d7ce0` at `0x1407d97ab` | Complete nested schema still unjoined |
| +0x3e0, then +0x460 | Tail `0x1407d3f70` at `0x1407d562e` | `0x1407d8250` at `0x1407d97cc` | Two nested calls precede the final byte; nested schema still unjoined |

Full aggregate instructions support this order. Ghidra produced partial
decompilations for the aggregate and +0x2c8 helper despite `completed:true`;
those outputs are retained with warnings. Naming an edge does not close its body.

## Complete collection — J221-2/J221-3

Writer `0x1407d62b0` reads the 64-bit size at collection+0x18. Values above
`0x02000000` emit a compact zero count and return. Otherwise it emits the count
using `0x140877970`, then traverses the sentinel list at collection+8. Each node
supplies its +0x10 BE32 key and +0x18 string through `0x140876d80`.
The string writes a compact byte count followed by exactly those bytes; lengths
above `0x2ffff` emit zero and omit the payload. Embedded NUL bytes are data.
No text interpretation is established.

The writer traverses to the sentinel independently of the stored count. It
contains no count/list consistency check: matching output requires a valid native
container. Its order is the current linked-list order, without sorting or an
insertion-order promise.

Reader `0x1407da980` uses `0x14087b5c0` for the count, rejects values above
`0x02000000`, and consumes exactly the wire count of key/string pairs, even when
duplicates reduce the resulting map size. Each BE32 key uses `0x14087a220` and
each string uses `0x14087a3d0`; insertion `0x1407ddb90` occurs only after both
succeed. Strings accept byte lengths 0..`0x2ffff`.

The [joined compact codec](REGISTRATION_RESPONSE_BODY_CODEC.md#compact-counts--b218-3)
applies: the writer is canonical; the reader accepts nonminimal widths 1..5 and
uint32 wrapping. Value bounds do not restrict accepted prefix width. In particular,
`f0 00 00 00 20` decodes to zero. Canonical count/string limits need at most 4/3 bytes.

Insertion allocates a 64-byte aligned node and moves the temporary string into it.
On a duplicate key it unlinks and frees the new string/node, decrements size and
returns the existing value. The reader ignores the insertion flag: **first value
wins**, while all duplicate bytes are consumed. Rehashing rebuilds buckets and
list order while retaining node/string ownership; input order need not survive.
Calling the helper on an existing map does not clear or roll it back. The actual
selected decoder constructs an empty map, so that caller distinction matters.

## Failure, cursor and ordinary cleanup — J221-4

| Failure | Code | Cursor/output effect |
|---|---|---|
| Missing compact first byte | 1 | No movement or decoded count assignment |
| Incomplete compact tail | 1 | First tag consumed; incomplete tail remains |
| Collection count above `0x02000000` | 4 | Complete prefix consumed; no element read |
| Short BE32 scalar/key | 2 | No movement or destination assignment |
| Element string length at least `0x30000` | 4 | Key and complete length prefix consumed; no insertion |
| Short element string payload | 2 | Available bytes consumed one by one; sized temporary partly filled, no insertion |
| Final+0x460 byte missing / above1 | 3 / 4 | Missing byte stays unread; invalid byte was consumed; destination unchanged |

Earlier completed nodes remain at collection-helper failure. Its current temporary
is released; the actual top decoder then destroys the entire freshly constructed
object through +0x38 with flag0 (`0x1407cff40`). Collection destructor
`0x1407e51e0` frees buckets, heap strings and nodes, then restores empty state.
Flag0 preserves the caller's placement allocation. Allocation exceptions, native
faults, concurrency and further caller ownership remain unproved.

Adjacent+0xa0 differs from element strings. Its writer uses the same length bound;
its reader `0x1407fc670` fails with code1. It copies/moves the announced payload
**before** the final extent check through `0x140879590`. If that copy returns,
a short payload leaves the post-prefix cursor unchanged and destination modified.
Potential overread/exception behavior was not executed. A later safe offline parser
must prevalidate payload extent and document that stronger behavior.

After both +0x3e0 nested reads succeed, `0x1407d8250` reads the final byte.
Only 0/1 succeed; the writer normalizes any nonzero source byte to 1. A successful
helper defines the success byte, without assigning a meaningful error-code byte.

The receipt records targeted counter-review and required workspace validation.
These checks do not supply the remaining +0xc0/+0x2c8/+0x3e0 schemas, current
discriminator/framing inverse, authoritative field meanings or live acceptance.
#212 and Milestone1 remain open. The next bounded prerequisite is +0xc0's concrete
writer/reader schema, followed by the other separately scoped nested fields.

## Follow-up #222

[Complete field+0xc0 schema](REGISTRATION_REQUEST_C0_CODEC.md) now closes that
separate prerequisite at the same image. Field+0x2c8/+0x3e0 and full body/framing/
authority remain open; #221 evidence above retains its original collection scope.
