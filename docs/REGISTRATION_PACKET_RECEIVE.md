# Current incoming packet records

Actionables #277, root workItemId 164, is a source checkpoint with **Partial**
aggregate acceptance. [K404–K406 receipt](../research/evidence/current-registration-packet-receive.json)
pins the owned image, exact selected functions, original private reports,
corrections and critical review. No server codec changes follow from this
checkpoint. Native packet delivery and the join to the higher registration
callback remain unproved.

## Record fields (K404)

The cached input helper supplies an owner, state, incoming aggregate and a
stack reader to the 3,203-byte parser. The caller takes the reader's address;
the parser's local alias is a separate register. An initial predicate can
select an alternate event path that bypasses normal record parsing.

Normal parsing reads eight flag bits and a sixteen-bit payload length. The
following gates describe this function's supplied reader, rather than an
accepted network datagram or a complete protocol specification:

| Gate | Selected operation |
| --- | --- |
| 0x20 set | Read eight channel bits; otherwise retain the preceding channel. Require channel below four. |
| 0x04 set | Read a sixteen-bit field at node +0x1a; otherwise use one. |
| 0x08 set | Increment a local per-channel sequence; otherwise read sixteen bits into node +0x1c. |
| 0x10 clear | Read the second explicit sixteen-bit sequence; otherwise use a local per-channel value. |
| 0x01 set | Increment that local value when 0x10 is set; also store a Boolean at node +0x14. |
| 0x80 set | Store a Boolean at node +0x2a. |

Explicit sixteen-bit byte swaps require both helper AL success and a zero
DWORD at reader +0x24. The copy helper below does not read that DWORD.
No special 0x40 layout is shown in these gates; this is a local observation.
Local implicit counters have unproved initial values and are distinct from
persistent state ordering and queue slots. Cursor/end loop tests use equality,
and partial field writes precede combined validity checks.

## Bit copy (K405)

The directly called 277-byte helper receives reader, destination and requested
bit count. Its reader fields are base +0, offset +8, cursor +0x10, end +0x18
and error byte +0x20. A latched error or an unsigned requested-count comparison
against end minus cursor rejects the read and latches error. Success/failure
is established in **AL**, not the whole return register.

The subtraction wraps if cursor exceeds end. Neither this guard nor success
proves a valid physical source/destination extent or lifetime. With aligned
offset plus cursor, the helper copies the ceiling of requested bits divided
by eight through the previously pinned memcpy import, then reloads and adds to
the cursor. Exact final cursor arithmetic requires ordinary callee return and
nonalias assumptions.

The unaligned branch merges adjacent source bytes and emits the same rounded
byte count. Each store precedes a cursor reload and increment of eight, so the
alignment offset persists. It does not mask a final partial byte. The guard
bounds requested bits, rather than the rounded advance or adjacent physical
read. The selected parser requests multiples of eight; its starting alignment
and other callers remain unknown.

## Payload and queue effects (K406)

The common path compares payload length against owner +0x3c, allocates a
buffer, stores it at node +0x20 and requests length times eight bits. No
allocation-null check is shown. For channels other than three, a sixteen-bit
length accumulator in the **incoming aggregate** changes before AL is tested.
It is neither the parsed node's +0x1a field nor a success-only effect.

Channel three inspects the final payload byte under logical checks. This peek
also needs valid alignment and physical extent. IDs at most five can enter the
same common sequence/allocation/copy/list path. Other branches include a
release path, an unqueried ID-six helper, and an ID-seven thirty-two-bit read.
The ID-seven virtual call receives the object at owner +0x10 as receiver, state
as its next argument and the read value as the following argument.

After successful payload read, this function links the node, increments a
channel-indexed state counter and updates a state slot. Sequence comparisons
and wrapping differences do not establish complete reassembly. Header/payload
failures set an error-state byte without a direct node release at those exits;
there is no demonstrated rollback of previous writes or queued nodes. The
owner-to-state common exit copy is bypassed by the initial alternate path.

## Next source edge and evidence limits

After the parser, the cached caller conditionally invokes virtual slot +0x48
on the object at owner +0x10, with state and an address inside the incoming
aggregate, then performs aggregate cleanup. The target, body and actual
payload drain remain unknown. This is the next concrete source edge, not a
proved registration callback.

Two new PDATA roots total 3,480 executable bytes; the cached caller is 3,263
bytes. The private seal checks exact image bytes and listings. Original errors,
failed queries/seal and two correction addenda are retained rather than
rewritten. Eight known full image identity passes include failures; imported
static data, virtual BSS, navigation and bounded reads are accounted separately.
The source-only work acquired no game, runtime listener or native observer.
Unchanged 1,960-case workspace support is reusable only with the closure's
actual selected-input reconciliation. Type values, appropriate server response,
authentication, playable world and Milestone 1 remain unproved.
