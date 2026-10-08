# Explicit current registration adapter

Actionables #266 under workItemId164/178 connects the existing original
[request decoder](REGISTRATION_REQUEST_RECEIVE.md) and
[response record encoder](REGISTRATION_RESPONSE_RECORD.md) to
`RegistrationAdapter`. This is an offline-tested server component. The actual
incoming Carrier placement, runtime type bindings, appropriate response fields,
authentication and native client acceptance remain unproved.

## API and state

The constructor accepts three optional inputs together:

- `current_request_type_index`: explicit uint32 selector, including zero.
- `current_response_type_index`: explicit uint32 selector, including zero.
- `current_response_body`: exact immutable `RegistrationResponseBody` with
  every field supplied by the caller. Appropriate runtime values and remote
  authentication semantics remain unproved.

Supplying only some inputs fails before peer state is created. Omitting all
three retains the historical request/reply path. There is no CLI selection for
this profile. The current profile does not choose an identity, token, version,
authentication result or captured response fields.

After the existing connect/candidate gates, the current profile accepts one
complete raw physical request through the original decoder: CRC32, BE32 count,
nil outer UUID, selected fresh wrapper, explicit selector and exact BODY extent.
It requires immutable bytes and a total size of 1–4096 bytes, including the
eight-byte physical header. Prefixes, trailing bytes and rejected current
streams never fall through to a historical parser. These bounds and strict
canonical/exhaustion checks are server policy, not a recovered native receive
implementation. Decoded fields are discarded; events contain fixed metadata.
Peer state retains existing input hashes and outgoing reply bytes, not decoded
request values. The caller still owns input buffers; this is not secure erasure.

The caller response is encoded before peer resources with fresh wrapper flags0
and its exact compact record prefix. The complete encoded record must fit4096
bytes. It is passed directly into the pinned frame codec, without a second
length prefix. Existing send/cursor/ACK gates apply. Successful first send caches
the framed reply; duplicate/fresh retries reuse it. A short send does not advance
the successful reply state. Progress classification excludes the configured
request selector. Every acceptance marker remains `client_acceptance_proven=False`.

## Evidence and limits

[Original integration receipt](../research/evidence/current-registration-adapter-current.json)
pins main2effa03 and the exact changed adapter/test bytes. Focused646 cases cover
34 original request literals across three explicit response selectors, current
configuration, rejection/no fallback, byte boundaries, short sends and privacy.
The independent mock-peer experiment uses actual pinned FirstLight frame/wire
and ACK code. Its minimum response is the hand literal
`15000103000000000000000000000000000000000000`; synthetic selector3 is not
evidence of the runtime binding. No sockets or game client were used in that
experiment. Full workspace validation and its owned loopback lifecycle are
recorded separately in ROADMAP.

The existing full Carrier plaintext cap is also4096 bytes. A raw4096-byte request
can pass the schema and exceed the Carrier cap once framed. Exact frame overhead
depends on the selected record; the independent report records its tested
boundary. This component therefore proves a controlled integration with the
pinned codec, not the missing current-client transport provenance.

Eleven older public receipts bind the changed adapter/test and now report stale
local inputs. Their original results remain historical; unaffected image/static
source claims and unchanged codec/literal checks remain reusable. No historical
receipt is rewritten to claim a new native result. Existing private trial
manifests also bind the adapter: by source inspection, the launcher guard would
reject changed input hashes before admission. The controller was not run.
The consumed October7 native creation grant remains closed;
this component neither prepares nor authorizes another attempt.
