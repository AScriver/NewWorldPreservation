# First Light historical client setup

Task: **M1-02H**. Current status and ordering belong to [ROADMAP](ROADMAP.md#exact-next-blocker).
Investigated October 4, 2026. This is a source/history review and read-only installed-client
inspection, not a reproduced client launch or private-DTLS result.

## Decision

**Later October 4 authorization:** the user explicitly requested changing repo
boundaries and verifying Frida startup/runtime trust changes. The earlier decision
below records the preceding source-only review. Its authorization blocker is
superseded by the bounded [owned-copy Frida trial](FRIDA_PRIVATE_DTLS_TRIAL.md);
historical recipe uncertainty and the need for actual runtime evidence remain.

The later trial now reproduces direct startup and private DTLS on the owned
Steam22469132 build: two handshakes with decrypted application counts. Its permissive
runtime policy is explicitly separate from unchanged-stock trust. See the executed
[trial result](FRIDA_PRIVATE_DTLS_TRIAL.md#executed-results); the source-only decision
below is historical, and the unsent question is optional provenance clarification.

First Light documents a concrete historical mechanism: start `NewWorld.exe` through
Frida instead of its launcher, supply Steam application context, then load a runtime
trust hook before the private connection. It does **not** establish that the current
owned installation can use that method within this project's intact-launcher/EAC and
no-process-memory-write boundaries. A separate copy would protect installed files,
but would not establish launch compatibility or bring those runtime operations within scope.

The missing checksum is **not** the reason to stop. Following the user's clarification,
build/hash metadata are identity aids, not an independent prerequisite to deciding
whether the mechanism is usable. The material missing input is a reproducible launch
and private-trust recipe that fits the authorization boundary, or a clear maintainer
statement that the historical result depended on operations outside it. No runnable
client experiment is admitted from the present evidence. The maintainer question below
is the deliverable; it has not been sent.

The FAQ distinguishes two historical workflows: its live-Steam/private-server claim
uses a memory patch after EAC initialization, whereas decrypted in-process capture
uses an archived/pre-EAC target. The final capture guide instead defines non-EAC by
omitting the launcher through Frida spawn. Do not infer that a special SteamCMD build
was required merely to connect. Disabling the trust patch is documented for real-server
capture, with a warning that local mock routing then fails validation ([guide185–198](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/tools/client-hooks/README.md#L185)).

## Inputs and evidence limits

- Workspace HEAD: `8c877be640ceebefdc451d21b9454a092b1d948d`. Existing changes to
  connectivity, ledger, trust policy, roadmap, catalog and the fresh blocked-audit
  receipt were present before this task and preserved. Exact initial hashes are in
  the ignored `.scratch/first-light-historical-20261004/inputs-before.json`.
- First Light: clean ignored checkout at
  `63756a3f7ff0ae41752dcc7c80267802c3fa7548`; 608 reachable commits, not shallow.
  Relevant docs/tools are included in its sparse checkout. Source bindings and public
  metadata observations are in [the review receipt](../research/evidence/first-light-historical-client-review.json).
- Public GitHub metadata was read without authentication or messaging: one branch
  at the same head, no tags/releases, 25 issue/PR bodies across two complete pages.
  Selected comments on 5, 21 and 25 supplied no launch recipe. This is bounded public
  evidence; private community discussions and unindexed archives remain unknown.
- Registered/conventional Steam libraries identify one installation; two case spellings
  in the private inspection receipt refer to the same Windows path. This was not an
  exhaustive search for old archives or a full asset-integrity verification.

## What the historical sources establish

All source links below pin the same First Light revision. Claim classifications and
stable IDs are recorded in [the ledger](EVIDENCE_LEDGER.md#first-light-historical-client-setup--october-4).

| Fact / claim | Evidence and classification | Limit |
|---|---|---|
| The final guide defines non-EAC by direct Frida spawning, claims Steam-identical executable bytes, and requires logged-in Steam | [Client-hooks guide, lines 29–36](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/tools/client-hooks/README.md#L29); historical claim | No executed proof here that this works on today's owned installation |
| The actual capture launcher defaults to the installed Steam executable, writes adjacent `steam_appid.txt`, spawns through Frida and loads the trust hook by default | [Defaults](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/tools/client-hooks/frida_capture.py#L56), [spawn](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/tools/client-hooks/frida_capture.py#L243), [default trust flag](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/tools/client-hooks/frida_capture.py#L356); strongly source-supported | Documentation's no-disk-write description is contradicted by this file write; source was inspected, not run |
| The archived-binary plan reports initial Steam-context failure, then a May 5 working-route assertion | [Plan](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/docs/non-eac-capture-plan.md#L3); historical claims | Initial failure and later assertion are preserved; no successful launch receipt binds the complete configuration |
| A guide attributes its hook location to a May 6 SteamCMD download, while FAQ calls the capture target pre-EAC and provides no sourcing path | [Guide provenance note](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/tools/client-hooks/README.md#L240), [FAQ](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/docs/faq.md#L7); historical/unknown | Exact Steam branch/depot/build, full version, hash, and relation between these targets are not established; date is a reported download date, not a release identity |
| The May 2 public reference is a different evidence item; its analysis labels `6031`, Javelin `600415`, retail, AppID `1063730` | [Reference metadata](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/info/nw-login-safe-20260502-153840/README.md#L1), [V3 analysis](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/analysis/v3_request/BODY_DECODE.md#L42); strongly source-supported metadata | Those strings do not identify the executable or link that capture to the May 6 download/private-server launch |
| The checked-in hook changes client memory and chooses a permissive certificate-verification path | [Actual hook](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/tools/client-hooks/frida_dtls_trust_patch.js); strongly source-supported | It does not implement retained-private-CA verification/unrelated-root rejection; the FAQ's older code-rewrite/live-EAC story is not proof of current compatibility |

History anchors: `81e93c6` introduced the archived-client plan; `4a77957` added adjacent
AppID creation; `155bfc4` changed its status to working on May 5; `5fbd83e` moved the
hooks to `tools/client-hooks`. Older [capture-route notes](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/docs/capture-routes.md#L29)
report failed instrumentation/no working route. These notes and later success claims
describe different checkpoints and do not form a verified, complete setup record.

Targeted source challenge also found that the FAQ's named [standalone wrapper](https://github.com/nw-private-server/first-light/blob/63756a3f7ff0ae41752dcc7c80267802c3fa7548/tools/client-hooks/frida_dtls_trust_patch.py#L30)
looks beneath a missing nested `tools/tools` path and attaches before reading the file
(lines82–83). Its adjacent hook exists; the capture launcher resolves it differently.
The current hook installs an interceptor and writes a pointer, while the FAQ describes
an older byte rewrite. The hook's own comment reports that rewrite failed before a
ClientHello. These are source mechanics and historical reports, not executed trials
here; the FAQ command is not a runnable recipe at the pinned revision.

## Owned installation and reproducibility

Read-only inspection at `2026-10-04T16:45:41Z` observed:

| Item | Observed identity |
|---|---|
| Steam app / build | `1063730` / `22469132` |
| Client file/product version | `1.400.6031.6004151` |
| Executable SHA-256 | `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e` |
| Launcher SHA-256 | `5a9217fafb5656c0b72b516583287ca362c3e1a87e1b5b515ad64a6402b292ec` |
| Client / launcher signatures | Both valid |
| Installation | `C:\Program Files (x86)\Steam\steamapps\common\New World` |
| Existing adjacent AppID file | `Bin64/steam_appid.txt` absent |

An owned Steam installation is available; historical incompatibility is **not** proved.
Nor is successful direct launch/private DTLS proved. The historical executable's exact
identity remains unknown, but that alone does not rule out using the owned files. The
checked-in entry point is unsuitable as a guarded experiment against the installed path:
it writes there and intentionally performs the launcher/instrumentation/trust operations
described above. No such operation was executed. Existing stock-client CA investigations
remain parked unless concrete new evidence changes their premises.

## Exact missing information

1. **Meaning and source of the target:** was the successful capture client the ordinary
   Steam-owned executable launched differently, an independently obtained pre-EAC
   release, or some other artifact? Explain its legitimate acquisition/entitlement and
   whether a separately staged copy of today's installation is sufficient. A build or
   manifest is useful if known; absence of a checksum is not itself a stop condition.
2. **Successful launch context:** exact entry point, working directory, arguments,
   Steam state/AppID context, and whether the functioning setup required omitting,
   disabling or evading EAC rather than an ordinary supported launch option.
3. **Private-DTLS dependency:** did the reported private handshake require the runtime
   trust hook/code rewrite/proxy DLL? Is there an evidenced verification-preserving
   private-root mechanism on the historical target, with no process-memory writes?
4. **A reproducible observation:** one dated, sanitized command/config/result record
   tying those conditions to a completed handshake against a private endpoint. No
   copyrighted executable/assets, accounts, credentials or raw secret-bearing capture
   should be requested or shared.

## Optional maintainer provenance question — not sent

> We reproduced two private DTLS1.2 handshakes on an isolated copy of our legitimately
> owned Steam22469132 client (`1.400.6031.6004151`), using direct Frida spawning and
> the trust hook at63756a3. The installed executable/launcher were preserved. Your
> client-hooks guide describes non-EAC as direct Frida spawning of Steam-identical
> `NewWorld.exe`, while the FAQ/plan refer to an archived or pre-EAC binary. Which
> historical setup actually completed private DTLS, and did the archived/pre-EAC
> descriptions refer to connection testing or only in-process capture?
>
> Could you provide the successful entry point, working directory, arguments, Steam
> context and required file/config changes, including how EAC was handled and when the
> runtime trust hook was applied? Which repository revision and exact hook/launcher
> produced the successful handshake, when was it installed relative to EAC and DTLS
> initialization, and did it remain attached? A known version/build is useful, but we're primarily
> asking for provenance and a sanitized result, not a binary download or checksum.
> Our responder currently stops at decrypted application counts, so this reproduces
> transport rather than game registration, world entry or actor behavior.

The defunct repository notice says its issue tracker is unmonitored. This draft can be
provided to verified maintainers through a user-chosen channel; no continuity or current
invite is assumed from public third-party comments. This task does not authorize sending it.

## Experiment admission and cleanup

The following is the **earlier review's historical decision**, superseded only for
the specifically authorized [Frida trial](FRIDA_PRIVATE_DTLS_TRIAL.md).

No executable client experiment is supplied because the launch/trust prerequisites above
are unresolved. After receiving concrete new evidence, prepare **one** separate procedure:
stage only legitimately owned files under ignored private storage; account for every
write; identify its child processes and loopback services; prove endpoint isolation before
launch; and stop at the DTLS outcome. Do not use the upstream default Steam path, permissive
hook, capture hooks or all-interface service defaults as a project runbook. Any launcher,
memory, capture, trust or routing operation must still meet the existing authorization.

For an admitted future experiment, cleanup must stop only owned children/listeners,
restore only its routing/rules/config changes with exact readback, preserve the user's
retained CA policy, and compare installed client/launcher/manifest plus adjacent-file
state before/after. Keep client copies, keys and diagnostics ignored. An isolated copy
protects installed files; it does not prove historical compatibility or authorize EAC
circumvention. The source review/installed-client inspection created documentation and
ignored receipts, with no game or system-resource changes. Required offline workspace
checks separately used transient loopback children and isolated test files; their
cleanup and preservation readback are recorded in [verification](../research/evidence/first-light-historical-client-validation.json).
No Steam, routing, firewall or trust change and no client process operation occurred.
