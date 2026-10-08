# Initial receive-object state assignment

Actionables #281 under work item164/parent277 closes the selected construction
and state-assignment source edges. The [receipt](../research/evidence/current-registration-receive-state.json)
pins clean a3834d1 and the owned image. These are static observations useful to
the replacement server; no game session or native acceptance was tested.

## Lookup node (K416–K417)

Direct helper145de1a30 requests0x50 bytes with alignment8 and zero flags through
141499110. It publishes the returned pointer in the output slot before copying
fields and linking the node. There is no local null guard. It writes the selected
vptr148480720 at node+0x10, copies factory+8 into node+0x18 and returns the output
slot address. Other explicit fields include a DWORD counter and the selected
address-area bytes. Two sequential16-byte copies remain distinct operations;
overlap or source mutation can change their effects. Some padding/tail bytes are
not initialized by the preceding factory. Allocator/lifetime/list consistency
and failure atomicity remain unknown.

The [280 receive factory](REGISTRATION_ADDRESS_FACTORY.md) supplies zero at
factory+8 and returns node+0x10 as the lookup object. With the stated ordinary
return, nonalias and preservation conditions, object+8 initially receives that
zero on the new-node path. This is not a claim about every existing node.
The cached caller checks object+8, then follows additional flag/limit/helper
gates before calling145dcecd0 with the address of the same holder local.

## State assignment and callbacks (K418)

Helper145dcecd0 requests0x13c8 bytes with alignment8 and zero extra arguments
through a virtual allocator. On nonzero allocation it invokes140f53590 with
the allocation and caller objectA; its returned pointer isS. The initializer
and allocator are opaque. A zero allocation leavesS zero and is followed by
a dereference, so successful null-return behavior is not established.

The helper loadsP from the holder, conditionally increments DWORD[P+0x18],
replaces QWORD[S+0x28] withP and decrements the prior pointee's DWORD+0x18.
Its zero-count callback uses QWORD[prior+0x10] as receiver, then virtual+0x98.
After that callback it reloadsP2 from the holder and writesS intoP2+8. P2 need
not equalP if the intervening operation or aliases change the holder.

The store occurs before the callback on QWORD[A+0x10] virtual+8, the optional
callback on QWORD[A+0x30] virtual+0x18 and opaque145de16a0. Their effects can
change fields or lifetime; stable reciprocal identity through return is unproved.
The helper returns savedS. The caller stores that result in a local, rather than
independently writing object+8 after return.

Two roots194+370=564 bytes and no new table windows were sealed. Critical review
and original corrections/failures are preserved privately. Nine known image
identity passes include the failed first size assertion; static imports/BSS,
metadata navigation and selected code are counted separately. Relevant catalog,
binding and unchanged1960-case validation reuse are recorded in ROADMAP.

The cached fallback table conditionally identifies the first callback target
145dcff90; its role is the next bounded source question. Full packet delivery,
reassembly, compact/type dispatch, appropriate reply, authentication, world
entry and Milestone1 remain unproved. No codec mismatch or server change follows
from this source unit.
