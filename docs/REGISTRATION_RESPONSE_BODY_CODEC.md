# Current registration response body codec — #218

October 6, 2026; workItemId: 164 / parent #178. The selected current response
body codec is now joined to **concrete scalar, compact-length, byte-string and
boolean readers**, their bounds/status behavior and result ownership. This closes
the response-body encoding gap left by #210/#211. It supplies a body contract for
an offline codec; actual Carrier placement and the sender-envelope inverse remain
separate. No client or native client code was executed.

Inputs: clean main `2e032d6cfc1d69c02e6623f17e9ed0f330085fb1`, build22469132,
version1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
Exact current code/data spans, map/reference/system-export identities and executed
checks: [original receipt](../research/evidence/current-registration-response-body-codec.json).
#215/#216/#217 are carried forward; their local metadata/empty-result roles do not
establish authenticated identity.

## Selected body and field order — B218-1/B218-2

Descriptor `0x1407f2e80` owns serializer `0x147f46910` at descriptor+0x48.
Its +0x10 allocates a 0x60-byte result, +0x20 selects writer `0x1407cceb0`,
+0x28 selects decoder `0x1407cd040`, and +0x18 frees the allocation. The decoder
constructs message vtable `0x147f46db8` and performs these reads in order:

| Native field | Body encoding | Concrete read path |
|---|---|---|
| +0x08 | Four big-endian bytes, 32-bit bit pattern | `0x14087a220` |
| +0x10 | Eight big-endian bytes, 64-bit bit pattern | `0x1461acd90` → `0x14087ad90` |
| +0x18 | Compact uint32 byte count, then exactly that many raw bytes | `0x1407fc670` |
| +0x38 | Same counted byte-string encoding | `0x1407fc670` |
| +0x58..+0x5b | Four separate one-byte values, each 0 or 1 | `0x1407da5e0` |

Reader converters `0x146167950`/`0x1461679c0` reach the client's WS2_32 ordinal14
import; the refreshed system DLL maps it to `ntohl` and a complete byte-swap leaf.
The 64-bit helper swaps both halves and their positions. The +0x10 wrapper adds
no scale or sign conversion. Complementary writer helpers use ordinal8/`htonl`
with the same byte-swap body. These are encoding bit patterns, independent of
status/clock application semantics. The byte strings preserve counted bytes,
including embedded NUL; their native destination has an additional NUL terminator.

The writer emits the same order, normalizes the four booleans to 0/1, and emits
a zero string length instead of content when an input string exceeds 0x2ffff bytes.
The reader rejects declared string counts >=0x30000. The minimal canonical body
is 18 bytes; message type, wrapper and outer framing are outside this body.

## Compact counts — B218-3

Writer `0x140877970` and reader `0x14087b5c0` use a prefix-width format. Each
following byte contributes eight bits, least-significant group first:

| First-byte range | Total bytes | First payload bits | Canonical writer values |
|---|---:|---:|---|
| 00..7f | 1 | 7 | <0x80 |
| 80..bf | 2 | 6 | <0x4000 |
| c0..df | 3 | 5 | <0x200000 |
| e0..ef | 4 | 4 | <0x10000000 |
| f0..ff | 5 | 3 | Remaining uint32 values; writer first byte is f0..f7 |

The reader accepts wider-than-needed encodings, f8..ff aliases and high final-byte
bits that wrap away at the uint32 destination. It checks neither continuation
bits nor canonical width. For example, `80 00` reads as zero; `83 02` reads as131
and `83 01` as67. A missing first byte consumes nothing. A truncated tail consumes
the first byte but none of the incomplete tail.

## Bounds, status and cleanup — B218-4

The reader is a borrowed 24-byte `{base, end, cursor}` view, constructed by
`0x140870be0`, with direct helpers and no vtable or sticky status. Raw read
`0x140878610` and advance `0x140879590` check cursor+count<=end and advance only
on success. The top decoder stops at the first failing field; earlier reads and
boolean stores are not rolled back.

| Failing condition | Helper error code |
|---|---:|
| Incomplete compact count, count >=0x30000, or insufficient string payload | 1 |
| Short 32-bit or 64-bit field | 2 |
| Short boolean byte | 3 |
| Boolean byte >=2 | 4 |

Result storage has a separate success byte. **The error-code byte is meaningful
only on failure**; successful helpers can leave an earlier byte unchanged.
An invalid boolean byte is consumed before its code4 failure.

The native string helper obtains the current pointer, constructs and move-assigns
the counted string, then tests/advances its payload extent. That ordering performs
the copy before the final extent check. Failure leaves prefix bytes consumed and
the payload cursor unchanged. On an ordinary failed return it cleans the result through
message+0x38 → `0x1407cdcd0`, which releases +0x38 then +0x18 heap storage and
resets the strings; the generic wrapper then frees the result allocation. An
offline codec must check the full slice before copying and identify that as
stronger bounds behavior. No native malformed-input execution was performed.
Fault or exception cleanup after the native copy remains untested.

## Record and message ownership — B218-5

The selected frame parser `0x146ae44f0` directly calls the same compact reader
at `0x146ae453c` on a copied view. Only a successful length-prefix parse commits
its consumed count to the parent. After the full declared record is available,
it creates a local body view, advances the parent through that complete record
**before** the synchronous callback, retains backing storage across the callback,
then resets its framing state regardless of body success. Thus incomplete outer
prefixes leave the parent unchanged, and a body failure cannot roll back its
record. No exact-body-exhaustion gate is shown in this selected callback chain.

On success the generic wrapper transfers a separate shared native-message pair;
the response handler runs downstream and the local message pair is released.
Buffer ownership, native-message ownership, field parsing and application
acceptance are separate. This joins the selected outer reader's algorithm and
cursor boundary, without reconciling Carrier placement or the sender's reserved
header/descriptor representation.

Exact source checks, sparse Ghidra and targeted counter-review passed. Two
restricted source-instruction simulations independently checked writer/prefix
equations; these were simulations, not native execution. The original receipt
records focused/offline validation separately. #212's fresh construction/member/
framing gates, #178/#164 and Milestone1 remain open.
