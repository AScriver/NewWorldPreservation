# Current connection callback and system ACK input

Actionables work164 / leaf282 / parent277. This closes K419–K421's selected
static source and synthetic byte comparison. Parent277/263 and Milestone1
remain Partial. Official-game recordings are original behavior references.

## Source identity

Clean checkout224684da971366eb3df5e14f94e5e99c5be193d3; owned NewWorld.exe
179204176B, SHA2568654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e.
Type-map SHA256f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75.
The [receipt](../research/evidence/current-registration-connection-ack.json)
pins original notes, exact raw/query/decompiler/native checks, review and
synthetic results. Client-derived outputs remain private and ignored.

Two new PDATA roots:145dcff90..145dd0100 (368B/80 instructions),
145dd79f0..145dd8033 (1603B/427 instructions). No new table window or third
root. The192B cached fallback table retains its historical checkout/dirty
provenance; selected bytes were independently resealed against the owned image.
Four agent and two primary identity passes total1075225056B. Initialized static
imports75697152B and virtual BSS11118896B are separate from selected1971B code.
The two agent bounded native checks read3267 logical bytes including PE metadata.

## K419: conditional first-state-field callback

[The prior state helper](REGISTRATION_RECEIVE_STATE.md) passes
RCX=C=QWORD[owner+10], RDX=state slotS, R8=&S+28. The unchanged constructor's
fallback interface table slot8 targets145dcff90; alternate/runtime bindings
remain unproved. IfQWORD[S] is already nonzero, this body exits without explicit
state stores. Otherwise it uses C+8/+48/+54/+58, invokes the pair's object
virtual+10 and cleans/moves local fields. Capacity cleanup uses unsigned>=16.
The literal QWORD[C+48]+0xd693a400 is modular arithmetic; its time units are unknown.

At145dd00cc it calls opaque145de1900 with RCX=R8=C+20,
RDX=&[RBP+168], R9=&[RSP+50]. It then reloadsQWORD[C+28], adds0x10 modulo64,
and storesQWORD[S]. The final local cleanup can have effects. The selected body
does not parse or drain a packet. It establishes neither successful-null
construction, nonnull final state, a fixed object identity nor a semantic return
status. Opaque calls, aliases, caller selection and lifetime remain limits.

## K420: system-ID6 grammar and cursor placement

The cached current parser145dd4a90's channel3/nonzero-length path checks logical
remaining bits, peeks the last payload byte directly, and selectsID6 when the
nodeDWORD14 is zero. No cursor write occurs between the peek and direct call
145dd52a8(owner,state,reader). This supplies the helper's selected input cursor.

The helper uses cached bitreader140f7c420. Its branches are:

| Selection | Fields read after the marker | Processing gate |
| --- | --- | --- |
| Initial error clear and marker80 set |16-bit base, then(low7 marker) bytes of bitmap | Count<=64 bytes; prior errors clear plus bitmapAL predicate |
| Otherwise marker40 set | Two16-bit fields | Initial, first-field and final reader errors clear |
| Otherwise marker20 set | No further field | Early exit without list processing |
| Otherwise | One16-bit field | Initial and final errors clear |

Each16-bit swap requires its bitreaderAL success and readerDWORD24==0. The
bitmap count is multiplied by8, up to512 bits in a64B local buffer. Its final
predicate uses the saved earlier error and bitmapAL via AND, rather than a fresh
post-bitmap error load. Counts>64 and marker20 exit without explicitly setting
reader error. Low marker bits are not generally canonicalized or rejected.

After the helper, caller145dd52ad..52d0 checks error and>=8 remaining bits,
then advances the cursor8 bits. It does not compare that byte with the peekedID
or require record exhaustion. Under aligned, preserved input, normal successful
reads and configDWORD24==0, marker40 consumes5 bytes; a6B payload leaves the
one byte that the caller skips. Physical bounds, alias/mutation and actual
runtime selection are not established by this cursor calculation.

## K421: list effects and server comparison

For a valid predicate and nonnull state,145dd79f0 traverses state+190 and reads
nodeWORD8. In differing-field mode, a visited node is selected when equal to
either field, or when u16(secondField-node)>0x7fff AND
u16(firstField-node)<0x7fff. The exact threshold equality is excluded from that
interior test. Nonselected nodes can call interface virtual+40 or stop at the
other modular threshold. This is a traversal rule, not proof of processing an
entire interval or of callback semantics.

Virtual+40 call sites explicitly supply receiver/state and retain other registers;
no two-argument signature or retransmission meaning is established. Selected
nodes are unlinked; state+180 can be updated and QWORD188 decremented.
The body calls QWORD[owner+10] virtual+38 with(state,&nodeWORD8,&outByte),
conditionally145dcfd20, then cached145dcc3d0(owner,node). Range mode can move
the node128/130/138 range into a0x78B event and enqueue it at owner2f8 under
owner2e8/2ec locking. Single/bitmap mode starts at u16(base-bitmapBits), visits
bitmap bits descending with LSB numbering inside each byte, then an implicit
true base. Zero bitmap length supplies one base iteration if list flow reaches
it. Allocator failure,
queue validity, callback mutation, object ownership and semantics remain unknown.
140f8aa90 is opaque and only called on paths reaching145dd800d;
no semantic return contract is established.

The pinned clean FirstLight63756a3f7ff0ae41752dcc7c80267802c3fa7548 ACK builder
emits marker40, BE16last, BE16first,06 inside a14B channel3 record. An independent
pure experiment passed13 literal calls:9 emitted records matched exact bytes,
the pinned frame parser and the selected source cursor model;4 guard cases
returnedNone. A final-ID5 control took another route. Values7ffe/7fff/8000/ffff
were included; this tests layout, not native queue acceptance or wrap semantics.
An out-of-domain input control demonstrated silent16-bit masking. The builder's
numeric wrap guard and caller input validation are separate policies.

No production mismatch was established, so the existing server builder is reused.
No client, game, hooks, memory observer, endpoint, listener or new native trial
was started. Relevant catalog/preflight and exact binding checks passed; the
unchanged1960-case/50-module/five-PowerShell/closed-loopback validation is reused
only through selected-input reconciliation. Frozen report arithmetic/byte-count/
capacity/cursor wording errors and their separate corrections are retained.
Full Carrier physical validity, reassembly-to-compact/type/reply provenance,
authentication, world state and two-client gameplay remain unproved.
