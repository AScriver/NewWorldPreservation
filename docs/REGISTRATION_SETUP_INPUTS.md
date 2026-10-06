# Current registration setup inputs — #227

October 6, 2026; workItemId164 / parent178. A current state-method path builds
the persona/character pair from named settings lookups and copies it through
setup into the registration request. The concrete registered provider, string
getter and local string-to-UUID conversion are joined in source. No client or
native client code was executed. Exact hashes, source review and executed pure
checks are recorded in the [receipt](../research/evidence/current-registration-setup-inputs.json).

Input: clean main `17807b1542af522607abb4268beb2ab6fa5e6ebf`, Steam build22469132,
version1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
The approved type map, reference checkouts, tool versions and relevant file
state are pinned in the original receipt. These are source-supported paths;
current handler selection, settings values and identities remain unobserved.

## Actual caller and pair — J227-1

Array method `0x14646c720` calls `0x14646d460`, then state method `0x14644a070`.
Its case9 reaches `0x146425f20`, which reads its registration owner at wrapper
+0x1000. On the ordinary branch, owner vtable+0x18 resolves to setup
`0x146b6d600`; the actual indirect call is `0x1464263d7`.

The caller initializes two adjacent 0x40-byte records, each with an empty owned
string, zero raw16 and tag0. It invokes `0x1463e3cb0` using getter thunk
`0x14057153c`, descriptor adjustment0 and these keys:

| Lookup | Call | Local pair record | Retained owner | V3 / V2 request |
|---|---|---|---|---|
| `javelin.impersonate-persona-id` | `0x146426192` | First, +0x00 | +0x510 | +0x3e0 / +0x2d0 |
| `javelin.impersonate-character-id` | `0x14642616d` | Second, +0x40 | +0x550 | +0x420 / +0x310 |

The pair base is stored at outgoingRSP+0x28, Windows x64 argument6 counting the
receiver. Setup copies both records; the builder supplies that retained pair
to the concrete request constructor. String, raw16 and tag are copied regardless
of which arm is active. A nonempty character lookup also replaces wrapper+0x12f0
and its associated raw/tag fields after a separate default-character conversion.
That local replacement supplies no identity validation or permission conclusion.

## Concrete provider and dispatch — J227-2

Provider constructor `0x140845950` installs vtable `0x147f4d700`. Its registration
block at `0x140845c80` publishes a receiver container through the context returned
by `0x1406d17b0` and writes its primary receiver pointer into one slot and the
end pointer. This block establishes no general append/preservation rule. The lookup helper uses the
same context+0x20 container and current entry plus the descriptor adjustment.
Its supplied thunk dispatches receiver virtual+0x1b8; this provider's slot is
concrete getter `0x140852480`, which calls lookup `0x140852900`.

The getter copies the stored string for a lookup tag other than0x0e; missing
tag0x0e produces an empty returned string. It does not establish strict identity
or value-type validation. Lookup flag+0x71 nonzero selects the aggregate map;
zero selects reverse layer traversal. The constructor initializes that byte1.
Actual flag, map population, configured values, per-invocation context identity
and other receivers remain unknown.
This reuses and rehashes the provider evidence carried by [K57](EVIDENCE_LEDGER.md)
and [its existing report](REP_TRUST_POLICY.md#descriptor-consumption-and-provider-population--october-3-continuation);
it adds the registration input join and revisits no trust/file-loading experiment.

Ordinary dispatch copies returned text only through its firstNUL into a new
owned local string, performs the concrete conversion below, then moves/replaces
the output string and copies raw16/tag. Each visited receiver can overwrite prior
output, including with an empty result. When no output-writing callback runs,
the caller defaults remain.
The getter's returned string object and the subsequent tagged record have
different storage roles; getter+0x20 must not be called the record's raw UUID.

An optional router path `0x1463e9550` uses the same getter descriptor, NUL copy,
conversion and output replacement. It writes output before checking local
dispatch state. State2 stops; an exhausted nonzero state also returns true and
suppresses the ordinary loop. Routerfalse can already leave output; the top
helper explicitly returnsfalse when a router consumes the call. Neither return
Boolean identifies output absence or acceptance. Concrete state writers and
runtime route selection remain unjoined.

## String/raw16 producer — J227-3

Local conversion `0x140875880` resets raw16 and tag, then calls parser
`0x14143bb90`. The latter admits declared length32..38, an optional opening
brace, and sixteen hex-byte pairs; a hyphen after byte4 enables required hyphens
before bytes6/8/10. Exact tables join upper/lower hex digits to nibble values.
The selected instructions check neither a matching closing brace nor exact
consumption of the input; trailing characters can be ignored by this parser.

After successful parsing, named imports `islower`/`isupper` classify the entire
original string. Mixed ASCII letter cases retain the string arm with raw0/tag0.
Otherwise raw16 is stored and tag becomes bit0 plus bit1 for an opening brace,
bit2 for a hyphen at position8 or9, and bit3 when no lowercase letter occurs.
All-digit UUID text gets bit3. Trailing letters outside the consumed hex can
change these flags or force mixed-case fallback. This joins [#224's formatter
flags](REGISTRATION_REQUEST_3E0_CODEC.md); it is a local representation rule,
with no authenticated identity conclusion or proposed wire value.

## Ownership and verification — J227-4

Returned provider text is copied before the temporary is released. Conversion
preserves the owned original string while setting raw/tag. Output move-assignment
releases prior owned text; setup assignment may reuse capacity or skip exact
self-assignment, and normal request construction owns its string copy. Pair
destructor `0x1407e6810` frees/resets second then first string, leaving raw/tag.
The request uses the then-current retained snapshot. Sequential copies establish
no atomic rollback, synchronization, native fault or full unwind guarantee.

Independent initial caller and retained-input reports, guided narrow provider
adjudication and targeted counter-review are distinguished in the receipt.
Counter-review corrected the setup callsite, excluded midinstruction window
prefixes and qualified return Booleans. It rechecked seven caller/parser bodies
and four retained pair spans, exercised26,112 finite ASCII mutations and twelve
boundary examples; the separate retained review checked2,146 instructions and
262,144 optional-field model cases. Final getter review rechecked seven bodies
and twelve frozen source ranges, confirmed constructor-internal registration and
qualified allocation success: a capacity-helper Boolean can reflect requested
length despite a null allocation result. Native allocation failure was untested.
These are executed pure/static checks, not native behavior. Failed no-PDATA, timed-out, bounded-cap and misaddressed queries
remain private; none supplies an absence claim.

The selected producer chain is closed. Actual settings/handler state, key
declaration semantics, other setup inputs, authoritative ticket/principal/peer
binding, #212's construction/member gates and Milestone1 remain unproved.
Parent178/164 stay open; no live trial, endpoint, replay, push or publication ran.
