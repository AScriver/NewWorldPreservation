# Current registration stream framing — #226

Later [#263 byte-path checkpoint](#packet-assembly-calls--263) identifies the
conditional record writer and chosen-buffer lower-call ABI. Concrete bit copying,
reciprocal child identity and lower emission remain unproved.

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

## Follow-up #230

[The bounded original encoder](REGISTRATION_REQUEST_STREAM_CODEC.md) now implements
the selected empty ordinary stream using the corrected #229 nilouter/inner-type
placement and unchanged verified BODY. Type index and opaque8 fields are explicit;
no native receive inverse, Carrier hookup or observed runtime values follow.

## Follow-up #261

[The original lower-dispatch receipt](../research/evidence/current-registration-lower-send.json)
joins the previously unresolved fallback boundary, using the same owned image
and map at3282a87 with only TASK_BRIEFS dirty. Backend constructor145dba8d0 stores
the wrapper returned by145dbae90 at backend+130. Wrapper+0 takes config+0's supplied
interface when nonnull. Otherwise the selected factory allocates0xc0 bytes and
calls145dbe0f0 with two config option bytes and zero. Runtime selection and the
supplied interface's actual vtable remain unknown.

The fallback initializer calls145dbe1e0 before installing table148480888. Its
decompiler omitted arguments; exact instructions preserve RCX/RDX/R8/R9 to the
callee. The zero fourth argument selects a separate0x18-byte callback allocation
with table148480758, stored at interface+20. Callback+8 points to the interface;
callback+10 points to its +10 member. These are conditional source routes with
successful allocations, not observed constructed objects.

Fallback table+68 points to140889240, a short leaf without PDATA ownership. The
guarded function query was rejected; a bounded decoded instruction window alone
shows its interface+20 load and tail dispatch to callback virtual+30. That slot
points to backed method140f82280. When its handle is not -1, it passes a separate
local buffer containing byte0x47, length1, flags0 and a16/28-byte address argument
to the owned PE's WS2_32.dll ordinal20 IAT entry. The local installed DLL file
exports ordinal20 as sendto; the game's loaded dependency, resolved address,
return value and emitted traffic remain unobserved. The IPv4 branch builds its
address from0x7f000001 and the interface+18 port. IPv6 destination semantics are
not adjudicated here.

This supports a separate control/wakeup interpretation. The immediate send
buffer is not the queued physical registration stream. Broader callbacks or
workers may access queued state; their actual queue drain and packet assembly
remain unjoined. This boundary supplies no final Carrier header or supported
reply choice. Do not feed the local control byte into the registration decoder.

## Historical parser alignment — #261

The pinned First Light retry parser skips32 opaque bytes, then requires exactly
six BE32 key/one-byte length/value records with ID set0..5. It does not validate
the stream checksum/count, outer UUID, wrapper flags/presence, class selector or
fallback UUID. Its tail is opaque. The832-byte strict parser uses different
fixed offsets/trailer checks and is not an envelope validator either.

An original synthetic profile with exactly six short field10 values reproduces
one structural alignment: flags0 and explicit one-byte nonzero selector19 put
BODY at27, field08 at27–30, collection count at31 and its first key at32. Both
old retry and current server decoder accept that full stream. Across nine valid
flags0/1/3 × selectors19/300/0 combinations, the current decoder accepts and
round-trips all nine; old retry accepts only the first profile in this matrix.
Selector19 is an experiment input, not a discovered runtime binding.

Four controlled prefix mutations remain accepted by old retry: corrupt CRC,
declared count larger than available payload, nonnil outer UUID and selector18
instead of expected19. The new decoder rejects them as checksum,
payload-truncated, outer-uuid and type-mismatch respectively. The latter two
cases recompute CRC to isolate the semantic checks. Earlier0/34 comparisons of
existing neutral/rich fixtures in BODY/payload/full-stream forms also tested
their collection semantics; the six-field positive counterexample prevents a
general framing-incompatibility conclusion.

Bounded adversarial review retained the native ABI/back-pointer/conditional
claims and independently tested stronger parser counterexamples: an entirely
zeroed32-byte prefix, an FF-filled prefix and truncation immediately after the
six records all remain accepted by old retry. The current decoder rejects them
as outer-uuid, payload-limit and payload-truncated. Retry acceptance therefore
does not establish a complete BODY either. Control/wakeup remains an
interpretation; actual broader worker processing is not disproved.

These are original synthetic checks, not recovered historical860 request data,
wire placement, authentication or server acceptance. Sender/BODY/receiver/old
fixtures and Carrier responder remain unchanged. Three new backed function
slices and two table windows cover940 unique executable bytes; all private
query children exited without runtime resources. All36 affected catalog/runner
checks pass and actual preflight index/bindings are ready/matching; unchanged code/fixtures reuse the
1641-case/49-module workspace, five PowerShell suites and closed loopback receipt.

## Callback and record dispatch — #262

[The original partial checkpoint](../research/evidence/current-registration-worker-dispatch.json)
follows the stored145ddab20 callback at760a51a/TASK_BRIEFS-only query state. In the
factory's zero-result branch, a callable stores that function and owner pointer,
then is passed to14149c930. The address of its saved return value is passed to
140e863f0 with destination owner+2cd8. The decompiler's qword index+59b is not a
byte offset. Opaque helper effects, handle role and actual thread execution remain
unproved; native instructions establish the calls and arguments.

The callback checks stop byte+2ce8 and pops an internal tagged-record queue:
owner+2c0 block array, +2c8 block-bound operand, +2d0 cursor and +2d8 depth. Indexing
uses cursor>>4 and cursor&15, then advances/wraps the cursor and decrements depth.
The first dword selects record tags0–3. This record queue is distinct from the
prior child+90+mode*40 chunk lists. A null pop exits to continuation; treating
that as a complete internal drain assumes valid nonnull queued records.

For tag2, p=*(record+10) must be nonnull. Optional owner+30 virtual+20 receives
p+28; owner+10 virtual+10 then receives p. These are different receivers, and p
is not the tagged record. Owner+10 holds the supplied config+8 object or a
successful fallback0x60 allocation with table148480670. Conditional fallback+10
maps to145dd05d0, which clears *p before searching. Only a matching list node is
unlinked, passed through opaque disposal/allocator-like calls and counted down.
Its1f8/8 arguments are extent/alignment, not a proved copy size.

The null-pop continuation calls145dd4570, then owner+10 virtual+90; the selected
fallback145ddd470 updates accumulated state. Later exact callsites pass the
original owner to145dddfa0 at145ddb4e1, invoke (*owner) virtual+8 at145ddb4ec, then
pass the original owner to145ddeee0 at145ddb4f2. These unqueried helpers are the
next concrete byte-path candidates. The callback's indirect work can affect
shared queues; absence of a direct old chunk-helper call proves no broad absence
of sends. Actual registration bytes, final packet assembly and reply choice
remain unresolved.

Four new backed roots/eight ranges cover6452 unique executable bytes and one
192-byte table. Primary rehashes all spans/artifacts and re-decodes the already
queried3306-byte factory, without another function root. Bounded adversarial
review retains the source claims with explicit gate, pointer, matching-node and
null-pop conditions. No native/process/network resources were acquired; all
static children exited. All36 affected catalog/runner cases and actual preflight
index/new receipt bindings pass. Exact unchanged-input closure is
.scratch/registration262-primary-20261008T0136Z/closure.json; code/fixtures retain
the1641-case/49-module workspace, five PowerShell suites and closed loopback support.

## Packet assembly calls — #263

[Original partial receipt](../research/evidence/current-registration-bytepath.json),
K368–K370, pins db060e0 with TASK_BRIEFS-only query changes, the same image/map,
four new backed ranges totaling8017 bytes and one16-byte table. Raw instructions,
decompiler output and databases remain ignored; no client or native code ran.

`145ddeee0` reads a state object's child pointer at +20 and reaches the four
mode-list layouts also used by `145dcc970`. Count/container is child+90+mode*40;
sentinel/head is child+98+mode*40. Producer nodes store copied buffer at+20 and
uint16 byte count at+28. Consumer `145dcadf0` reads those fields. The old helper
queues child+10 state; the consumer dereferences state+20. The reciprocal
identity `*(*(producerChild+10)+20)==producerChild` remains unproved, so this is
a conditional matching-topology join rather than unconditional same-object proof.

Eligible nodes are unlinked and counters updated **before** opaque writer calls.
Writer virtual+8 receives flag byte8 bits, uint16 byte count16 bits, conditional
mode byte/record+1a/+1c/+1e metadata, then payload pointer with byte count*8 bits.
Zero writer+20 byte-order flag reverses16-bit scalar bytes before those calls.
This proves call arguments/order, with no successful copy or transactional-drain
guarantee. No semantic names or accepted identities follow from these fields.

Reused factory `145dbae90` initializes embedded writer owner+2d00 with table
147fbe6e8, backing owner+2d28, cursor0, capacity80000 and owner+2d20 byte-order
flag0. Table+8 resolves to140f8bfd0; its concrete bit-copy body is unqueried.
Assembly calls that writer for byte80/81, byte01 and a16-bit sequence value,
then the record helper. Computed byte count is ceil(bit count/8). Outputs of
four bytes or fewer use local packet/record cleanup through145dcc3d0.

For longer outputs, an optional owner+28 virtual+28 transform can preserve the
first four bytes while replacing the tail/buffer/count when its output shrinks;
otherwise the original is retained and bit0 cleared. Its algorithm/effects are
unproved. Optional owner+30 virtual+28 receives state+28, chosen buffer and
DWORD byte count first. When absent/zero, lower *owner virtual+50 receives
RCX=*owner, RDX=state+28, R8=chosen buffer, R9D=chosen byte count at145ddf70d.
Optional nonzero AL takes145ddf714; lower nonzero EAX takes145ddf761, a distinct
status/event branch. Reused fallback table+50 points to145dda0d0, unqueried;
supplied runtime selection and final socket/Carrier emission remain unknown.

Input helper145dddfa0 independently obtains a pooled buffer and calls lower+58.
Lower zero can be followed by optional owner+30 virtual+38 input. The selected
bit-reader/event path therefore has conditional provenance; its reassembly to
the higher compact-length response callback remains unjoined. Existing wrapper,
BODY and compact-reader proofs separately support a pure typed response record
encoder with explicit caller values, without proving that physical envelope.

Critical review corrected qword index5a4 to byte offset2d20, byte-versus-bit
units, sentinel/count separation, reciprocal identity and call/return/input
conditions. Agent aggregate6993 was wrong: exact ranges total8017 bytes.
Primary's first table recheck used192 rather than recorded128 bytes and failed
closed; the repaired extent/hash passed. All new instruction listings were
independently reconstructed from pinned PE bytes. All36 affected catalog/runner
checks and actual preflight bindings pass; unchanged1641/49/fivePS/closed-loopback
support is compared in .scratch/registration263-primary-20261008T0150Z/closure.json.
All owned static processes exited; no runtime resources were acquired. Acceptance
stays partial for concrete bit-copy, reciprocal identity and lower emission.
