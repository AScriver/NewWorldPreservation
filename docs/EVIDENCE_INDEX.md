# Evidence and fixture index

The [JSON catalog](../research/agent-evidence-index.json) maps each protocol boundary
to ROADMAP tasks, ledger claim IDs, slice docs, original scripts, tests, receipts
and sanitized fixtures. It is navigation and fixture identity metadata. Current
status and the exact next blocker remain in [ROADMAP](ROADMAP.md).

| Boundary ID | Tasks | Read first |
|---|---|---|
| `current-registration-request-serializer` | M1-06B | [V3 selection and interface role](REGISTRATION_REQUEST_SERIALIZER.md) |
| `current-registration-response-body-codec` | M1-06B | [Current body contract and offline codec](REGISTRATION_RESPONSE_BODY_CODEC.md) |
| `current-registration-acceptance-subscriber` | M1-06B | [Concrete conditional subscriber](REGISTRATION_ACCEPTANCE_SUBSCRIBER.md) |
| `ghidra-function-slices` | Offline tooling | [Function-scoped Ghidra](TOOLS.md#function-scoped-ghidra-default) |
| `reference-environment` | M1-00 | [First Light analysis](FIRST_LIGHT_ANALYSIS.md) |
| `historical-client-setup` | M1-02H | [Historical review](FIRST_LIGHT_HISTORICAL_CLIENT.md), [executed owned-copy Frida/DTLS trial](FRIDA_PRIVATE_DTLS_TRIAL.md) |
| `bootstrap-https-ownership` | M1-01 / 02A | [Connectivity](CURRENT_CLIENT_CONNECTIVITY.md) |
| `channel-token-request` | M1-02B / 02B1 | [Channel](BOOTSTRAP_CHANNEL.md) |
| `token-envelope` | M1-02B2 | [Token session contract](TOKEN_SESSION_CONTRACT.md) |
| `credentials-selection-queue` | M1-02B3 / 04 / 05 | [Private handoff](PRIVATE_GAME_HANDOFF.md) |
| `local-dtls` | M1-03 | [DTLS](DTLS_REGISTRATION.md) |
| `rep-trust-settings` | M1-02C | [Trust policy](REP_TRUST_POLICY.md) |
| `registration-spawn` | M1-06 / 07 | [Carrier trial](CARRIER_REGISTRATION_TRIAL.md), [spawn evidence](SPAWN_SEQUENCE.md) |
| `replication-reconnect-acceptance` | M1-08 through 12 | [Architecture](ARCHITECTURE.md) and [ROADMAP acceptance](ROADMAP.md#acceptance-boundary) |

## Search and freshness

Search boundary IDs, task IDs, claim IDs or filenames with `rg`. For example:

```powershell
rg -n 'rep-trust-settings|K46|current-queue-handoff-result' .\research\agent-evidence-index.json
rg -n '\| K46 \|' .\docs\EVIDENCE_LEDGER.md
& C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 -Path .\scripts\Get-ProjectPreflight.ps1 -Execute
```

For machine processing, use `Get-ProjectPreflight -OutputFormat Json` through the
wrapper. It reports the environment, upstream pins/cleanliness/reference fixture,
dirty and untracked paths (bounded details), every catalogued fixture hash and the
public source/runtime bindings in catalogued receipts. Missing references are
explicit; they do not block the workspace-only test profiles. A specific new run
can be checked with `-Receipt .scratch/offline-validation/run-<id>/receipt.json`.

Receipt freshness has three meanings:

- `local-bindings-match`: the checkable public inputs match the receipt. Private
  artifact/client/runtime observations can still be unverified.
- `stale-local-inputs`: at least one bound source/fixture/runtime input differs or
  is missing. Revalidate the affected claim if using it as current support; retain
  the old observation as historical evidence.
- `unknown`: no checkable public binding, malformed/unavailable metadata, or a
  changing file. This is not a passing freshness check.

Preflight never reads private/raw artifacts, installed client bytes or private
keys. External/private bindings are counted as unchecked. It does not create
files, run probe code, download/sync dependencies, open game processes or listeners,
query Windows trust/hosts, or rerun the recorded experiment. Git/files are observed
sequentially; the runner separately compares selected input hashes before/after.

## Classification and maintenance

Each receipt/fixture has a classification and limit: observed metadata,
offline-executed controls, source inference, historical upstream, or synthetic.
Synthetic candidate schemas may be compatible under a recorded live comparison;
their replay is still an offline test. Empty current actor/registration fixture
lists deliberately identify missing evidence rather than inventing a wire shape.

When adding a lawful sanitized fixture, add its path, provenance/classification,
SHA256 and boundary to the catalog and connect it to its tests. Preflight reports
unknown fixtures, missing paths, unknown claim IDs and missing ROADMAP task links.
When changing fixture bytes, review provenance and rejection cases, deliberately
update its catalog hash, and rerun the relevant profile. Do not regenerate existing
research receipts to make their hashes look current.

Update [offline-test-profiles.json](../scripts/offline-test-profiles.json) when a
reviewed offline test/module or direct input changes. The complete workspace profile
refuses unreviewed test modules rather than silently selecting them. The reviewed
REP read-only fake-API test is included in the complete profile and has its own
focused profile; its live probe CLI remains outside the offline command.
When adding/removing a group member, update the reviewed inventory count in
`validate_offline.py` as part of the same reviewed change. The upstream helper's
zero-case exception is pinned explicitly; unexpected empty modules remain errors.
