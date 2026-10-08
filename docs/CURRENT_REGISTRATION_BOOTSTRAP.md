# Current registration and world bootstrap — #213

The current-format registration responder can select the existing optional
heartbeat, SelfIdentification, spawn notification, LevelInfo and empty state
bundle stages through the CLI and private trial controller. Previously the
adapter constructor composed these inputs, while those entry points refused
them. The change exposes that implemented send path; it adds no wire message,
response default, player entity or readiness model.

The user's October8 direction makes replacement game-server implementation the
active scope. Official two-player recording is deferred indefinitely. Further
reference collection and off-machine backup are outside this work.

## Configuration

Keep the four explicit current-registration inputs from
[the server profile](REGISTRATION_ADAPTER_CURRENT.md): request and response
uint32 selectors, a private canonical BODY file and its exact SHA256. Existing
bootstrap options remain off unless selected:

| Option | Retained prerequisite |
| --- | --- |
| `--heartbeat-15d` | Pinned heartbeat codec |
| `--self-ident-default` | Heartbeat selected and exact owned-version guard |
| `--spawn-point-notification` | Default SelfIdentification selected |
| `--world-activation` | Spawn notification selected |
| `--self-ident-current-length` | Default SelfIdentification; native controller also requires the existing guarded observer |

For the native controller, existing selected-stage bindings still include the
owned version receipt, current type mappings, original codec/contracts and
owned map asset. Current BODY/verifier/interpreter bindings and pure preflight
remain required before resources. Observer admission still requires world
activation. No observation site or containment exception is added.

`--server-version` / `registration_server_version` selects the existing owned
literal as **guard metadata**. Current response bytes come entirely from the
caller BODY; the version is not injected into `field_38` or another field.
An empty `field_38` remains empty. Its required native contents and acceptance
semantics are unknown. Encoding a response never establishes authentication.
At the #213 checkpoint, current registration with player creation was rejected
by the CLI, controller and direct API. The later [#286 integration](CURRENT_REGISTRATION_PLAYER_INTEGRATION.md)
permits the complete original candidate with all existing preparation guards.

## Send state and readiness

One accepted selected physical request after the existing connect gate emits
the exact caller response. A successful send schedules heartbeat at +0.5 seconds
and SelfIdentification at +1 second. These are independent deadlines: the
scheduler evaluates actor stages first, so a delayed first tick may send
SelfIdentification before the first heartbeat. Timed-mode heartbeat failure
does not itself prevent later SelfIdentification. User-stop send failure is
terminal and prevents subsequent stages.

Successful SelfIdentification schedules spawn notification; successful spawn
notification schedules LevelInfo; successful LevelInfo schedules the empty
bundle. Each delay is one second after the preceding successful send. Failed
actor sends suppress their successors. All stages reuse the existing Carrier
envelope, channel/reliable and ACK cursors. Exact duplicates reuse the cached
reply; fresh registration retries do not restart bootstrap deadlines.

These are local send conditions. Heartbeat echoes, Carrier ACKs, sent LevelInfo,
an empty bundle and a loading screen do not establish asynchronous map/context
readiness or a rendered, controllable player. Historical native callbacks retain
their original scope. Current native request placement, type selectors,
response/authentication values, map readiness and actor readiness remain open.

## Verification and continuation

The unit verifies the actual current-request path with deterministic order,
omission, retry, delayed-tick, byte-preservation and failure controls. The
independent localhost DTLS exchange uses original synthetic inputs and literal
message oracles; it is not a New World client. Final commands, counts, exact
source hashes, retained failures and cleanup belong to
[the original receipt](../research/evidence/current-registration-bootstrap.json).

Full #213 acceptance remains partial because native asynchronous context and
actor conditions are unobserved. The next client transition to prove is accepted
current registration followed by map/context readiness; then fresh player
construction/designation and camera/input ownership. Do not add guessed messages
to move a loading screen.

A native attempt needs fresh private bindings and a specific grant under
[AGENTS.md](../AGENTS.md). The consumed October7 grant does not authorize another
attempt. This offline implementation does not launch a client or change hosts,
firewall, trust stores, hooks or installed Steam/EAC files.
