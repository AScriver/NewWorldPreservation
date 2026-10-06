# One fresh private trial character

This original local record removes fixture identity reuse before the first
server-driven player experiment. It is ephemeral backend input, with no official
account, ticket signature or native authentication claim. WorkItem164, leaf253
under247; baseline clean `bbadb9d`.

`scripts/private_trial_character.py` owns one frozen record: four distinct fresh
UUIDv4 values for local session, character, persona and ticket, a UTC creation
time, a small original ASCII name and one once-assigned GdeRef. The reference
uses the existing [trial policy](CREATION_TRIAL_REF.md); caller-supplied occupancy
is local knowledge, not an observation of native client maps. The three old
fixture identities are rejected. The default name is `Preservation`; its name
policy is an experiment constraint, not the game's complete naming rules.

The strict original JSON schema is confined to ignored `.scratch/` or `private/`
paths in this checkout, bounded to4096bytes and written exclusively. Reading
rejects unknown/duplicate fields, malformed IDs, references or timestamps and
known reference collisions. An existing record cannot be overwritten. IDs,
reference bytes and request contents are absent from success output and logs.

## Joined inputs

The optional `trial_character` API parameter supplies the same record to both
`session_handoff_probe.response_case/make_server` and
`queue_contract_probe.response_case/make_server`. Queue retains that same record
and delegates it to selection. With the parameter absent, every legacy response
remains byte-identical.

| Boundary | Original record fields |
|---|---|
| Login-info selected character | CharacterId, PersonaId, Name, CreatedDate, ModifiedDate |
| Queue response and token | TicketId at both levels; token CharacterId and PersonaId |
| PlayerIdentityBody | Exact UTF-8 character ID and name |
| Creation member | Same once-assigned GdeRef |
| Local evidence correlation | Session UUID in the private record; not a new wire field |

The supported world/location remains `pdx-nwp-local-1`. Existing token clocks,
signature and other experiment defaults remain unverified synthetic values.
Only `seed-character` and `token-loopback` accept a supplied record; contradictory
empty cases and wrong record types fail before certificate loading or binding.

## Offline administrative preparation

Run these Python entry points through a validated task-specific PowerShell
script, with explicit native argument arrays:

```text
.venv/Scripts/python.exe -B scripts/private_trial_character.py create --path .scratch/<unique-trial>/character.json --known-empty-occupancy
.venv/Scripts/python.exe -B scripts/private_trial_character.py verify --path .scratch/<unique-trial>/character.json --known-empty-occupancy
```

`--known-empty-occupancy` is the caller's explicit assertion about its new local
backend reference set. Otherwise provide each `--occupied-low64` value. Creation
draws fresh values once; verification never regenerates them. Queue CLI can read
the same file through `--trial-character` with either
`--trial-known-empty-occupancy` or repeated `--trial-occupied-low64`.

This unit adds no controller forwarding, Carrier messages, client launch or
observer sites. Use one retained file for an eventual admitted fresh trial;
create another after a restart rather than recycling this session's identities.

## Verification and remaining blocker

The [receipt](../research/evidence/private-trial-character.json) records selected
source/fixture hashes and executed checks. An isolated original HTTPS exchange
joins selection and queue ID/persona/ticket/world values to the identity BODY and
inert creation candidate, with exact server/thread/log cleanup. Negative checks
cover input, path, extent, occupancy and exclusive-write guards; legacy byte
parity remains covered.

This proves local consistency. It does not prove the native local-ID provider,
runtime delivery mode, resource load, entity creation or designation. The last
real-client result remains context initialization followed by spawn timeout.
The next useful experiment is a separately admitted nonempty creation candidate
using this same fresh record, with rendering, camera/input and later movement
acceptance observed independently. See [the immediate milestone](ONE_PLAYER_MILESTONE.md).
