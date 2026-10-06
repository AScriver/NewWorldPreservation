# Current V3 field+0xc0 codec — #222

October 6, 2026; workItemId164 / parent178. The selected request's +0xc0
aggregate now joins a complete wire schema: fifteen counted byte strings, five
BE32 bit fields, one raw byte and a presence-first optional boolean. Ordinary
fresh construction and returned-failure string cleanup are also joined.

Clean input main `45f2e47ea9992a616d5e653a41d9930f0597de66`, owned build22469132,
version1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
[Original receipt](../research/evidence/current-registration-request-c0-codec.json)
pins image/map/references, exact source ranges/windows, dirty report identity and
executed checks. This is instruction-supported source inference. No native client
code ran; field meanings, authentication significance and runtime acceptance are
unknown. [#221's selected sequence](REGISTRATION_REQUEST_COLLECTION_CODEC.md)
and #215–#220 remain scoped evidence.

## Complete paired layout — J222-1

Actual aggregate calls `0x1407d5509` and `0x1407d96a6` select c0 writer
`0x1407d5f30` and reader `0x1407db350`. The concrete writer chain continues
`0x1407d4920` → `0x1407d4b50` → `0x1407d42c0` → tail `0x1407d46a0`
→ tail `0x1407d4490`. Reader `0x1407db350` → `0x1407d8840` →
`0x1407d8a10` success-gates every item. Offsets below are relative to c0,
not the enclosing message.

| Wire order | Source/destination offsets | Encoding |
|---|---|---|
| 1–5 | +0,+0x20,+0x40,+0x60,+0x80 | Five raw byte strings |
| 6 | +0xa0 | BE32 bits |
| 7–11 | +0xa8,+0xc8,+0xe8,+0x108,+0x128 | Five raw byte strings |
| 12–14 | +0x148,+0x14c,+0x150 | Three BE32 bit fields |
| 15 | +0x158 | Raw byte string |
| 16 | +0x178 | BE32 bits |
| 17 | +0x17c | One raw byte, any value 0..255 |
| 18 | +0x180 | Raw byte string |
| 19 | +0x1a1, then +0x1a0 if present | Presence byte, conditional boolean value |
| 20–22 | +0x1a8,+0x1c8,+0x1e8 | Three raw byte strings |

The writer normalizes optional presence and value to 0/1; absent presence omits
the value. The reader requires 0/1 for both. The raw byte at+0x17c has no boolean
range check. These are structural facts, without identity/policy interpretation.

All fifteen strings use the [joined compact codec](REGISTRATION_RESPONSE_BODY_CODEC.md#compact-counts--b218-3)
and byte lengths 0..`0x2ffff`. Writer oversize emits zero and omits the payload;
reader length at least `0x30000` fails with code1. NUL bytes are payload; storage
terminators are excluded. Canonical writer output and accepted nonminimal/wrapped
reader prefixes retain their different rules. Five scalar fields use the carried
BE32 helpers, with signedness/semantic interpretation unspecified.

Partial decompilation warnings at the aggregate and writer tails, plus an
unrecovered indirect tail, are retained despite `completed:true`. Exact
instructions and Windows x64 argument bindings support the paired order.

## Incremental read state — J222-2

Every string reaches `0x1407fc670`: it copies/moves the announced bytes before
the final payload extent check. On an ordinary returned short-payload failure,
the destination may already change while the cursor stays after its prefix.
Code1 covers its prefix/length/extent failures. Native overread/fault/exception
outcomes were not executed. A later safe offline decoder must prevalidate extent
and document that stronger behavior.

Short BE32 input gives code2 without consuming four bytes or assigning that
field. Missing raw byte+0x17c gives code1 without consuming/assigning it.
Earlier successful items and cursor changes remain; none of these readers rolls
back the object or stream. A successful c0 helper defines result+1, without
assigning a meaningful error-code byte.

| Optional input | Code / partial state |
|---|---|
| Missing presence | 3; optional pair unchanged |
| Presence above 1 | 4; invalid byte consumed, pair unchanged |
| Presence 0 | +0x1a1 becomes0; +0x1a0 remains unchanged and no value byte is read |
| Presence 1, missing value | 3; +0x1a1 already1, prior value unchanged, no value consumed |
| Presence 1, value above 1 | 4; invalid value consumed, presence remains1, prior value unchanged |
| Presence 1, value 0/1 | Value stored at+0x1a0; later failure preserves both stores |

The presence commit is at `0x1407d8aee`, before value read `0x1407d8b0f`.
Fresh construction supplies both bytes 0. A reused helper destination can retain
an inactive prior value when presence0; that is distinct from the actual fresh
placement caller.

## Ordinary ownership and limits — J222-3/J222-4

Placement constructor `0x1407e37d0` directly calls c0 entry `0x1407e2990`.
Its bounded straight-line entry-through-RET window initializes fifteen empty
inline strings (size 0/capacity 15), five scalar/default fields, raw byte and
optional pair 0/0, without calls or heap allocation. The refused PDATA selection
and incomplete 256-byte window are retained; only the observed 457-byte window
through RET `0x1407e2b58` supports the constructor claim.

Destructor `0x1407e68f0` releases the fifteen owned strings in reverse order,
then resets each string. It does not restore scalar/optional/cursor state.
Selected top failure calls +0x38 with flag0 (`0x1407cff40`), reaching c0
destruction at `0x1407cff6e` on the normal path; placement allocation stays
caller-owned. Success leaves the object alive for its caller. Corrupted large
allocation metadata can enter invalid-parameter/INT3 handling; OOM, native faults,
exceptions, concurrency and later successful-caller disposal remain unproved.

The receipt records targeted counter-review and required offline workspace checks.
This closes c0's schema prerequisite. Separate +0x2c8/+0x3e0 schemas, full request
body/fixture readiness, current discriminator/framing inverse, authoritative field
meanings and world-entry prerequisites remain open. #212 and Milestone1 remain open.
