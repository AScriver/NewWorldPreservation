# Current registration identifier placement — #229

October6,2026; workItemId164 / parent178. The selected V3 message's concrete
descriptor construction now joins the sender's type emitter. Its class UUID is
an **inner type-selector fallback**, while the separate physical-header UUID is
nil on this registration path. Wrapper fields precede the BODY. This corrects
the proposed outer placement rather than treating an opaque endpoint as closure.
No client or native client code was executed.

Input: clean main `e7b4237904c050390ddd8cabeba37b3f1405754a`, build22469132,
version1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
[Original receipt](../research/evidence/current-registration-identifier-placement.json)
binds current instructions/data, retained failed queries and executed pure checks.

## Selected outer slot — J229-1

Builder `0x146b6e190` constructs V3 through `0x146b66820`, then calls owner
virtual+0x30 at `0x146b6e48c`. Owner constructor `0x146b69ad0` installs
`0x148590ab8`, whose +0x30 selects `0x146b706f0`. That method retains/moves the
message into a fresh wrapper and initializes a separate local tuple with two
nil UUIDs from `0x1407f7d80`.

Gateway `0x146b6ffb0` passes tuple+4 as writer argument3. Gateway construction
installs `0x148590be8` at +0x108; writer+0→`0x146b0f430`, raw16 method+0x20→
`0x146b0f640`. This writes that supplied nil UUID at physical bytes8..23 after
the reserved CRC/count header. The V3 class UUID does not occupy this slot.
The nil helper initializes writable static storage; no universal immutability,
concurrent-mutation or native fault guarantee follows.

## Descriptor object and inner selector — J229-2

V3 constructor installs `0x147f479a8`; +0x30→`0x1407cfca0` is a five-byte
tail jump to factory `0x1407f2c50`. The factory parses literal `0x147f48660`:
`0B826B33-89F5-49E0-B8CB-FE4433427778`. The factory's sequential hex-pair loop
produces raw16 `0b826b3389f549e0b8cbfe4433427778`, matching the map's V3 entry.

Helper `0x1407de270` allocates0x68 and returns `{allocation+0x10, allocation}`.
Constructor `0x146152b10` copies the UUID to descriptor+0x18/+0x20 and zeros
qwords+0x48/+0x50. The factory stores that object/owner pair at `0x14a2e82f8`
and installs the selected serializer at object+0x48. **The returned global is a
handle pair, not UUID bytes.** Its cached dword+0x54 starts zero.

Generic `0x146167110` writes its wrapper prefix and body-presence byte, calls
the message metadata accessor, invokes `0x1461673b0`, then calls serializer
+0x20 at `0x146167262`. The V3 serializer remains `0x1407ce860` from #220–#225.
The type emitter dereferences a valid descriptor handle and uses this order:

| Current cache / lookup result | Inner selector bytes |
|---|---|
| Cached index nonzero | Compact uint32 index only |
| Cache zero; UUID lookup supplies nonzero index | Copy found index to cache; compact index only |
| Cache zero; lookup misses or supplies zero | Compact zero, then descriptor UUID raw16 |

Compact writer `0x140877970` is the proved current uint32 encoding: e.g.19→`13`,
131→`83 02`. Map entry19 supplies a naming cross-check; it does **not** prove a
runtime cache/index19 or an emitted discriminator. A valid handle containing a
null object gives zero in the standalone emitter, but the full generic writer
then dereferences the object; this is not successful null-metadata serialization.

## Fresh wrapper and placement — J229-3

Constructor `0x146153e70` starts flags at0 and moves the message shared pair to
+0x60/+0x68. Helper `0x146165a00` may populate two opaque eight-byte fields and
change bits0/1 using ambient/TLS state. It does not set bit2 on this fresh path.
With stable ordinary ambient/sentinel state, selected flags are0,1 or3; current
values and their authority are unobserved. General writer bit2/context capability
does not establish such a block on this selected fresh registration wrapper.

For this selected source path and an empty ordinary stream, the joined layout is:

`CRC_BE32 | count_BE32 | nil16 | flags_u8 | [raw8 if bit0] | [raw8 if bit1] | presence1 | compact_type_index | [V3_UUID16 if index0] | V3_BODY`

The two optional fields follow bit0 then bit1. Physical byte24 is the wrapper
start, not BODY. Count and CRC cover nil16 plus the actual remaining bytes as
proved in [#226](REGISTRATION_STREAM_FRAMING.md). No receive inverse is inferred.

## Ownership, checks and limits — J229-4

The moved wrapper/message shared owner survives synchronous serialization and
is released afterward; the queued stream retains its separate owner as in #226.
Factory guard/retained handle support ordinary construction, not complete global
teardown, allocation rollback, concurrent mutation or current registry state.

Exact instruction/data rehash and targeted counter-review establish the source
join. Original compact, branch and placement models execute Python only; required
repository checks are recorded separately in the receipt. Initial no-PDATA,
interrupted broad-xref, virtual-storage read and handle-layout errors are retained
with their corrections. No historical860 mapping, observed wire bytes, configured
identity, authentication, lower datagram emission, #212 readiness or Milestone1
acceptance follows. Parent178/164 and bilateral movement remain open.
