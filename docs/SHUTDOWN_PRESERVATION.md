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

The same video-only packet now preserves four further exact, privacy-reviewed
Game Bar clips. Source/copy SHA-256 hashes match; all pixels and audio stay private.
[Gameplay and return receipt](../research/evidence/official-session-video-20261007.json)
binds each claim to clip hashes, explicit playback seeks and private review receipts.

| Clip | Preserved visual reference |
|---|---|
| Main, 56.7171 seconds / 69,772,275 bytes | Selection/Play/loading; visible local player; changed world view/pose, ability effects, gathering notifications, chopping and tree falling. Movement/control inputs are separately user-reported; pressed keys and network acceptance were not observed. |
| Return, 76.050433 seconds / 89,470,897 bytes | Inventory before logout; main-menu exit confirmation; selection/Play/loading; local player rendered again in the same visible vicinity. No remote removal/reappearance or actor identity evidence. |
| After return, 38.140133 seconds / 48,726,810 bytes | Inventory wood-icon counts 46/31/2 match the pre-logout frame; one wood tooltip identifies its visible stack. Mounted rest, rise and landing are sampled. This is a later clip in another location with uncontrolled intervening actions; equality supports visible count continuity only. |
| Fast travel, 43.683566 seconds / 55,198,393 bytes | Map choice/confirmation, departure countdown, loading at 28–30 seconds, destination player/HUD at 32 seconds and changed world position/view afterward. This is an ordinary supported route, without a claim about backend map/context boundaries. |

The test is 60 fps, as are main/return/travel; the after-return clip reports 120 fps.
Direct review covers named decoded frames, not continuous playback or independent
audio review. Source file UTC, collection UTC and playback offsets remain distinct.
No pre-gather inventory count was captured: exact gathering delta, stable item IDs
and authoritative persistence remain unknown. No unmounted jump was established.
These precision gaps do not require repeating completed solo sequences unless a
specific preservation question needs them. The next necessary live session is F1/F2.

Offline review of the existing return clip also fills one ordinary loot-count
comparison. Inventory at24seconds shows reagent-icon counts40/54; interaction
pose/progress at28.5seconds precedes reward UI at30seconds (+14/+12, totals54/66);
inventory at32seconds shows54/66. The arithmetic agrees. Icon order changes, so
the comparison follows appearance/reward labels, not pane slots or stable item IDs.
[Loot comparison supplement](../research/evidence/official-session-loot-comparison-20261007.json)
binds14 new private frame files and the reused after-return15second frame.
That later frame shows54/77: the first count agrees, the second differs. Uncontrolled
intervening play prevents a claim that both counts persisted unchanged. This is a
container-loot UI reference; the earlier tree's pre-gather count and backend
inventory authority remain unknown. No new live collection was needed.

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

## Collection checklist and remaining gaps

| Gap | Collection and completion boundary |
|---|---|
| S1: rendered entry and local controls | Preserved selection/loading/local player, changed view/pose and ability effects in main clip. Mounted rest/rise/landing appears in after-return clip. Key/button causality, unmounted jump and queue remain unobserved; no routine repeat requested. |
| S2: visible ordinary return | Preserved exit confirmation, selection/Play/loading and local rendered return in the return clip. This fills the missing local visual reference; remote actor removal/reappearance remains F2. |
| F1: mutual visibility and movement | Defer execution. A consenting friend with their own legitimate client/account records viewpoint B. Capture approach/departure, then walk/turn/stop/jump in both directions with the observer stationary. Both clips must support the attributed observations. |
| F2: remote logout/reappearance | With that friend, A remains recording while B logs out and returns. Preserve A's visible disappearance/reappearance plus B's local safe transitions. Then swap if needed to cover the opposite role. Actor IDs/reuse and packet causes remain unknown. |
| S3: gathering, loot and visible state continuity | Preserved gathering/tree-felling/reward UI, wood-icon count equality across logout/return, and a same-clip container-loot before/reward/after count comparison (40+14=54;54+12=66). Later reagent counts54/77 retain counterevidence to unchanged full inventory. The tree's pre-gather count and uninterrupted intervening activity were not recorded; exact tree delta/backend persistence remain unproved. Repeat only for a specific missing comparison if needed. |
| S4: supported travel transition | Preserved one ordinary fast-travel map/confirmation/countdown/loading/destination/movement reference. Post-travel inventory was not opened; inventory continuity across travel remains unknown. Do not repeat routes without a concrete missing question. |

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
- `recordings/`: only exact user-selected, stopped, reviewed local clips; no desktop or credential-prompt footage.
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
The October 7 solo clips supplement S1/S2/S3/S4; they do not pass F1/F2.
The user explicitly deferred second-player recording on October 7. Resume only when
the user is ready and a consenting friend can use their own legitimate client.

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
