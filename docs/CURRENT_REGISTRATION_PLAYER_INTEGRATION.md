# Current registration and fresh player integration — #286

The explicit current-registration profile now selects the existing original
creation/identity candidate after the tested bootstrap sequence. One fresh
private record supplies selection, queueing and the candidate's character ID,
name and GdeRef. This is implemented and verified offline; a rendered player,
local designation, camera/input and movement remain unproved.

WorkItem164, parent179; baseline clean main40cee5f. The source encoders,
scheduler, response BODY, existing hooks and observer are unchanged. Only the
three profile exclusions were removed. Complete candidate prerequisites and
verification still run at the CLI, adapter and controller. Historical #213
and #214 results retain their exact inputs and limits.

## Existing candidate and guards

Select all four current-registration inputs, then the existing opt-in
`--player-creation-candidate` with the SHA-bound private character file, pinned
typeIndex, explicit `resource-index` mode and one occupancy choice. Require the
owned-version guard, heartbeat, default SelfIdentification with the current131
prefix, spawn notification and world activation. The native controller also
requires its existing guarded observer and exact source/type/map/asset bindings.
Ancillary creation inputs with the option absent remain invalid.

The same immutable record supplies both HTTPS responders and Carrier. The
identity member uses its exact UTF-8 character ID/name; the creation member
uses its once-assigned fresh GdeRef and the owned player AssetId. SelfIdentification
remains the separate fixed-default127-byte BODY. Current response bytes still
come entirely from the caller BODY; owned-version selection is guard metadata.

The candidate has one outer slot0 record: creation key0/class10 precedes identity
key9/class3935. With the default `Preservation` name its typed extent is107bytes,
using the existing one-byte application length. Canonical preparation and the
final send boundary retain extent/header/digest checks. The shared Carrier
cursors, one lifetime peer and once-attempt latch remain unchanged. A failed
predecessor blocks creation; failed or uncertain candidate sends never retry.
Exact/fresh registration retries reuse their response without resending creation.

Creation is attempted one second after the successful empty bundle. This is an
experiment delay, not a map-readiness test. Asynchronous context readiness may
depend on player construction. Runtime key9 delivery, class-table installation,
resource loading, effective identity override and designation remain conditional.
The existing observer does not measure the later async readiness or creation
callback directly. No new hook/site or guessed identity field is introduced.

## Verification

452 focused Python cases passed, including both registration profiles, delayed
ticks/retries, all predecessor guards, final digest corruption, failed sends and
peer limits. Executed PowerShell tests isolate the actual helpers and creation
admission statements; their mapping-hash read is explicitly modeled. A separate
readback ran the selected input-admission checks against156 real bound
inputs, real canonical verifiers and captured child argument construction.
It excludes elevation, runtime containment, one-attempt and retained-root checks;
the preparation separately checked current CA validity and unused run files.

An independent real synthetic localhost DTLS exchange verified literal response
and bootstrap bytes and the exact107-byte candidate once in order,1.000s after
the empty bundle. Cursors remained shared; requests before/after creation did
not replay it. Six cold-invalid cases opened no log/certificate/listener, and a
second peer was refused. The owned child exited0, its dynamic UDP port rebound
and certificates were removed. This synthetic client supplies no native gameplay
proof. Complete workspace validation and review are recorded in the
[receipt](../research/evidence/current-registration-player-integration.json).

The first isolated PowerShell statement test exposed missing file-backed
PSScriptRoot. Its test now supplies the original controller directory through a
task variable; production admission expressions were unchanged. Retain this
failed check and its correction with the private verification output.

## Prepared next client experiment

`private/frida-trials/run-20261008T2112-current-player` contains a new original
private record,107-byte candidate and156 unique bindings. Manifest SHA256:
`082904e8141f2f239c7584c3279db70ab677c9e36005c31b0e0d7e68d48299e9`.
Candidate SHA256:
`6c02da121095bd0e5fa938db66a635ed25a3fbf4722063d2eb81bae6b9607310`.
It reuses the existing verified isolated client copy, request19/response3,
18-zero-byte BODY, existing trust hook and three-site/seven-boolean observer.
The character/candidate and raw metadata remain private. No runtime resources
or native client were started by preparation. The reused local CA expires
October9 at18:58:22UTC; recheck its validity and all bindings before admission.

The proposed lifetime is user-stop with no elapsed cutoff, retaining genuine
startup/transport/owner failure controls and exact cleanup. The previous grants
are consumed. [AGENTS](../AGENTS.md) requires a new specific single-attempt grant;
this preparation adds no native permission. After approval and launch, the user
selects **Play**, reports whether a player appears, and tests ordinary camera,
movement/turn/stop if controls work. A timeout, return to selection, sent payload
or ACK is preserved as its own result. Restart reproducibility remains a separate
subsequent acceptance step; one grant never authorizes multiple attempts.
