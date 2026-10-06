# Original two-member player creation candidate — #252

The inert [composer](../scripts/current_player_creation_candidate.py) connects
the proved [creation BODY](CREATION_MEMBER_BODY.md),
[identity BODY](PLAYER_IDENTITY_BODY.md), [record codec](CREATION_REPLICATION_RECORD.md)
and [type8 BODY](TYPE8_BUNDLE_BODY.md). It constructs exactly one explicit record
with two class-specific members and returns its record, BODY and typed bytes.
It starts no backend/client and sends nothing. The
[receipt](../research/evidence/current-player-creation-candidate.json) records
source/input identity and actual offline verification. WorkItem164, parent248,
child252; the [one-player milestone](ONE_PLAYER_MILESTONE.md) remains pending.

## Explicit inputs and source constraints

`compose_player_creation_candidate` requires every input; no runtime value is
selected implicitly:

| Input | Candidate policy | Evidence / limit |
|---|---|---|
| AssetId | Exact owned raw16 `a660eeebebc75cb7be6bab11eb831731`, suffix2 | Owned catalog/package join; native asset load unobserved |
| Assigned GdeRef and occupied low64 set | Reuse caller's raw16 unchanged; current trial-ref policy must pass | Known keys are caller-supplied, not live map observation or guaranteed root entity ID |
| Character ID/name | Both nonempty immutable NUL-free byte strings | Stored-text codecs; ID setter's first-NUL scan motivates stronger candidate policy, not native BODY rejection |
| Record slot and creation key | Explicit uint16/uint32; creation key strictly below identity key | Reader inverse; sorting keeps creation first on inspected1–32-member route; no valid runtime slot chosen |
| Delivery mode/key | Explicit `resource-index` and identity key9 | Conditional on runtime setting false and native resource/component loading; no assigned ordinal assumed |
| Class indexes/table | Explicit nil-first immutable UUID table; each nonzero index resolves to its BODY class, or explicit0 emits raw UUID | Configured table and cached native selectors remain runtime conditions |

The current owned map file has creation UUID at10 and identity UUID at3935;
those are checked file positions, not guaranteed live selectors. Raw UUIDs avoid
the indexed-table lookup, but still require a registered descriptor/factory.
Unknown classes, mismatched indexes and unsupported BODY shapes fail without an
opaque-payload escape or skip. Lower-level record behavior preserves caller member
order/duplicates; the candidate separately enforces its two-role ordering policy.

Freshness is the caller's responsibility. This helper neither generates a
character nor derives GdeRef from character text. In an integrated trial a new
backend-owned character ID must reach login-info, queue and this identity member
unchanged; the existing independent fixed fixtures do not achieve that.

## Composition and extent

The record codec now selects only the two established BODY types by corresponding
UUID. Its key/selector/BODY writer is source-joined; outer slot/count encoding
remains inverse-reader experimentation because the native producer is unjoined.
The composer places one record in a constructor-default `BundleBody`, then uses
the existing three-byte current type8 header. It adds no Carrier wrapper, ACK,
cursor allocation, retransmit state or live-send option.

Original synthetic goldens use16 `I` bytes for ID and32 `N` bytes for name;
these are test values, not a previous game identity. Creation BODY is38 bytes,
identity BODY53. Explicit slot0, creation key0 and identity key9 give:

| Explicit selectors | Record payload | Type8 BODY | Typed message |
|---|---:|---:|---:|
| Raw0/0 with both UUIDs | 129 | 136 | 139 |
| Indexed10/3935 | 98 | 104 | 107 |

Raw payload length129 uses the proved current compact prefix `81 02` inside
the BODY. The **outer application-length** reader/placement remains a different
unjoined boundary. The admitted131-byte SelfIdentification comparison cannot be
applied to this139-byte candidate. Indexed107 stays below128 for these test
inputs; choosing that path still requires the current runtime class table.

Decoders return consumed record/BODY prefixes and exclude enclosing suffixes.
Unknown classes and malformed identity BODYs return no successful partial record;
this offline API does not simulate native partial mutation, drain, rollback,
scheduler state, application or player creation.

## Verification and remaining transition

The receipt retains literal/round-trip, proper truncation, mixed selector,
precise failure offset, suffix ownership, missing input, numeric/mode/key/asset,
strict ordering, NUL and collision checks. Source refresh rehashed the owned
image/mapping,193 native spans,77 finite windows,361 private artifacts, four
owned file pins and two public reference files. These are disk/static checks.

The latest real-client behavior remains context initialization followed by spawn
timeout under an empty bundle. Native class/mode selection, loading, cloning,
binding, local-ID provider/readiness, designation, camera/input, movement and
restart repetition are unobserved. This candidate makes a concrete nonempty
experiment possible; a new send is outside the currently enumerated trial
exceptions. Fresh identity propagation and a reviewable bounded integrated trial
must precede any required approval or live attempt. Do not rerun the unchanged
empty bundle or infer gameplay from these offline checks.
