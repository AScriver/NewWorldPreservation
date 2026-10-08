# Driver buffer and forwarding paths

Actionables272, child267/root164/178, preserves source effects needed to connect
the current registration codecs to the client's transport. The [original receipt](../research/evidence/current-registration-driver-buffer-edges.json)
pins cleanmain6a0b6c0, image/map, native/query/cache/private review hashes.
The local component closes; aggregate socket/receive/Carrier acceptance stays partial.

Existing constructor145dbdd30 installs separate driver table148480a20. Its+0x10
and+0x18 targets lack PDATA owners. Exact64B windows show only5B JMPs to
145dcb690 and145dcb480;118 remaining bytes are not decoded. Those direct targets
have declared boundaries. No entry-function extent is guessed.

| Claim | Positive source effect | Limits |
|---|---|---|
| K388 | Table+10/+18→two direct JMP targets | Conditional driver identity, separate from primary14858c358; no runtime invocation |
| K389 | Cached3389B input-buffer routine passes qword[driver+e0] and DWORD[driver+118] to backend virtual+20; forwards holder/length through145db4ef0 | EAX gate is nonzero, not positive/valid-length proof. Backend, output holder, aliases and raw bytes' socket/Carrier identity unknown |
| K390 |522B queue routine checks64-bit extent, calls copy-shaped helper, advances queue, and conditionally calls backend virtual+18 | Loaded buffer qword[driver+d8]; state-relative fields, separate low32 signed length; oversize also consumes cursor/count. No delivery/success meaning |
| K391 |584B shared helper invokes caller-supplied code during guarded list/hash traversal | Loaded receiver fields and reloadedDWORD each invocation; second context call conditional. Handler bodies/registration/primarycallback/retention unknown |

In K390, listnode+0x50 contains a pointer to queue/state. Ring fields+0x50/+0x58/
+0x60/+0x68 and counter+0x20dc belong to that state, not the list node. Queue slots
have stride0x520. Extent is(qword[slot+0x518]-slot) modulo2^64; an unsigned check
compares it with zeroextendedDWORD[driver+0x118]. Fitting entries pass destination
qword[driver+0xd8], source slot and extent to147aad05b. Reused265 pinned-image
static import metadata names`memcpy`; this does not establish a loadedDLL/copy
outcome or freshness of265's old probe binding after266.

After that call, low32 length is recomputed. Cursor/count advance on fit and
oversize paths before the signedEBP<=0 exit. Positive length initializes a local
holder as node+0x10; it is not the provider return from holder virtual+0x30.
The backend receives providerreturn, localproviderDWORD, a previously loaded
buffer pointer and itemlength. EAXzero gates forwarding; it is not proof of full
delivery. Conditional holder release and state counter/predicate follow.

K391 passes qword[entry+0x28] orqword[entry+0x10] as handlerRCX, not the address
of those fields. The DWORD source is reloaded for each invocation; callbacks may
observe different values. The opaque context supplier is called again only on
the first traversal branch and need not return the same context. Caller-supplied
code14057143c/444 is not joined to primary callback146b714d0. Original agent
shorthand and failed guard attempts remain preserved with primary qualifications.

Two helper batches selected1106Bcode; cached3389B was rechecked without another
query. Two metadata refusals,128B entry windows/10B branch evidence, zero newdata
windows,75697152B initializedstatic imports and11118896B BSS extension are
separately counted. Agent eleven fullimage reads total1971245936B repeated access;
one failed near-full hash attempt has no exact byte count. Primarybaseline/seal
each read the179204176B image once. Owned static children exited.

Native/hash/critical review passes for these precise effects. Affected36 checks,
actual preflight/binding checks and exact1890/50/fivePowerShell/closed-loopback
input reconciliation are retained before commit under
`.scratch/registration272-primary-20261008T0540Z/closure.json`.
Next is the driver initialization/backend field+0x20 and concrete virtual+0x18/
+0x20 destinations. Current selectors, valid response values, authentication,
native acceptance and Milestone1 remain unproved. Codecs/adapter/trial unchanged.
