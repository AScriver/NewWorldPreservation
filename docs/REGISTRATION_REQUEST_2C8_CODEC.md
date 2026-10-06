# Current V3 field+0x2c8 codec — #223

October 6, 2026; workItemId 164 / parent 178. The selected request's +0x2c8
aggregate now has a complete paired schema: three BE32 bit fields, eight counted
raw strings and one strict boolean. Fresh defaults and ordinary returned-failure
string disposal are also joined.

Clean input main `1249cd50ef1a27c5d0d0231b1484caf310b2163a`, owned build 22469132,
version 1.400.6031.6004151, image SHA256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`.
[Original receipt](../research/evidence/current-registration-request-2c8-codec.json)
pins image/map/references, source ranges, report identity and executed checks.
This is instruction-supported source inference. No native client code ran;
field meanings, authentication significance and runtime acceptance remain unknown.
[#221's selected sequence](REGISTRATION_REQUEST_COLLECTION_CODEC.md) and
[#222's c0 schema](REGISTRATION_REQUEST_C0_CODEC.md) retain their separate scopes.

## Complete paired layout — J223-1

Actual aggregate writer `0x1407d54a0` inlines the first four wire items, then
calls `0x1407d4540` at `0x1407d5607`. Reader `0x1407d9620` inlines only the
first two items, then calls `0x1407d7ce0` at `0x1407d97ab` for the rest.
Offsets below are relative to field+0x2c8, not the enclosing message.

| Wire order | Member offsets | Encoding |
|---|---|---|
| 1 | +0 | BE32 bits |
| 2 | +0x110 | One boolean byte |
| 3 | +4 | BE32 bits |
| 4–6 | +8,+0x28,+0x48 | Three counted raw byte strings |
| 7 | +0x68 | BE32 bits |
| 8–12 | +0x70,+0x90,+0xb0,+0xd0,+0xf0 | Five counted raw byte strings |

The writer's nested chain is `d4540` → tail `d46a0` → tail `d4490`.
`d4540` emits +0x28/+0x48 strings, +0x68 scalar and +0x70/+0x90 strings;
`d46a0` emits +0xb0, then `d4490` emits +0xd0/+0xf0. Exact jumps at
`0x1407d4699` and `0x1407d471a` and outgoing register/stack assignments join
those pointers. Ghidra folds the last tail into a single printed body; its
warning at `0x1407d4525` remains explicit, and the instructions govern the split.

Reader call arguments supply +4/+8 in R8/R9 and +0x28/+0x48/+0x68/+0x70/
+0x90/+0xb0/+0xd0/+0xf0 on the stack. `d7ce0` success-gates each primitive.
It has an exact PDATA span `0x1407d7ce0..0x1407d7e59`, SHA256
`786b48264d2e1978580ec273f3d7335e61b509a4a1ed350ba808a6a34151176f`,
and RET at `0x1407d7e58`. Fresh parent/role queries correct the historical
no-PDATA interpretation; the failed assertion and earlier bounded window are
retained privately. A refused batch does not establish that every entry lacks
metadata. None of this changes the established wire sequence.

## Bounds and partial read state — J223-2

All strings have compact uint32 byte counts and raw payloads. The writer uses
lengths 0..`0x2ffff`; above that it emits zero and omits content. The reader uses
`0x1407fc670`, rejects lengths at least `0x30000`, and accepts the already joined
nonminimal compact prefixes and uint32 wrapping. Embedded NUL bytes are data;
no character encoding or semantic labels are established.

| Ordinary failure | Code | Cursor and destination effect |
|---|---|---|
| Short BE32 field | 2 | Four bytes not consumed; that destination unchanged |
| Missing +0x110 byte | 3 | No byte consumed; destination unchanged; +0 already committed |
| +0x110 byte above 1 | 4 | Invalid byte consumed; boolean unchanged |
| String prefix, oversized length or short payload | 1 | Shared compact/string effects; earlier fields and cursor remain committed |

The writer normalizes any nonzero boolean to 1; the reader accepts only 0/1.
A valid boolean is stored before the later helper runs. All eight string reads
inherit the carried copy/move-before-final-extent behavior: if the copy returns,
a short payload can change the destination while leaving the cursor at its
post-prefix position. Native faults, overreads, exceptions and allocation
failures were not executed. A safe future offline parser must check payload
extent before copying and describe that stronger handling.

The helper has no rollback. Full helper success assigns only result+1; no
meaningful success error-code byte is established. Later +0x3e0/final+0x460
processing still has to succeed for full body decode.

## Fresh construction and normal disposal — J223-3

Selected placement constructor `0x1407e37d0` initializes the embedded `0x118`
bytes before the next field. Defaults are scalar +0=15, +4=0, +0x68=0,
boolean +0x110=false, and eight empty SSO strings at the listed offsets,
with size 0/capacity 15. These are construction defaults, not accepted gameplay
or authentication values. The last string occupies `[0xf0,0x110)`; the boolean
starts at +0x110 and does not overlap it. Initialized extent is not wire length.

On ordinary returned body failure, `0x1407ce8e0` invokes virtual+0x38 with flag 0.
The current table resolves to `0x1407cff40`, which calls `0x1407e5f90` at
`0x1407cff62`. It destroys the eight strings in reverse order, frees valid heap
storage when capacity exceeds 15, and restores empty string metadata. It does
not restore scalar/boolean values or cursor state. Flag 0 preserves caller
placement allocation. Corrupt large-allocation metadata reaches an invalid-
parameter/INT3 path; cleanup is not guaranteed for that state. Exceptions,
unwinding and eventual successful-object disposal remain unproved.

## Scope and checks — J223-4

The receipt binds static source checks, targeted counter-review and required
workspace validation. Pure models and repository tests supply offline evidence;
they do not establish current-client acceptance. Separate +0x3e0 nested schema,
full request body implementation, discriminator/framing, authoritative field
meanings, #212 construction gates and Milestone 1 remain open.
