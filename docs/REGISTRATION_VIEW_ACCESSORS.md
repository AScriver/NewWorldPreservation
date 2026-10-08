# Registration copied-view pointer/count mapping

Actionables269 under164/178/267 closes the two native accessor results used by
the owned client's incoming registration parser. [Original source receipt](../research/evidence/current-registration-view-accessors.json)
records K381 at clean8c89ee8. This is static source evidence, not a game session
or replacement-server receive test. The [invoker checkpoint](REGISTRATION_RECEIVE_INVOKER.md)
retains the separate upstream transport and runtime limits.

The directly evidenced call targets now have bounded native observations:

- 140879580 returns qword(view+8) minus qword(view+0) in64-bit RAX.
- 1402f2d90 returns qword(view+0) in RAX.

For the same locally copied view, caller146b6ba90 saves the first result and
passes it in R8, passes the second in RDX, and passes existing child+f0 in RCX
to146af20c0. The exact local mapping is raw pointer=field0 and raw count=
(field8-field0) modulo2^64. These sequences add no offset or scaling and contain
no underflow guard. They do not establish a valid, nonnegative allocated span.

Two64-byte executable windows were read from exact relative CALL targets;
only the8-byte and4-byte linear sequences through RET are claimed. Both lack
evidenced PDATA ownership. The direct instruction observations preserve that
earlier helper refusal without guessing unwind/function boundaries. Exact
image/map/caller/window/listing hashes and critical review support this mapping.

The24-byte helper copies three view fields sequentially; the third field's
meaning remains unknown. Pair movement before copying and unknown aliasing
prevent a blanket guarantee of unchanged caller fields or payload. Buffer
validity, lifetime, intended units beyond raw subtraction, checks elsewhere,
actual secondary+20 caller/view producer, Carrier placement, runtime active
identity, authentication and native acceptance remain unproved.

Original codecs/adapter/candidates/trial are unchanged. Relevant validation
and exact full-suite reuse are recorded in ROADMAP. No runtime resources were
acquired. Component completion does not complete267/268 or Milestone1.
