# Replacement-server registration stream decoder — #260

This original pure decoder receives the physical stream the current selected V3
client sender is proved to produce. It reuses the existing BODY decoder and all34
literal sender fixtures. It establishes an offline server component, before the
still-unjoined Carrier placement, runtime selector binding and authentication.
Native receive behavior is not reconstructed or claimed.

Input clean33e38a6, workItemId164/parent178, build22469132, imageSHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`;
mapSHA256 `f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75`.
Reuse the unchanged [sender contract](REGISTRATION_REQUEST_STREAM_CODEC.md),
[physical framing](REGISTRATION_STREAM_FRAMING.md),
[identifier placement](REGISTRATION_IDENTIFIER_PLACEMENT.md) and
[BODY contract](REGISTRATION_REQUEST_BODY_CODEC.md).

## API and receive behavior

```python
decoded, consumed = decode_registration_request_stream(
    data, expected_type_index=0, max_payload_bytes=1024 * 1024,
)
```

[The module](../scripts/current_registration_request_receive.py) accepts bytes,
bytearray or a contiguous memoryview. `expected_type_index` is required and must
be a true uint32; this example explicitly selects fixed-UUID fallback, without
asserting the client actually uses it at runtime. Nonzero indices require the
caller's own explicit binding. Map19 is never selected by default.

The decoder reads BE32 checksum/count, checks the declared count against the
configured cap and available bytes, then snapshots exactly that payload. CRC and
all parsing use the same immutable snapshot. It requires nil outer UUID16,
flags0/1/3, optional raw8 fields in bit0/bit1 order, presence1, current compactuint32
selector and, for zero, the literal V3 UUID. It then decodes exactly one complete
V3 BODY. `DecodedRegistrationRequest` contains frozen BODY, type index and separate
opaque `field_04`/`field_0c` bytes; no values borrow mutable input storage.

`consumed` includes the8-byte header and selected payload. Bytes after that extent
remain caller-owned: they are neither parsed nor included in its checksum/cap.
The caller can process a second record from `data[consumed:]`. No Carrier records,
reply serialization, request logging or authentication is performed here.

## Explicit receiver policy

| Check | Meaning and limit |
|---|---|
| Default1MiB payload cap | Configurable resource policy; not a measured native or Carrier limit. Require a positive true uint32 |
| Canonical selector bytes | Accept only the current sender's shortest compact encoding; reject native-reader nonminimal/reserved/wrapping aliases as server policy |
| Exact selected BODY extent | Reject bytes remaining inside this payload after BODY decode; not proof the native receiver enforces exhaustion |
| Fresh flags0/1/3, presence1, nil outer UUID | Selected proved sender domain; other generic wrapper/context variants remain unsupported |
| Explicit selector binding | Reject another selector or incorrect fallback UUID; grammar acceptance does not authenticate a client or prove runtime table meaning |

The BODY decoder's existing safe bounds/error behavior is retained, including
its source-supported compact-count aliases and first-value collection handling.
Canonical-selector policy applies to the envelope selector alone, not all BODY
counts. No runtime value or semantic field name is inferred from these bytes.

`StreamDecodeError` exposes a fixed `reason` and absolute stream `cursor`.
BODY failures also preserve `body_code`; they do not expose the input fields.
Invalid caller configuration raises ValueError before buffer access; unsupported,
noncontiguous or released buffers produce a fixed TypeError. These failure
interfaces are original server policy, not native helper return values.

## Verification and remaining joins

The original tests decode every existing literal sender fixture, exercise all
compact widths/optional fields, separate inside-payload bytes from outer suffix,
and reject truncated or corrupted headers/prefixes/BODY without partial success.
Controlled mutation during CRC proves parsing uses the checksummed snapshot.
An independent Tester uses separately constructed malformed inputs, reserved
flag/presence values, huge counts with tiny payloads and unusual buffer views.
Exact executed checks and input hashes are recorded in the
[original receipt](../research/evidence/current-registration-request-receive.json).
The complete workspace passes1641 Python cases across49 modules, all five
PowerShell suites and the owned loopback lifecycle, with unchanged inputs,
closed listener and child exit0. Its exact private receipt is
`.scratch/offline-validation/run-9gi9b4je/receipt.json`; the public receipt above
retains the focused and independent source bindings without rewriting them.

Client sender → physical stream → lower backend/Carrier placement remains the
next receive-side join. Actual type/index/fallback choice, historical860-byte
request discriminator, authentication and source-supported response selection
remain open. The historical Carrier responder is unchanged; this module adds no
live send, native trial or private world/player/Milestone1 acceptance.
