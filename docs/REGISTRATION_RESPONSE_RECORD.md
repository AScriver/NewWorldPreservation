# Current typed registration response record — #264

The original pure [encoder](../scripts/current_registration_response_record.py)
adds the selected typed wrapper and compact record length to the existing
[response BODY codec](REGISTRATION_RESPONSE_BODY_CODEC.md). This is the record
view accepted by the proved compact-length callback/parser chain. The lower
transport/Carrier-to-callback byte provenance remains unjoined, so this is a
server construction component with a bounded record claim.

Inputs: main9668f01, unchanged owned image/map and generic wrapper/response BODY/
compact-reader proofs; original new module/tests/fixtures. Exact identities and
executed checks belong to the [receipt](../research/evidence/current-registration-response-record.json).
No client or native client code was executed.

## API and selected layout

`encode_registration_response_record(record, *, type_index, field_04=None,
field_0c=None)` accepts the existing immutable `RegistrationResponseBody` and
returns immutable bytes. The selector is a required true uint32; it has no
runtime map3 default. Optional fields are caller-supplied exact eight-byte
`bytes`, preserved in order, without inferred identities or authority.

| Part | Selected bytes |
|---|---|
| Record extent | Canonical current compact uint32 byte count of the entire following typed payload |
| Fresh wrapper flags | 0,1 or3, selected by absent/first/both optional fields |
| Optional fields | field_04 then field_0c, eight opaque bytes each when selected |
| BODY presence | Literal1 for the supplied nonnull response |
| Type | Canonical compact explicit selector; zero selects16-byte response UUID fallback |
| BODY | Unchanged BE32/BE64, two counted raw strings, four booleans |

Second-only optional fields are rejected within the deliberately selected fresh
wrapper domain. This restriction does not establish the full native decoder's
accepted flag domain. BODY string bounds and rejection policy remain those of
the existing codec. The output length counts actual wrapper/type/BODY bytes;
there is no sender CRC or nil outer descriptor in this selected record API.
The first record's declared extent excludes a following record or other suffix.

## Source and verification boundary

Existing writer146153e70/1461673b0 and decoder1461ac8d0 select the wrapper/type;
compact parser146ae44f0 dispatches the declared record, and the decoded response
can reach146b6f190. These source joins do not resolve lower input provenance,
actual runtime selector, field values or application acceptance.

Seven hand-derived literals cover minimum/rich BODY, opaque fields, explicit
selectors, all-zero fallback selection and uint32 maximum.113 new checks plus45
unchanged BODY checks pass (158 focused cases). Tests exercise all compact
selector widths, outer lengths127/128/16383/16384, maximum raw strings,
concatenated records and invalid caller arguments. Independent Tester passed
five original reader experiment groups, including shifted optional-field length
boundaries and a393274-byte maximum-valid record. Existing BODY decoding is a
Python model; this is not an independent native receive experiment.

The response UUID text is104145a7-ff95-44f1-9468-21fb41c8ac2b. Existing getter
parses its hex pairs sequentially. New1407de270/146152b10 source queries prove
the parsed array is copied unchanged into descriptor+18..27 by one128-bit
MOVUPS load/store. The outer helper returns an out-pair address; pair[0] contains
allocationBase+10 descriptor. With successful construction, nonnull descriptor
and resulting selector zero, generic writer submits descriptor+18/length16 to
virtual+40. This supports the chosen fallback bytes104145a7ff9544f1946821fb41c8ac2b
at the typed-record boundary; it does not prove actual runtime selection or
physical emission. Two roots/516 bytes and no data windows are sealed; primary
reconstructed native instructions and critical review retained these conditions.
The initial independent harness syntax error was corrected in ignored scratch;
production code did not change. Actual workspace/preflight closure is recorded
in ROADMAP and the private closure receipt after its checks complete.

No classifier, Carrier responder, reply choice, native trial or game client is
changed by this encoder. Full physical response placement, authentication,
native acceptance, world/player creation and Milestone1 remain open.
