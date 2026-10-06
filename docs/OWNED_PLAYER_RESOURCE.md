# Owned player resource input — #246

The file-only lookup resolves the exact owned `slices/player.dynamicslice`
catalog record to raw16 `a660eeebebc75cb7be6bab11eb831731` and uint32 **2**.
Both primary and associated catalog keys agree. These supply a concrete input
candidate for the existing creation AssetId field's raw16/BE32 representation.
The lookup uses the exact path record without hashing a filename, choosing a
nearby UUID, decompressing assets or executing client code.

Work item164, parent190, child246. Clean baseline main0d2f93c; owned
build22469132/version1.400.6031.6004151/image SHA2568654f01d…fdc8e.
Original resolver/tests/docs were dirty during verification. The
[receipt](../research/evidence/owned-player-resource-20261006.json) pins source,
catalog/package and private observation inputs. Successful resource loading,
fresh player creation and local-player designation remain unobserved.

## Native record and corrected observations

RASC v1 reader146367ca0 reads40-byte rows beginning at40. Header+16/+20
locate two raw16 tables; +24/+28 locate directory/filename pools; +36 is count.
Row+0/+4 form a raw16/u32 key, +8/+12 the associated pair, +16 another raw16
index, +24 an opaque u64, +32/+36 directory/filename offsets. Row+20 is unread.
Directory and filename are concatenated. Helper1462d6a30 compares8+8+4 bytes.
Finite pinned-image instructions corroborate the material decompiler claims.

Exact player row24364840 has UUID indices193616, suffixes2, type index2,
opaque u64=367528, directory offset407228 and filename offset26393786.
The indexed raw16 is at162044480. Independent ZIP metadata locates exactly
one367528-byte player resource in SharedDataStrm-part8.pak, unencrypted custom
method15. The slice was never read or decompressed. Optimized catalog bytes
also contain the raw16/suffix2/367528 combination.

Initial speculative alignment mixed neighboring rows and suggested suffix100
and a size discrepancy. The proved boundaries resolve those values to
`remoteplayer.dynamicslice`; the player row agrees with its package size.
This agreement does not name the opaque u64 field. Native1463686b0 contains
both RAOC version1 and version2 branches; the initial version2-rejection claim
was falsified and corrected. This original lookup implements RASC only.

Native14639e9c0 passes a path and output-key pointer to virtual+b8, then hashes
the20-byte result. Its concrete provider/method binding remains unjoined.
The resolver reconstructs serialized fields; it does not invoke that method
or claim runtime catalog selection, registry population or native loading.
AssetId reader1417b3670/writer141727250 separately prove raw16 plus BE32.

## Original API and verification

[`owned_player_resource.py`](../scripts/owned_player_resource.py) exposes inert
`parse_player_resource(bytes)` and guarded `read_owned_player_resource(Path)`.
The owned lookup verifies exact image/Engine/resource-package sizes and hashes
before and after inspection, one bounded stored catalog and its hash, and
exact resource ZIP metadata. Only the catalog member is read. Its parser
rejects wrong header/extent, overlapping tables, invalid selected indices,
invalid string starts, missing paths and ambiguity. These are stricter offline
guards, not native rejection claims; unrelated dependency sections are unparsed.

Read-only CLI, from the repository root, in a validated task script:

```powershell
$pythonExecutable = 'C:\Code\NewWorldPreservation\.venv\Scripts\python.exe'
$lookupArguments = @('-B','scripts/owned_player_resource.py','--game-root',
    'C:\Program Files (x86)\Steam\steamapps\common\New World')
& $pythonExecutable @lookupArguments
```

Original synthetic tests cover literal layouts/AssetId bytes, truncation, bad
extents/indices, neighboring-resource selection, ambiguity, hash failures,
post-read changes and catalog-only reading. Executed counts and workspace
results are in the receipt. No game, hooks, service or game endpoint ran.
Continue child247's GdeRef/local identity inputs, then candidate248. Parent190,
visible private world entry and Milestone1 remain open.
