# Current player identity BODY — #250

The pure [codec](../scripts/current_player_identity_body.py) encodes the first
two fields of the UUID-registered player member. It supplies original text
bytes for the synthetic `Preservation` character. It starts no client or
listener. The [receipt](../research/evidence/current-player-identity-body.json)
pins the owned image, type mapping, private source evidence and offline checks.

## Concrete member and field order

Current type index3935 maps to raw UUID `bddda784a6e7416ba041449920d90fb6`.
Getter `1468161e0` joins its descriptor/factory to constructor `146711e90`
and member table `148557af0`. The retained allocation's control table is a
different object. The constructor appends two groups; group1 has nine fields.
Its first two registrations are `characterId` at member+0x7c0 and
`characterName` at +0x870, whose value objects at +0x7d0/+0x880 match the
[PlayerFacet identity input](PLAYER_DESIGNATION_JOIN.md).

Only these two fields are selected here. Generic writers `141727cc0` and
`141728100` yield group mask02 and field mask03 when both are present and all
other fields are absent. The continuation bit depends on the highest present
field, not the nine-field registration count. Fresh constructor metadata alone
does not mark these fields present; selection is an explicit offline input.

| Selected field | BODY bytes after masks |
|---|---|
| CharacterId | flag00, compact32 byte length, unchanged stored text |
| CharacterName | compact32 byte length, unchanged stored text |

The native ID writer also has a flag-selected raw16 sidecar branch. This codec
supports flag00 only, avoiding an unjoined string-to-sidecar setter. Native
length writer `140877970` and reader `14087b5c0` match the existing compact32
helper. Both text readers bound the decoded length at0x2ffff. Native writers
normalize an over-limit string to empty; this offline API instead rejects it.
There is no implicit Unicode conversion or UUID byte-field swap.

The original53-byte control is `02 03 00 24`, the36 bytes
`00000000-0000-4000-8000-000000000020`, then `0c` and the12 bytes
`Preservation`. That ID comes from the repository's synthetic queue fixture.
It is not the user's official character ID or an authenticated game identity.
Decode returns the consumed prefix and leaves a following record untouched.
Other groups, fields, continuation masks and ID flags are refused deliberately.

## Decode, reconciliation and delivery

Successful CharacterId and CharacterName readers set their field-present bytes
at field+0xa0/+0x68. Generic BODY decode does not directly set member+0x7a0.
The member's ordinary reconciler `14172ce70` consults field virtual+0x60 and
can enable that byte; member virtual+0x20 reads it. The queued replay path
`14167a490` calls `14167b2a0` with reconciliation enabled before testing the
gate and dispatching facet virtual+0xb0. PlayerFacet's target is `14683c8d0`.
These are conditional static call paths, without native execution.

The record member key selects a component in the cloned root's vector+0x160;
it is separate from typeindex3935. `14171bbd0` builds this vector. The client
setting `javelin.set-replication-index-on-creation` selects either assigned
zero-based component ordinals or the resource's reflected
`FacetedComponent.m_replicationIndex` (offset0x90, four bytes). In the latter
branch zero is omitted and duplicate indexes overwrite a slot. Configuration
is refreshable; false is the no-handler fallback, not an observed runtime value.
The selected resource's actual field and qualifying component order remain to
inspect. Neither3935 nor a guessed0 is an established delivery key.

This unit proves an original identity BODY subset and its source joins. It
does not prove the asset load, component index, queue provider's runtime ID,
local registry designation, context readiness, spawn, visible world entry or
Milestone1. Those remain acceptance gates for the assembled candidate.
