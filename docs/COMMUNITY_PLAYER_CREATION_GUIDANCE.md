# Community player-creation guidance

The user relayed Open World Discord replies on October 6, 2026, then asked to
retain the information and defer further questions while we investigate locally.
The full Rust snippet and its comments are in the ignored
[private reference](../private/community-reference/gde-ref-discord-20261006.md).
Contributor identities, message links, license, generator revision and tested
client/build were not supplied. This is an original summary, not imported code.

## Reported resource and identity contract

| Lead | Community report | Project verification boundary |
|---|---|---|
| Player resource | AssetId should identify `player.dynamicslice` | Its exact AssetId, trailing uint32 value, owned-build availability and successful instantiation remain unverified. |
| GdeRef lifetime | Deterministically derived from a character UUID, intended to stay static per character | The same input and fixed helpers/constants make the shown construction repeatable. This establishes no authentication, reconnect policy or local-player designation. |
| Low half | First eight wire bytes are `low64` in little-endian order, called the SHORT ID / `facet_target_id` | The current member decoder already preserves raw16 and derives its first LE qword as the creation key. The facet-target label/relationship is a community lead. |
| High half | Final eight bytes are `high64` in little-endian order | This is explicit in the supplied function; broader high-half semantics remain unknown. |
| Generation constraints | Both qwords nonzero; low64 even, so byte0 bit0 is clear | The low-half parity fits the current native mode-2 predicate below. No full GdeRef validity contract or successful local spawn was executed here. |

The snippet uses two mixed/hash-derived halves, clears low64 bit0 and replaces
a resulting zero low64 with 2. `K1`–`K4`, `splitmix64` and `force_nonzero` were
omitted, so the exact converter cannot be executed from this excerpt alone.
Its constants/hash recipe are not established as protocol requirements. Distinct
hash expressions also do not prove that the halves can never coincide.

The comments attribute a Frida/live result to July 5, 2026 and name
`javelin.offline-id-version = 2`, `local-player-gde-identity.md` section 1 and a
module-level `gde_ref mint` note. Those documents, the measured configuration,
tested binary and live result were not provided or reproduced.

## Current static support and limits

The [member BODY contract](CREATION_MEMBER_BODY.md) joins raw GdeRef to its first
little-endian qword. The [application contract](PLAYER_MEMBER_APPLICATION.md)
joins that key to `146165f20`, then to `14178db00`'s false-predicate creation
dispatch. The owned image is version `1.400.6031.6004151`, Steam build `22469132`,
SHA-256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
Exact native spans and artifact identities remain in the
[existing source receipt](../research/evidence/current-player-member-application.json).

The retained instruction trace has multiple numeric-mode branches:

- Mode 2 returns either key bit0 or whether the low three bits equal 1, depending
  on helper `14615e330`. An even key makes both predicates false and permits the
  creation-dispatch branch. Some odd keys are false in the low-three-bit branch;
  the community statement that every odd key skips creation is not a universal
  conclusion from this source.
- Mode 1 tests whether the key's upper 32 bits are zero. Other modes return false.
  Clearing bit0 alone does not characterize every mode.
- Actual mode/helper values remain unobserved. Creation dispatch still depends on
  active handlers, interception, maps, resource readiness, binding and designation.

The intake cross-check rehashes the pinned image, the two native code spans and
their retained instruction artifacts. It checks the parity/registrar instruction
bytes and an inert model of both mode-2 predicates for all 256 byte0 values.
These are static/offline checks, not executed client code or accepted gameplay.

October 6 intake validation passed: image/span/artifact hashes, 11 exact
instruction checks, the 256-case byte0 model with retained mode/helper
counterexamples, document links and ignored-source checks. The private
[intake review](../.scratch/discord-gde-ref-intake-20261006/review.json) retains the
identities. The required `workspace` profile also
[passed](../.scratch/offline-validation/run-ac6nnqqt/receipt.json); the client and
supplied Rust generator were not executed. Later edits only record these results.

## Continue locally; defer questions

The user's October 6 preference is to avoid further contributor questions for
now. Use these leads for the next authorized local investigation:

1. Resolve `player.dynamicslice` to its exact resource metadata and both AssetId
   fields in the owned copy, retaining client-derived material privately.
2. Trace the mode initializer/helper and any remaining GdeRef constraints. Preserve
   the distinction between field encoding, native branching and runtime selection.
3. Establish the low-key/entity/facet/character relationships before selecting
   values or implementing a generator. Validate any original implementation with
   inert stability, byte-order, parity and sentinel cases under its actual scope.

If local work reaches a concrete unresolved blocker, the named identity/mint notes
are possible future references. No new question is due now. This intake changes
no live procedure, protocol code, Actionables acceptance or Milestone 1 result.
