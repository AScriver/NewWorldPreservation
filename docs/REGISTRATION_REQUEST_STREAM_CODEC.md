# Offline selected V3 sender stream encoder — #230

October6,2026; workItemId164 / parent178. The original pure encoder joins the
verified V3 BODY to the actual selected sender layout proved in
[#229](REGISTRATION_IDENTIFIER_PLACEMENT.md) and [#226](REGISTRATION_STREAM_FRAMING.md).
Its output is an empty ordinary physical stream, before lower backend/Carrier
emission. No client or native client code was executed.

Input clean main `551c9f253092de40bfd30b2ed4db2d2d9fb24372`, build22469132,
image SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
[Original receipt](../research/evidence/current-registration-request-stream-validation.json)
pins source rehash, implementation/fixture/test hashes, executed checks and limits.

## API and exact output — J230-1

`encode_registration_request_stream(record, *, type_index, field_04=None, field_0c=None)`
in [the original module](../scripts/current_registration_request_stream.py) returns
immutable bytes. `record` must be the existing
[RegistrationRequestBody](REGISTRATION_REQUEST_BODY_CODEC.md); the BODY module is
reused unchanged. Fields are named by wrapper offset and remain semantically opaque.

| Input / byte segment | Rule |
|---|---|
| type_index | Required true integer0..0xffffffff, never inferred from map19 |
| field_04 / field_0c | None or exactly eight immutable bytes; second requires first |
| Physical header | IEEE CRC32 and actual payload count, both BE32 |
| Physical bytes8..23 | Nil outer UUID16 |
| Wrapper | Flags0/1/3; optionalraw8 bit0 thenbit1; presence1 |
| Type selector | Current compactuint32 index; index0 adds fixed literal-order V3UUID16 |
| Remaining bytes | Complete existing V3 BODY |

Fixed V3UUID is `0b826b3389f549e0b8cbfe4433427778`. It belongs to the inner
fallback selector, not the physical outer16 slot. Supplying nonzero index19 is
an explicit synthetic/caller assumption, not proof of current cache/index19.
Opaque fields encode supplied bytes; native ambient/TLS values are not reconstructed.

## Safe bounded domain — J230-2

Only fresh ordinary wrapper flags0/1/3 are admitted; source-supported bit2 clear
and second-only flag2 outside that stable domain lead to no generic context API.
Invalid record/index/opaque field inputs fail before BODY encoding. CRC covers
every payload byte, including nil16, prefix/type bytes and BODY, with folding off.
Count is the complete payload length; values above0xffffffff are rejected instead
of reproducing native narrowing. Native huge allocation/overflow/fault behavior,
nonempty high-water streams, recycling and mutable native storage are unmodeled.

The reused safe BODY encoder fully encodes or raises. This API returns no partial
stream after helper failure, while the native writer ignores its body Boolean;
no universal native success/atomicity claim follows. No decoder is added because
the actual native receive inverse remains a separate unproved boundary.

## Original checks and remaining limits — J230-3/J230-4

The [34 original vectors](../tests/fixtures/registration/current-request-stream-original.json)
use literal compact-width bytes, selected flags, original neutral/rich BODY bytes
and a separate reflected bitwise CRC calculation. Tests verify exact output,
outer/inner separation, raw8 order, BODY offsets, checksum/count coverage, required
index and rejection boundaries. The reported oversized-body test uses a synthetic
length only; it performs no huge allocation. Independent finite source-model checks
and the reviewed workspace inventory are recorded in the receipt.

No observed wire bytes, current runtime index/metadata, authentication, valid
world/player construction, lower datagram emission, #212 readiness or two-client
acceptance follows. Parent178/164 and Milestone1 stay open.
