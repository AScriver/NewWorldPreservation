# Shutdown-critical official evidence

This chat's October 7 scope is official-server evidence that cannot be collected
after service ends on **January 31, 2027**. The [official announcement](https://www.newworld.com/en-us/news/articles/the-future-of-new-world-aeternum-what-to-expect)
gives the date without an exact shutdown hour. Use workItemId **164** and the
existing **#166** evidence branch. The separate chat owns private implementation,
spawn debugging, native serialization and isolated-client trials.

## Reconciled baseline

| Preserved item | Evidence and limits |
|---|---|
| Owned client archive | Prior executed source/destination verification: 374 files, 76,744,359,425 bytes, Steam build 22469132, version 1.400.6031.6004151, image SHA-256 8654f01d…e0fdc8e. October 7 bounded inventory/hash reconciliation agrees. Reuse this archive; no new whole-archive hash or copy is needed. Restore/launch and off-machine backup were not proved. |
| October 6 solo entry | Initial Login Malfunction, supported Play and visible main-character entry are **user reports**. No footage or direct screen observation exists. Discovery, selection, queue, connection/loading visuals remain unknown. |
| October 6 logout/relogin | Ordinary logout and return are **user reports**. They do not prove remote actor removal/reappearance or protocol identity continuity. |
| October 6 diagnostics | 26 fixed own-log markers, 252 samples over a 300-second collector. The installed hash is not live-image proof; protected image-path refusal yielded zero socket samples. Report collection timestamps are not action timestamps. |
| Artifact integrity | All eight current official-session files checked October 7 match the public receipt. Archive inventory SHA-256 and canonical inventory digest agree with prior preservation metadata. Full archive bytes were not rehashed. |
| Two-player evidence | Not collected. One local instance is available; friend's consent/account/client/availability, both viewpoints and clock alignment are unconfirmed. |

October 7 continuation: a safe user-confirmed Game Bar test clip was copied privately
with source/copy SHA-256 `dbd827a02257a46893576e1f23ab89b99fc2a1ea754d6b28ceac9bd6dbe88373`
(36,898,887 bytes; 32.4169 seconds; 1920x1080, 60 fps). Direct decoded-frame review
at 2/10/20/30 seconds shows startup logo, title UI, character selection and a world
loading screen. Those four samples fill part of the missing visual record; they
do not show a controllable world player or logout/return. Audio/full-video privacy
remain user-attested; only sampled pixels were independently inspected.
[Continuation receipt](../research/evidence/shutdown-preservation-20261007.json)
binds review hashes and limits.

The initial Steam-window clip and a later user-reported Codex-window clip are
excluded. The user reported a natural internet disconnect before the main clip
started; no disconnect footage exists. The first strict collector closed at
protected-path refusal, and its late log-only start was refused after normal game
exit. Cold arming of the corrected already-running game was also refused. The
working test belongs to a **video-only** packet; no live log/socket collector runs.
The user can retry recording independently and submit the successful exact clip.

See [archive evidence](OWNED_CLIENT_ARCHIVE.md), [October 6 reports](OFFICIAL_SESSION_20261006.md)
and [capture boundaries](OFFICIAL_SESSION_CAPTURE.md). Done #241/#242/#243/#245
retain their exact limited outcomes; supplementing their evidence does not turn
reports into footage or reopen those checkpoints.

## Concrete missing evidence, in value order

| Gap | Collection and completion boundary |
|---|---|
| S1: rendered entry and local controls | Record safe loading → visible player/world; walk, turn, stop, jump and move camera. Inspect the clip with playback offsets. Distinguish visible motion from reports about pressed controls; game logs do not fill missing frames. Capture startup/selection/queue only when privacy permits; mark each omitted transition explicitly. |
| S2: visible ordinary return | During the same solo session, record ordinary logout/selection and relogin/loading/local return where safe. Stop before credential or identifying screens; use separate clips as necessary. This one repetition fills the missing visual evidence. |
| F1: mutual visibility and movement | Defer execution. A consenting friend with their own legitimate client/account records viewpoint B. Capture approach/departure, then walk/turn/stop/jump in both directions with the observer stationary. Both clips must support the attributed observations. |
| F2: remote logout/reappearance | With that friend, A remains recording while B logs out and returns. Preserve A's visible disappearance/reappearance plus B's local safe transitions. Then swap if needed to cover the opposite role. Actor IDs/reuse and packet causes remain unknown. |
| S3: one server-driven state change | Useful while F1/F2 are deferred: one ordinary gathering interaction plus the own inventory before/after and after the already planned relogin. Record the visible item/count change, not an inferred backend transaction. Do this only where private recording excludes unrelated players/identifiers. |
| S4: map transition, if needed | After S1/S2/S3, one ordinary supported zone/fast-travel transition can preserve destination/loading/control and inventory continuity. Record a concrete missing map-transition dependency first; do not repeat routes to accumulate footage without a question. |

No forced failures, purchases, account deletion, new characters or special
instrumentation are necessary for these sequences. Official observations preserve
a behavioral reference, not server source, wire schemas or private gameplay.

## Recording and review packet

Windows Game Bar is installed, and the user selected it for the October 7 solo
run. Installation is not proof of successful recording. With the game focused,
**Win+G** opens controls and **Win+Alt+R** starts/stops a clip; inspect the microphone
control and keep it off. Use supported game-only audio or mute capture audio to
exclude voice chat/other applications. Default MP4 destination is Videos/Captures;
if customized, use the actual user-confirmed location. [Microsoft instructions](https://support.microsoft.com/en-gb/accessibility/windows/use-a-screen-reader-to-record-your-screen-with-xbox-game-bar)
support the controls and default destination.

Handle login manually. Begin capture after credential prompts, hide chat/nameplates
through supported controls, and stop before an unsafe screen. First inspect a short
game-window clip to confirm the right application and privacy. Game Bar recording
cannot be started or verified merely by a metadata collector.

Each run has an ignored unique `private/official-sessions/<run>/` directory:

- `capture-plan.json`: ordered scenario, privacy requirements and explicit pending status.
- `source-snapshot/` and its manifest: exact original collector/test/lock bytes and hashes.
- Existing collector state, events and ownership receipts, when actually collected: fixed own-log categories
  and supported public process attribution, preserving protected-path refusal.
- `recordings/`: only exact user-selected, stopped, reviewed local clips; no desktop/login footage.
- A review record binding each visual claim to **clip SHA-256, viewpoint and playback
  interval**, reviewer/source, user privacy attestation and limitations. A report about
  a clip is still a report until someone actually inspects its pixels.
- Final scenario manifests, source/input hashes, reproduction notes and cleanup receipt.

If the game is already running, preserve supported recordings with a separate
video-only manifest: exact selected clip, source/copy hashes, file UTC, reviewer
offsets, original source snapshots and public process attribution if available.
Do not bypass a cold-start collector refusal, fabricate collector events or restart
merely to collect already preserved log categories. A clip named for New World is
still unverified until inspected. Check the test file before recording the full
sequence; Game Bar can target Steam/Codex when they have focus. Use the actual
game's Capture widget, not a desktop shortcut invoked from this chat.

Record UTC/host-monotonic collection times, clip-relative offsets and the method's
limits. File creation/modification time is not the exact game action time. For friends,
record each clock's stated UTC and offset uncertainty privately; a shared countdown
and distinct visible actions provide approximate alignment, not synchronized clocks
or network causality. Do not record voice countdowns.

Hash checks establish file integrity. If video needs privacy repair, obtain an
explicit edit instruction; retain a clear derivative/source relationship and review
the resulting artifact before accepting it. Never publish these recordings.

## Friend packet, ready when available

Confirm consent to private recording, legitimate account/client and availability
before any friend evidence is collected. Agree on A/B roles and a quiet same-world
location using normal gameplay; do not put names/account IDs into receipts.

1. Both start safe game-window clips. Record the clock/alignment method and limits.
2. B approaches A, leaves view, and returns. Preserve both viewpoints.
3. A stays still; B walks, turns, stops, jumps. Leave visible pauses between actions.
4. Swap roles and repeat the four actions.
5. A stays; B ordinarily logs out. A records visible disappearance and eventual
   reappearance; B records safe selection/loading/local return. Stop sensitive clips.
6. Stop recordings, review privacy, bind hashes/offsets, then exit normally when done.

With one instance and no confirmed friend, this is a prepared procedure only.
Continue useful solo S1/S2/S3 collection in the meantime.

## Resources and closure

The user owns Steam launch, credentials, game actions, recording controls and normal
game exit. This chat owns only its unique collectors and private metadata outputs.
Do not share game state with an isolated-client trial. If another chat owns a running
game or routing/resource change, serialize before normal official collection.

Accept protected-path denial; never retry with memory/instrumentation/elevation.
The existing log-only procedure admits exact public PID/name/creation time plus
user-confirmed normal Steam session. Stop only owned collectors with their run's
`stop.request`; never force-stop the game, Steam, launcher, EAC or unrelated processes.
Verify ownership receipts say `collector_closed`, the exact recorded game process
has exited normally when the user is finished, and no routing/system changes occurred.

Commit only original docs/tools and sanitized receipts, after relevant validation
and staged-diff review. Keep footage, private manifests and source snapshots ignored.
#166 remains open until its original aggregate acceptance is actually met; no
official session closes the private milestone. #244 remains uncollected until F1.
