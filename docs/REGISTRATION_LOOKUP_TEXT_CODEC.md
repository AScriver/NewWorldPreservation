# Offline registration lookup-text conversion — #228

October6, 2026; workItemId164 / parent178. The original BODY module now exposes
`tagged_from_lookup_text(text: bytes) -> TaggedField`, implementing the local
conversion closed by [#227](REGISTRATION_SETUP_INPUTS.md). It supplies an active
tagged value for the [#225 BODY API](REGISTRATION_REQUEST_BODY_CODEC.md).
This does not select configured values or establish identity/authentication.

Clean input main `f5166334de14352f2843ba79f4ed488647a43953`; owned build22469132,
image SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
[Original validation receipt](../research/evidence/current-registration-lookup-text-validation.json)
records current source rehashes, implementation/fixture identity and executed checks.
All44 source code spans/14 windows and six carried BODY bindings matched before edits.

## Conversion and deliberate limits

Input must be immutable `bytes` of at most0x2ffff bytes. Only the prefix before
the first NUL is examined; that prefix must be ASCII. Non-ASCII bytes after the
NUL are ignored. Rejecting an oversized full input and non-ASCII retained prefix
is an explicit stronger offline rule; native locale, allocation and fault behavior
remain outside the proved domain. Existing BODY string fields still accept raw bytes.

The parser accepts lengths32..38, optionally skips an opening brace and reads
16 sequential hex pairs. A hyphen after byte4 enables required separators before
bytes6/8/10. It checks neither a matching closing brace nor complete consumption.
Both ASCII lettercases anywhere in the retained prefix force text/tag0, even if
the hex pairs parsed. Failed parsing also retains the original prefix as text/tag0.

Other successful parses produce raw16 in input byte order and tag bit0, adding
bit1 for an opening brace, bit2 for a hyphen at character8 or9, and bit3 when no
lowercase ASCII letter occurs. All-digit input sets bit3; accepted suffix letters
can change flags or force text fallback. No strict UUID normalization is added.
The result contains only the active wire payload; native inactive original text,
allocator/context fields and partially mutated native objects are omitted.

For example, `01234567890123456789012345678901` produces tag9 and sequential
raw16. Appending `aa` produces tag1; appending `aA` produces text/tag0. An opening
brace without a closing brace can still parse. These are original synthetic values.

## Verification

[Original vectors](../tests/fixtures/registration/current-lookup-text-original.json)
cover all eight generated formatting tags, case/suffix effects, missing braces,
length boundaries, invalid hex and first-NUL behavior. The existing BODY test
module adds all16 separator masks, non-ASCII/domain/type/full-size checks and an
exact persona-first(+3e0)/character-second(+420) BODY golden. Focused checks pass
433 cases, including66 new cases; the receipt separates independent model checks
and required workspace regression from native/current-client observations.

No native/client code ran. Runtime getter contents/selection, other setup input
producers, authority, lower transport selection/emission and #212's fresh
construction/member/framing gates remain open. Parent178/164 and Milestone1
retain their actual acceptance requirements.
