# Offline current V3 registration request body codec — #225

Later offline implementation: [#228's optional lookup-text helper](REGISTRATION_LOOKUP_TEXT_CODEC.md)
converts the #227 proved ASCII domain into this API's active `TaggedField`.
Its first-NUL and permissive parser rules are separate from general BODY raw strings.

Later source closure: [#227's setup input producer](REGISTRATION_SETUP_INPUTS.md)
joins the actual persona/character lookup caller, registered string provider,
local text/raw/tag conversion and request copies. Current values, authentication
authority and other setup input producers remain unproved; earlier receipts stay
historical.

October 6, 2026; workItemId164 / parent178. The selected V3 request BODY now
has an original pure Python encoder/decoder and synthetic byte fixtures. The
implementation follows the current descriptor/caller and paired nested schemas
closed by #220–#224. Fields retain neutral offsets and unsigned bit patterns;
no principal, credential, authentication or gameplay meaning is assigned.

Clean input main `4b724f3228d2c77420cd00b260e5ccafaa6b74d8`, owned build22469132,
version1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
[Validation receipt](../research/evidence/current-registration-request-body-codec-validation.json)
pins source contracts, implementation/report identity and executed offline checks.
All163 carried code spans and34 windows were rehashed against this image before
implementation. Historical shared-document drift is retained separately.

## API and selected sequence

[Original module](../scripts/current_registration_request_body.py) exposes
`RegistrationRequestBody(field_08, field_10, field_a0, field_c0, field_2c8,
field_3e0, field_420, field_460)`, with frozen `FieldC0`, `Field2C8` and
`TaggedField` values. Nested members use offsets relative to their aggregate.
`FieldC0.field_1a0` is None when absent or a strict boolean when present.
`TaggedField.field_30` stores the raw byte; even tags use only `field_00` bytes,
odd tags only the exact16-byte `field_20`. `encode_body(record)` emits bytes;
`decode_body(data)` returns `(record, consumed)`. `DecodeError.code` and `.cursor`
describe failures. Mutable input buffers are copied into owned immutable values.

The wire sequence is BE32 field+8, collection+0x10, raw string+0xa0,
[c0](REGISTRATION_REQUEST_C0_CODEC.md), [2c8](REGISTRATION_REQUEST_2C8_CODEC.md),
[two tagged objects](REGISTRATION_REQUEST_3E0_CODEC.md) at+0x3e0/+0x420,
then strict boolean+0x460. The [collection contract](REGISTRATION_REQUEST_COLLECTION_CODEC.md)
and [selected descriptor](REGISTRATION_REQUEST_SERIALIZER.md) establish the callers.
This API consumes/emits only that body; no type, record-length prefix or Carrier
wrapper is added. Trailing bytes are accounted for through the consumed count.

Collection values use unique key/value pairs for encoding. Decoding consumes
every wire pair, retaining the first value for duplicate BE32 keys. Its stable
first-appearance presentation is an offline choice, not native hash-list order.
Tagged values contain the raw tag and active wire payload only: odd bit0 means
16 bytes; even bit0 means a counted raw string. All tag bits are preserved.
Derived formatted text, inactive binary bytes and native allocation state are
outside the body representation. Optional boolean absence omits its value byte;
presence precedes value on wire.

## Bounds and ordinary failures

Strings are owned raw bytes, including embedded NUL, bounded at0x2ffff; collection
count is bounded at0x02000000. The encoder rejects oversized values rather than
silently substituting the native writer's zero count/empty string. Its counts
are canonical; the reader accepts nonminimal widths, f8..ff aliases and uint32
wrapping. Incomplete compact tails consume the first tag byte only.

Failures report the helper-specific code and consumed body cursor. BE32 short2
does not advance; missing boolean/presence3 does not advance, invalid4 consumes
its byte. Missing c0 raw byte is1. Missing nested tag is2; short odd raw16 is1
after its tag, without advancing payload. Collection oversize count/element
length gives4; short element string gives2 after consuming available bytes.
Other counted strings use code1 and leave a short payload cursor after its prefix.

The safe reader checks extent before copying. For fc670 strings this deliberately
strengthens the observed native copy/move-before-final-extent path. The API
returns no partially mutated native object and promises no native rollback,
allocation/fault/unwind or concurrency behavior. A successful native helper's
error-code byte remains unspecified; the offline API invents none.

## Original fixtures and verification

[Original goldens](../tests/fixtures/registration/current-request-body-original.json)
contain hand-derived69/101/126-byte bodies; the neutral69 bytes are structural
synthetic input, not constructor defaults. The126-byte vector marks every scalar
and counted-string slot distinctly. [Focused tests](../tests/test_current_registration_request_body.py)
and existing response/runner tests passed367 cases. The first neutral fixture
was seven bytes short and was corrected without changing the codec; its failed
result and the JUnit metadata-count repair are retained in the validation receipt.

Independent scratch oracles compared exact69/126-byte output and decoded values,
24 anchored failures, nine success mutations, all126 rich truncations and five
string thresholds. Later probes passed512 tag-position/value cases,21 invalid
inputs,14 incomplete tails and decoded ownership after input mutation. All
comparisons used the same module hash. These are executed Python checks against
instruction-derived contracts, not native-client experiments.

The new test is explicitly included in fixtures-static and workspace profiles;
the reviewed group/file counts are updated with it. Existing response-codec
behavior is preserved. The receipt separates current source rehashes, executed
pure byte/oracle checks and repository regressions. No client or native client
code ran. Current record discriminator/framing, actual input authority/semantics,
#212's fresh construction gates, live acceptance and Milestone1 remain open.
