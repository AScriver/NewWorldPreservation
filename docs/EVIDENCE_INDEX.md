# Evidence and fixture index

The [JSON catalog](../research/agent-evidence-index.json) maps each protocol boundary
to ROADMAP tasks, ledger claim IDs, slice docs, original scripts, tests, receipts
and sanitized fixtures. It is navigation and fixture identity metadata. Current
status and the exact next blocker remain in [ROADMAP](ROADMAP.md).

| Boundary ID | Tasks | Read first |
|---|---|---|
| `current-connect-ack-retry` | M1-07 | [Validated retry correction and fresh pending proposal](PLAYER_CREATION_TRIAL.md) |
| `private-player-creation-trial-20261007` | M1-07 | [Closed pre-creation guard failure and cleanup](PLAYER_CREATION_TRIAL.md) |
| `private-trial-lifetime` | M1-07 | [User-confirmed creation trial lifetime](PLAYER_CREATION_TRIAL.md) |
| `current-character-identity-override` | M1-07 | [Selected owned identity-override inputs](CHARACTER_IDENTITY_OVERRIDE.md) |
| `private-player-creation-trial-preparation` | M1-07 | [Default-off one-candidate trial and pending admission](PLAYER_CREATION_TRIAL.md) |
| `private-trial-character` | M1-07 | [One fresh original record across HTTP and player inputs](PRIVATE_TRIAL_CHARACTER.md) |
| `current-player-creation-candidate` | M1-07 | [Original two-member type8 candidate](PLAYER_CREATION_CANDIDATE.md) |
| `owned-player-delivery-index` | M1-06A | [Observed baked index and conditional delivery](PLAYER_DELIVERY_INDEX.md) |
| `current-player-identity-body` | M1-06A | [Concrete identity fields and bounded BODY codec](PLAYER_IDENTITY_BODY.md) |
| `current-creation-trial-ref` | M1-06A | [Original fresh reference policy and source limits](CREATION_TRIAL_REF.md) |
| `owned-player-resource` | M1-06A | [Exact owned player resource input](OWNED_PLAYER_RESOURCE.md) |
| `current-type8-bundle-body` | M1-06A | [Paired BODY and bounded payload codec](TYPE8_BUNDLE_BODY.md) |
| `current-creation-replication-record` | M1-06A | [Record reader inverse and paired member writer](CREATION_REPLICATION_RECORD.md) |
| `current-creation-member-body` | M1-06A | [Concrete member class and BODY](CREATION_MEMBER_BODY.md) |
| `current-player-member-application` | M1-06A | [Decoded member to guarded creation dispatch](PLAYER_MEMBER_APPLICATION.md) |
| `current-player-entity-clone` | M1-06A | [Nested Entity clone and Id treatment](PLAYER_ENTITY_CLONE.md) |
| `current-player-entity-vector` | M1-06A | [Owned vector and guarded binding receiver](PLAYER_ENTITY_VECTOR.md) |
| `current-player-entity-binding` | M1-06A | [Current typed reference binding and guard ownership](PLAYER_ENTITY_BINDING.md) |
| `current-registration-request-stream` | M1-06B | [Offline selected V3 sender stream encoder](REGISTRATION_REQUEST_STREAM_CODEC.md) |
| `current-registration-identifier-placement` | M1-06B | [Current outer UUID and inner type-selector join](REGISTRATION_IDENTIFIER_PLACEMENT.md) |
| `current-registration-lookup-text` | M1-06B | [Offline verified lookup-text conversion](REGISTRATION_LOOKUP_TEXT_CODEC.md) |
| `current-registration-setup-inputs` | M1-06B | [Actual setup input caller and tagged pair](REGISTRATION_SETUP_INPUTS.md) |
| `current-registration-stream-framing` | M1-06B | [Current physical stream and queued backend join](REGISTRATION_STREAM_FRAMING.md) |
| `current-registration-request-body-codec` | M1-06B | [Offline selected V3 BODY API and original fixtures](REGISTRATION_REQUEST_BODY_CODEC.md) |
| `current-registration-request-3e0-codec` | M1-06B | [Complete V3 field+3e0 schema](REGISTRATION_REQUEST_3E0_CODEC.md) |
| `current-registration-request-2c8-codec` | M1-06B | [Complete V3 field+2c8 schema](REGISTRATION_REQUEST_2C8_CODEC.md) |
| `current-registration-request-c0-codec` | M1-06B | [Complete V3 field+c0 schema](REGISTRATION_REQUEST_C0_CODEC.md) |
| `current-registration-request-collection-codec` | M1-06B | [V3 sequence and first collection](REGISTRATION_REQUEST_COLLECTION_CODEC.md) |
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

## Community reference navigation

The [player-creation guidance](COMMUNITY_PLAYER_CREATION_GUIDANCE.md) preserves
the user's October 6 Discord resource/GdeRef leads, mode-2 static cross-check,
missing generator inputs and preference to investigate locally before asking more
questions. The raw snippet stays private; no current player-spawn result follows.

The [feature catalog guide](COMMUNITY_FEATURE_CATALOG.md) records the user's
October 6 Discord download, its verified index/UUID agreement and attributed
creation-metadata, position-state and level-acknowledgement labels. It connects
those leads to M1-06/M1-08 documents and the ignored full reference. This is source
navigation, with no new accepted protocol boundary, fixture or gameplay claim.

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
