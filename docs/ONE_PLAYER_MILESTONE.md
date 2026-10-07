# Immediate milestone: one controllable private player

User priority, October6: ONE freshly created private character, visibly spawned
and controllable in the actual owned New World client, in a world served by the
replacement backend. This resumes the earlier #251 pause. Preserve the existing
project and broader [two-client Milestone1 roadmap](ROADMAP.md#acceptance-boundary).
The active Codex goal carries this same acceptance; this file is its durable
checkpoint. Work remains under top-level Actionables **164**.

## Definition of done

1. Restart into a fresh private session and create a new backend character. A
   script/admin operation and minimal documented defaults are sufficient.
2. Enter a rendered world showing that new entity as the local player with
   appropriate camera and input ownership. Loading, callbacks, selection preview,
   spectator views and a server's send log do not satisfy this.
3. Normal controls move, turn and stop the character; retain an interactive
   session for at least five minutes without spawn timeout, disconnect or return
   to selection. Five minutes is a minimum acceptance criterion, not a stop time
   or protocol fact. The October7 direction removes the prepared trial's elapsed
   time cap; the user confirms completion or refocuses the goal.
4. Correlate session, character, entity and movement in client/server evidence.
   Show a server-originated position reflected in the client, or equally strong
   network-participation evidence. State the movement authority actually
   implemented; receiving client positions alone proves no authoritative physics.
5. Repeat after restarting client and backend. No prior official session,
   gameplay replay or Amazon world simulation supplies the result. Record any
   Steam/launcher dependency separately; durable persistence is unnecessary.

All five conditions are **pending**. On success retain reproduction commands,
correlated logs and visual evidence or explicit user confirmation, mark this
milestone complete, and proceed to the existing multiplayer acceptance gate.

## Furthest real-client behavior

The closed [0655 private trial](../research/evidence/current-self-length-prefix-trial.json)
used the isolated owned copy, loopback containment, existing trust hook,
heartbeat and guarded callback observer. SelfIdentification entered and set the
self flag; actor-connection success and ClientContext Initialize were logged.
The load return latched activation and consumed pending LevelInfo. There were
238 matched local heartbeat acknowledgements and ACK coverage for the five
outbound envelopes. The user saw loading, brief black, character selection, then
server-spawn timeout. Immediate context readiness was false; later asynchronous
readiness was unobserved. No private player, rendered world or control was proved.
The bundle was empty. Cleanup and independent resource readback passed.

These are historical live observations, not a new trial. At the initial clean
checkout `e73121e`, five current adapter/runner/controller/observer inputs still
matched the closed receipt. Later source-supported codecs add offline support,
not new real-client behavior.

## Working dependency hypothesis

Verify this chain rather than assuming wire order:

| Transition | Current support | Missing observation / obstacle |
|---|---|---|
| Fresh session/character identity | One original immutable record joins login-info, queue and identity BODY; default-off controller forwarding is prepared | Native local-ID provider acceptance and admitted live forwarding pending |
| Entity creation | Owned player AssetId, fresh GdeRef policy, creation BODY/record parser | Trial sends no creation member; native construction/slot placement unobserved |
| Resource loading and component delivery | Exact owned player resource; baked PlayerComponent index9 | Native load and refreshable runtime index mode unobserved |
| Local-player designation | Exact text comparison, reconciled identity delivery, guarded registry path | Matching provider availability, binding, keyed readiness and actual designation unobserved |
| Camera/input ownership | Local-player and context-readiness gates identified | Rendered player/camera/input not demonstrated |
| Movement exchange | No current implemented acceptance | Networked move/turn/stop, server update, five-minute survival and repeat unproved |

## Current execution checkpoint

Completed offline leaf: **#252** under248/190/171/164 now
[composes](PLAYER_CREATION_CANDIDATE.md) the already evidenced creation and
identity BODYs into one bounded original nonempty type8 candidate. Targeted,
independent and required workspace checks passed. It uses exact owned resource, a caller-assigned
fresh reference and explicit character identity/record/class/delivery inputs.
Resource index9 is conditional; reader-inverse record construction and live
Carrier placement remain experimental. Candidate construction grants no new
live sends or observer sites.

Offline leaf **#253** now supplies [one fresh private character](PRIVATE_TRIAL_CHARACTER.md)
consistently to login-info, queue and the identity BODY/candidate. The record is
ephemeral original backend data; native authentication/designation remain unknown.

Offline leaf **#254** prepares [default-off controller/Carrier integration](PLAYER_CREATION_TRIAL.md)
of that same SHA-bound record. One original107-byte indexed candidate, one attempt
after empty activation and one lifetime peer are ready for the specific live-send
grant. Exact byte/digest checks and failure controls do not establish client acceptance.

October7 follow-ups256/257 replace elapsed trial deadlines with user-confirmed
completion/refocus and exact-controller loss detection. Startup/cleanup and
explicit protocol failures remain guarded. See the trial's lifetime contract.

Next relevant work is that specifically admitted isolated-copy trial. Expected
first observable result: native resource/
player construction after the previously observed context activation. Local
designation, rendering and control must then be checked separately.

Keep the working isolated-copy connection path. Defer stock trust alternatives,
multiplayer, combat, NPCs, quests, crafting, production persistence, dashboards,
broad refactoring and packaging unless a demonstrated dependency requires them.
Do not rerun the unchanged empty-bundle timeout to manufacture progress.

Existing [AGENTS](../AGENTS.md), [Carrier trial](CARRIER_REGISTRATION_TRIAL.md) and
process/resource/cleanup boundaries apply. The priority instruction expands no
authorization. A new creation send must be concrete and reviewable before any
needed approval; unperformed live checks stay pending. Record the furthest
observed behavior, exact blocker and next justified experiment in this checkpoint
as the loop advances.

The October7 user instruction supersedes the300-second resume cap. The prior
trial exhausted no observed Carrier budget: its transport closed after30.638s
without inbound traffic. Preserve that distinction; a longer interactive trial
uses the user-confirmed lifetime in the prepared trial, with real failure and
cleanup controls retained.
