# Owned-copy Frida private DTLS trial

Task M1-02H. The October 4 user instruction explicitly authorizes changing the
repository boundary to verify direct Frida startup and runtime trust changes.
Offline validation still never starts or instruments the game. This procedure
preserves the installed Steam client, launcher and EAC; the trial omits the launcher
only for a physical private copy. Access denial or startup refusal ends that attempt.
No EAC service/driver changes, arbitrary capture hooks or Amazon game traffic are admitted.

## Inputs and prerequisites

- Legitimately owned New World installation, Steam already running in its ordinary
  logged-in account; no preexisting game/launcher or listeners on TCP443/UDP64003.
- Pinned owned executable SHA256
  `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`,
  version `1.400.6031.6004151`, Steam build22469132. These identify this experiment;
  absence of a historical SteamCMD checksum is not a prerequisite.
- Full physical copy in one ignored `private/frida-trials/run-*/client` directory,
  with no hardlinks/junctions. October4 staging copied194 files/76,416,682,357 bytes.
  Only the copy receives adjacent `Bin64/steam_appid.txt` containing1063730.
  The installed EXE/launcher/manifest hashes and signatures are checked before/after.
- Clean local First Light reference at
  `63756a3f7ff0ae41752dcc7c80267802c3fa7548`. Load only its unchanged
  `tools/client-hooks/frida_dtls_trust_patch.js`, SHA256
  `42ebaa8fe9804588a5c41a26cd1d2bbf7c0492845a114dfbb4e15c16d236811d`.
  No upstream code is copied into tracked files. Its standalone Python wrapper has
  the wrong hook path; its capture launcher writes installed files and captures
  broader data. Neither is run.
- Shared Frida17.22.0/Python3.11.9 via the validated `Run-Tool.ps1` entry; repository
  pinned `.venv` for existing original HTTPS/DTLS responders. Every PowerShell
  script is parsed/checked with `Invoke-CodexPowerShell.ps1` before execution.
  Windows venv `python.exe` is a redirector: both measured runtimes create a second
  Python311 process. The services therefore use the measured base interpreter
  directly with repository venv site-packages; containment also covers the actual
  base image used by Frida. Requested launcher PID is not service-owner evidence.
- Existing user-retained private CA, expiring October9, is reused without a store
  import/remove. Windows elevation is necessary for owned hosts/firewall changes.

## Resource contract and execution

One serial controller, [Invoke-FridaPrivateTrial](../scripts/Invoke-FridaPrivateTrial.ps1),
owns a fresh run manifest, rule group, hosts transaction, three retained service
Process objects, and the synchronous Frida dispatch. All source/configuration inputs
are hash-bound in the private `trial-inputs.json` before dispatch.

Before any game starts, block all non-loopback addresses for every staged executable,
the actual protocol/Frida Python runtimes and PowerShell. Installed game/helper paths
also receive temporary rules to contain a possible Steam broker relaunch. Read back
rule scope in ActiveStore, map only the three previously observed bootstrap/token
names to127.0.0.1/::1, and verify exact owned HTTPS listeners and UDP127.0.0.1:64003.
The existing Steam licensing broker stays outside the job and is unmodified.
Firewall readback establishes configuration, not an independent packet trace.

[frida_client_trial.py](../scripts/frida_client_trial.py) directly spawns the copy
suspended with SteamAppId/SteamGameId1063730 and its Bin64 working directory. It
retains the exact process handle/creation time, assigns a kill-on-close Windows Job
Object with no breakaway and one-process limit, and enables Frida child gating.
The restriction on children is an experimental condition, not a claim about historical
launch requirements. No child is admitted. A refused job assignment/attach ends startup.

The original [observer](../scripts/frida_trial_observer.js) checks main image path/name
and pinned initializer-entry bytes before intercepting RVA0x5dce750. It records only
whether slot+0x288 was nonzero at entry and zero at initializer return, plus success
booleans. Load the unchanged upstream trust hook only after that gate, then resume.
The upstream hook writes that pointer in memory, selecting a permissive policy.
This intentionally changes certificate verification for the trial; it is not a stock
CA configuration fix or evidence of unrelated-root rejection.

The subsequent bounded map/context diagnostic may opt into the three exact
callback/gate sites in [its contract](../research/evidence/current-context-gate-contract.json).
All additional entry prefixes are verified before resume. It records only
entry/return, seven booleans or unknown values and ephemeral tags, capped at96 events;
it adds no memory writes. Follow the separate admission and source bindings in
[the registration procedure](CARRIER_REGISTRATION_TRIAL.md).

The single October4 attempt allows240 seconds after resume. If the private character
preview appears, Play may trigger the existing queue contract and DTLS initializer.
The existing metadata-only services discard incoming authorization/body values and
DTLS application bytes; they do not implement a world, private credential security
or new application wire formats. No raw packet capture is collected.

Keep four outcomes separate: spawn/attach/resume; hook registration; an observed
initializer invocation/entry-return pointer readings; and actual attributed private
DTLS completion. Entry/return readings do not by themselves prove the exact instant
of the upstream write. Hook registration does not prove the function was invoked.
Responder handshake completion does not prove world entry, actors or Milestone1.

## Cleanup

Create `stop.request` to close admission. The runner holds `runner.lock` open from
before admission through exact game-job cleanup. The controller requires exclusive
access to that file before releasing containment, so a delayed/orphaned runner cannot
start after rules are removed. Terminate only the retained game job and exact owned
service handles. Detaching a Frida session alone does not undo modified runtime data.

Confirm no game/launcher and no trial listeners; compare installed hashes/signatures
and adjacent AppID absence; restore only the journal's unique hosts block; remove only
the run's matching firewall name/group/description/program rules and verify both stores.
Retain the user's existing CA. Any process/rule identity or cleanup ambiguity keeps
remaining containment and requires reconciliation. Never stop a preexisting process.

The client copy and all raw receipts stay ignored for reproducibility. To reclaim its
roughly76GB later, first confirm cleanup, resolve the exact run path inside
`private/frida-trials`, and remove only that owned copy using native PowerShell;
never delete or move the installed Steam directory.

## Executed results

**Reproduced October4:** one isolated game PID5708 directly spawned suspended,
attached, installed the pinned trust hook and resumed. The user reached the private
preview and clicked Play twice. Two initializer invocations recorded nonzero entry
verification slot→zero at return and successful initializer return. Two server-side
DTLS1.2 handshakes completed at18:00:00.159 and18:00:42.550UTC with
ECDHE-RSA-AES256-GCM-SHA384. Each delivered124 decrypted application records,
2,156bytes, whose contents were discarded. Bound UDP endpoint ownership and exact
HTTPS tuple lookup associated the staged PID. See the [executed receipt](../research/evidence/first-light-frida-private-dtls.json).

This demonstrates the mechanism on the owned build. Historical binary identity and
exact launch-environment equivalence remain unknown. No matched unhooked control
or immediate post-write reading was collected, so exact write causality/necessity is
not established. The executed runner lost its observer-registration log because a
callback keyword collided with the logger parameter after setting admission state;
its invocation logs remained. The later strict logging/sanitization fix is tested
offline only. As-executed runner bytes are preserved privately and hash-match the
input manifest; future code is not retroactively substituted for them.

Both clicks showed the user's generic Connection Error popup. The probe supplied no
application replies and closed each peer at its128-datagram limit around13.38seconds
after handshake. That failure cannot diagnose a missing message under this deliberately
nonresponsive responder. Carrier/V3, world entry, actors and Milestone1 remain unproven.

One service preflight failed on virtual-environment launcher-versus-child PID identity
before any game start, and fully cleaned up before the corrected single game run.
Final cleanup initially stopped because the Steam manifest hash changed. Reconciliation
verified unchanged installed EXE/launcher hashes/signatures, same manifest app/build,
closed job/ports and exact rule ownership, then restored hosts byte-for-byte and removed
the11rules. Current Steam metadata was preserved; its change cause is unknown. The
retained CA remains Root1. No entire-directory or EAC runtime integrity attestation is
claimed. The ignored76GB copy remains for reproducibility.

For this completed local experiment, private `trial-inputs.json` records all manifest
keys/input hashes and exact paths; `cleanup-reconciled.json` records final readback.
The guarded staging/dispatch/recovery scripts are under ignored
`.scratch/frida-trial-20261004/`. A future attempt requires a fresh run manifest,
revalidated resources and a bounded application procedure; do not reuse closed logs
or simply remove `stop.request`.
