# October 6 official entry and ordinary relogin

Under the user's separate normal-session authorization, the archived installed
Steam build `22469132` / version `1.400.6031.6004151` was launched through ordinary
Steam/launcher/EAC. The cold preflight found no existing NewWorld process. The user
handled login and reported an initial **Login Malfunction**, followed by pressing
Play and entering the world with their main character. They subsequently reported
ordinary logout and successful return. No service failure was induced.

These rendered outcomes are **user reports**, with five fixed action marks and
later report-collection UTC/host-monotonic timestamps. No footage or direct pixel
observation was collected. Discovery, character selection, queue, connection and
loading screens were not separately reported; their visible behavior remains
unknown. Same-character return is reported by the user; protocol/actor identity
continuity is unproved.

Protected executable-path access was unavailable. The strict observer stopped
with **zero socket samples**, without retrying protected access. Installed image
SHA-256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`
pins the preserved files; it does not verify the live process image. Subsequent
observation used only the conventional own-user Game.log suffix, attributed by
the user's normal session and exact public PID/name/creation time. Its 300-second
bound completed with 252 samples. It retained 26 fixed markers: 21 connection-wrapper,
two REP-connection and three level-load markers. Names, addresses, raw lines,
credentials, identities and message bodies were not retained by the parser.
These marker categories establish no wire format, connection authority or spawn.

Collection armed at `2026-10-06T19:39:54.693378Z` and the initial manifest closed
at `19:52:23.993360Z`. The private run is
`private/official-sessions/entry-20261006T193940Z/`. It contains separate entry,
movement and relogin manifests, hashed metadata, ownership and cleanup receipts.
The movement manifest is explicitly `not_collected`: a second player's consent,
legitimate client/account, both viewpoints and clock alignment remain unconfirmed.
Remote actor removal/reappearance is also unobserved. Earlier manifest versions
are retained privately beside the scope-review correction. Exact earlier source
snapshots for the log-only helper were not preserved; current-source tests are
separate evidence.

Artifact hashes and fixed output fields were independently checked after
collection. Both collectors closed; after the user chose normal exit, all three
recorded process IDs were absent. No process was forcibly stopped. Steam, launcher
and EAC were unchanged. [Sanitized receipt](../research/evidence/official-session-20261006.json)
records artifact hashes, action provenance, redaction and unknowns.

Checkpoint #243 preserves the successful reported entry with incomplete screen
coverage; #245 preserves reported logout/relogin with no remote viewpoint. #244
remains uncollected pending confirmed consent and availability. The next prepared
action is the two-viewpoint sequence in [the capture procedure](OFFICIAL_SESSION_CAPTURE.md).
Zone/fast-travel remains deferred until it resolves a concrete dependency after
the earlier priorities. Official observations and passing offline tests establish
no playable private server or Milestone 1 acceptance.
