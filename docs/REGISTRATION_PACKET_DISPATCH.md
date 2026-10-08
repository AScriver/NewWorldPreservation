# Conditional post-parser dispatch

Actionables #278, under #277/root164, classifies the selected fallback source
path. [K407–K409 receipt](../research/evidence/current-registration-packet-dispatch.json)
binds the original private reports, instruction seals and critical review.
The larger incoming-payload-to-registration join remains **Partial**.

## Receiver construction (K407)

The cached caller dynamically loads owner +0x10, that object's current vtable
and slot +0x48 after record parsing. It passes state and an address eight bytes
inside the incoming aggregate. A cached constructor stores a supplied interface
from parameters +8 at owner +0x10. If it is zero, the constructor requests
**0x60 (96 decimal) bytes**, installs the selected fallback table and stores the
result. A zero allocation can leave owner +0x10 zero.

That table's +0x48 slot provides a concrete candidate. Construction stores and
table membership do not prove the object's identity or vtable at the later
call. Opaque calls, lifetime, aliasing and the supplied-interface alternative
remain limits. The constructor also copies a configured DWORD into fallback
+0x58, without Boolean normalization.

## Captured connected flow (K408–K409)

The function-slice helper rejected this entry because it has no evidenced
PDATA/unwind owner. The refusal was retained; no guessed function extent or
forced leaf decompilation followed. Two explicitly bounded executable windows,
32 and 64 bytes, supplied sixteen connected instructions through a return.
Their requested lengths total 96 bytes and overlap by three. Neighboring code
was not decoded, and a whole function extent remains unestablished.

Under the conditional caller binding, the selected flow:

1. Reads a WORD at incoming aggregate +0x18, adds it to a DWORD through the
   pointer at state +0, and increments another DWORD.
2. Reads a WORD at aggregate +0x1a. If nonzero, it adds that value to another
   DWORD, increments another DWORD and sets a byte to one.
3. Tests the receiver's configured DWORD +0x58. Any nonzero value admits a
   modular DWORD decrement; only a zero result clears another byte.
4. Returns with the residual zero-extended second WORD in RAX. Its declared
   return type and semantic meaning remain unknown; the caller does not use
   that result before preparing aggregate cleanup.

The first writes precede the second read. With overlapping storage, that read
need not equal the entry-time aggregate value. The state pointer is a register
snapshot; physical validity, lifetime and nonaliasing are not established.
Field names and protocol meanings remain unknown. These are sequential scalar
effects, rather than an atomic packet-acceptance result.

The captured normal return paths contain no call, payload traversal or bulk
copy. This rules out payload dispatch on this selected flow. It says nothing
about another supplied interface, exceptions or actual runtime dispatch. The
next useful source target is a consumer of the specific per-channel receive
queue written after the parser's successful payload read.

## Validation and limits

Exact image/window/constructor/table seals and targeted critical review support
this conditional classification. The new receipt's bindings, 36 affected
catalog checks and preflight are checked separately; unchanged 1,960-case
workspace support requires actual selected-input reconciliation. No codec or
server change follows from these scalar effects.

Seven known full image identity passes include failed attempts. Zero completed
PDATA roots and zero Ghidra imports do not mean zero executable bytes inspected.
The first failed prefix script was edited before its original hash was saved;
the missing original bytes and failure are disclosed. Other original refusals
and corrections are preserved. No native runtime resources were acquired.
Physical Carrier/compact-callback provenance, correct response values,
authentication, playable world and Milestone 1 remain unproved.
