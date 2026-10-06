# Current V3 serializer selection and interface role — #220

October6,2026; workItemId164 / parent178. The previously opaque interface236
is now joined to a concrete reflected **REPClient default receiver**. The selected
outgoing V3 body uses a separate descriptor-owned writer, **0x1407ce860**. This
closes the selection/role/ordinary ownership boundary; nested request encodings
remain a separate source prerequisite. No client or native client code ran.

Clean input main `6094d8a294727ec20a41fb225b4b671c7c044afd`, owned build22469132,
version1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
[Original receipt](../research/evidence/current-registration-request-serializer.json)
pins refreshed image/map/references, exact code/data seals and actual checks.
#215–#219 are carried forward without new identity/authentication claims.

## Concrete default dispatch — J220-1/J220-2

Descriptor factory `0x1407f1870` binds the name REPClient and UUID
`532e765a-3393-4a50-9010-b73c627512b2` (owned map236). Serializer
`0x147f45570` +0x28→`0x1407ca770` placement-constructs `0x1407e30d0`, installing
primary table `0x147f47a60` and secondary query table `0x147f47a98`.

The default primary +0x30→`0x140294860` is an immediate no-op return.
Its `RET imm16 0` **does not assign a numeric return value**. The query path
+0x30→`0x1407c4ad4`→`0x1407f93c0` applies the vtordisp adjustment, compares both
UUID qwords and returns the complete-object pointer or null, without AddRef.

V3 message +0x50→`0x1407cfd10` returns false for a null supplied receiver or failed
query. Otherwise it passes scalar+8, five field pointers (+0x10,+0xa0,+0xc0,+0x2c8,
+0x3e0) and byte+0x460 to the returned interface's +0x30, then sets **AL=1 after
normal return**, independently of the callback result. This is a dispatch result.
It cannot establish a write or acceptance. The reflected default construction is
concrete; which implementation was supplied at runtime remains unobserved.

## Selected body writer — J220-3

Generic writer `0x146167110` obtains the message's descriptor at `0x146167240`,
calls type-emitter `0x1461673b0` at `0x14616724c`, then calls descriptor+0x48's
serializer+0x20 at **0x146167262**, after the emitter returns. V3 metadata accessor
`0x1407cfca0` jumps to descriptor factory `0x1407f2c50`; that factory installs
serializer table `0x147f47278`, whose +0x20 selects `0x1407ce860`.

The concrete writer calls the already joined BE32 helper `0x140876cd0` for field+8,
then calls `0x1407d54a0` with **six pointers**, including +0x460. This differs from
the interface callback's final byte-by-value argument. It establishes the direct
writer/helper boundary, without supplying the nested helper's complete field
sequence, encoding, bounds or failure contract. Constructor string/aggregate
copies are object-layout evidence. They are not wire encodings. Map19/V3 and
map236/REPClient remain distinct; no historical860-byte discriminator follows.

## Ordinary ownership and limits — J220-4

The descriptor owns its 16-byte serializer and deletes a replaced value; its
deleting destructor frees that allocation with flag1. The REPClient factory owns
constructed-state rollback: failure invokes destruction with flag0, leaving
caller-owned placement storage allocated; flag1 also frees the 0x740-byte object.
The concrete query result borrows the receiver's lifetime.

The inspected top writer/interface methods contain no direct field retain/capture.
Retention in nested helper `0x1407d54a0`, stream methods, arbitrary receivers and
callback manager `0x140799ec0` remains unjoined. Exception/final descriptor cleanup
and global lifetime safety are not established. Targeted counter-review preserved
these limits. Current decoder `0x1407ce8e0` and the nested aggregate helper are the
next bounded body-codec targets; no request fixture or implementation is supplied.
#212, authoritative ticket/peer semantics, Carrier/framing and Milestone1 remain open.
