# Current V3 field+0x3e0 codec — #224

October 6, 2026; workItemId 164 / parent 178. The selected request's final
nested field contains two tagged objects. Each raw tag chooses fixed16 bytes
or a counted raw string. Its paired schema, partial read state, formatted text
ownership, construction defaults and ordinary failure disposal are now joined.

Clean input main `5885527da7ea0865814065d37168125520c5ae9c`, owned build 22469132,
version 1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
[Original receipt](../research/evidence/current-registration-request-3e0-codec.json)
pins current image/map/references, source ranges, report identity and checks.
This is instruction-supported source inference; no native client code ran.
[#221's selected sequence](REGISTRATION_REQUEST_COLLECTION_CODEC.md),
[#222's c0 schema](REGISTRATION_REQUEST_C0_CODEC.md) and
[#223's 2c8 schema](REGISTRATION_REQUEST_2C8_CODEC.md) retain their scopes.

## Selected caller and wire sequence — J224-1

Writer `0x1407ce860` → `0x1407d54a0` → `0x1407d3f70` at `0x1407d562e`
supplies actual message+0x3e0 and +0x460. Reader `0x1407ce8e0` →
`0x1407d9620` → `0x1407d8250` at `0x1407d97cc` supplies the same fields.
Exact stack/register rebasing joins both callers. Each nested object occupies
0x40 bytes; the second starts at message+0x420. Initialized size is not wire size.

| Wire order | Memory relative to each object | Encoding |
|---|---|---|
| 1 | +0x30 | Unmodified raw tag byte |
| 2, tag bit0 set | +0x20 | Exactly 16 raw bytes |
| 2, tag bit0 clear | +0 | Compact uint32 byte count followed by raw string |

The pair is emitted/read in order, then the existing strict +0x460 boolean.
Writer `d3f70` calls `0x140876fa0` at `d3f95` and `d3fab`, then writes the
normalized boolean. These calls have no success gates; progression assumes
normal returns. Reader `d8250` calls `0x14087aab0` at `d8283` and `d82b2`,
checks each success, then reads +0x460. Missing final byte is code3/no advance;
invalid >1 is code4/consumed; valid 0/1 is stored. Full success sets result+1,
without establishing a meaningful error-code byte.

## Tag branches and partial reads — J224-2 / J224-3

All 256 tag values are preserved; no tag<=1 validation or normalization occurs.
Bit0 alone chooses payload. Bits1..3 affect derived text in the raw branch;
bits4..7 have no formatter effect. No enumeration, UUID or authentication
meaning is inferred from the byte or text shape.

Even writer `fa0` jumps at `0x140877000` to `0x1407d60d0`; even reader
`aab0` calls `0x1407da950` at `0x14087abed`, adapting to `0x1407fc670`.
The string bound is 0..0x2ffff. Oversized native writers emit zero and omit
payload; readers reject >=0x30000 with code1. Carried compact nonminimal
prefixes and uint32 wrapping remain accepted. Even reads update tag/string
and leave inactive raw16 unchanged. Embedded NUL bytes remain string data.

| Ordinary failure | Code | Cursor/output effect |
|---|---|---|
| Missing tag | 2 | No advance; tag/payload unchanged |
| Short odd raw16 | 1 | Tag consumed/stored; payload not copied or advanced |
| Even string failure | 1 | Tag committed; carried compact/string effects persist |

Odd reader stores tag at `0x14087aadc`, checks all 16 payload bytes, copies at
`0x14087ab01`/`ab04` and advances at `ab09`. The extent check gives no partial
payload copy on ordinary bounds failure. Hardware atomicity, aliases, faults
and concurrent reads are unproved. Even `fc670` copies/moves before its final
extent check; ordinary short payload can alter string output while leaving
cursor after the prefix. Native overreads, faults, OOM and exceptions were not
executed. The helper has no rollback; earlier fields/cursor remain committed.

## Formatted text and ownership — J224-4

Odd reader calls formatter `0x14147f850` at `0x14087ab4e` with source+0x20,
a stack destination and capacity39. It processes bytes0..15 in order, high
nibble then low, using table `0x147feded8`. Tag bit1 enables braces, bit2
hyphens before byte indices4/6/8/10, and bit3 selects imported CRT toupper
rather than tolower. The required count including NUL is
`33 + 2*braces + 4*hyphens`; masked controls make its maximum39 fit the call.
The formatter terminates the output, allocates nothing and changes no source
or tag. Ordinary CRT behavior is inferred; runtime DLL/locale was not checked.

String copy at `ab84` and move at `ab91` transfer 32..38 formatted characters
into the object's owned string, independently of embedded raw16 and the stack
buffer. Move clears the temporary owner. Raw/text representations are not
synchronized on the even branch. Successful caller retention/disposal is unjoined.

Constructor `0x1407e37d0` stores two empty SSO strings (size0/capacity15), zero
raw16 and tag0 at `e39ee..e3a7b`; final+0x460 defaults false. These values
establish construction, not valid identity or gameplay input. Ordinary returned
body failure invokes virtual+0x38 with flag0 → `0x1407cff40` → `0x1407e6810`
at `cff56`. It destroys second string then first, freeing valid heap storage
for capacity>15. Large-allocation handling uses **capacity+1 >= 0x1000**.
String metadata resets; raw/tag/cursor do not. Flag0 retains caller placement
storage. Corrupt allocation metadata reaches invalid-parameter/INT3; cleanup,
exception/unwind and allocation-failure guarantees remain unknown.

The receipt separates instruction seals, pure countermodels and required
workspace checks. Folded/indirect decompiler warnings and corrected writer-gate/
capacity interpretations are retained. This closes the selected +0x3e0 schema
prerequisite. Full body implementation/fixtures, discriminator/framing, actual
input authority/field semantics, #212, live acceptance and Milestone1 remain open.
