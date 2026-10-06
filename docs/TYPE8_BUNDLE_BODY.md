# Current type8 bundle BODY codec

Actionable **#239**, under **#177 / workItemId 164**. The original codec implements
the pinned current paired `ReplicatedStateBundle` BODY reader and writer, with
immutable values, explicit bounds and synthetic fixtures. It also composes the
verified creation record reader inverse inside a bounded payload. Current task
status stays in [ROADMAP](ROADMAP.md).

Before discovery, #239 recorded its outcome, acceptance and exclusions: pin source
and dirty inputs, trace actual readers/writers/constructors/consumers, cross-check
instructions, then implement and verify literal bytes, round trips, malformed
inputs, boundaries and suffix isolation. Required workspace validation, task-owned
local commit, tracking readback and claim release close the checkpoint. Runtime
selection, valid creation values, player creation and Milestone 1 stay open.

## Paired layout

Source inference uses owned build `22469132`, image version `1.400.6031.6004151`,
SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e` and
mapping `f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75`.
The mapping's index8 does not prove runtime table activation or incoming selection.
Baseline was clean `d1b3bbd`; its separate README commit is preserved.

Factory table `0x148502a48` virtual `+0x20` selects `0x14644b260`, whose bounded
trampoline reaches BODY writer `0x146ae6db0`. Decoder `0x146b07870` is the paired
factory decoder established by [the recipient join](TYPE8_RECIPIENT_JOIN.md).
No-PDATA refusals, repaired leaf bounds and decompiler warnings remain in the
[source receipt](../research/evidence/current-type8-bundle-body-contract.json).

| Order | Wire field | Value/API domain |
|---|---|---|
| 1 | Strict Boolean sequence presence; if1, compact-u64 sequence | `None` encodes absent; unsigned0..2^64-2 encodes present. Native all-ones sentinel canonicalizes to absent. |
| 2 | Raw byte at message+0x30, then raw byte+0x31 | `field_30`, `field_31`, each0..255; no invented gameplay meanings |
| 3 | Strict Boolean+8, then strict Boolean+9 | `field_08`; +9 derives from `optional_structure is not None` |
| 4, if+9 | Compact-u32 scalar, compact-u32 count, count BEu16 items | Struct base=message+0x38; scalar helper+d0=message+0x108. Raw meanings unproved; at most100 items. |
| 5 | Compact-u32 payload length, then exactly that many bytes | Copied immutable payload0..256000 bytes; no extra payload transformation |

Compact-u32 is the existing current primitive: widths1..5 with first-byte payload
bits7/6/5/4/3 and low-order tail bytes. The compact-u64 pair
`0x140877a90/0x14087b770` extends widths through9, payload bits
7/6/5/4/3/2/1/0/0, with transitions at2^7,2^14,2^21,2^28,2^35,2^42,2^49,2^56.
Decoder aliases/nonminimal widths survive; u32 high bits narrow to32. A prefix
`f8` needs six compact-u64 bytes, while the u32 reader can decode a five-byte alias.

Sequence helpers `0x1461672d0/0x1461acca0` reject presence bytes above1. Present
all-ones is accepted by the reader but the writer emits absent `00` for that value.
Absent decoding skips the destination write; the fresh factory initializes it to
all-ones. The pure value decoder returns `None` independently of native reuse.
Both BODY Boolean bytes likewise reject values above1.

Optional helpers `0x146a68c90/0x146a6ddb0` place the scalar before the count.
Item helpers `0x140876ca0/0x14087a1c0` call current WS2_32 imports `htons`/`ntohs`,
resolved through ordinal9/15 and the local export table. That import contract
supports BEu16 wire conversion; no native call was executed. Absent structure
differs from present scalar0/count0. Default BODY is exactly `000000000000`;
present-empty structure is `0000000001000000`.

## Extent, ownership and safe policy

The input advance helper checks declared length against the current stream end
before passing its saved pointer/count to message+0x110 storage. The fresh factory
sets maximum payload storage to256000; inline capacity is2048 and overflow
migrates to owned heap storage. The helpers copy bytes rather than retaining input
addresses. Message destruction releases heap storage. The synchronous consumer
borrows a view over retained data; it does not extend ownership or prove concurrency.

The native decoder can consume an available over-cap tail, set owner error, and
report success while retaining zero bytes on a fresh object. Reused storage can
retain old data/errors; its cap compares existing length+request. Native allocation
and runtime reachability remain unobserved. The original API rejects over-cap
payloads before copying and returns no partial value on failure. Its diagnostics
do not reproduce native error codes, partial mutations or final drain cursors.
The cap applies to payload bytes: a maximally populated BODY can be256223 bytes.

The tail writer reads count and data from the same selected child, assuming a
stable message. Message+0x988 instead records total consumed BODY bytes. Returning
`(body, consumed)` leaves enclosing suffix bytes outside `body.payload`.

The record consumer receives exactly that retained-payload view. Native unknown
member failure drains its remaining payload, including later records, but excludes
an enclosing BODY suffix on the fresh in-cap path. There is no per-record length
that permits unknown-class skipping. The original composition parser rejects the
whole result without application, drain or input mutation.

## Offline API

Use [current_type8_bundle_body.py](../scripts/current_type8_bundle_body.py):

- `BundleOptionalStructure(field_d0=0, items=())` preserves a raw scalar and ordered
  immutable u16 tuple. It rejects count101 instead of native writer count0 substitution.
- `BundleBody(sequence=None, field_30=0, field_31=0, field_08=False,
  optional_structure=None, payload=b"")` validates immutable explicit values.
- `encode_body(body)` emits only this BODY. `decode_body(data)` returns one decoded
  prefix and its consumed count; it accepts contiguous bytes-like input and copies
  returned payload bytes.
- `encode_creation_payload(records, class_table=table)` concatenates explicit
  [creation records](CREATION_REPLICATION_RECORD.md); their native outer slot/count
  writer remains unjoined. `decode_creation_payload(payload, class_table=table)`
  returns all supported records within this extent or raises a local payload error.

The existing empty activation candidate delegates its BODY to the new default
encoder. Its literal bytes are preserved; this does not add framing support.
No table/index/value is selected from private client state. Fixtures use an explicit
synthetic nil-first UUID table and invented values, not observed player data.

## Verification and remaining work

Seven [original synthetic vectors](../tests/fixtures/replication/current-type8-bundle-original.json)
cover absent/present sequence, raw fields, absent/present-empty structure, BE items,
large sequence and bounded indexed creation payload. Focused tests cover all width
transitions, aliases/sentinel normalization, strict flags, proper small truncations,
count100/101, payload2048/2049 and256000/256001, maximum BODY size, copied inputs,
declared extent/suffix isolation and failed later records. The initial handwritten
maximum-sequence and2047 literals were corrected; their failed receipt is retained.
Independent8probe groups passed; its historical86-case run predates the added
maximumBODY test. Current87BODY/200focused cases and required workspace1135cases/39
modules,threePowerShell suites and synthetic127.0.0.1 lifecycle passed. Listener
closed,childexit0; ten implementation inputs unchanged. Results are recorded in the
[validation receipt](../research/evidence/current-type8-bundle-body-validation.json).

This BODY pair closes the declared payload extent around K303–K307. It does not
close the native outer record writer, remaining #210 physical receive/Carrier,
ACK/resend, historical860, authority or runtime selection gates. Actual member
class/table activation, valid AssetId/Gde values, construction/designation and
#212/#232/#177 aggregate acceptance remain unproved. Continue the nearest eligible
offline dependency after this checkpoint; child completion does not stop work.
