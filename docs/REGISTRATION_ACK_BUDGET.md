# Current ACK callback and budget update — #283

The selected ACK path now has a source-supported output-byte predicate and a
traced local update helper. This closes the callback question left by
[#282](REGISTRATION_CONNECTION_ACK.md). The original server adapter is unchanged:
these sources justify no new registration response or authentication behavior.

[Receipt](../research/evidence/current-registration-ack-budget.json) pins clean
main4569ed8, the owned image/map, immutable earlier receipts, exact private
instruction artifacts and reviews. No client or native client code was executed.

## Conditional callback and its output

The ACK reader calls interface slot38 with `C=QWORD[owner+10]`, state pointerS,
node+8 and the address of a zero-initialized local byte. The cached constructor
and table conditionally select140f6e420 as the fallback. Actual runtime interface
selection remains unproved. Define **T** as QWORD[S] loaded at428 and retained
inR10; later comparisons use this snapshot pointer. They do not reload QWORD[S].
Offsets below are hexadecimal.

The selected connected graph contains95 instructions/412 bytes and reaches
two explicit output stores and returns. At523/527 it reads QWORD[C+48] and
compares it with QWORD[T+1a8]. Equality branches at52e to write output byte0
and return. Inequality stores the value atT+1a8, updates/clamps DWORD[T+1c0]
through the selected branches, writes output byte1 and returns. This is a
conditional source predicate for normal completion with valid pointers;
field meaning, units, aliasing, faults and semantic return status remain unknown.

Before this decision, the callback adds/clears scalar fields, conditionally
updates floating-point averages and subtracts a node WORD from DWORD[T+1b8].
The incoming R8 pointer is node+8, so WORD[R8+10/+12] refers to node+18/+1a;
QWORD[R8+8] refers to node+10. R8D is overwritten with DWORD[T+1bc] at53b.
Both selected integer divisions have local nonzero divisor guards. Arithmetic
still uses native widths, truncation and wrap behavior; no real-number budget
formula or safe pointer/alias contract is inferred.

The caller tests the output byte and conditionally calls145dcfd20(owner,S).
It does not branch on that helper's RAX. Seven separately declared instruction
windows cover the selected graph. Captured adjacent bytes after its returns
remain charged and preserved but support no adjacent-function claim.
The earlier PDATA query was refused and stays refused: connected-graph closure
does not establish a PDATA owner or whole-function extent.

## Direct helper and local object append

The609-byte PDATA helper145dcfd20 is also called conditionally by the cached
outgoing emitter when its locally loaded pointee's BYTE+37c is nonzero.
These callsites do not establish that their state slots or pointees alias.

Entry arguments are ownerA and stateS. BYTE[A+251]==0 skips the body.
Otherwise, interface virtual+a8 receives S and an output buffer; virtual+98
uses a freshly reloaded interface pointer, S, zero, another output buffer and
two zero stack arguments. Those output buffers are not initialized locally.
Their contracts and the referenced floating-point constants remain opaque.

The helper performs a low32 multiply by1010, zero-extended integer-to-float
conversion, floating-point division/truncation, unsigned multiplication and
an integer division. This last divisor lacks a local zero guard. NaN,
exception, rounding, overflow and caller contracts prevent treating this as
a safe arithmetic formula. The helper snapshots H=QWORD[S+20] and writes
BYTE[H+37c]. Both normal flag values continue toward object creation.

It requests0x78 bytes aligned8 and, for nonnull allocation, calls an opaque
constructor with argument6. It then stores a **fresh** QWORD[S+20] reload
at returnedobject+8 and a computed DWORD at+44. The fresh pointee need not
equalH after opaque calls. Null returns reach unguarded stores. Under selected
owner lock operations, the helper passes the pointer to a local append helper.
Constructor argument6 does not establish a tagfield or a network system ID.
No selected explicit frame or socket-send operation identifies a reply;
opaque effects, actual queue consumer, ownership and lifetime remain unknown.

## Evidence and verification

ClaimsK422–K424 distinguish the conditional fallback output predicate, guarded
scalar helper and local object append. The initial refusal, partial-prefix
reports and seals remain immutable. Separate continuation/adjudication artifacts
correct the original void-signature shorthand, comparison/branch-address
shorthand and snapshot-versus-reload descriptions.

The final byte seals cover one609-byte PDATA body and seven windows:704 bytes
captured/535 unique, totaling1144 unique selected code bytes. Only412 callback
bytes are reachable in the selected graph. Seven known full-image identity
passes total1,254,429,232 bytes. Initialized static imports37,848,576 bytes,
BSS extension5,559,448 bytes, bounded reads and reused192-byte table are
accounted separately. No additional Ghidra query or import was used for the
final connected observation.

Relevant catalog/preflight/binding closure and reuse of unchanged1960 cases,
50 modules, five PowerShell suites and the closed loopback exchange are recorded
in the private closure receipt using actual selected inputs. Parent277/263
physical receive/reassembly-to-compact/type/reply/authentication/world and
Milestone1 remain Partial. Official recordings remain normal-game references.
No native trial, live memory observation, endpoint traffic or publication follows.
