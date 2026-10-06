# Private owned-client archive

October 6, 2026: checkpoint #241 under #166 / workItemId 164 preserved and
verified the installed static client before shutdown-dependent observations.
The archive stays outside the source checkout at
`D:\NewWorldPreservationArchive\owned-build-20261006T191830Z`.
No assets or raw configuration contents are committed.

Verified inventory: **374 files / 76,744,359,425 bytes**. This includes 192 owned
installation files, the Steam executable, and 181 Steamworks Shared redistributable
files. Installed launcher and EAC inputs are included. Two mutable log files were
excluded; account stores, user logs/settings, credentials and raw Steam ACF are
outside the archive scope. The ACF contributes only build/app/hash metadata.

Build `22469132`, executable version `1.400.6031.6004151`, executable SHA-256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
Private `inventory.json` records every archived relative path, size, source
identity and SHA-256. Its canonical file-inventory digest is
`ddcc7d8819af2be003001f4edf61d080f774897d8c9f8019332d870514237536`.

The collector streamed each copy, rehashed every source and destination, checked
the final source inventory and rechecked Steam identity. It rejected overwrites,
source/destination overlap, reparse points, insufficient space and source changes.
An independent synthetic review found that filename filtering alone could copy
sensitive configuration values. The tool now also screens loose text conservatively.
Follow-up review of all 37 archived text files passed; the exact owned shader-list
hash and complete permutation-list grammar admit its static cookie feature names.
Opaque packaged/binary assets stay undecoded. This is not a guarantee about arbitrary
unrecognized secret encodings. All 11 archive synthetic checks passed after the fix.
Collection ran from `2026-10-06T19:19:03.005927Z` through
`2026-10-06T19:21:53.253598Z`. It started no game or listener and left no collector
running. The archive is a private file copy on this machine; it is not a separate
off-machine backup, restore test or proof of post-shutdown Steam/EAC launch viability.

To preserve a later build, close your client normally and choose a **new** private
destination outside the repository:

```powershell
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Preserve-OwnedClient.ps1 -Execute -ArgumentList '-ArchiveRoot','D:\NewWorldPreservationArchive\NEW-UNIQUE-BUILD-DIRECTORY'
```

Read the fixed final status. Only `STATIC_ARCHIVE_VERIFIED` and private
`inventory.json` with `verified: true` establish completion. A failed copy remains
unverified; do not overwrite or treat `scope.json` as a completed inventory.
The installed Steam/launcher/EAC files are read, never changed. Public metadata
and limits are in [the original receipt](../research/evidence/owned-client-archive-20261006.json).
Successful official-session evidence and private-server gameplay are separate.
