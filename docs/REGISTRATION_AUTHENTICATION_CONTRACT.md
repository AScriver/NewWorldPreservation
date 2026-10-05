# Current registration authentication and peer ownership — #211

Only Actionable **211**, under **workItemId 164**, was worked. Current source
establishes conditional request construction, client interpretation of received
authentication results, local response-field ownership and connection-to-owner
routing. It does **not** establish the current authoritative ticket/identity/peer
contract. This report records the exact missing joins; it implements no protocol.

The [#210 report](INITIAL_REGISTRATION_CONTRACT.md) completed its bounded research
alternative. Its historical 860-byte request discriminator, transport/framing
bridge and concrete body codecs remain unproved. Done does not close those joins.
The [original #211 receipt](../research/evidence/current-registration-authentication-contract.json)
pins selected function/data spans, source ranges, input identities and verification.

## Inputs, ownership and method

Initial main HEAD `ec5597277dd4c56a9abde8e337edbb527f3b6f32` had a clean index and
tracked working tree. Current disk checks pin app 1063730/build 22469132, executable
version 1.400.6031.6004151, 179204176 bytes, SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
The existing approved type map rehashes to
`f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75`;
it was not regenerated. First Light `63756a3f7ff0ae41752dcc7c80267802c3fa7548`
and Aeternum `820156dbc44c86c9436af81aa0dba72e94cb636b` were clean. Relevant
source/build/tool/dirty-file identities and later concurrent changes are recorded
separately in the receipt.

The claim entered Researching and recorded the outcome, C1–C5 acceptance/checks,
file ownership and exclusions before analysis. Independent producer and
response/ownership passes used file-backed instruction/data reads, PDATA/chained
unwind ranges, Capstone 5.0.7/Python 3.11.9 and bounded sparse
Ghidra 12.1.4/PyGhidra 3.1.0. Material recovered types/branches were checked against
instructions. The primary checked pinned reference/original adapter source using
AST inspection without importing or executing the reference servers. A targeted
challenge pass and narrow disputed-join adjudication followed the primary ledger.
Tracked report edits follow Ready/In progress. Private derived output stays ignored.

## J211-1 — producer provenance and conditional request construction

Owner constructor `0x146b69ad0` retains its incoming second argument at owner+0x50.
Setup `0x146b6d600` creates/replaces gateway owner+0x118 and copies argument-backed
values into retained owner fields including +0x138, +0x1c8, +0x1e8, +0x510 and
byte+0x590, plus vector-like storage. Those immediate copies establish data/lifetime
provenance at the API boundary. They do not identify an account, ticket, credential
or authoritative peer. Source labels from historical parsers are not native names.

Builder `0x146b6e190` requires gateway+0x160. A false connection-result gate enters
the error/event route; the retained connection-result closure can run on failure
as well as success. The normal route obtains data through owner+0x90 virtual+0x10,
checks two global/config predicates and `0x146b6df50`, then conditionally allocates
V3 (0x470, constructor `0x146b66820`) or V2 (0x360, `0x146b66a60`). These predicates
must not be named authentication modes without their source-owner join.

V3 constructor fields +0x10/+0xa0/+0xc0/+0x2c8/+0x3e0 and byte+0x460, with
scalar+8, reach `0x1407cfd10` and serializer interface UUID
`532e765a-3393-4a50-9010-b73c627512b2` (owned map 236). Immediate copies are
established; meanings and encodings remain distinct questions. Map 19/V3 and
map 2/V2 are native class-table identities, not recovered tags from the 860-byte
records. No selected comparison is joined to ticket validity or account-to-peer
authorization. Checks can exist in unresolved callers/providers/serializers or
remote/lower-layer authority; this is no whole-program absence claim.

The narrow follow-up joins two immediate setup callers on owner vtable
`0x148590ab8`: slot+0x10 → `0x146b6d580`, slot+0x18 → setup, slot+0x20 →
`0x146b6d9a0`. The first calls setup at `0x146b6d5e4` after cloning its incoming
argument 6 into owner+0x3f0 through `0x146b6b930`; it forwards arguments 3/4/5/7
and argument 8's byte to setup's retained fields. The second calls setup at
`0x146b6da7c` with incoming arguments plus locally constructed descriptors and
constant byte 1. Their upstream invocation sites and business labels remain
unjoined. The second route prevents treating every setup value as a directly
supplied identity structure.

`0x146b6df50` reads thread-local/global configuration state and a string-like
setting; its lazy initialization registers a Javelin metric-level override name.
No setup/request field is passed to its selected call. Its exact configuration
comparison/import target remains unresolved; it is not a source-joined ticket or
account check. Constructor initializes owner+0x90 to null, with no direct assignment
in these selected setup/caller methods. Its concrete setter/provider creation,
class and ownership are the missing join. No global absence of the provider follows.

## J211-2 — client interpretation of authentication results

Handler `0x146b6f190` recognizes `RegistrationResponseMsg` through the incoming
object's virtual+0x30, comparison helper `0x146158ba0` and descriptor
`0x1407f2e80`. The current UUID is `104145a7-ff95-44f1-9468-21fb41c8ac2b`, map 3.
It checks owner+0x600 and writes handled=1 **before** evaluating response dword+8.
A duplicate while handled is set reports local error 2.

Nonzero response+8 is interpreted by `0x146b70d00` and reported through
`0x146b6c500`. Exact current branches include these advertised failure categories:

| Received status | Client interpretation | Authority limit |
|---|---|---|
| -10 | connection-ticket claim failed | No claim store/redemption transaction joined |
| -110 | login-token signature invalid | No signature algorithm/key/verifier joined |
| -120 | login token expired | No issuer/clock/expiry policy joined |
| -160 | login ticket invalid | No ticket schema/identity/ownership check joined |
| -310 | auth-token credentials invalid | No credential-to-principal validation joined |
| -340 | platform ID invalid | No platform identity-to-peer binding joined |

Other selected branches describe soft/hard lifetime limits, world/endpoint,
capabilities, host, version/type-index, platform/EAC/API and EOS-related failures.
The receipt seals exact status/branch/label references privately. These are
client-side result interpretation, not implemented server checks or evidence that
any particular ticket was validated. No real status, credential or request was
collected by #211.

For response+8==0, byte+0x5b creates a separate conditional path:

1. Zero jumps to the common accepted path at `0x146b6f447`.
2. Nonzero checks owner+0x768. Zero there reports error 13 but continues this path.
3. A result string starts with a nonempty EOS error marker; `0x146b679f0` dispatches
   through its bus/router/subscriber machinery and thunk `0x140571494` to subscriber
   virtual+0x48. Its concrete subscriber, inputs and authority remain unjoined.
4. The handler checks the **final output string length**, not the dispatcher's
   return byte. Successive subscribers overwrite prior output at
   `0x146b67b85..0x146b67b92`. Nonempty final output reports error 8 and exits;
   empty rejoins the accepted path. Neither all subscribers succeeding nor an
   early subscriber's error determining the final result is established.

Thus `status==0 && byte5b==0` is not a universal acceptance rule. Nor is
owner+0x768 a proved authenticated-identity flag. Subscriber behavior, runtime
selection and side effects remain unknown.

## J211-3 — accepted fields: copy, borrowed input and clock state

The selected accepted path has distinct ownership operations:

| Source field | Destination/action and exact site | Established limit |
|---|---|---|
| response+0x10 | `0x146b6f584` → `0x146afed90` → `0x146afedb0`, owner+0x130 | Current-time subtraction, offset/initialization/smoothing support a clock-state role; units and policy unknown. No peer/account identity established |
| response+0x18 | string copy to owner+0x598 at `0x146b6f5a7`; getter `0x146b6cb40` copies it out | Owner retains its own string. Semantic name, issuer, principal association, validity/use and revocation unknown |
| response bytes+0x58..0x5a | copy to owner+0x6f0..0x6f2 at `0x146b6f5ac..0x146b6f5c4` | Values and meanings unknown |
| response+0x38 | optional owner+0x110 callback virtual+0x10 at `0x146b6f5e0..0x146b6f5e4` | Borrowed address for this call; downstream copy/retention and meaning unjoined |

Owner+0x601 is set to 1 at `0x146b6f5ca` **before** that callback; getter
`0x146b6df30` reads it. A separate event dispatch follows. Receive
`0x146b6eb70` retains the decoded wrapper/control block for the handler call
at `0x146b6ed39` and releases it afterward. Durable use of the borrowed +0x38
field therefore needs the concrete callback's retention/copy contract.
No dangling-reference defect or secure token capability was demonstrated.

Selected response object provenance is strengthened: descriptor `0x1407f2e80`
uses serializer object `0x147f46910`; virtual+0x10 → `0x1407cbe90` allocates
0x60, and virtual+0x28 → `0x1407cd040` constructs vtable `0x147f46db8` and
dispatches decoding of +8/+0x10/+0x18/+0x38/+0x58..0x5b. This joins native
field locations to the selected decoder. Its helper encodings, complete wire
codec and transport placement remain unproved. No codec was implemented.
The imported response's `session_token`/`server_version` names cannot name
these current fields solely by matching shape or position.

## J211-4 — connection association and lifetime boundaries

Setup `0x146b6d600` creates a gateway with build, disconnect and receive closures
capturing the raw owner. Constructor `0x146b6a270` clones them into gateway storage,
with active pointers +0xa8/+0xe8/+0x158, and retains the selected connection/control
block at +0x60/+0x68. Connection result closure `0x1485916a8` → `0x146b713e0`
captures that gateway. A successful connection getter sets gateway+0x160 and
installs receive closure `0x148591708`, also capturing the gateway.

Record callback `0x148591738` → `0x146b714b0` loads gateway+0x158;
`0x1485915b8` → `0x146b71590` loads the captured owner and enters
`0x146b6eb70`. Decode success and a nonnull body are required before the response
handler. This is concrete **connection → gateway → owner** association. The handler
receives an owner and message reference, not a separately validated account proof.
No credential/account/ticket-to-peer comparison or authoritative server binding
is joined by this selected route.

| Boundary | Selected local behavior | What remains unknown |
|---|---|---|
| Connection state | selected primary+0x308==4 getter `0x146b28390`, gateway+0x160 | Account/authorization meaning is not implied by transport success |
| Response handling | owner+0x600 set before checks; builder clears it after dispatch at `0x146b6e667` | Reentrant/runtime ordering; handled is not accepted or authenticated |
| Disconnect | `0x146b71530` clears gateway+0x160, unregisters callbacks, then invokes owner route; `0x146b6e7c0` calls external callbacks before directly clearing +0x601 | No direct +0x600/+0x598 clear in that body; final callback state and ticket revocation unknown |
| Replacement/setup | new owner+0x118 installed at `0x146b6d740` before old gateway destruction; clock and retained queue object replaced | Concrete setup caller effects, generation ordering and old in-flight callbacks unknown |
| Stop | `0x146b70be0` nulls/releases child and retained queue object, directly clears +0x5b8/+0x600/+0x601, then calls virtual+0xe0 | Selected stop does not directly erase +0x598. External effects/final state and credential validity unknown |
| Destruction | owner `0x146b6b230` releases string storage; gateway `0x146b6b6f0` unregisters callbacks before close/release and closure destruction | Retained storage lifetime is not ticket authorization lifetime |
| Callback cancellation | selected connection virtual+0x88 → `0x146b27ca0` removes registrations and destroys/nulls slots; owner pointer copies are raw | Already-in-flight quiescence, generation checks, thread serialization and reentrancy unproved; no race shown |
| Error reporting | `0x146b6c500` has a retained error callback and locked error queue; response callsites pass third argument 0 | Presentation does not prove immediate disconnect, rollback or accepted-flag clearing |

The selected receive thunk/handler have no current-gateway generation comparison.
That narrow fact does not demonstrate a reachable stale callback. No current
account owner or authority is supplied by these local lifetime operations.

## J211-5 — pinned reference tickets and local probe peers

These are separately source-supported **reference/local-code contracts**, not
current game authentication semantics. Exact one-based ranges and hashes are in
the receipt's source symbol table.

First Light `server/auth_mock.py` creates one server `Ctx` (main:1581,
server:1519–1523, handler dispatch:1471–1495). It stores one mutable persona/world/
character set and a locked queue-ticket map. `set_persona:450–456` updates that
persona and existing characters. `handle_omni_token:1183–1208` extracts a JWT payload
subject by base64/JSON and updates the context without a signature verifier in
that extraction. Its comment about client verification was not verified here.

`Ctx.issue_queue_ticket:547–577` creates a UUID-keyed dictionary with character,
app/version/channel, readiness/refresh and location fields. It stores no principal,
expiry field or consumed marker. `refresh_queue_ticket:579–589` looks up that key,
increments refresh count and rewrites readiness/location without an owner/expiry/
use check in that method. AST inspection finds only map initialization, insertion
and lookup as direct attribute references in the file; no direct deletion/retirement.
That mock storage lifetime is not the current native ticket lifetime.

`handle_login_queue:777–892` takes request CharacterId and app data, uses the shared
context persona/world, and issues a replacement on an unknown refresh key.
`make_fake_login_ticket:258–314` emits current integer times and a ticket-ID-derived
signature marker; it does not sign a token or implement an expiry rule. Requested
character ownership is not established by those selected methods.

First Light `server/rep_responder.py:1280–1340` keeps sessions keyed by UDP peer
address. The selected registration handler:597–703 chooses random response bytes
or echoes a length-compatible parsed session UUID, with a lenient fallback. That
handler does not redeem the HTTP queue ticket or establish a verified principal.
The selected route supplies no joined redemption/owner check for the HTTP queue
ticket. The source has no direct queue-map reference or auth_mock import; the AST absence
check is limited to those syntax references. DTLS context:167–176 uses
`VERIFY_NONE` for client certificates. Idle removal happens only on socket timeout
with an enabled threshold:1287–1306; it is peer inactivity, not ticket expiry.
Optional historical substitution/replay is outside this task and was not executed.

The original probe's `scripts/dtls_transport_probe.py:70–79,269–280` assigns a fresh
local UUID to a Peer/SSL object and maps UDP address/SSL object to it. `VERIFY_NONE`
at115 and event189 explicitly leave client certificate authentication false.
The same Peer object reaches the adapter at201–202. Closing removes the DTLS maps
at173–178; the adapter's separate UUID-keyed `_PeerState` lifetime map:246–258 is
not an account registry. It discards the parsed registration object:442–465,
generates response bytes:645–652, and sets `v3_sent` only after local send success:
665–669. Recognition, send, ACK, callback handling, acceptance and authenticated
identity remain separate claims. No source-supported ticket redemption or
credential-to-peer authorization is supplied by that adapter path.

## J211-6 — precise missing joins and #210 dependencies

| Missing join | Current evidence boundary | Required before the dependent conclusion |
|---|---|---|
| Native producer meanings | setup arguments/owner fields → request constructors/interface | Concrete source owners and meanings for identity/ticket/credential-bearing inputs, including owner+0x50/provider+0x90 and global predicates |
| Authoritative ticket/principal validation | response error interpretation ends at client handler/status mapper | Actual issuer/validator/claim-store operation, signature authority, expiry units/policy, principal/character/world ownership and consumption/reuse behavior; client labels supply none |
| Conditional subscriber authority | response+0x5b → bus/router → subscriber virtual+0x48 | Concrete subscriber/source inputs, owner+0x768 source and result/side-effect contract |
| Response identity ownership | +0x18 copied to owner+0x598, +0x38 borrowed by owner+0x110 callback | Semantic field names/issuer, concrete callback retention/consumption and association with a principal/ticket |
| Authenticated peer association | concrete connection/gateway/owner callback route | Authoritative accepted principal/ticket → exact connection/peer binding and disconnect/reconnect/revocation scope |
| **#210 actual request identity** | native V3/map19 or V2/map2; discarded historical860 parser-compatible records | Actual discriminator/runtime branch/index or UUID fallback joined to that record. A mapped class or parser match cannot supply it |
| **#210 transport bridge** | pre-transport writer/queued streams versus compact-length receive | Queue consumer/physical stream buffer/Carrier placement and inverse joined. Local object association does not validate message placement |
| **#210 body codec** | V3 serializer interface236 and selected response factory/field decoder | Concrete request/response helper encodings and schemas joined to current transport/type. Native offsets and imported bodies are insufficient |
| Lifetime/callback ordering | selected direct clears, release and unregister order | Concrete current cancellation/scheduling/generation guarantees and downstream callbacks before claiming isolation, revocation or final postconditions |

The first five source questions can be recorded without resolving #210's framing.
Any wire fixture, synthetic authentication acceptance/rejection, ticket-to-wire
authorization or comparison to the historical860 requests additionally needs the
three explicit #210 joins. No such fixture or experiment was made. No private
authentication design was substituted for missing current semantics.

## Challenge, verification and completion boundary

Targeted challenges P211-3 through P211-10 survived within their bounded static
scope. The challenge independently checked 2,987 instruction lines across 22
artifacts, 28 status-label branch destinations and six source hashes. Three limits
were retained: only the final subscriber output controls the +0x5b branch;
callback effects/cancellation prevent durable teardown postconditions; and the
new response factory/decoder join narrows #210 without closing its full codec.
The primary separately rehashed 64 unique selected functions, 70 primary span
parts and two complete tiny thunks against the pinned image.

A reference ownership counterexample follows from source: issue a ticket under
the shared persona A, switch the context to B, then refresh the old key; selected
code combines retained CharacterId with current context persona B. This was
reasoned from source, not executed as a synthetic authentication test. Locks do
not establish principal isolation. No race, dangling reference, credential
revocation rule, authoritative authentication acceptance or current wire behavior
was demonstrated.

Failed private helper attempts (a nonexistent source selection, incorrect AST
class name and missing/order-sensitive Capstone import) were corrected before
successful receipts. No claim relies on their failed output. Broader auth absence,
uniform +0x5b rejection, imported field-name equivalence and local-store final-state
inferences were rejected as unsupported.

Focused checks refresh exact image/map/reference/source identities, selected
instruction/data spans, source symbol ranges, authoritative #211 scope and unrelated
byte preservation. The complete Test-Offline workspace is regression verification
at its own source/config snapshot; its existing synthetic/loopback tests add no
authentication-semantic or current-client acceptance evidence. Actual counts,
commands, receipt hashes, changed-input checks and owned cleanup are in the receipt.

Deferred: pinned upstream request/logging and optional historical replay paths can
retain request-derived data. This task only inspected their source, did not run
them, and made no upstream changes or additional Actionable. Concurrent tooling
changes remain separately owned and are preserved.

Static tools exited and private databases were closed. The offline harness owns
only its unique temp/loopback resources and must verify their cleanup. No client,
game endpoint, hook, capture, process memory, credential source, historical body,
system/trust/routing resource, contributor message or publishing was used.

Completion closes only #211's bounded missing-join research alternative, after
verification, scoped local commit and Resolution/Done/released-claim readback.
Parent #178/#164 and Milestone 1 remain open. Authenticated gameplay, secure ticket
implementation and another task are not established or begun. The actual local
commit and final task state are reported in the completion handoff.
