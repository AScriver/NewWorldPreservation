# Community feature catalog

The user supplied `feature-slices.md` from a Discord post on October 6, 2026.
The complete download is retained in the ignored
[private project copy](../private/community-reference/feature-slices-20261006.md).
Its SHA-256 is
`15d2a820b4cd26fc391747f011b49309c44728ead50e2934b31197bc0baca9ff`.
The [original review receipt](../research/evidence/community-feature-slices-review.json)
records the source, mapping/image identities, comparison and failed native-name query.
The upstream URL, generator revision and license remain unknown; the raw catalog
is kept private. This document is an original summary of relevant findings.

## What was verified

All **3,486 unique index/UUID pairs** agree with the retained **7,052-entry**
type mapping used in the owned-image investigations. No duplicate index, duplicate
UUID or mismatched pair was found. This establishes agreement with that retained
mapping; original generator build, native class names, runtime registry selection
and actual emitted wire indices are separate questions.

The catalog groups 1,824 facet entries into 184 component slices and 1,662
non-facet entries into 179 namespace buckets. Its client facets are labeled
server-to-client and server facets client-to-server. These directions are community
classifications. Non-facet entries also include reflected data, traits and internal
actor types; catalog inclusion alone does not establish a client/server packet.

## Leads for the current work

Indices below are decimal, with hexadecimal shown explicitly. Names and
directions remain attributed to the community catalog.

| Index | Community class label | Relevant project work |
|---|---|---|
| 10 / `0x0a` | `MB::GdeMetadataReplicatedState` | [Creation member](CREATION_MEMBER_BODY.md), M1-06A: matches UUID `203dc8c7-0c60-454b-a46f-566114314b84`, whose AssetId/GdeRef BODY and conditional application were already source-supported. |
| 13 / `0x0d` | `MB::PositionInTheWorldReplicatedState` | [Actor baseline and delta brief](TASK_BRIEFS.md#m1-08--actor-baseline-and-delta-encoding), M1-08: UUID `79c28008-4fc5-4efb-88a1-538f4fb7dde1` is a concrete position-state research target. |
| 5181 / `0x143d` | `Javelin::ClientMessages::PlayerComponentServerFacet_OnAckLevelInfoChanged` | [World-entry brief](TASK_BRIEFS.md#m1-06--current-registrationworld-entry-contract), M1-06: UUID `971ddbb2-67db-4beb-9632-85851d0ee00e`, labeled client-to-server, is a level-information acknowledgement lead. |

For index 10, the existing native BODY writer/reader table slots were rechecked
and matched their recorded targets. A separate guarded RTTI query did not
establish the friendly class name; no type-name parse followed the failed guard.
The community label therefore supplements the existing UUID evidence without
renaming it as a native-confirmed class or supplying valid player state.

For index 13, join the actual descriptor/factory to its paired writer/reader and
application path before deriving fields, quantization, transforms or ownership.
No position layout or codec was verified by this catalog review. Decimal 13
(`0x0d`) is distinct from decimal 19 (`0x13`), the retained V3 registration entry.

For index 5181, verify the facet envelope, actual handler and ordering before any
use. The method name establishes no payload, readiness transition or Carrier
ACK/resend semantics. It adds no message to the admitted live-trial procedure.

## Alignment with existing investigation names

| Retained index | Community label | Existing project reference |
|---|---|---|
| 8 / `0x08` | `Amazon::Hub::ReplicatedStateBundle` | [Type 8 BODY contract](TYPE8_BUNDLE_BODY.md) |
| 19 / `0x13` | `REPClient::RegistrationRequestV3Msg` | [Identifier placement](REGISTRATION_IDENTIFIER_PLACEMENT.md); mapping position is not an observed emitted selector. |
| 1617 / `0x651` | `Javelin::ClientViewListenerTrait::ReceivePlayerSpawnPointMsg` | [Spawn evidence](SPAWN_SEQUENCE.md) and [admitted trial](CARRIER_REGISTRATION_TRIAL.md) |
| 1628 / `0x65c` | `Javelin::ClientMessagesTrait::PlayerManagerSelfIdentificationMsg` | [Spawn evidence](SPAWN_SEQUENCE.md) and [admitted trial](CARRIER_REGISTRATION_TRIAL.md) |
| 1635 / `0x663` | `Javelin::ClientMessagesTrait::LevelInfoChangedMsg` | [Spawn evidence](SPAWN_SEQUENCE.md) and [admitted trial](CARRIER_REGISTRATION_TRIAL.md) |

These alignments provide source-navigation labels. Existing native/source and
private-trial evidence retains its original scope; no new gameplay result follows.

## Companion sources named by the download

| Companion | Why it would help |
|---|---|
| `uuid_to_class.json` | The catalog says Marshal/Unmarshal addresses are retained here, keyed by `type_idx`; compare their build identity before selecting native functions. |
| `catalog.md` | Defines the source schema, including type index, name, handler entries and RTTI namespace. |
| `facets-rmi.md` | Describes the facet RMI layer; evaluate it against the native envelope/dispatch path before implementing it. |
| `gen_feature_slices.py` | Explains how source records become feature slices and how names/directions are classified. |

These companions were not found beside the download and are not represented by
placeholders or inferred layouts. Current status and Milestone 1 acceptance remain
in [ROADMAP](ROADMAP.md). This source intake changes no Actionables state,
protocol implementation or live-operation authorization.
