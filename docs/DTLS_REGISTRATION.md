# Current REP DTLS trust and Carrier/V3 registration

## Scope and current evidence boundary

Continuation of [private queue handoff](PRIVATE_GAME_HANDOFF.md), clean parent HEAD `4bf6511468fa66d3935fca5859b2657c3ca3183b`. Target unchanged stock Steam22469132 / version1.400.6031.6004151 / installed SHA256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`. Prior own client reached selected127.0.0.1:64003 and sent ClientHello-header observations; prior observer sent no replies. This alone did not test certificate trust.

Work in this slice: verified local DTLS peers, owned current-client handshake/trust, then current Carrier/V3 **only if transport succeeds**. No actor/gameplay implementation, memory writes, executable/EAC change, other-user traffic, official-system authentication bypass, remote publication or mouse/keyboard control.

## Evidence ledger for this slice

| ID | Claim | Classification / limit | Evidence |
|---|---|---|---|
| D36 | Two isolated local DTLS clients verify the retained CA and exchange distinct payloads | Executed with normal and reversed completion order; presented-leaf-as-anchor control raises certificate verify failed and sends no application data. Not New World trust or hostname verification | Ignored `.scratch/dtls-local-exchange/probe.py`, results.json, experiment-report.md and validated run.ps1; fresh ephemeral127.0.0.1 sockets all closed |
| D37 | Existing Python DTLS BIO setup is a reusable integration boundary | Source-supported, clean First Light63756a3: per-source-tuple SSL.Connection/accept/feed/handshake/drain; server VERIFY_NONE means no client-certificate authentication, **not** a client trust bypass | `server/rep_responder.py:167–177,275–283,316–364,1308–1334`; no source vendored |
| D38 | Historical responder does not explicitly drive DTLS timers and emits unsafe raw logs for this task | Source-supported: no DTLSv1_handle_timeout call; record/parse-error/V3 payload dumps and identity/token logging. Do not run this responder unchanged | `rep_responder.py:433,451,601–613,631,673,768,771,1138`; old dtls_bridge one-client/WIP |
| D39 | Current-client private DTLS trust remains separate from HTTPS | Unknown until owned responder sends certificate and current client outcome observed; old Frida patch reports are not evidence for this build | Prior handoff receipt; retained CA untouched, no historical addresses/patches transferred |
| D40 | Original responder and portable controls preserve workspace regression | Executed268 pass/no failures/errors/skips;7 new actual-local/mock-error tests. Independent retained-CA experiment remains separate; no game acceptance | [Validation receipt](../research/evidence/dtls-local-validation.json),23explicit modules/36source hashes |

The original local experiment uses Python3.11.9 / pyOpenSSL26.4.0 / cryptography50.0.2, the same installed dependency lock as the workspace. Both clients negotiated First Light's `ECDHE-RSA-AES256-GCM-SHA384` with separate server states. Test CA/leaf PEM-file hashes differ from DER fingerprints; compare like formats. No certificate/private key was copied into the test scratch folder. Its negative trust source was the presented leaf itself, not an unrelated CA; failure is scoped to those verification flags. The separate portable responder tests use temporary certificates, not game sessions or installed trust.

## Owned responder design and observability

Use existing pyOpenSSL memory-BIO boundaries in an original loopback-only diagnostic, not First Light's raw-logging responder or an OpenSSL subprocess bridge. Each source tuple owns an independent connection/state and outbound encrypted BIO route. OpenSSL, not a speculative New World codec, implements the handshake and encryption. Explicit public timeout handling covers timer-driven handshake retransmission; actual loss behavior must be tested separately.

Reuse `private/connectivity/retained-test-ca.json` certificate_directory, `server.pem`, `server.key`, `ca.pem`; never print key/PEM bytes. Startup leaf/root DER fingerprints describe **configured** material, not a wire capture or proof of certificate transmission. Record whether the root chain is supplied separately from actual output/peer evidence. Same CurrentUserRoot thumbprint `1AEE2B69AD82A5C6F2CF52A80127D22A4487CECA`, expiry2026-10-09T18:58:22Z; no import/removal/new approval. Configurations differ only where explicitly documented.

Required timestamped evidence: fresh Steam/PID/start identity; queue HTTP200/hash; received UDP bind-owner readback (not exact flow); handshake state changes; outgoing encrypted byte counts; optional SNI presence/class with unknown values discarded; SSL alert direction/level/description; negotiated version/cipher on server completion; decrypted application **length only**; timeout/close and client-first cleanup. Server completion alone must not be promoted to gameplay/authentication or a final client trust decision. A no-response timeout is not pinning proof.

Protocol/library references: [RFC6347](https://www.rfc-editor.org/rfc/rfc6347.html) for DTLS framing/handshake flights, and [pyOpenSSL SSL API](https://www.pyopenssl.org/en/stable/api/ssl.html) for BIO, info callbacks and DTLS timeout methods. These describe standard DTLS/library behavior, not New World packet schemas.

## Historical Carrier/V3 map — not yet current-client proof

| Boundary | Existing reference implementation | Current limitation |
|---|---|---|
| DTLS → Carrier | `parse_envelope` then `parse_datagram`; envelope plaintext0x80/proto0x01/BE16sequence | Only apply to actual decrypted current data; lengths/flags may differ |
| Connect request | Channel3, system-msg trailing ID1 | Current request not yet observed |
| Connect ACK | Historical default reliable ch3 flag0x21, body00 00 00 05 02 plus inline ACK | Envelope-sequence echo is a historical hypothesis; ack-variant CLI is ignored by sender |
| V3 request | Historical flags0xe0/0xf0 and no-length framing; strict old832bytes plus lenient identity extraction | Responder's generic flags&0x40 heuristic is too broad for a current semantic claim; real auth blob/identities must not be logged |
| V3 response | Existing 88byte codec, VLQ-length framing, default reliable ch0, optional piggyback ACK | Help says mirror request but implementation defaults ch0; success/current dependencies untested |

Sources: clean ignored First Light `server/javelin/frame.py:40–94,142–225`, `v3_request.py:111–169,295–347`, `v3_response.py:149–175`, `rep_responder.py:425–480,639–765,1069–1140`. No payloads, proprietary client code or upstream source are copied here. Parser round-trips and field names do not prove registration acceptance.

## Reproduction and gates

Offline responder checks completed:7 focused tests and full268-test regression, with temporary unrelated-CA rejection/read-fatal-unknown_ca, separate local peers, timer retransmission and socket-error controls. Corrected startup fingerprint labels and historical negative-anchor identity after targeted review. Live outcomes will be recorded separately with exact exercised source hashes. Live routing uses the prior TokenServices profile, owned HTTPS443 and selected UDP64003; only our game executable is blocked from nonloopback destinations. ActiveStore readback is configuration evidence, not whole-machine/helper packet enforcement proof.

Responder CLI: `.venv\Scripts\python.exe scripts/dtls_transport_probe.py --certificates <same-retained-directory> --log <fresh-private-jsonl> --port 64003 --duration 600 --chain full`. Bind is fixed127.0.0.1. `--chain leaf` changes the presented chain only; it does not regenerate certificates or alter trust. Default decrypted application handling records length then discards bytes, with no Carrier response. The optional callback is for later evidence-constrained integration, not enabled by this CLI.

No already-running client/listener is replaced. All helper scripts require full PowerShell validation, fresh ignored run journals and explicit process/start/parent/script ownership. Normal Steam launch; user advances Continue/Preservation/Play manually. Stop owned game before restoring hosts/firewall; stop owned responder/listeners and verify original hosts bytes/hash, rule absence and same retained CA.

Next decisions must follow evidence: local configuration/root/chain behavior first; if current private trust rejects, preserve the exact error and narrowly inspect the **current** transport trust path. Never apply an old memory hook, manufacture a certificate/signature, modify the running game's memory, or mislabel a generic popup as pinning. Actor work waits for transport/registration/private identity and current spawn evidence. Milestone1 remains unachieved.
