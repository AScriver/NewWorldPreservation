# Driver list and shared buffer table

Actionables #274 under164/267 follows the conditional backend evidence from
#273. [Original receipt](../research/evidence/current-registration-driver-input-buffers.json)
pins clean main93620b8, the owned image, exact PDATA bodies and private native
cross-checks. This is source inference; no game client or network was exercised.

- K396: driver table+0x08's previously proved jump reaches a677-byte list worker.
  It conditionally transfers state, processes entries, updates bucket accounting
  and releases/unlinks nodes. Its broader setup or transport role is unknown.
- K397: direct817-byte callee performs hash-bucket lookup/insertion over a
  string-shaped input. It hashes qword field+0x10 bytes with signed-byte FNV-style
  arithmetic, selects inline/heap storage using field+0x18, and returns a node
  pointer plus an existing/new byte. Other caller output bytes remain uninitialized
  by this body; valid extent, representation and lifetime are unproved.
- K398: two sites test qword field+0x18 against16 unsigned, then conditionally
  call an unresolved global-context virtual+0x10 with a pointer, field+0x18+1
  modulo2^64, and1. This quantity is separate from the+0x10 hash count.

The original investigator report called the gate quantity a length. Critical
review corrected that identity; the original and correction are both preserved.
The field also controls inline/heap storage, so storage release or allocation-size
handling is a plausible explanation. The dynamic target and its effect remain
unknown. Compression, encryption, Carrier framing and server-reply behavior are
not established by these calls. Shared callee identity also does not equate the
three known callers' inputs, bytes or subsequent output use.

Both admitted static batches completed:1494 selected code bytes,75697152 initialized
static bytes,11118896 virtual BSS bytes separately. Metadata walks and repeated
full image identity reads have separate counters. Primary native/PDATA/table/entry
checks and related critical review qualify the local claims. Affected catalog and
preflight validation plus reuse of unchanged full-suite inputs are in ROADMAP.
Static children exited; outputs remain ignored. No codec or native trial changed.

The actual incoming transport producer, primary callback/Carrier placement,
response values, authentication and native client acceptance remain unproved.
These routines add no supported wire behavior to the server. The next practical
unit is an explicit runnable local selection of the current registration codecs.
