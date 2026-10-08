# Receiver factory and view candidate — #270, partial

[Original source receipt](../research/evidence/current-registration-receive-producer.json)
pins clean1b3fd5c, exact owned image/map, current267/268/269 bindings and private
native/query/review artifacts. These are owned-client static observations for
server work; the upstream incoming byte path remains unjoined.

- K382: factory146b393d0 constructs primary at wrapper+0x10 only after a
  nonzero allocation, passing saved originalRCX as constructorRDX. Existing
  constructor installs secondary at primary+8, hence wrapper+0x18 on this path.
  When control reaches output stores, it writes{wrapper+0x10,wrapper} and returns
  the output address. A zero allocator return skips construction and mechanically
  writes{0x10,0}; allocator failure/throw policy and lifetime are unproved.
- K383:45 of47 raw+20 hints align within25 complete PDATA bodies/12273 reused
  code bytes from the old128KiB interval. Eight predecessors/one successor per
  context do not establish receiver/table/signature, arity, producer or absence.
  Two hints without PDATA remain unselected. Counterexample liveR8 prompted a
  full-body query; initial signature/exclusion wording is retained historically.
- K384: cached146b3c250 supports queued-send and shared-holder/lifetime effects.
  Coincident+2b0 is not object identity; whole-function incoming behavior is not
  excluded. Factory and dispatcher133B/5210B native spans are exactly sealed.
- K385: full301B/83 instructions of146b2ba60 preserve entryR8 as an output
  destination. A nested owner+90 virtual+20 return contributes to the unsigned64
  capacity-shaped guard; helper31bd0 may replace owner+90/+98 and release pairs.
  A separate second return forms(RBX+0x39+RAX) modulo2^64 at output+8. Owner+90
  reload precedes a third return, whose EAX gives(0x10000-EAX) modulo2^32 at
  output+0. Direct stores omit padding+4 and field+16. Distinct returns/objects,
  aliasing and unknown callees prevent coherent valid-buffer guarantees.

EntryRDX may reach the initial opaque callee, then is locally overwritten for
the pool helper/pair values. Nested table/targets/signatures, actual callers,
factory-to-invocation and incoming view/pair provenance remain unknown. No
Carrier/header/network interpretation or codec change follows from this query.

Native consistency and critical reviews survive with these limits. Resource
acceptance failed: alignment read4096B PE metadata outside its clarified range;
the selected helper query imported37,848,576B static data plus301B code versus
the524288B file-backed cap, and read179,204,176B for image identity. Both deviations
remain recorded; further queries stopped. Failed agent native decoding lacked
Capstone; primary repaired the full listing with its existing private package.
Future budgets must guard code/tables, static imports and identity memory separately.

Affected36 catalog/runner checks, actual preflight and eight public/35 private
bindings pass. Exact selected input-set reconciliation reuses1890 Python cases/
50 modules/fivePS suites/closed loopback; four source receipts and three metadata
files differ since that full run. Closure remains under
.scratch/registration270-primary-20261008T0440Z/closure.json. Static query and
validation children exited0; no game/runtime resources were acquired. Goal and
resource acceptance remain Partial; authentication/native acceptance/M1 unproved.
