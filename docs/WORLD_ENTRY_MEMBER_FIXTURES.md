# Current world-entry member fixture gate — #212

Actionable **212**, workItemId **164**, parent **179**, is **Blocked**. Fixture
validation is incomplete: **zero fixtures created and zero positive, truncation
or unknown-type fixture-decoder cases executed**. This is a prerequisite audit
and handoff, not completion of the requested fixture outcome. The exact receipts,
fresh input hashes and executed checks are in the
[original readiness receipt](../research/evidence/current-world-entry-member-fixture-readiness.json).
Current progress remains in [ROADMAP](ROADMAP.md); evidence claims are K210–K213.

## Scope and acceptance recorded before changes

Only #212 was claimed, then entered Researching. Its complete task description,
scope, acceptance criteria, planned checks, ownership and exclusions were read
and recorded in Actionables before tracked edits.

Acceptance requires original, source-supported current world-entry fixtures with
exact build, type, body, channel, direction and state; exact framing/member fields
and consumed/output-size boundaries; and meaningful positive, truncation and
unknown-type cases against the actual decoder. A positive construction/member
contract and relevant registration framing are prerequisites. A local round trip
establishes agreement between local implementations, not current-client compatibility.

Planned checks: (1) refresh checkout/build/type-map/reference/source identities;
(2) verify the positive prerequisite contracts, including their explicit limits;
(3) construct fixtures and exercise decoder cases only if those gates pass;
(4) otherwise verify the exact blockers and preservation, run the required workspace
offline profile and record all fixture checks as unrun; (5) validate task-owned
documents/metadata, commit locally, hand off #212 Blocked, release and stop.

Owned edits are this report, its receipt and small #212 insertions in TASK_BRIEFS,
ROADMAP and EVIDENCE_LEDGER. No codec or test implementation is admitted after the
failed gate. Excluded: resolving construction, designation, authentication or
framing gaps; other tasks including #213; guessed messages, historical actor/persona
replay, client launches/process reads/hooks/captures, game endpoints, credentials,
hosts/trust/EAC changes, upstream changes, publishing/push or contributor messages.

## Current input identity and evidence limits

Audit checkout: clean main at `d4b6a2c535c5d9f8f48293c235f4767cfb575e48`, with
221 tracked paths snapshotted before edits and 33 selected source/input bindings.
The initial Git display was ahead 3; a later local ref comparison was ahead 0 at
the same HEAD. This task performed no fetch or push and assigns no cause to that
ref change. Existing commits and underlying shared-document bytes are preserved.

Fresh on-disk checks match Steam app **1063730**, build **22469132**,
FileVersion/ProductVersion **1.400.6031.6004151**, executable size **179204176**
and SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
The existing approved private type map rehashes to
`f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75`;
it was not regenerated. First Light `63756a3f7ff0ae41752dcc7c80267802c3fa7548`
and Aeternum `820156dbc44c86c9436af81aa0dba72e94cb636b` are clean and pinned.
The four imported source files sealed by #210 still match their recorded hashes.

The read-only preflight reports older #208/#209 receipts with changed public
documentation/configuration inputs. Those executions retain their historical
identities. This audit freshly hashes their reports/receipts and the same owned
image, but reruns neither native analysis nor private/live observations. Matching
hashes do not prove an unknown join or upgrade a prior experiment. The gate result
means the reviewed positive contracts are insufficient, not that another path is
impossible. #211's selected response factory/field decoder narrows #210's earlier
factory gap; it does not complete helper encodings or framing.

## Exact blocking dependencies

| ID | Required positive contract | Current boundary and required resolution outside #212 |
|---|---|---|
| B212-1 | Concrete decoded member creates a fresh player | #208 MJ208-1 stops at class descriptor+48, factory create+8, member decode+90 and application+38/+48/+60. The implementation/adapter connecting these to PlayerComponent creation is unknown. Member index alone is not class selection. Identify the concrete class, callbacks and complete field codec. |
| B212-2 | Member fields have valid entity/context and lifetime semantics | #208 MJ208-2–4 leave fresh gameplay entity allocation, valid key+58, tuple+40/+48/+50 and owner-map/context writers, memory/control/guard authority, and construction/registration/invalidation/removal/disposal order unjoined. Defaults and registry insertion supply no valid player identity or lifetime. Resolve these before assigning semantic fixture values/state. |
| B212-3 | Exact current transport/framing and consumed/output boundaries | #210 J210-3's reserved 8-byte header, 16-byte descriptor and queued streams are not joined through the transport queue consumer/physical buffers/Carrier placement and inverse to J210-4's compact-length receive. The checksum algorithm is also unresolved. A current compact integer helper alone cannot establish outer member/message boundaries. |
| B212-4 | Current type-specific body encodings at that framing boundary | #210's actual historical 860-byte discriminator/runtime branch/index or UUID fallback and complete V3 request field codecs remain unknown. #211 joins a selected response factory/field decoder, while its helper encodings and transport placement remain unknown. Native fields/map indices and imported 860/88-byte shapes cannot become current wire fixtures. |

Source references: [#208 construction and required joins](PLAYER_CONSTRUCTION_JOIN.md),
[original #208 receipt](../research/evidence/current-player-construction-join.json),
[#210 framing/type contract](INITIAL_REGISTRATION_CONTRACT.md) J210-3/J210-4/J210-6,
and [#211 codec dependency boundaries](REGISTRATION_AUTHENTICATION_CONTRACT.md) J211-3/J211-6.
These dependencies are documented; no Actionables dependency edges were created
or changed, and no prerequisite task was claimed, reopened or worked.

[#209](PLAYER_DESIGNATION_JOIN.md) adds conditional string classification, keyed
readiness, early designation latch and guarded registry-result conditions. Its four
construction/authority/lifecycle prerequisites remain #208's unknowns; none
supplies member wire fields or a fresh player's valid state. Context readiness
remains a separate condition. #209 Done therefore cannot unlock B212-1/B212-2.

[#211](REGISTRATION_AUTHENTICATION_CONTRACT.md) separately lacks authoritative
issuer/validator/claim-store, semantic producer/provider, subscriber authority,
principal/ticket-to-peer and cancellation/generation joins. These additionally
gate any fixture claiming authenticated identity or ticket semantics; they are
not a blanket prerequisite for an inert constructor-default body. No authentication
fixture or private security design was substituted here.

## Decoder review and rejected shortcuts

The actual pinned source was read without importing or executing reference servers:

- First Light `server/javelin/frame.py` parses Carrier record headers and payload
  sizes into records. Its local framing behavior is a reference implementation;
  it does not resolve B212-3 or a current fresh-player schema.
- First Light `server/javelin/dispatch.py:92–149` sends type8 to
  `chunked_stream_08.decode_either`; unregistered types return `None`. The type8
  decoder validates a historical anchor or minimum 16-byte fallback and retains
  the remainder as `opaque`. Its encoder concatenates those bytes. Such a round
  trip cannot validate current member fields, unknown-member rejection or gameplay.
- Aeternum `Tools/nw_capture/decode_dtls_ledger.py:118–232` parses Carrier/LZ4,
  preserves opaque message payloads and returns leftover trailer bytes. These
  outputs do not decode current PlayerComponent members or prove full consumption
  at the missing application/member boundary.
- The original `current_world_activation.py` encodes a default empty type8 body
  of 6 bytes. It supplies no member/entity/player payload. The original Self codec
  emits 127 default body bytes and a 4-byte typed header. Reusing either cannot
  satisfy a positive current world-entry member fixture.

The [Self prefix contract](../research/evidence/current-self-length-prefix-contract.json)
and [closed trial](../research/evidence/current-self-length-prefix-trial.json)
support only the exact 131-byte typed SelfIdentification candidate, changing
`83 01` to `83 02` with its body unchanged. Prior callback/self-flag/context
observations are historical at that run's identity. They neither identify nor
generalize the outer reader and supply no nonempty member schema. No trial was rerun.

## Acceptance checks and executed verification

| Requested fixture check | Outcome |
|---|---|
| Exact build/type/body/channel/direction/state for a positive current member | Blocked by B212-1/B212-2; image identity is verified, member fields/semantics are unknown |
| Exact member/framing consumed and output sizes | Blocked by B212-1/B212-3/B212-4 |
| Meaningful positive member case against actual decoder | Unrun; no admissible fixture constructed |
| Truncation boundaries and unknown-type/member rejection | Unrun; no admissible positive baseline or current member codec |
| Round-trip agreement and current-client compatibility | No new round trip executed; no current-client compatibility claim |

Executed before report edits: validated read-only project preflight, 12 original
identity/explicit-contract checks, fresh image/map/reference/source hashes and the
221-path preservation baseline. Decoder findings above are source inference, not
executed decoder cases. The workspace profile, run through validated `Test-Offline.ps1`,
ran October5, 17:11:45–17:12:58 America/Phoenix: **469 Python cases across33 files**
passed with zero failures/errors/skips, all three synthetic PowerShell suites passed,
and the owned127.0.0.1 HTTPS child returned200/exited0 with its listener closed.
No selected input changed during the run. Raw receipt:
`.scratch/offline-validation/run-6psj50vw/receipt.json`.

The original document review passed292 integrity/preservation/link checks:218
unrelated tracked paths,30 unchanged selected bindings,26 local links, and exact
underlying bytes beneath all three #212 insertion blocks. Report verification text
and receipt metadata were finalized after the workspace run; focused document/
preservation checks then recheck that final state. Exact commands/results/hashes
are recorded in the readiness receipt. This verifies repository regression and
report integrity; it does not satisfy any unrun fixture check.

Resources are the unique ignored `.scratch/actionable-212-20261005T1703/` metadata
and the offline harness's isolated temp/loopback resources. No game, shared service,
fixed port, capture, native instrumentation or credential resource is used. The
harness must verify its owned child/listener cleanup; unrelated resources remain
untouched. Original metadata is eligible for the local commit; private raw output
and client-derived content remain ignored.

Handoff: keep #212 **Blocked**, with fixture acceptance unmet, and release its claim
after the focused local commit and actual validation are recorded. Resume requires
separately authorized positive construction/member and relevant framing/body
contracts closing B212-1–B212-4 at freshly bound inputs. No resolution of those gaps,
new task, #213 work, client trial or publication begins in this session.
