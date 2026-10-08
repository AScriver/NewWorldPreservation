# Incoming buffer and reader construction

Actionables #279 under164/277 connects a conditional receive method to the
incoming reader used by the record parser. The [source receipt](../research/evidence/current-registration-incoming-reader.json)
records static evidence from the pinned owned image. This narrows the source
model for the replacement server; native acceptance remains untested.

The caller145dddfa0 allocates a buffer using its configured DWORD capacity.
It invokes virtual+58 on its interface receiver, passing buffer/capacity,
a qword output slot and a DWORD status slot. Conditional construction of the
fallback interface installs148480888, whose+58 target is145dd8b90. The new
302-byte function forwards the buffer/capacity to virtual+20 on interface+20.
When the separately constructed24-byte backend148480758 remains selected,
this reaches the already-sealed194-byte140f7c980 and its on-disk WS2ordinal17
association. The [backend receipt](REGISTRATION_DRIVER_BACKEND.md) qualifies
the `recvfrom` result, retry and error behavior. Actual interface/backend
selection, loaded import, socket invocation and buffer extent are unknown.

The wrapper clears/releases the old output qword, using the vtable of the
receiver at oldobject+10 for the zero-refcount branch. A nonzero backend EAX
invokes interface virtual+a0 and replaces that output with an opaque object.
A null output zeroes the local result. Cached145db4ef0 conditionally invokes
unclassified140571444 across registry nodes, passing the current DWORD result
by value and the output-slot pointer. The wrapper reloads its result afterward,
clears the caller status DWORD if nonnull, and returns EAX. Opaque calls and
aliases remain relevant; this is not an AL return or an unconditional unchanged
socket count. The28-byte local address area supplied to the backend is distinct
from the allocated packet buffer and the qword output object.

The optional caller field+30 filter can retry the receive after a nonzero
result or supply a substitute count after zero. On the nonzero normal path,
the caller zero-extends EAX, multiplies it by8, and creates a reader atRSP+60.
Its base/offset/cursor/end fields are at0/8/10/18; error is a byte at20 and
configuration a DWORD at24. The initial offset/cursor are zero on the selected
path. Reading the first header byte advances the cursor by8. The valid
untransformed header path reaches32 bits: high bit set, bits7e clear, next
byte1, then a byte-swapped16-bit value. These field checks agree with the
pinned four-byte envelope parser. Opaque calls and aliases must preserve
the reader; no full framing or physical-extent guarantee follows.

When the low header bit is set, an optional field+28 transform receives the
remaining input span and a separate
output buffer/capacity. Its selected reset requires EAXzero, no latched error,
the first output quantity times8 within remaining bits and exact consumption
of the old logical end. Qword counts multiplied by8 wrap modulo64; no local
overflow or output-count-versus-capacity check is shown. It rebuilds
base/offset/cursor/end/error/configuration, starting cursorzero, then passes
the reader asR9 to145dd4a90. Pointer validity, transform semantics,
output extent and alias effects remain unknown. The parser's conditional
explicit16-bit swaps under configurationzero support big-endian fields on
this initialized, aligned and preserved path, consistent with the pinned
FirstLight parser. This
source component establishes no new codec mismatch.

One new PDATA root302B,4658B reused code and192B reused tables were sealed.
Initialized static imports37848576B, BSS5559448B and four full-image identity
passes716816704B are accounted separately. The failed native-check launch read
no image; its original-script availability is disclosed in the private audit.
Relevant catalog/preflight/binding checks and exact1960-case input reuse are
recorded in ROADMAP. No server code, native client or runtime resources changed.

Parent277's queued payload/reassembly-to-compact/type/response/authentication/
world join and Milestone1 remain Partial. Official-game footage is reference
behavior; it provides no evidence of the private server's acceptance.
