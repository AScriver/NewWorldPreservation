# Current registration callable and scalar provenance

October 5, 2026; workItemId **164**, parent **178**, task **215**. The previously
unresolved owner+0x90 join is closed for the concrete installation below. It is
a captureless diagnostic callable, rather than a direct registration-value
supplier. A separate producer join identifies V3 request+8 as the CRC32 of the
bytes returned by the type-index file abstraction. These are static conclusions;
no client execution or authenticated gameplay was tested.

Analysis used clean `defa065ab4fe1f264ad87cfc1bb205f6f0787043`, image
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`
(179204176 bytes, Steam build22469132, version1.400.6031.6004151). Mapping and both
reference checkouts were refreshed. The [original receipt](../research/evidence/current-registration-data-provider.json)
seals their identities, exact native spans, vtable slots and verification outputs.
Raw instructions, decompiler output and working notes remain ignored.

## J215-1 — creation, installation and concrete target

Factory `0x146b6c490` allocates0x770 at `0x146b6c4ac..0x146b6c4b1`, constructs
the owner through `0x146b69ad0` at `0x146b6c4c6`, and returns it through an output
slot. Constructor `0x146b69b15..0x146b69b1c` installs owner vtable `0x148590ab8`.
Caller `0x146425cb0` calls the factory at `0x146425cf0` and transfers that pointer
to caller+0x1000 at `0x146425d02`.

| Joined edge | Exact current-image evidence |
|---|---|
| Caller retrieves this owner | `0x1464261df`, in `0x146425f20`, loads caller+0x1000 |
| First callable is constructed inline | `0x146426217..0x14642622c` installs vtable `0x148502988` in stack storage and sets its active pointer at storage+0x38 |
| First callable enters owner installer | RDX names that storage at `0x14642623c`; `0x146426243` calls owner virtual+8, whose table entry is `0x146b70af0` |
| Installer assigns owner+0x58 | `0x146b70b17..0x146b70b1b` passes that destination and the original RDX to `0x14056cee0` |
| Active pointer becomes owner+0x90 | Helper's inline copy at `0x14056d009..0x14056d00c` installs the returned destination at destination+0x38 |
| Concrete copy and invocation | Vtable `0x148502988` slots0/+8 → `0x146471c30`; slot+0x10 → `0x146474e80` |

The complete14-byte copy body writes only its vtable and returns the destination.
It copies no captured object or registration fields. Only the **third** callable,
passed in R9, captures the caller at `0x1464261f5`; it is installed in another
owner storage. Its capture must not be attributed to owner+0x90.

## J215-2 — supplied values and downstream meaning

Builder `0x146b6e190` loads owner+0x90 at `0x146b6e25e`, null-checks it and invokes
virtual+0x10 at `0x146b6e26d`. The concrete target's complete19-byte body
`0x146474e80..0x146474e93` loads two fixed static literal addresses into RDX/RCX
and tail-jumps to `0x14143e010`. It reads no captured state. That routine formats
text through the imported `__stdio_common_vsnprintf_s` at `0x14143e076`, dispatches
it through `0x1411cfc30`/`0x1411d1480`, and, when unhandled, calls fallback
`0x14143ba70`. The fallback calls imported `OutputDebugStringA` at `0x14143bb2f`.
PE import records and actual consumers establish the diagnostic role independently
of the message's wording. The builder consumes no return from this invocation.

The concrete callable therefore supplies a fixed category and diagnostic text to
output machinery. It directly supplies no request fields. Registration's retained
setup inputs are separate; their authentication labels are not established here.
Dynamic diagnostic-handler side effects and alternative callable installations
remain outside this conclusion.

## J215-3 — separate type-index scalar producer

Loader `0x1461661c0` opens the `typeindex.json` input at `0x146166201` and reads
through `0x14144b810` at `0x1461662ad`. It passes the returned byte count in RAX
to the CRC's length argument at `0x1461662b5`, disables ASCII case folding, and
computes the CRC through `0x1412f47d0` → `0x141462980` at `0x1461662c4`.
Two initialization callers directly join the loader's receiver to registration's
registry accessor: `0x14102ee8b..0x14102ee93` and `0x14643f10b..0x14643f113` each
call `0x146162150`, move its returned pointer to RCX, then call wrapper
`0x14615f720`. That wrapper forwards RCX to the loader at `0x14615f72d`.
On the successful loader branch, `0x146166692..0x14616669d` stores the CRC in
registry+0x70. Accessor `0x146162150` returns the registry within its process-wide
instance; leaf `0x146165190` copies registry+0x70 to the builder's local scalar.
Builder `0x146b6e464..0x146b6e46b` supplies that local to V3 constructor
`0x146b66820`, which copies it to request+8 at `0x146b6684f..0x146b66851`.

The current CRC uses the IEEE table at `0x147fe6730`, initial0xffffffff and final
complement. All256 table entries and four harmless buffers match independent
polynomial construction and `zlib.crc32`. This identifies the scalar's producer;
it establishes no ticket, principal, credential or cryptographic authority.
The file abstraction can return handler-provided bytes/counts. A complete physical
file read, actual runtime file identity and successful load are unobserved; the
registry constructor's zero default also remains possible.

## J215-4 — ownership and lifetime

The first callable is copied into owner+0x58, with active pointer owner+0x90;
it does not borrow its source stack storage or the caller. The assignment helper
disposes replaced/temporary targets through virtual+0x20, and installer
`0x146b70b3f..0x146b70b88` disposes and clears the source temporaries. This
callable's disposal target `0x14078fa10` returns for inline storage and otherwise
tail-calls sized deallocation with size0x10.

Owner construction initializes +0x90 to null. Destructor `0x146b6b590..0x146b6b5a9`
loads the active target, selects the inline-versus-other disposal flag, invokes
virtual+0x20 and clears it. Wrapper `0x146b6bea0` calls the destructor and can free
the0x770 owner. Caller replacement at `0x146425d02..0x146425d16`, and cleanup at
`0x14642d363..0x14642d377`, release the prior owner through its deleting slot.
These joins establish storage ownership and teardown, not runtime cancellation,
generation isolation or callback quiescence.

Sparse Ghidra results were cross-checked against instructions, and a targeted
counter-review survived the installation, diagnostic and lifetime challenges;
its CRC challenge narrowed the claim to returned bytes. The final source seal
passed25 native bindings/67 instruction sites. Required offline workspace checks
passed469 Python cases, three PowerShell suites and the isolated loopback lifecycle,
with no changed inputs and the listener closed. Those regression results do not
prove client behavior. Only task215's source result is complete; parent178/164 and
Milestone1 remain open.
