# Ordinary official-session observation

This is the user's separate October 6 authorization under workItemId 164.
It permits normal Steam/launcher/EAC sessions while the user is present, manual
login, ordinary local logs and supported gameplay recordings. It adds no private
Frida, hook, process-memory, decryption, replay, official API or system-change authority.
Checkpoints #241–#245 sit under the evidence coordinator #166. Its original
private acceptance remains open. Official evidence cannot satisfy Milestone 1.

## Prepared scope

The owned [private archive](OWNED_CLIENT_ARCHIVE.md) pins build 22469132 and image
SHA-256 8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e.
The collector refuses another image/build, an already running game, game hosts
redirects, proxy/key-log environment settings or ambiguous/denied process identity.
It changes none of those settings. Steam, launcher and EAC remain intact.

`Start-OfficialObservation.ps1` creates a unique ignored
`private/official-sessions/<run>/`, then observes for at most 900 seconds (default
600). Optional `-LaunchThroughSteam` performs only Steam's ordinary `-applaunch
1063730`; login and recording remain manual. Without it, the user starts Steam.
The observer matches exact executable path/PID/start time and checks identity
again after socket queries. Refused metadata ends collection without evasion.
The observer never terminates the game or unrelated processes.

If the protected executable path is unavailable, accept that refusal. The October
6 run stopped socket observation with zero samples. An already armed run may
continue only its ordinary own-user Game.log suffix through
`Collect-OfficialLogSuffix.ps1`, with the exact public PID/name/creation time of
the user-confirmed normal Steam session. This is local file observation, with no
protected-path retry or socket query. Its installed-file hash is not proof of the
running image. Record that attribution limit in the receipt.

Use the recorded PID and UTC creation time, never another process chosen by name
alone, and choose a bound of 5–600 seconds. Validate and execute the helper through
`Invoke-CodexPowerShell.ps1`, passing `-RunDirectory`, `-ExpectedProcessId`,
`-ExpectedStartTimeUtc` and `-Seconds`. Stop on mismatch, refusal or client exit.
Verify both ownership files report `collector_closed` before finalization.

Saved output is fixed own-log categories and TCP state/port/address-family and UDP
local-binding metadata, sampled approximately once per second. Remote addresses
and arbitrary hostname/path labels are omitted to avoid retaining unverified peer
identifiers. No packet capture or payload exists. UDP remote endpoints, DTLS
version/cipher, Carrier fields, message schemas and authority remain unknown.
Markers such as LoadLevel are locally exposed diagnostics, not visible spawn proof.

Existing Game.log bytes are skipped. Replacement/truncation is marked and new
bytes read; partial/oversized lines and sensitive-signal lines are discarded.
Same-inode overwrite beyond the old offset can evade this bounded rotation check;
missing early log markers remain unknown. Collection time is UTC plus host
monotonic timing; source event UTC is retained only when explicitly logged as UTC.
User action marks carry report time, not an invented exact action timestamp.

## User action for first collection

Close New World normally first. When the prepared collector is armed, start the
game through ordinary Steam (or let its opt-in Steam launch do so). Handle all
login/credential prompts yourself. Report each reached screen: startup,
discovery, character selection, queue or immediate entry, connection/loading,
then your visible player and usable world view. Do not paste logs, names, tickets,
tokens, character/account identifiers or credential screenshots into chat.

If supported gameplay recording is available, use its game-window capture after
all credential prompts. Pause at any sensitive prompt. Hide chat/nameplates and
unconsenting players through supported controls; if identifiers cannot be kept
out, skip video and report the visible transitions. Do not record desktop/login,
voice chat, other accounts or secret-bearing overlays. Review footage before
registering it; this tool records a user attestation, not automated pixel redaction.
Keep reviewed recordings in ignored `private/official-sessions/<run>/recordings/`.

```powershell
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Start-OfficialObservation.ps1 -Execute -ArgumentList '-RunDirectory','C:\Code\NewWorldPreservation\private\official-sessions\UNIQUE-RUN','-Seconds','600','-LaunchThroughSteam'
```

Writing the owned run's `stop.request` stops only this collector at its next poll.
Let its wrapper finish and verify resource-ownership.json says collector_closed.
Then add fixed action marks and reviewed recordings through
`official_session_metadata.py mark` / `recording`; finalize once with `finalize`.
Each scenario receives its own private manifest with build, consent, UTC/monotonic
timing, expected/observed actions, artifact hashes, redaction status and unknowns.
Hash verification establishes artifact integrity. User reports, rendered footage,
log markers, socket metadata, historical references and synthetic tests stay distinct.

## Consenting movement and reconnect

Proceed only after explicit confirmation of the friend's consent, legitimate
account/client and availability. Both players record their own game views safely.
Record clock alignment limits; a shared countdown is only an approximate visual
alignment aid, not proof of synchronized clocks or network causality.

1. B enters then leaves A's view; both note visible appearance/removal.
2. A stays stationary. B walks, turns, stops and jumps, with one action at a time.
3. Swap roles and repeat. Keep unrelated players and identifiers out of recordings.
4. Use ordinary logout/relogin; note selection/loading/local return and, with
   consent, remote removal/reappearance. Do not force failures or infer actor IDs.

Without a second consenting player, movement and remote actor observations remain
uncollected. Zone/fast-travel or simple gameplay is eligible only after these
priorities and only for a concrete unresolved preservation dependency.

## Handoff and cleanup

Finalization refuses an active collector and changed recordings. It saves hashes
for allowlisted artifacts and scenario coverage; missing actions stay explicit.
Both-viewpoint/timing verification remains false until actual evidence review.
An untouched scenario is marked `not_collected`. Ordinary relogin reports do not
establish remote actor removal/reappearance or protocol identity continuity.
No closed metadata manifest, synthetic check or successful official entry proves
private-server world entry, movement, reconnect or authority. Keep all raw/client
material private; commit only reviewed original tools and sanitized receipts.
