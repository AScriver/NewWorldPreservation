# Original fresh GdeRef trial inputs — #249

The pure [input helper](../scripts/current_creation_trial_ref.py) selects and
checks an original raw16 reference for a bounded creation candidate. It enforces
the current source's local routing constraints and a caller-supplied collision
boundary. Passing this policy does not establish native identity validity or
successful player creation. It starts no client, listener, capture or hook.

The [receipt](../research/evidence/current-creation-trial-ref.json) pins clean
`6f74c1e` source input, owned image version1.400.6031.6004151/build22469132,
current type map, references, private source seals and executed verification.
Nine fresh function slices and20 instruction assertions support the native
claims. All native behavior described here is static inference.

## Routing and identity

`146165f20` obtains `javelin.offline-id-version` through `140fc7f90`; mode2
also uses `14615e330`'s `javelin.enable-offline-capitals`. These are cached
process configuration results, latched after first dispatch even when no
handler writes a value. The incoming GdeRef cannot choose them. Actual
providers, runtime values and all reset paths remain unknown.

| Inspected configuration | Predicate that selects the alternate route |
| --- | --- |
| Mode1 | upper32(low64)==0 |
| Mode2, helper true | low64 bit0 is set |
| Mode2, helper false | (low64&7)==1 |
| Other numeric mode | false |

Predicate false admits the creation dispatcher in `14178db00`; it does not
guarantee construction. This helper conservatively requires **even low64 with
nonzero upper32**, which makes every shown predicate false. Small even2 and
odd3 are counterexamples to simpler policies. The helper preserves all chosen
bytes instead of repairing a failing value or guessing a community hash recipe.

The key is `int.from_bytes(raw16[:8], "little")`. `141747c60` compares this
low64 alone in the shown operation and receiver maps. Changing high64 cannot
avoid that collision. Both API calls require an explicit immutable uint64
`occupied_keys` set; it covers only the caller's known keys, without observing
live client maps. `new_trial_ref` makes at most128 independent16-byte draws.
The caller assigns the returned bytes once and reuses them in dependent records.
This assignment policy is original; no native character UUID/name generator
or persistence rule has been reconstructed.

## Independent construction gates

`1416631d0`'s deferred setter continuation also requires a live operation,
nonnull receiver, state2, nonzero AssetId raw16 and nonzero GdeRef raw16.
`1407f7d80` establishes the GdeRef comparison default as all-zero16.
A zero high64 with nonzero low64 passes that particular comparison; the helper
therefore accepts it. Neither examined gate requires UUID version bits,
different halves or the community's missing K1–K4 constants.

`14171e370` independently refuses source resource key `00000000ffffffff`.
Source flag mask0x04 chooses preserved entity IDs or
`oldId XOR sourceKey XOR requestedKey`. Resource source IDs, flags and keys
control the resulting IDs. A fresh requested key alone cannot guarantee that
the root receives it, that remapped IDs are unused, or that component binding
and local designation succeed. Those resource/runtime conditions remain open.

Original synthetic controls cover byte order, zero-high acceptance, same-low
collisions, alternate-route counterexamples, immutable input, uint64 bounds,
unchanged draws and exhausted/broken draws. They establish the Python policy,
not native execution. Aggregate tasks247/190/177 and Milestone1 remain open.
