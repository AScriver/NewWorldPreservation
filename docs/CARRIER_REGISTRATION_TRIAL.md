# Owned-copy Carrier and registration experiment

## Active actor/bootstrap continuation — October4

The closed0417 actor trial established one private DTLS connection and234 matching
local heartbeat acknowledgements over about120 seconds. The client acknowledged
the registration/SelfIdentification/spawn envelopes. It remained loading, then
the user observed "Timed out while waiting for gameplay on the server." The peer
later closed on the responder's idle deadline; no traffic-budget rejection was
recorded. Fixed log metadata shows response receipt and actor START, without an
actor-success marker in the inspected log. Cleanup and independent readback
verified resource removal and unchanged installed executable/launcher hashes.
See [the closed receipt](../research/evidence/current-actor-callback-trial.json).

The closed0440 `world_activation=true` admission kept those exchanges and added
two source-supported current-image messages, using original codecs:

- LevelInfo current0x663:63 bytes including its4-byte typed header. Name only the
 existing owned map `newworld_vitaeeterna`; keep the second string/entry vector
 empty, numeric/boolean fields at construction defaults and context byte0. The
 final big-endian u64 is the fresh local deduplication counter1, chosen to differ
 from initialized0. It is not a world or player identity.
- ReplicatedStateBundle current0x8:9 bytes including its3-byte small-ID header.
 Its six-zero-byte body has absent sequence, context0, false flags, absent optional
 structure and empty payload. It can trigger pending context initialization and
 contains no entities or player state.

Send LevelInfo once, one second after successful local spawn-notification send,
then the bundle once, one second after successful local LevelInfo send. A failed
send disables that stage and prevents its successor. Existing heartbeat and all
messages share Carrier envelope/reliable/record/ACK cursors. No new process hooks
are added. Bind the original codec, [static contract](../research/evidence/current-world-activation-contract.json),
private evidence seal, owned mapping and the existing map asset hash before launch.
Require the same resource locks, loopback containment and cleanup below.

Inspect only fixed log markers for LevelInfo, context initialization, actor success
and named prerequisite failures. Listener veto, missing callback prerequisites,
default-field suitability, asynchronous map completion and creation of a live
PlayerRegistry player remain distinct unknowns. A map loading screen alone does
not prove a playable world. Do not invent a player/entity packet to bypass them.

0440 transmitted both messages once and client ACK ranges covered their envelopes.
The owned log recorded two LevelInfoChanged labels and one bundle-without-context
diagnostic; the user again observed gameplay-wait timeout. The inspected diagnostic
is emitted after the context-load call irrespective of its result, so it does not
identify the failed prerequisite. No context-init/actor-success marker was found
in the filtered log. There were234 matching heartbeat ACKs and no budget rejection.
Cleanup04:49:58 UTC and independent readback05:25:01 UTC verified owned resource
removal, original hosts and intact installed images/signatures. The next question
is context-load prerequisites/ordering and fresh PlayerRegistry creation.
[Closed world trial](../research/evidence/current-world-activation-trial.json).

New fixed markers from the stable owned common Game.log correlate the previous
eight replies with client response receipt, actor-connection START and a disconnect
about10 seconds later. START does not mean actor success. Current-image static
control flow places it after a REP interface check and enters actor wait.

The prepared heartbeat-only `run-20261004T2255-heartbeat` never started: ordinary
Windows RunAs reported cancellation before controller dispatch or containment.
Independent checks found no game, trial ports or run-owned rules; its admission
is closed and it supplies no protocol result. Do not confuse that cancellation
with any earlier accepted UAC instance.

The first actor admission0254 reached its controller after UAC but stopped before
client/service startup because Steam was absent. Cleanup04:14:53 UTC and readback
04:15:48 UTC verified game/port/rule absence, original hosts and intact installed
images/signatures. Steam was then started normally. No protocol failure is inferred.

The closed `run-20261005T0417-actor-default` reused the physical copy and existing
containment/ownership procedure below. The optional `heartbeat_15d=true` admission
enables only the clean pinned `HeartbeatPing15D` encoder:12-byte typed ping,
new local counter and random nonce, every500ms after a registration reply. The
responder loop owns the timer; no incoming traffic is required to drive it.
Existing VLQ/reliable channel0 framing and ACK builder are used. New messages
share per-peer envelope/record cursors; exact cached retransmissions retain their
bytes and IDs. The MN connect ACK's already-used channel3 IDs0/1 are accounted for
before subsequent ACK allocation. These are combined changes, so an improvement
will not isolate heartbeat from sequencing as the cause.

The owned type mapping confirms heartbeat0x15d. Current-image serializer/factory/
dispatch evidence also establishes two original fixed actor candidates, separate
from the incompatible historical SelfIdentification codec:

- `self_ident_default=true`: current type0x65c,131-byte typed message including all
 127 body bytes. Values are the client's construction defaults: two empty tagged
 strings, three null identity records, zero/empty/false settings and +0f32 words.
 Send once per peer, one second after its successful registration reply.
- `spawn_point_notification=true`: current type0x651, four-byte typed message with
 no body. Send once per peer, one second after successful local SelfIdentification
 transmission. That timing and send prerequisite do not prove client completion.

Both use existing VLQ/reliable channel0 framing and the shared fresh cursors.
Binding requires the original codecs, current contract receipt, owned image and
matching installed/copied typeindex hash. Null defaults reach the inspected actor
completion path only with an existing game/context/actor. Dispatch return alone
does not establish completion. Require the fixed client actor-success marker or
other state-specific evidence; a once-too-early negative cannot alone falsify the
codec. The spawn notification releases the next wait gate, but LevelInfo/context
activation and a PlayerRegistry player remain separate necessary world conditions.
[Static contract and limits](../research/evidence/current-self-ident-default-contract.json).

Match the existing strict36-byte heartbeat acknowledgment against a recently sent
local ping; output only metadata/boolean match and discard client hash/contents.
Carrier delivery, valid heartbeat echo, survival past the previous failure window
and actor/world readiness are distinct observations. The historical timeout report
supports a trial, not a current diagnosis. No captured replay, speculative
SelfIdentification codec or historical world/replica state is introduced. The
next LevelInfo/empty-bundle candidate is the explicit current-image exception
above. Prior run
receipts remain unchanged. New allowlisted owned-log observations retain only
fixed diagnostic labels and timestamps, with credential-bearing lines discarded.

The user authorized continuation on October4 after two private DTLS handshakes
with the owned-copy Frida route. This continues that route; the stock client's
earlier CA rejection remains a separate historical result. No stock CA
investigation is repeated.

## Target and prerequisites

Owned Steam app1063730/build22469132, executable version1.400.6031.6004151,
SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
Reuse the physical copy belonging to the closed
`private/frida-trials/run-20261004T1733` run. Fresh admission, logs, hosts journal
and firewall identities belonged to `run-20261004T2216-version`, now closed.
Earlier closed attempts are `run-20261004T2015-registration`,
`run-20261004T2141-lz4` and `run-20261004T2154-schema`. All preceding runs'
stop request and evidence remain intact. The runner holds both the new run lock
and a copy-use lock until its exact game job exits.

Require an existing legitimate Steam session, no game/launcher, free loopback
ports443/64003, enabled firewall profiles and the already retained unexpired CA.
No certificate-store modification is made. Exact installed executable/launcher
hashes and valid signatures remain required; the Steam manifest may change only
while app/build identity stays the same. Preserve its current metadata.

Use shared Frida17.22.0 through validated `Run-Tool.ps1`, the pinned unchanged
runtime trust hook and original guarded observer. The existing procedure's
process identity, child rejection and loopback firewall rules still apply.
An access denial or startup refusal ends the attempt; no protection evasion,
installed launcher change or EAC service/driver change is admitted.

## Supported exchange and its limits

The original `carrier_registration_probe.py` loads the clean local First Light
checkout `63756a3f7ff0ae41752dcc7c80267802c3fa7548`, checking source hashes and
module origins. No upstream source is vendored; redistribution licensing remains
unresolved. It uses the existing Carrier parser/marshaler, connect ACK method,
ACK builder and registration response encoder. The upstream raw-logging session,
registration dump handler and replay server are never started.

1. Parse Carrier envelopes/records in memory. For compressed type0x81, decompress
   the entire body after the four-byte envelope header, then use the same record
   parser. Unknown or malformed input produces a fixed rejection label.
2. On a system connect request, try the implemented default MN connect ACK plus
   inline ACK. These historical bytes are a trial candidate; current acceptance
   requires subsequent client behavior.
3. After that ACK, require exactly one non-system data record in the envelope,
   on channel0, and no simultaneous connect request. Classify a no-length record
   or a reliable record with exact flags0x21 using the existing strict/structured retry
   schemas. Try raw bytes or one canonical complete VLQ length prefix established
   by the existing encoder. Initial V3 has a separate opaque prelude; do not require
   a generic type prefix or assert exact wire type from flags or schema success.
   Ambiguous/unresolved input receives no registration response.
4. Only after compatible schema parsing, try the existing88-byte registration response, channel0/reliable0x21 with
   VLQ length and echoed Carrier envelope sequence. Generate a fresh local
   token; no request identity or credential bytes are echoed. A parser mismatch
   stays unresolved rather than being repaired with guessed fields.
5. Observe retries, ACKs, disconnects and subsequent application records. Sending
   a response or seeing unrelated data does not prove `rep.ready`, authenticated
   private ownership, world entry, actors or Milestone1.

The response encoder contains historical version/default fields whose current
meaning is not independently established. No old world records are replayed.
No SelfIdentification, LevelInfoChanged, actor or movement packets are invented.
The source-supported fixed current callback candidates above form the next bounded
experiment; usable identities, level data and player replicas still need evidence.

Compression follows the executable path of the clean adjacent Aeternum checkout
`820156dbc44c86c9436af81aa0dba72e94cb636b`,
`Tools/nw_capture/decode_dtls_ledger.py` SHA256
`d5563a4ea694d45a81ab4db0d74ff86c940db95794a872a9393b2761efc9e15b`.
Its old module docstring says to skip two body bytes; its executable path and
inline correction instead decompress the entire body. Preserve that conflict;
the docstring is not the algorithm used here. The AGPL reference is inspected,
not vendored, imported or run as a capture tool. Original integration uses the
project-pinned `lz4==4.4.5` raw-block API with existing size hints
256/1024/4096/16384/65536/262144. These are allocation bounds, not discovered wire
lengths. Input is at most4096 bytes; expanded output is at most262144 bytes and
at most32 parsed records are admitted. Parsing work is bounded by the expanded
byte cap before the record-count check. The API cannot distinguish corrupt input
from an insufficient output buffer, so exhausted hints produce a combined fixed
failure label. [Official raw-block API](https://github.com/python-lz4/python-lz4/blob/master/docs/lz4.block.rst).
The decoder's source/hash and installed package version are checked before use;
the trial binds the package files and decoder alongside its other inputs.

## Resources, logging and cleanup

Primary session owns one game job, the three exact service handles, ports443 and
64003, the fresh hosts transaction and named program rules. These resources must
not overlap another live trial. Reuse the known queue/HTTPS responses; request
authorization, query values and body contents stay discarded.

The game lifetime is at most300seconds after resume. DTLS has at most4096 total
and2048 per-peer datagrams, eight active transport peers and existing
handshake/idle deadlines. The adapter separately admits eight lifetime peer states;
a reconnect after transport closure can complete DTLS but exceed that local budget.
Logs contain framing integers, lengths, fixed labels and booleans only. They do
not contain raw plaintext, auth blobs, identity strings, tokens, parser dataclass
representations or exception text derived from packets. Private contents are
handled transiently and discarded; no raw capture is collected.

Task-specific staging, binding, validation and dispatch scripts live under ignored
`.scratch/actor-default-20261005/`. Validate each complete PowerShell script
through `Invoke-CodexPowerShell.ps1` before execution. Bind admission, stage receipt,
adapter, controller, runner, observer, codecs and resource inputs before launch;
preserve copies of original executed sources in the new private run.

Close admission with `stop.request`. Terminate the retained game job before any
containment release; require runner lock exclusion, no game/launcher, exact owned
helpers stopped and ports closed. Then check installed binaries/app/build, restore
the journal's hosts block and remove only matching run-owned firewall rules from
both stores. Retain the CA and ignored physical copy. Any cleanup ambiguity retains
containment for guarded reconciliation.

## Status

The closed uncompressed attempt completed private DTLS, sent two connect ACKs,
and rejected ten compressed envelopes. It decoded no registration candidate and
sent no registration response. The user observed a Connection Error in the same
instance launched after delayed UAC acceptance. A broad historical
`CLIENT_DATA_AFTER_CONNECT_ACK` event was only system traffic including a
disconnect; it proves no application progress. The corrected marker requires a
data-channel candidate or validated known typed record. Cleanup completed at
21:29:46 UTC, preserving installed executable/launcher hashes and the current
Steam manifest with the same app/build. [Executed receipt](../research/evidence/carrier-registration-uncompressed-trial.json).

The bounded compression change passed15 fake-only controls and two explicit
pinned-source/LZ4 synthetic checks. Complete workspace validation passed399 Python
cases, three synthetic PowerShell suites and a local HTTPS lifecycle with unchanged
selected inputs. [Validation receipt](../research/evidence/carrier-registration-lz4-validation.json).
At that checkpoint a separate fresh live run was required to test
current-client compression and registration; the old discarded contents cannot
be recovered. Registration acceptance, world entry and Milestone1 remain unknown.
Raw decompression and framing compatibility are separate observations. A known
typed wrapper checks length/CRC/type prefix, not the message-specific body schema;
even a post-response typed record leaves client acceptance unproven.

The fresh compression attempt then decoded an actual733-byte body into882 bytes
using hint1024. Its two records were a system ACK and a reliable channel0 record
flags0x21/payload860; no generic typed wrapper validated. The historical0x40
candidate filter is specifically MF_NO_LENGTH, so this record was excluded. Its
type cannot be inferred from discarded contents. User saw a spinner for about16
seconds followed by Connection Error. Controller cleanup and independent readback
passed. [Live receipt](../research/evidence/carrier-registration-lz4-trial.json).

The following slice used bounded schema classification, retaining the same decompression
and containment. Try existing strict832-byte and structured-retry parsers on raw
post-connect reliable channel0 data, or after one canonical whole-body length
prefix established by the existing VLQ encoder. This inverse-encoder check is
original integration, not a discovered inbound API. No guessed header stripping,
opaque-field search or schema repair is admitted. Schema compatibility is candidate
evidence; wire type remains unproven. An unresolved parse must not emit a V3
response, including on the historical no-length path. System-only records never
count as post-connect application progress.
The initial classifier passed19 fake-API tests and three explicit pinned-source
synthetic checks, then full403-case workspace validation. Boundary review required
the channel0/single-data admission above before launch; those earlier checks are
historical for the affected gate until the tightened source is validated.
These checks exercise generated schemas and privacy gates; they do not identify
the previously discarded860-byte record. The strict parser's structural authority
is weak, so compatibility remains a trial candidate, not exact type proof.
The tightened source passed22 focused controls and three explicit pinned-source
synthetic checks, including good-schema counterexamples on another channel,
mixed data records and a simultaneous connect request. Full workspace verification
passed406 Python cases, three synthetic PowerShell suites and the local HTTPS
lifecycle with unchanged selected inputs. Final delta review confirms both
candidate branches share the stricter admission.
[Schema validation](../research/evidence/carrier-registration-schema-validation.json).

The schema trial then observed eight raw860-byte records compatible with the
structured retry parser and eight existing88-byte registration responses. The
client automatically reconnected with error4 after one Play click; nine DTLS
sessions completed, but the ninth exceeded the adapter's eight lifetime peer
states and produced140 budget rejections. No later non-system data or registration
acceptance was demonstrated. All resources were cleaned and independently checked.
[Schema live receipt](../research/evidence/carrier-registration-schema-trial.json).

The final experiment changed only the existing `V3RegistrationResponse.server_version`
field from its historical default `[RETAIL].Javelin.1.365.6031.6006993` to the exact
owned-image ASCII literal `[RETAIL].Javelin.1.400.6031.6004151`. Static literal
presence is not proof that a match is required. The optional CLI admits only this
candidate; omission preserves the historical default. Controller admission binds
the private static receipt to the same image hash before any resource mutation.
No token echo, field repair, sequence, ACK or packet-layout change is made.

New passive metadata records only an exact source-shaped channel3 ACK: flags0x20,
system ID6, six-byte payload with marker0x40/trailing06 and two BE-u16 range values.
Report its first/last sequence numbers and envelope sequence, plus the response
record/reliable sequences and fixed version-choice label. An ACK range by itself
does not prove which message was accepted or registration/world readiness.
The one-field encoder/ACK changes passed28 focused controls and four explicit
pinned-codec synthetic checks; the88-byte body differs only in its35-byte version
field. Full workspace verification preceded launch.
That final verification passed412 Python cases/30 modules, three synthetic
PowerShell suites and a local HTTPS lifecycle with unchanged selected inputs.
[Version validation](../research/evidence/carrier-registration-version-validation.json).

That version experiment completed nine private DTLS sessions, decoded eight
structured-retry compatible raw860-byte records and transmitted eight88-byte
responses. All eight response-bearing Carrier envelope4 transmissions were
covered by a later client ACK range2–4;24 ACK-range events were logged. The client
again showed Reconnecting...(4). No subsequent non-system data or
`POST_REGISTRATION_CLIENT_DATA` was observed in the eight admitted peers. The
ninth exceeded the adapter lifetime8-peer budget and produced140 fixed
`peer_limit` rejections. Total878 application records/18,919 bytes were discarded.
This one-field change did not remove the reported error in this configuration;
the version matching requirement and semantic registration acceptance remain
unknown. ACK coverage proves delivery at the Carrier envelope layer only.
[Version live receipt](../research/evidence/carrier-registration-version-trial.json).

Cleanup completed22:26:15 UTC; independent readback22:30:23 UTC verified no game,
closed ports443/64003, absent owned firewall rules, byte-exact restored hosts and
intact installed EXE/launcher hashes/signatures. The retained CA count remains1,
with no trust-store mutation. The ignored physical copy remains for authorized
reuse. Steam metadata changed with unchanged app/build; its current bytes were
preserved and the cause remains unknown. The receipt binds129 admission files,
the as-executed source snapshots and private metadata-log hashes. Later recording
edits to this document do not revise those historical admission bytes.

## Next required input

The clean pinned responder's post-V3 path loads and sends captured server messages
(`server/rep_responder.py:776–828,931–1014`). That replay is outside this trial.
Its SelfIdentification codec distinguishes an unresolved four-byte trigger from
an unvalidated structured form (`server/javelin/self_ident.py:34–80`); LevelInfo
states that its schema lacks real-session validation and leaves deployed type,
fields and ordering unknown (`server/javelin/level_info_changed.py:1–38,63–103`).
Codec existence does not establish accepted current-build semantics or a fresh
world-state constructor. Obtain the current registration/state-transition contract
and an original, validated bootstrap contract using new local identities before
implementing those state messages. The exact
[maintainer question](REGISTRATION_MAINTAINER_QUESTION.md) is drafted and unsent.
