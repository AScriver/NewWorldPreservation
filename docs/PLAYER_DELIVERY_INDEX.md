# Owned player delivery index — #251

The owned `slices/player.dynamicslice` contains one `PlayerComponent` with
`FacetedComponent.m_replicationIndex` bytes `00 00 00 09`. Under the pinned
public ObjectStream-v3 grammar this is unsigned index9. It is a conditional
candidate for the resource-index branch identified in
[the identity contract](PLAYER_IDENTITY_BODY.md), not an observed runtime key.
The [original bounded reader](../scripts/owned_player_delivery_index.py) and
[metadata receipt](../research/evidence/owned-player-delivery-index-20261006.json)
retain the field selection, input pins, checks and limits.

## Owned file and format observation

The earlier [resource lookup](OWNED_PLAYER_RESOURCE.md) supplies the exact
catalog key and ZIP member. This separate file-only inspection verified the
same image/package pins, local-header identity, unencrypted method15 member,
44,796 compressed bytes and 367,528 declared output bytes. Method15 alone does
not identify a standard compression codec. The selected `8c 06` header admits
the public Kraken-type6 decoder; a standard-ZSTD magic assumption was rejected
before decoding.

A clean ignored checkout of [powzix/ooz at0503806](https://github.com/powzix/ooz/tree/05038060aa68f9187ae9923b2388ca8db40e58d1)
was built with MSBuild18/MSVC14.50.35717/v145. Its source header permits GPL3
or later; source/build outputs remain external and ignored. Flags `-dq` select
the public decompressor rather than a client DLL. The tool's eight-byte output
length prefix is an analysis container, not a game wire format. An original
32-byte stored-block control decoded unchanged. The selected asset then matched
its original ZIP CRC32 `a52d1752` and SHA256
`513e5f9bc3f8ca9896fdea164c9889dfbf2bd9587d7273f19395b1b83b3af377`.
Upstream build warnings are retained; no native game code was executed.

The decoded file has a binary-tag0, big-endian version3 header and one Entity
root. The original structural reader consumes all12,242 nodes and the complete
extent. It selects exactly one PlayerComponent, its direct FacetedComponent
base, and one direct field with name CRC `81e598c5`, raw type UUID
`43da906b7def4ca89790854106d3f983`, and four value bytes. Unrelated component
contents, asset bytes and decompilation stay ignored.

The metadata grammar and BE32 interpretation are cross-checked against pinned
public [O3DE ObjectStream](https://github.com/o3de/o3de/blob/3be07620eeec2c66b8426804c24572df2972e559/Code/Framework/AzCore/AzCore/Serialization/ObjectStream.cpp)
and [primitive serializers](https://github.com/o3de/o3de/blob/3be07620eeec2c66b8426804c24572df2972e559/Code/Framework/AzCore/AzCore/Serialization/SerializeContext.cpp).
These public references are not proof of the current client's primitive Load
callback or successful native asset instantiation.

## Current-image joins and configuration limit

PlayerComponent constructor `146711440` installs table `148536b70`. Its
virtual0 leaf `1465827c0` reaches UUID getter `141048fe0` and the literal
`D50340CF-A082-4B90-9933-8C42387C0C77`; the same table's name getter returns
`PlayerComponent`. The selected asset class matches these current-image facts.
Separate reflection-registry insertion was not traced in this pass.

Current FacetedComponent reflection registers `m_replicationIndex` at offset
0x90, width4, using primitive type getter `1407867a0`. Native CRC routine
`1412f4730` folds ASCII uppercase to lowercase before reflected CRC32 with
polynomial0xedb88320 and initial/final xorffffffff. All256 table entries and
the computed field CRC agree with the asset; using case-sensitive CRC would
select the wrong field. Exact instructions/tables and private artifact hashes
are sealed separately from the file observations.

The exact setting `javelin.set-replication-index-on-creation` is absent from
the inspected loose `bootstrap.cfg`, `system_windows_pc.cfg`, `engine.json`
and the CRC-verified1952-byte packaged `client.json`. This does not determine
runtime provider values, precedence, refresh or selected mode.

| Runtime branch | Source-supported interpretation | Remaining gate |
|---|---|---|
| Setting false | Baked field9 is a candidate vector key; zero is omitted and duplicates overwrite | Current native Load and actual mode/instantiation unobserved |
| Setting true | Eligible instantiated components receive traversal ordinals from0 | Selector qualification and runtime entity/component order unobserved |

Serialized node counts or asset order cannot substitute for a runtime assigned
ordinal. Neither class index3935 nor an assumed ordinal0 establishes delivery.

## Offline API and continuation

`parse_player_delivery_index(bytes)` accepts a strict bounded v3 subset and
returns the selected scalar, offsets and node count. It rejects ambiguous class/
base/field selection, wrong primitive width/type, unsupported flags, incomplete
trees, trailing data, mutable input and byte/node/depth bounds. It does not
instantiate or convert classes. `read_pinned_player_delivery_index(Path)` reads
only the exact size/hash-pinned decoded artifact under this project's ignored
`.scratch` or `private` directories. Artifact production, package/CRC verification
and native source identity are separate receipt-recorded procedures.

Synthetic tests use original bytes only. Required workspace and focused results
are recorded in the receipt and ROADMAP. The reader launches no decoder, client,
listener or service and changes no game/configuration files.

The user requested pause after the next commit. Close this unit, commit locally
and release tracking, then pause. Child252's original creation/identity type8
composition remains unstarted. No live-send authorization is added here. Native
loading, player designation, context readiness, visible Preservation world entry
and Milestone1 remain unobserved; two-player acceptance awaits a consenting friend.
