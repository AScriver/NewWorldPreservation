# Registration receive callback checkpoint

Actionables #267 under164/178 resolves callback storage and downstream argument
flow in the selected owned-image transport. [Original source receipt](../research/evidence/current-registration-receive-callback.json)
records K377/K378, clean3259724, four bounded query roots/3202 bytes and one
192-byte table. One setter span repeats earlier sealed source; the helper,
constructor bodies and table add the new evidence. No client or runtime ran.

## Stored callback

Existing connection-result code146b713e0 tests the primary+8 return in AL. On
the selected nonzero path it builds closure148591708/captured child and invokes
primary+48. The selected primary table14858c358 maps that slot to146b28f70.
This setter passes destination=this+278 to14056cee0, whose active-pointer slot
is destination+38=this+2b0. Its normal branches call opaque virtual copy/move/
cleanup methods and replace that slot. Helper returns the destination address,
not a success result. The setter writes byte+130=1 without checking the active
pointer, then conditionally cleans/clears the incoming callable. The flag
therefore does not prove a callable is available. Allocation, exceptions,
virtual-method semantics and runtime installation remain qualified.

No direct byte-span operation is visible in this setter. It does not identify
the later invocation that supplies the received stream.

## Distinct arguments

Callback146b714d0 receives its capture in RCX, a stream/view argument in RDX
and a separate opaque two-qword pair in R8. It moves/zeros the pair, passes the
original RDX through140870bc0 and calls146b6ba90 with RCX=&capture.child,
RDX=helper result and R8=the moved local pair. The callee dereferences that child
slot and addresses parser member child+f0; the shown code does not construct it.

It calls140879580 and1402f2d90 on the copied/adapted view, then passes the latter
result in RDX and the former in R8 to146af20c0→146af1d90. Existing source then
reaches the compact-length record reader. These are exact caller argument edges.
The copy/accessor internals and earlier byte producer remain unjoined. Neither
the pair's shape nor the downstream reader proves network-to-view transparency,
descriptor/header removal, full Carrier framing or actual response acceptance.

## Separate lower driver

The queried146b36920 construction branch guards owner+48==0 and dword+7c==1.
It stores the constructed145dbdd30 driver at owner+50; the guard is not a proved
driver+50-null check. A later factory result is stored at+48. Constructor installs
the separate148480a20 table, whose+48 (decimal72) points to unqueried140f684a0;
+28 (decimal40) points to145dcd610. No receive role or callback edge is established
for either target. A same-numbered slot on different tables is not an object join.

Primary raw-instruction/table/hash seal and critical review retain these limits
and correct the preliminary slot/semantic wording. The best next source edge
is a caller that reads the selected primary active slot+2b0 and supplies RDX/R8
to the stored callback. It must be joined to the same primary object; an offset
match in another object's layout is insufficient.

Original codecs and the current adapter are unchanged. Relevant validation,
current-input reconciliation and process cleanup are recorded in ROADMAP.
Authentication, current runtime binding, complete transport byte provenance,
native acceptance and M1 remain unproved. This partial checkpoint authorizes
neither a reply-format change nor another native trial.
