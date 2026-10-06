# Registration response callback ownership — #216

October 5, 2026; workItemId: 164 / parent #178. The selected owner+0x110 callback
**copies response+0x38 into local metadata labelled "Server version"**. Its separate session
label update reads owner+0x598, whose response source is +0x18. This corrects the
unresolved response-identity presumption in #211 for this concrete installation.

Acceptance: exact installation/target; actual input stores, comparisons and
consumers; replacement/destruction; supported local role. Static/offline only;
owner+0x90 remains #215's closed diagnostic callable. No framing/codec, ticket,
authentication-design, client/live, upstream or publication work was performed.

Inputs: clean main `b955532c3817414908087b6c0a80faeaeaba58a0`; build 22469132,
version 1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
The map, references and all 29 #215 spans were refreshed. Exact native/data seals,
private output hashes and checks are in the [original evidence delta](../research/evidence/current-registration-response-callback.json).

**J216-1 — installed callable.** Caller `0x146425f20` constructs the third R9
wrapper with vtable `0x1485029e8` and captures the caller at `0x1464261f5`.
Installer `0x146b70af0` passes owner+0xd8 to `0x14056cee0` at
`0x146b70b2f..0x146b70b39`. Its clone/active-pointer store makes destination+0x38
equal owner+0x110. Clone `0x1464733d0` copies the vtable and raw captured pointer;
virtual+0x10 is `0x1464755e0`. Handler `0x146b6f5d1..0x146b6f5e4` loads this
optional target and passes the address of response+0x38.

**J216-2 — concrete receiver.** Built-in creation `0x141043950` constructs the
static game through `0x140fec280`; its initialization `0x14102ee20` calls system
virtual+0x260 → `0x140f11070`, storing the game at system+0xe8. System's environment
is +0x88, published through `0x1472174d0`, so this is environment+0x60.
Callback `0x14647561a..0x146475630` uses that game's +0x28 interface, whose
constructor-installed vtable `0x147fc64f8` has +0x2d0 → `0x146449db0` and
+0x110 → `0x1464667e0`. These interface slots are distinct from owner+0x110 storage.

**J216-3 — consumption and retained input.** `0x146449db0` resolves the fixed
"Server version" key through `0x1402b91a0` in the game's owned hash map at +0x880;
the returned node's +0x30 is the value string. `0x146449e7a..0x146449eb4` compares
the input's counted length and bytes with that value. A changed value is copied
through `0x1402c43b0` at `0x146449ed1`; its existing-buffer and allocate/copy/free
branches own the destination bytes. The response address is borrowed for this
call and is not retained in the map. Equal values return without change output.
Changed values are formatted and sent through `0x146444f50` → `0x14143e010`, the
diagnostic formatter/output path already proved in #215.

Later updates replace the same key's owned value. Game destruction
`0x1410012d0` → `0x14640b860` calls `0x146409b70` on game+0x880. It releases buckets
and calls `0x14640a600`; that loop destroys both strings through
`0x1402ba7c0(node+0x10)` before freeing each 0x50-byte node and the sentinel.

**J216-4 — separate association and callback lifetime.** After the version setter,
the callable reloads captured-caller+0x1000 and invokes owner virtual+0x50 →
`0x146b6cb40`, which deep-copies owner+0x598. That owner's response handler copies
+0x18 into +0x598. The callable rebuilds the getter's first-NUL prefix; an empty
prefix still invokes the next method. On normal construction paths, interface
virtual+0x110 → `0x1464667e0` copies it into optional-object+0x528 when that object
exists, and calls `0x1402bb6b0` with the fixed key `session_id`. Concrete helper
`0x1402c3310` copies into an existing or free context slot when a context exists;
the value is capped at 255 bytes. Full context slots can leave the update unapplied.
The optional object retains the full reconstructed prefix; the two conditional
stores are separate operations. Empty values write an empty value, retaining the key.
These are local string associations; no principal/ticket validation or remote
authentication authority is supplied by the copied values or their labels.

The game owns/replaces/deletes its optional object at +0xa00. Deletion
`0x14641f8e0` → `0x14640f1b0` → `0x14640d4b0` → `0x141649840` releases its +0x528
string. Owner destruction `0x146b6b550..0x146b6b56c`, installer replacement and
source cleanup dispose the closure through virtual+0x20 → `0x14078fa10` and clear
the active pointer. Inline closure storage owns its copy, without retaining the
captured caller. Caller+0x1000 is reloaded after the version setter, so a fixed
owner generation or same-response association is not guaranteed by this code.

Scope: this closes the built-in installation and normal ownership paths. Runtime
provider selection, cache generation, exception paths and callback quiescence
remain unobserved. Instruction checks and targeted counter-review
support the delta; 469 workspace Python cases, three PowerShell suites and isolated
loopback lifecycle checks passed with unchanged inputs and cleanup. Raw working
output stays ignored. Completion covers only #216; #178/#164 and Milestone 1 remain open.
