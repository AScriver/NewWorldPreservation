# Receive address-associated object lookup

Actionables #280 under work item164/parent277 resolves the fallback interface's
virtual+a0 factory. The [source receipt](../research/evidence/current-registration-address-factory.json)
pins the owned image and exact current source. This component passes static
source review; native server acceptance remains untested.

One exact8-byte table entry at148480928 selects145dc9600, a124-byte function.
It builds a local record with vptr148480720, a zero qword, the interface pointer,
a zero dword and16 copied input bytes. Input WORD0x17 admits12 additional bytes.
Other tail bytes and padding are not initialized here. It passes interface+30,
a result slot and this local record to the380-byte145db6bd0 helper.

That helper uses WORD at local+0x20 and selected copied fields as a bucket key.
Selector2 hashes DWORD+0x24 XOR WORD+0x22; selector0x17 uses QWORD+0x28 XOR
that WORD; other selectors hashzero. Matching checks the selector WORD and
selected fields, not every copied byte. A saved bucket count bounds
the linked search; physical list validity and capacity remain unknown.

A match returns a node with result bytezero. Other paths invoke145de1a30,
then return a node with result byteone. That byte denotes the branch taken,
not validated allocation or durable insertion. Empty and exhausted buckets
pass different third arguments and obtain their nodes differently. Both pass
the local factory record inR9. The constructor and later rehash remain opaque.

The outer factory stores node+0x10 in the output holder and increments its DWORD
at+0x18 when the adjusted pointer is nonzero. The guard follows ADD; it is not
a raw-node null check. It returns the holder address. Types, physical extents,
ownership beyond these explicit operations and alias effects remain limits.

The [279 source chain](REGISTRATION_INCOMING_READER.md) conditionally supplies
the input from the receive backend's address-output area. This supports an
address-area association. It does not establish actual written bytes or a
runtime peer identity. Later caller object+8 is distinct from interface+38;
construction, state assignment and intervening callback/filter effects are
still unjoined. The selected functions do not directly parse packet bytes.

Two new PDATA roots504B and the8B entry were sealed. Initialized imports
75697152B and BSS11118896B are separate. Nine known full identity passes include
the shared primary baseline once; native disassembly remained504B. No failed
query, game/native execution, endpoint or runtime resources. Relevant36/PF/
binding checks and exact1960-case input reuse are recorded in ROADMAP.

Next concrete source target is145de1a30 and its use of the passed factory
record. Parent277's queued payload/reassembly/compact/type/reply/authentication/
world join and Milestone1 remain Partial. No codec mismatch or server change
follows from these container mechanics.
