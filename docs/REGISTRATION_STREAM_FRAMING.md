# Current registration stream framing — #226

October 6, 2026; workItemId: 164 / parent #178. The current sender's concrete
stream, queued byte handoff and concrete backend chunk-copy chain are joined.
Exact source checks and targeted counter-review support the bounded result.
No client or native client code was executed. Original source hashes, executed
pure checks and required workspace validation are recorded in the
[receipt](../research/evidence/current-registration-stream-framing.json).

Inputs: clean main `040d7357dce67f4c98500e9a6e63f5339fc5ecb9`, Steam build
22469132, version 1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
The approved map, clean reference checkouts, tool identities and dirty-file
boundaries are pinned in the private baseline and eventual original receipt.

## Concrete stream and header — J226-1

Connection method `0x146b27860` calls factory `0x146b36600`, which obtains a
0xd8-byte allocation O from the transport's +0x3d0 pool or constructs it through
`0x146a99bf0`. Wrapper `0x146ae55b0` returns shared pair `{O+0x50, O}`.
Stream S=O+0x50 has vtable `0x148582d68`; it owns backing pointer B at +0x08,
high-water length L at +0x10, capacity at +0x18 and write cursor P at +0x28.

Reserve `0x140878870` returns old P, grows capacity through `0x140874460`,
advances P and updates L=max(L,P). Write `0x14087bcc0` reserves then uses the
current PE's named `VCRUNTIME140!memcpy` import. Seek clamps to L;
`0x140879350` restores P=L. These concrete methods perform no compact-prefix
conversion, compression, descriptor removal or segmentation.

On the empty logical stream supplied by the selected new or ordinarily recycled
path, writer `0x146b0f430` produces:

| Relative byte range | Stored bytes |
|---|---|
| 0..3 | IEEE CRC32, big endian |
| 4..7 | Low 32 bits of actual count n, big endian |
| 8..23 | Exactly 16 supplied outer UUID bytes; nil on the selected registration path (#229) |
| 24 onward | Bytes actually written by the generic wrapper/body writer |

n is the descriptor cursor delta plus the generic writer's actual cursor delta.
The generic serializer result is ignored; this count does not prove a complete,
successful body. Patch `0x146b0f350` calculates over `[B+r+8, B+r+8+n)`, seeks
to reservation r, writes the two BE32 fields and restores P=L. The checksum uses
64-bit n; `0x146b0f3af` narrows the stored length to n modulo 2^32. For empty,
ordinary nonoverflowing extents and n<=0xffffffff, r=0 and L=8+n.

That equation does not generalize to a nonempty stream positioned before its
high-water mark. A synthetic L=100/P=4, n=40 case ends with L=P=100 and returned
length delta 0; the patch still occurs at r=4. Native huge allocation, integer
overflow, allocator failure, faults and exceptions were not executed.

Checksum `0x1412f47d0` calls `0x141462980`, which starts at 0xffffffff and
complements the result after `(state>>8) XOR table[(state XOR byte)&0xff]`.
All 256 entries at `0x147fe6730` match reflected polynomial 0xedb88320.
The selected caller disables ASCII folding at `0x146b0f36e`. This identifies
IEEE CRC32 over descriptor plus actual wrapper bytes. Null source stores zero;
that branch is not an allocator-safety guarantee. Primary and counter-review
models separately matched 525 and 276 original synthetic vectors against zlib.
These are pure model checks, not native execution.

## Queued byte handoff — J226-2

Submit `0x146b28e50` updates the elapsed-time sidecar at S+0x30 through
`0x140878c90`, then `0x146b3b3b0` appends a 0x20-byte record under the
transport's +0x1b0 lock. Its fields are key at +0x00, moved shared pair at
+0x08/+0x10 and flag at +0x18. The sidecar changes scalar timing state; it
does not rotate, rewrite or convert the message buffer.

Consumer `0x146b3c250` moves the +0x190 vector to local storage under that
lock. The actual queued-item loop begins at `0x146b3ca20`; an earlier release
loop handles an empty prior stash. At `0x146b3ca5c`/`0x146b3ca68`, the concrete
stream methods supply B and L. At `0x146b3caa8`, backend `[transport+0x48]`
virtual+0x48 receives B, low 32 bits of L, key and three flag-derived parameters:
the original flag, selector 1 when flag==0 or 2 otherwise, and flag==0.
No physical-byte conversion occurs between these getters and that invocation.
The shared owner remains retained across the synchronous call.

The constructor `0x146b34780` initially leaves backend+0x48 null. Selected
installers `0x146b36920` and `0x146b38c10` call `0x145dc8b00`, then store its
result there. That factory constructs a 0x218-byte object through `0x145dba8d0`,
which installs vtable `0x148480948`. Its +0x48 entry `0x140f7fb40` reshapes
arguments before calling concrete +0x40 method `0x145dda6c0`:

| Value | Queue caller to thunk | Thunk to concrete method |
|---|---|---|
| Receiver / bytes / length | RCX backend / RDX B / R8D low32 L | Unchanged |
| Queued qword | R9 | Stack argument 5 |
| Original flag | Stack argument 5 | Stack argument 6 |
| Mode 1 or 2 | Stack argument 6 | Stack argument 7 |
| flag==0 boolean | Stack argument 7 | Stack argument 8 |
| Separate owner slot | None | R9 points to an initialized-zero local qword |

The concrete method admits qword -1 as broadcast over its child-pointer list.
Otherwise it compares each list pointer directly with the queued qword, then
dereferences the matched child at +0x68. It does not compare the child's first
field. Only child+0x68==1 reaches `0x145dcc970`. This supplies a local pointer
membership/gate rule, with no authenticated identity or authority conclusion.

The helper's argument 8 is a nonnull address of a separate local owner slot
whose contents start zero on this path. Broadcast initializes that slot; the
targeted path moves the thunk's zero owned value into it and clears its source.
The pointer, its zero contents and the distinct inner argument 8 boolean must
not be conflated. No nonzero owner is supplied by this forwarding path.

Input length and chunk limit backend+0x108 are 32-bit; each
record's length and memcpy count are narrowed to 16 bits. For positive chunk
limit <=65535 and adequate supplied buffer capacity, it slices and copies the
submitted bytes through `0x145dc7970` and the named memcpy thunk. The allocation
helper pops a pooled buffer or calls the lower allocator using its +0x38 size.
The selected path does not validate these configuration relationships. Positive
input with limit 0 reaches division; limit 65536 can narrow a positive chunk
to 0 and fail to make progress in the pure arithmetic model. Zero input/limit 0
avoids division and models one zero-length record. Native allocation/division,
huge extents, insufficient capacity, faults and exceptions were not executed.

The initial fragment count is ceil(input/limit) when splitting is required and
is stored in each record modulo 2^16 as the remaining count decreases. A pure
input65536/limit1 model copies all bytes but stores initial count0. Byte-count
progress therefore does not establish lossless fragment-count metadata or
successful reassembly.

It stores sequencing/metadata and links buffer-bearing records into the child's
mode-specific list. The bytes supplied are the physical stream's low-32-bit-length
slice; this path does not decode or remove the reserved header or descriptor.
For the stated bounds, original stream ownership and backend copy ownership are
separate; eventual chunk retirement/disposal is outside this selected join.

Records enter the child's list at +0x90+mode*0x40 under its lock. The dword at
child+0x378 accumulates the narrowed record lengths across both selected lists,
modulo 2^32. The lower interface's +0x28 return is sampled once per helper call;
each chunk compares the shared total unsigned against the low32 product of that
sample and the current backend+0x1c. Any successful comparison sets a sticky
flag. The helper invokes lower virtual+0x68 once after the loop when that flag
is set, even if a later addition wraps the total below the threshold.

Pure counterexamples retain these limits: 0xfffffff0+32 wraps to 16 and may
remain below threshold100; 0x80000000*2 wraps the threshold to0; an earlier
comparison stays true across a later total wrap. These are model observations,
independent of the unknown runtime configuration and native flush outcome.

The lower interface can be supplied or constructed through a fallback branch;
exact runtime selection, flush execution and final datagram layout remain
unproved. The RTTI query for the installed table failed its COL guard, so no
class name is asserted. This closes the concrete consumer/buffer/chunking chain
without claiming Carrier emission or a compact-record inverse.

## Record direction and limits — J226-3

The selected receive path `0x146b6ba90` → `0x146af20c0` → `0x146af1d90` →
`0x146ae44f0` parses compact-length records. It decodes the prefix on a copied
view, commits prefix bytes only on success, advances a complete declared record
before its synchronous callback and resets framing state independently of body
status. That reader strips no additional 16-byte descriptor. Sender framing,
incoming record parsing and application acceptance remain separate boundaries.

The historical 860-byte records' discriminator remains unknown. The pinned
FirstLight `wire.py` source provides a historical CRC/header comparison; its
comments exclude pre-session V3 from the reported capture agreement. It supplies
no current inverse and no packet or entity data was replayed.

## Buffer ownership and verification — J226-4

Control-block strong disposal invokes callable `0x149f7faf8` → `0x146b1f2d0`
→ stream virtual+0x18, clearing L/P while retaining B and capacity. Final control
reclamation `0x146b17690` → `0x146b174b0` returns O to a live pool under its
lock if cache/capacity limits permit; otherwise `0x146aadb80` frees B and O.
The retained weak-like reference keeps the pool's lifetime-control object alive;
it does not keep the pool itself alive. Raw backing bytes need not be zeroed.
No raw runtime buffer was observed. Stream mutation methods have no lock;
shutdown races and concurrent safety are unproved.

Physical source, exact instructions, the complete CRC table and bounded pure
counter-review passed. The queue review rehashed 11 code spans, 42 frozen
artifacts and all 250 baseline tracked files; it exercised three ABI, two owner
slot, nine chunk and four threshold cases plus the pointer-membership example.
Those finite checks do not substitute for native execution.

Failed/partial scans and repaired harness errors remain private evidence. The
investigator's timer, early cleanup and same-ABI readings were corrected by
primary instruction dataflow. Counter-review falsified the subsequent
child-first-field/no-dereference, null helper-parameter and per-channel counter
wording. Frozen interim reports remain historical; this report incorporates the
adjudicated pointer/value, width and shared-total distinctions. The later queue
loop was guided primary adjudication, not a second independent discovery.

Field authority, authenticated peer binding, current wire selection, complete
reliability/ACK scheduling, #212's construction/member gates and two actual
clients with bilateral movement remain unproved. Parent #178/#164 and Milestone 1
remain open.

## Follow-up #229

[Identifier placement](REGISTRATION_IDENTIFIER_PLACEMENT.md) now joins the selected
registration call to this physical slot: nil outerUUID, then wrapper
flags/options/presence, inner class selector and V3 BODY. The class UUID is an
inner fallback when its actual cache/lookup index is zero; map19 alone supplies
no emitted-index proof. The #226 header/count/queue evidence keeps its original
ordinary-stream and lower-emission limits.
