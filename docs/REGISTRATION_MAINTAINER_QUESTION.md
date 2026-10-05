# Current-build registration/bootstrap question — unsent draft

Prepared for the maintainers; nothing has been sent. The original historical
launch/provenance question remains in
[FIRST_LIGHT_HISTORICAL_CLIENT](FIRST_LIGHT_HISTORICAL_CLIENT.md). Exact historical
successful binary identity is still unknown; the owned-build mechanism has now
been reproduced independently.

## Current question — unsent

On our legitimately owned1.400.6031.6004151 client, isolated on loopback with the
pinned First Light startup/trust method, registration response receipt and actor
START are logged and234 heartbeat acknowledgements match fresh local pings.
Original current-image codecs send SelfIdentification0x65c defaults, empty spawn
notification0x651, LevelInfo0x663 for the existing `newworld_vitaeeterna` map with
context0/default fields/fresh dedup counter1, then empty ReplicatedStateBundle0x8.
The client ACKs those envelopes and logs LevelInfoChanged plus the bundle diagnostic,
but still times out waiting for gameplay. We found no context-init/actor-success
marker in the filtered log; we are not replaying historical entities or world data.

Which prerequisites/order and field meanings are required for current
LoadContextAndLevel to initialize the context, and what source-supported messages
create a fresh live PlayerRegistry player after it? A lawful server-side fixture or
documented current-build contract for those gates would be sufficient; we do not
need client assets, credentials, proprietary source or recorded historical personas.

## Earlier registration question — historical draft

We are testing a legitimately owned Steam client1.400.6031.6004151 against an
isolated loopback responder, preserving the installed client, launcher and EAC.
Direct Frida startup with First Light63756a3's pinned runtime DTLS hook completed
private DTLS1.2. Our original integration uses that clean checkout's existing
Carrier/ACK/registration codecs and Aeternum820156d's whole-body raw LZ4 algorithm;
we do not run upstream capture hooks or replay historical world/actor data.

The current initial reliable channel0 record has flags0x21 and860 payload bytes,
with no validated generic typed wrapper. It is excluded by the historical
MF_NO_LENGTH0x40 filter but matches the existing structured-retry parser on its
raw body. Eight such candidates received existing88-byte type3 responses, using
source framing: channel0/flags0x21, record/reliable sequence0 and Carrier envelope4.
The client showed “unexpectedly disconnected from the server. Reconnecting... (4)”
and sent no later non-system data on those peers. A second trial changed only the
historical response version1.365.6031.6006993 to the exact owned-image literal
`[RETAIL].Javelin.1.400.6031.6004151`, with the same error. In this second trial,
later client ACK ranges2–4 covered each of eight reply-bearing envelopes. Schema
compatibility and Carrier delivery do not prove request identity or registration
readiness. Request contents and credentials were discarded.

What is the accepted current-build contract at this boundary?

1. Is this raw reliable record a registration retry, and what exact discriminator,
   serializer/schema and success/retry state transition establish that? Which
   response version, token/identity semantics and sequence/ACK ordering are required
   for acceptance? Our fresh local response token does not echo request fields.
2. After an accepted response, what is the validated ordering and wire/body contract
   for fresh private bootstrap state? In particular, which SelfIdentification form
   is used (four-byte trigger versus structured0x5d1), which fields derive from new
   local identities, and what deployed LevelInfo type/body/context is required?
   What original minimal implementation creates the initial replica/actor state
   without replaying a captured session?

Please point to a commit or provide an original, synthetic credential-free
specification/minimal implementation validated on the stated client build.
We are not requesting client binaries/assets, raw auth data, historical session
captures, proprietary material or leaked source.

## Why these inputs are missing

At clean First Light `63756a3f7ff0ae41752dcc7c80267802c3fa7548`:

- `server/rep_responder.py:776–828,931–1014` loads/sends captured post-V3 replies;
  it does not supply a validated constructor for fresh private world state.
- `server/javelin/self_ident.py:34–80` explicitly leaves trigger versus structured
  layout and field meanings unresolved. An encoder is not current-client proof.
- `server/javelin/level_info_changed.py:1–38,63–103` describes a speculative schema
  without real-session validation; deployed type/order/required values remain open.
- `server/javelin/v3_response.py:100–109` reports a `rep.ready` transition in
  comments; our current live observations do not establish that transition.

Current evidence: [schema trial](../research/evidence/carrier-registration-schema-trial.json),
[one-field version/ACK trial](../research/evidence/carrier-registration-version-trial.json),
[ledger K150–K156](EVIDENCE_LEDGER.md), [bounded procedure and cleanup](CARRIER_REGISTRATION_TRIAL.md).
The ninth automatic reconnect exceeded our adapter's eight lifetime-peer budget;
that local rejection is excluded from the eight candidate/ACK observations.
