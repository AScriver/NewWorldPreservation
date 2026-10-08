# Current registration-only trial preparation — #285

The trial controller can now select the implemented current-format registration
responder. It validates the private response before setting up containment or
services, forwards the four selected inputs only to DTLS, and permits the existing
user-stop lifetime. This is preparation for a separately admitted native trial.
No native client, controller top level, Frida, hosts or firewall operation ran.

[Receipt](../research/evidence/current-registration-trial-preparation.json) pins
the actual base cb94d38 and changed code/test inputs. The
[server profile](REGISTRATION_ADAPTER_CURRENT.md) still requires caller-selected
values; valid encoding does not establish response semantics or authentication.

## Admission and implementation

An explicit `current_registration: true` selects four manifest fields:

| Field | Required value |
| --- | --- |
| current_request_type_index | JSON uint32 integer, including 0 |
| current_response_type_index | JSON uint32 integer, including 0 |
| current_response_body | File resolving under private/ or .scratch/ |
| current_response_body_sha256 | Exact hexadecimal SHA256 |

Disabled selection with ancillary fields, incomplete fields, noninteger/bool
selectors, historical version or enabled actor/world/creation/observer mixtures
are refused. Selected BODY, verifier, interpreter and current codecs need unique
matching hash bindings. The pure verifier and runtime adapter share the same
bounded preparation: read at most 4097 bytes, admit 1..4096, require hash match,
complete canonical BODY and a typed record no larger than 4096. Verifier output
contains only selectors, sizes, digests and `client_acceptance_proven:false`.
It imports no actor, DTLS, cryptography or runtime adapter modules.

The controller invokes that verifier with `-B` and the intended dependency path
before resource setup, then forwards identical arguments to the DTLS child.
The child repeats validation before its own runtime admission. Changed files
after controller preflight are refused by that existing child boundary and
require the existing containment cleanup; preflight is not a filesystem lock.

Current selection may use the existing owner PID/creation-FILETIME guard and
stop.request path without player creation. The prepared next attempt has no
elapsed cutoff. Legacy timed paths remain available. Encoding, record framing,
reply/cache/retry behavior, observers and containment cleanup are unchanged.

## Concrete private preparation

`private/frida-trials/run-20261008T1242-current-registration` holds a fresh
manifest, admission metadata, dispatch and original BODY. It reuses the verified
1733 physical client copy; no client archive was recreated. All 152 bindings and
actual selected admission/lifetime helpers passed. Dispatch selects the existing
trust hook and user-stop lifetime, with no context-gate observer or actor stages.

The explicitly proposed values are request selector 19, response selector 3 and
an 18-byte minimal canonical zero BODY; its typed record is 22 bytes. These are
**experimental values** already exercised with synthetic inputs. Actual native
selector bindings, suitable response/authentication fields and acceptance remain
unknown. This candidate is not a success or authenticated-world claim.

At preparation, the retained CA was valid through October 9, 2026 at 18:58:22 UTC.
Actual admission must recheck current validity, hashes, process/resource ownership,
containment and installed-client integrity. No resource was acquired by preparation.
Historical manifests and closed attempts remain unchanged.

## Verification and remaining gate

295 focused Python cases and AST-isolated PowerShell admission/lifetime cases
passed. Independent cold CLI errors refused before listener/event-log creation.
One owned synthetic localhost DTLS exchange returned the independent literal
typed-response oracle, retried the entire datagram identically, and emitted no
typed reply for bad CRC, truncation or a valid-CRC wrong selector. Its child exited
and listener closed; generated private certs/BODY were removed. Controller
ordering/forwarding was verified through isolated helpers and source inspection,
not actual containment or a native trial.

Full offline validation passed 1978 cases in 51 Python modules, five PowerShell
suites and a closed loopback CLI exchange. An initial pre-collection inventory
failure is retained; registering the new module required updating the deliberate
24/50 inventory to 25/51. No protocol behavior changed in that correction.
Final catalog/preflight/hash closure reconciles actual selected inputs.

Claims K428–K430 cover pure preparation, controller admission/forwarding and the
synthetic exchange. Authentication, native acceptance, world entry and Milestone 1
remain unproved. Official recordings remain normal-game references.

[AGENTS.md](../AGENTS.md) states that the October 7 grant "does not authorize
another native attempt, new messages or observation sites." A fresh specific
grant is required before this one prepared registration-only attempt. If admitted,
use the isolated copy and existing loopback/ownership/cleanup procedure; the user
can select Play when the local selection screen appears. Observe only existing
allowlisted metadata and ordinary visual behavior. Preserve refusal or failure
and clean up the owned client before releasing containment.
