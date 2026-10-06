# Current initial registration contract — #210

Later source closure: [#227's setup input producer](REGISTRATION_SETUP_INPUTS.md)
joins the actual persona/character lookup caller, registered string provider,
local text/raw/tag conversion and request copies. Current values, authentication
authority and other setup input producers remain unproved; earlier receipts stay
historical.

Later source closure: [#226's physical stream and queued backend join](REGISTRATION_STREAM_FRAMING.md)
supplies concrete reserve/write/header/CRC, vector consumption and pooled chunk
copying. Actual lower emission, a compact-record inverse, historical860 selection
and authenticated authority remain unproved; the historical receipt below is
unchanged.

Only Actionable **210**, under **workItemId164**, was worked. The bounded research
outcome is a conditional current native contract and precise missing joins. The
historical reliable channel0, flags0x21, 860-byte records still have **no proved
request discriminator**. Neither parser recognition nor a matching native class
identifies those discarded records. No codec, response, live experiment or other
task is authorized by this result.

## Inputs, ownership and method

Current disk checks on October5,2026 pinned Steam app1063730/build22469132,
FileVersion/ProductVersion1.400.6031.6004151, 179204176-byte owned executable
SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
Previously approved owned type-map SHA256
`f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75`
was rehashed; it was not regenerated. FirstLight
`63756a3f7ff0ae41752dcc7c80267802c3fa7548` and Aeternum
`820156dbc44c86c9436af81aa0dba72e94cb636b` were clean. Current imported decoder,
lock, approved receipts and relevant source hashes are in the
[original evidence receipt](../research/evidence/current-initial-registration-contract.json).

Initial main HEAD `580b4a44b2cff984cb8ccdde84dda37c540dac42` had24 pending files
and an empty index. Independent commits62d1998 and
`fa5158347bd798039abf3a154af1b3c405e589ba` subsequently committed those changes.
Selected source and shared-document bytes stayed unchanged; their initial snapshots
remain the preservation baseline. Those commits are external history, not #210 work.

The claim entered Researching and recorded outcome/scope/C1–C5 checks/exclusions
**before analysis**. Primary owns this report, its receipt, and #210-only insertions
in TASK_BRIEFS, ROADMAP, EVIDENCE_LEDGER and the evidence catalog. Source work used
bounded file-backed instruction/data reads, PDATA/unwind ranges, exact span hashes,
Capstone5.0.7/Python3.11.9 and an independent ownership/lifetime pass using
PyGhidra3.1.0/Ghidra12.1.4. Selected positive edges were challenged against the
primary ledger. The framing Investigator was unavailable on two attempts; no
independent framing result is credited to it. Static-tool scripts were validated
through Invoke-CodexPowerShell/Run-Tool. No process-memory or runtime game observation
occurred. Private source-derived output stays ignored; this report is original analysis.

## J210-1 — what the imported parser actually establishes

Pinned `server/javelin/v3_request.py`'s structured retry parser requires at least62
bytes. It copies an **unchecked32-byte prelude**, then parses six bounded records:
BE32 numeric ID, one-byte string length, and that many Latin-1 bytes. The accepted
ID set is exactly0–5, independent of ordering. Bounds/IDs are checked; the prelude
does not supply a validated discriminator, field values are not authenticated or
schema-validated, and an opaque remainder is retained by the imported parser.
Its strict832-byte alternative is also a historical layout recognizer.

Current `scripts/carrier_registration_probe.py:443–465` tries the raw record or a
canonical imported length-unwrapped candidate. The surrounding filter checks the
prior connection ACK, one channel0 record and admitted flag conditions. The adapter
discards the parsed object and reports allowlisted metadata with
`exact_request_type_known=false`. No request body was read or recreated for #210.

The imported framing names flags0x21 as reliable plus data/channel-bearing. That is
a reference-model interpretation, not a new current-image Carrier decoder proof.
Payload size, flags, ordering and parser mode do not close a request-type join.

## J210-2 — current native producer and class identity

The selected current REP owner constructor `0x146b69ad0` installs vtable
`0x148590ab8`; setup retains a replaceable gateway at owner+118. The connection-result
closure `0x1485916a8` calls `0x146b713e0`. A successful connection getter sets
gateway+160, installs reception, then invokes the retained closure
`0x148591558`→`0x146b714a0`→builder `0x146b6e190`. The result callback is invoked
on failure too; the builder's gateway+160 gate routes that case to error handling.

| Conditional branch | Native constructor/class join | Owned map identity |
|---|---|---|
| V3 allocation0x470 | `0x146b66820`→vtable`0x147f479a8`, virtual+30→`0x1407cfca0`→`0x1407f2c50`; reflected name RegistrationRequestV3Msg | UUID`0B826B33-89F5-49E0-B8CB-FE4433427778`, index19/0x13 |
| Alternative allocation0x360 | `0x146b66a60`→vtable`0x147f478f0`, virtual+30→`0x1407cf9b0`→`0x1407f2a20`; reflected name RegistrationRequestV2Msg | UUID`DA4E5889-A65C-4480-8642-0278160125A7`, index2 |
| Selected response class | Incoming object's virtual+30 is compared by `0x146158ba0` to class descriptor `0x1407f2e80` in handler `0x146b6f190` | RegistrationResponseMsg UUID`104145a7-ff95-44f1-9468-21fb41c8ac2b`, index3 |

Both request branches call the same owner virtual+30→`0x146b706f0`, which wraps
the message through `0x146153e70` and calls gateway sender `0x146b6ffb0`.
Actual branch selection, live descriptor index, raw/UUID fallback and correspondence
to any860-byte candidate remain unknown. Map19 is a class-table join; it is **not a
measured first byte or record discriminator**. The response class/map3 similarly
does not validate the historical adapter's88-byte reply or a current response codec.

## J210-3 — concrete sender structure, with its layer gap

Gateway constructor `0x146b6a270` installs vtable`0x148590be8` in its embedded
writer at+108. Sender `0x146b6ffb0` obtains a stream through connection virtual+38,
calls the writer's first slot `0x146b0f430`, then submits the stream through
connection virtual+40. The selected writer performs these source-supported steps:

1. Reserve8 bytes using virtual+10→`0x146af7ba0`/stream virtual+48.
2. Write16 bytes from the supplied descriptor, or a default UUID pointer, through
   virtual+20→`0x146b0f640`/stream virtual+40.
3. Serialize the wrapped native message through `0x146167110`.
4. Patch the reserved header through virtual+18→`0x146b0f350`: first a calculated
   32-bit value from helper `0x1412f47d0` over bytes beginning at reservation+8,
   then a32-bit length counting descriptor plus wrapper/body bytes. The helper's
   exact checksum algorithm is not joined. Both writes use `0x140876cd0`→
   `0x1461656f0`→WS2_32 ordinal8. Static export inspection of the hashed installed
   WS2_32 identifies htonl and the byte-swap/return, supporting **BE32**.

This is the **pre-transport writer contract**. Selected stream creation
`0x146b27860`→`0x146b36600` obtains a pooled/new0xd8 object through`0x146a99bf0`
and stream pair through`0x146ae55b0`. Send`0x146b28e50` calls`0x140878c90` and
`0x146b3b3b0`, which transfers the shared stream pair, connection identifier and
flag into a32-byte entry in transport+190's locked queue. These selected routines
establish ownership transfer, not compression or compact-frame conversion. The
**consumer of transport+190 and physical buffer semantics of those stream helpers**
remain the precise bridge to Carrier placement and the receiving peer's inverse.
Do not treat these native writer steps as the actual
outer layout of the observed860-byte Carrier record.

The wrapper writer emits a flags byte, optional8-byte fields for bits0/1, optional
context fields for bit2, then a body-presence byte. Present bodies call
`0x1461673b0`: a registered class descriptor's+54 numeric index is written by
current compact writer `0x140877970`; zero selects a raw16-byte UUID fallback.
The descriptor's **field+48 contains a serializer object**, whose virtual+20
serializes the body. The constructor's `0x146165a00` can change native flags/IDs;
defaults cannot establish actual runtime wrapper flags. There is no proved fixed
32-byte prelude on this path. The current compact writer uses prefix-width encoding,
including a6-bit first-byte payload in the two-byte case; the imported general
7-bit length helper must not be presumed equivalent above127.

## J210-4 — current receive/typed decoding and remaining codec joins

The installed receive closure has the conditional static route
`0x148591708`→`0x146b714d0`→`0x146b6ba90`→`0x146af20c0`→`0x146af1d90`→
`0x146ae44f0`. The selected reader calls current compact reader `0x14087b5c0`
at`0x146ae453c`, stores length/parser state, waits for enough bytes, passes an
exact-length record stream to its callback, resets state and loops.

That callback follows `0x148591738`→`0x146b714b0`→child+158's retained closure
`0x1485915b8`→`0x146b71590`→owner `0x146b6eb70`. The same incoming record stream
reaches native wrapper decoder `0x1461ac8d0`. Flags are decoded through
`0x1461455f0`; body decoder `0x1417b2430` reads presence and resolves the type through
`0x1461ad130`→`0x1461acfe0`→`0x14087b5c0`. Index0 reads a raw16-byte UUID;
nonzero performs the bounded index-table lookup. Class lookup/factory selection
then allocates through dynamic descriptor virtual+10 and decodes through virtual+28.
Decode-success reaches response handler `0x146b6f190` at`0x146b6ed39`.

This consumer is concretely joined to the response handler, but its compact outer
length framing has **not been reconciled with J210-3's reserved header/descriptor**.
No extra16-byte descriptor skip is established in the selected receive route.
Transport direction/adapter/translation or distinct message layer remains a missing
join, not a reason to invent a matching envelope.

Native V3 virtual+50→`0x1407cfd10` queries the supplied serializer by interface UUID
`532e765a-3393-4a50-9010-b73c627512b2` from`0x1407fbc00` (owned map236, **separate
from message map19**). It calls the returned interface virtual+30 with seven field
arguments: scalar32-bit field+8, five field pointers (+10,+a0,+c0,+2c8,+3e0), and
scalar byte+460. Its local success return does not prove successful wire delivery.
The concrete implementation of that interface, complete field encodings, current
request-specific decoder and selected response-specific factory/virtual+28 remain
unjoined. Native offsets and interface map236 are not a wire schema/discriminator.

## J210-5 — retries, state and lifetime are separate contracts

| Authority | Source-supported current behavior | Limit |
|---|---|---|
| Application construction | Connection-result callback enters builder; gateway+160 must be set. A reconnect replaces the gateway | Event-driven path is established; no exact500ms periodic application retry, all triggers or repeated-record cause proved |
| Transport connection | Selected factory uses primary vtable`0x14858c358` and secondary interface at+8. Primary+308 states3/4/7 serve initiation/success/failure; getter`0x146b28390` tests4 | Other factory/runtime selection unknown; do not confuse secondary+300 with primary+300 connection identifier |
| Response handled | Selected class branch tests owner+600 then writes1 **before** status/other conditions. Duplicate recognized response while600 is set routes error2. Builder clears600 after dispatch at`0x146b6e667` | Handling is not acceptance; reentrant timing/thread effects unknown |
| Application accepted | Accepted branch writes owner+601 at`0x146b6f5ca`; getter`0x146b6df30` reads601; separate owner callback follows | Nonzero native byte+5b has branches that can rejoin acceptance. No universal `status==0 && byte5b==0` rule; no auth/ticket/peer semantics inferred |
| Disconnect and stop | Child`0x146b71530` directly clears gateway160, invokes retained owner route`0x146b6e7c0`, which directly clears601. Stop`0x146b70be0` nulls child, destroys/releases it and directly clears600/601 | No direct600 clear in selected disconnect body proves only local stores; external callbacks can alter state. Stop calls virtual+e0 afterward; final post-callback state and thread guarantees unknown |
| Callback disposal | Child destruction`0x146b6b6f0` invokes connection+88→`0x146b27ca0` unregister/clear callbacks before close/release and destroys retained closures | Raw owner captures make ordering relevant; cancellation does not prove no already-in-flight callback. No race was demonstrated |
| Carrier resend/ACK retirement | Selected queue-expiry lead`0x146b3c250` tests owner+fd or timestamp+1000*owner+e8<now, then indirect owner+48 virtual+20 | Exact callee, reliability resend/ACK-retirement, interval and retry-stop predicate unjoined; not proof of a registration watchdog |
| Local adapter budget | Current adapter MAX_PEERS8 retains per-peer identities; DTLS transport removes closed active peers separately | Eight lifetime adapter identities differs from eight active peers; successful local send sets v3_sent, not client acceptance |

## J210-6 — historical claims, missing joins and deferred work

The approved October4 version-trial receipt reports8 raw860-byte parser-compatible
candidates,8 local88-byte reply transmissions and24 Carrier ACK events:8 ranges2–3
and16 ranges2–4. Only the latter cover reply-bearing Carrier envelope4, across8
peers. Its reconnect/no-subsequent-non-system behavior and ninth-peer lifetime-budget
rejection are **historical metadata at their own source/run identities**. Later
approved actor/context observations are separate historical evidence. Nothing in
#210 reran those trials or retroactively recovered the discarded discriminator.

Keep these assertions separate: candidate parsing; local reply transmission;
Carrier ACK delivery; typed response callback; accepted601; subsequent client
behavior. None implies the next without its own evidence.

The acceptance outcome is a precise missing-join contract, with these unresolved:

1. Actual860-byte record discriminator/runtime request branch/registered index or
   UUID fallback. Discarded contents cannot be reconstructed from approved metadata.
2. J210-3 writer stream/send/compression/Carrier placement and its exact inverse;
   reconciliation with J210-4 compact-length receive framing and checksum algorithm.
3. Concrete V3 interface implementation/field encodings, current request decoder and
   response-specific factory/decoder. Imported retry recognition supplies none.
4. Actual current retransmission/ACK-retirement scheduler, intervals, all construction
   triggers and retry-stop predicate; relation of repeated records to those authorities.
5. Runtime factory/branch/callback ordering, reentrancy and in-flight cancellation
   guarantees. Selected direct writes establish conditional local ordering only.

Authentication/ticket/peer-binding semantics belong to211; player construction,
designation follow-ups, member fixtures and the generic subscriber remain excluded.
No related task was opened, claimed or changed. No contributor question was sent.
No response/codec, guessed framing, historical replay, credentials, client launch,
capture, hook, endpoint contact, EAC/system/trust changes, upstream edits or push.

## Verification, failed approaches and handoff

- Rehashed pinned inputs and selected function/data spans; decoder alignment and
  full selected PDATA/unwind blocks checked. Fresh build/version/reference identities
  and dirty-byte preservation are recorded separately from historical trial receipts.
- Independent ownership/lifetime evidence and targeted adversarial review retained
  conflicting branches. Corrected five-pointer/two-scalar serializer arguments,
  descriptor field versus vtable, handled-flag reset, post-callback state limits and
  exact ACK coverage. Static checks do not assert a compatible wire codec or gameplay.
- Failed leads remain historical: the parallel`0x146aaa130` route/class getter was
  not this concrete REP sender; an overlong vtable read crossed into ASCII and was
  replaced by bounded used-slot reads; a too-broad import-range heuristic failed
  uniqueness and was replaced by exact terminated IAT enumeration. No result uses
  data qwords as code. Framing agent capacity failures supplied no evidence.
- Source/document/preservation checks and the complete Test-Offline workspace result
  are recorded as executed verification in the receipt. Harness temp/loopback resources
  are isolated and its cleanup must pass; static helpers exited. No live cleanup exists.
- C1 identities/preservation; C2 exact joins/gaps; C3 falsification/separate authorities;
  C4 documentation/source/full workspace verification and focused local commit;
  C5 Resolution/Done/released claim and stop. Completion closes only210's research
  alternative, not parent178/164 or Milestone1. Missing joins remain explicit.

The final local commit and actual Actionables status/claim release are reported in
the completion handoff; no further task begins.
