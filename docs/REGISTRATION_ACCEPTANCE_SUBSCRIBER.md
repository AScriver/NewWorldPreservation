# Conditional registration acceptance subscriber — #217

October 6, 2026; workItemId: 164 / parent #178. The concrete current
`EOSSystemComponent` subscriber's virtual+0x48 **constructs an empty result
string**, without reading the component or calling a validator. Its virtual+0x50
reports the inverse of a local disable/failure byte. This closes the selected
subscriber chain left by #211 and corrects its presumed authentication role.

Inputs: clean main `db3dbf22997fc16da00ca722c8d3e82189b57754`, build 22469132,
version 1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
Exact native/data spans, refreshed map/reference/tool identities and executed
checks are in the [original receipt](../research/evidence/current-registration-acceptance-subscriber.json).
All behavior below is instruction-supported static inference; no client ran.
#215's diagnostic owner+0x90 and #216's server-version owner+0x110 findings are
carried forward without reinvestigation.

## Concrete receiver and registration — J217-1

Constructor `0x1444f42a0` installs primary vtable `0x14834e5a0` and subscriber
vtable `0x14834e6b0` at component+0xa8. The subscriber's type-method adjustor
`0x1444f99b8` subtracts 0xa8 and reaches `0x1444f0f00`, which returns the
`EOSSystemComponent` name. This joins the type through a method, beyond adjacent
data. Factory `0x1444f0cc0` allocates 0x390 bytes and calls the constructor;
`0x14474c6b0` provides another construction path.

Primary vtable+0x58 selects `0x1444f5700`. After its local gates, it publishes
exactly component+0xa8 into the context+0x20 registration node, stores the raw
interface pointer at component+0xb0, and retains the node handle at component+0xb8.
Getter `0x1444f77d0` selects a context through a provider lookup. Its storage
scope, runtime instance, registration order and framework activation ordering
remain unobserved; a thread-local context is not established.

## Complete result producer — J217-2/J217-4

Handler `0x146b6f190` constructs the zero-adjustment descriptor for
`0x140571494` and invokes `0x146b679f0`. That thunk tailcalls the stored
receiver's virtual+0x48. For this concrete interface the target is
`0x1402bfe50`, whose complete 34-byte PDATA body:

- zeros the output's first 16 bytes and length at +0x10;
- sets capacity at +0x18 to 15, writes NUL and returns the output pointer;
- reads no `this`, response, principal, ticket or captured state and calls nothing.

The output is an empty inline counted string; it allocates or borrows no buffer.
The dispatcher transfers the complete 32-byte representation into the caller's
result, freeing an earlier heap representation when necessary. Successive
subscribers can overwrite earlier results; this is the concrete effect if this
subscriber is the final completed callback, not proof of its runtime presence.

The branch remains conditional. Response+0x5b==0 bypasses it. Otherwise
owner+0x768==0 reports error 13 and normally continues to dispatch. Error helper
`0x146b6c500` can call owner+0x5f8's listener or queue the error in owner+0x620/+0x628;
the caller's zero R8B skips its explicit throwing/disconnect block. Those error
effects are not erased by an empty result. The handler starts with a nonempty
result (length 18), tests its final length at `0x146b6f3ad`, reports error 8 for
a nonempty result, and reaches its continuation at `0x146b6f447` for an empty one.
This local continuation does not establish durable acceptance, authenticated
identity or later error-consumer behavior.

## owner+0x768 producer and meaning — J217-3

Owner constructor `0x146b69e52` initializes this byte to zero. The selected V3
builder passes its address at `0x146b6e3fc..0x146b6e407` to `0x146b67c70`, with
descriptor `0x14029e0fc` tailcalling subscriber virtual+0x50. The bus writes each
returned AL to that destination. No subscriber leaves the previous value intact;
later subscribers can overwrite earlier values.

For the concrete EOS interface, +0x50 is `0x1444f77c0`: its complete 11-byte leaf
returns interface+0x88==0, exactly component+0x130==0. The constructor initializes
component+0x130 to zero. Registration sets it to one and returns for global
disable predicates at +0x244/+0x245/+0x246 or failure of
`0x1444f79e0(component+0x138)`. Its successful path does not itself clear an
earlier one. The global predicates' product meanings are not inferred from offsets.

That helper creates a loader for `EasyAntiCheat\EOSSDK-Win64-Shipping.dll`, loads
it and resolves 39 exports into its local state. The loader's concrete +0x20
method `0x141407920` reaches `GetProcAddress`; its load method `0x141422e80`
reaches `GetModuleHandleW` and `LoadLibraryW`. The wrapper `0x14141dae0` also has
optional module-initialization callbacks. Export lookup includes
`EOS_AntiCheatClient_BeginSession`, but this helper does not invoke the retrieved
EOS API pointers. Its module/callback/session effects were not executed.
Thus owner+0x768 can contain this subscriber's inverse local disable/failure
state, with retention and overwrite limits; it is not an authenticated or fresh
successful-session predicate.

## Ownership and verification — J217-5

The bus retains registration-node storage, not a reference to the component.
Disconnect `0x1444f5940` retires the interface pointer, clears its association,
releases the node reference and clears context+0x20 on the final reference.
Normal shutdown `0x1444f6610` calls it when component+0x130==0; full destructor
`0x1444f4970` also disconnects after resetting the subscriber base table.
The deleting-destructor path owns disposal of the 0x390-byte component allocation.
Dispatch bookkeeping exists, but full in-flight quiescence, exception ordering
and cross-thread serialization are not proved by these selected paths.

Fresh exact instruction/data checks and bounded sparse Ghidra queries passed.
Targeted adversarial checks preserved the same-object, output ABI, inverse-byte
and ownership joins, with the error-side-effect and context-scope qualifications
above. The offline workspace profile passed 469 Python cases, three PowerShell
suites and the owned loopback CLI lifecycle. Those checks prove tooling/report
integrity, not client acceptance or gameplay. #178/#164, #212's separate codec/
construction/framing gates and Milestone 1 remain open.
