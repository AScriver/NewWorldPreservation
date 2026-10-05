"""Bounded private Carrier connect and V3 registration adapter.

Only loopback DTLS, a pinned clean First Light checkout, and local fresh
session tokens are supported. Logs contain framing metadata, never bodies,
identity fields, token bytes, exception text, or raw datagrams.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
from importlib import metadata as package_metadata
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

import current_self_ident_default
import current_spawn_point
import current_world_activation

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "research" / "upstream" / "first-light"
AETERNUM = ROOT / "research" / "upstream" / "aeternum-world"
COMMIT = "63756a3f7ff0ae41752dcc7c80267802c3fa7548"
AETERNUM_COMMIT = "820156dbc44c86c9436af81aa0dba72e94cb636b"
AETERNUM_DECODER = "Tools/nw_capture/decode_dtls_ledger.py"
AETERNUM_DECODER_SHA256 = "d5563a4ea694d45a81ab4db0d74ff86c940db95794a872a9393b2761efc9e15b"
LZ4_HINTS = (256, 1024, 4096, 16384, 65536, 262144)
MAX_PLAINTEXT_BYTES = 4096
MAX_EXPANDED_BYTES = 262144
SOURCE_HASHES = {
    "server/javelin/frame.py": "798f6419114eacac5c5bfb1fd4822929239cd82fb66835e15242dd78a066b33a",
    "server/rep_responder.py": "d1e3a47de31258ba8442f4b8988060ac7cbe16983705591d7173c7617a785d73",
    "server/javelin/v3_request.py": "3e5d144de49dd83dedc696ca9ef31b5450d994833ecbf01803f4dc5aee84c9eb",
    "server/javelin/v3_response.py": "cff82bfb02e07270ee221134f2dee7b043dc9e8a17f83c7af7f0796d7d3c86ba",
    "server/javelin/wire.py": "bcb82f500455f9aa57312a596554954c04a462a1acc2cb23ae4a74ccd65d3a62",
    "server/javelin/dispatch.py": "a2b852bae63ec663504cdb518c0031c9f5e4f3768ec0070dfb43dcc417da3ae7",
    "server/javelin/heartbeat_15d.py": "c55863f379012f97186f33e806f336b59f957d0d162ff3279690474a91d32a43",
}
MAX_PEERS = 8
MAX_SEQUENCES_PER_PEER = 2048
MAX_HEARTBEATS_PER_PEER = 1200
OWNED_SERVER_VERSION = "[RETAIL].Javelin.1.400.6031.6004151"


def _git(reference: Path, *arguments: str) -> str:
    result = subprocess.run(["git", "-C", str(reference), *arguments], capture_output=True,
                            text=True, check=True, timeout=15)
    return result.stdout.strip()


def verify_reference(reference: Path = REFERENCE) -> Path:
    expected = REFERENCE.absolute()
    if (os.path.normcase(str(reference.absolute())) != os.path.normcase(str(expected)) or
            expected.resolve(strict=True) != expected):
        raise ValueError("First Light reference must be the exact local checkout")
    if (Path(_git(expected, "rev-parse", "--show-toplevel")).resolve() != expected or
            _git(expected, "rev-parse", "HEAD") != COMMIT or
            _git(expected, "status", "--porcelain")):
        raise ValueError("First Light checkout identity is not clean and pinned")
    for relative, digest in SOURCE_HASHES.items():
        path = expected / relative
        with path.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != digest:
                raise ValueError("First Light selected source hash mismatch")
    return expected


def load_codecs(reference: Path):
    reference = verify_reference(reference)
    sys.path.insert(0, str(reference))
    modules = tuple(importlib.import_module(name) for name in (
        "server.javelin.frame", "server.javelin.v3_request", "server.javelin.v3_response",
        "server.javelin.wire", "server.rep_responder", "server.javelin.dispatch"))
    for module in modules:
        if not Path(module.__file__).resolve().is_relative_to(reference):
            raise ValueError("First Light import origin mismatch")
    if (Path(modules[-1].heartbeat_15d.__file__).resolve() !=
            reference / "server" / "javelin" / "heartbeat_15d.py"):
        raise ValueError("First Light heartbeat import origin mismatch")
    return modules


def verify_aeternum_decoder(reference: Path = AETERNUM) -> None:
    expected = AETERNUM.absolute()
    if (os.path.normcase(str(reference.absolute())) != os.path.normcase(str(expected)) or
            expected.resolve(strict=True) != expected):
        raise ValueError("Aeternum reference must be the exact local checkout")
    if (Path(_git(expected, "rev-parse", "--show-toplevel")).resolve() != expected or
            _git(expected, "rev-parse", "HEAD") != AETERNUM_COMMIT or
            _git(expected, "status", "--porcelain")):
        raise ValueError("Aeternum checkout identity is not clean and pinned")
    with (expected / AETERNUM_DECODER).open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != AETERNUM_DECODER_SHA256:
            raise ValueError("Aeternum decoder hash mismatch")


class _SilentLog:
    def info(self, _message):
        pass


class _ConnectAckFacade:
    """Only the state and callbacks consumed by pinned send_connect_ack."""

    ack_form = "mn"
    log = _SilentLog()

    def __init__(self, peer, envelope_seq, outgoing_envelope_seq=None):
        self.peer = peer
        self.last_inbound_env_seq = envelope_seq
        self._inbound_env_first = envelope_seq
        self._inbound_env_last = envelope_seq
        self.out_msg_seq = [0, 0, 0, 0]
        self.connect_ack_count = 0
        self.sent_ok = False
        self.last_datagram = None
        self.outgoing_envelope_seq = outgoing_envelope_seq

    def wrap_envelope_echo(self, body, echo_seq):
        selected = echo_seq if self.outgoing_envelope_seq is None else self.outgoing_envelope_seq
        return b"\x80\x01" + (selected & 0xFFFF).to_bytes(2, "big") + body

    def send_app(self, datagram):
        sent = self.peer.send_app(datagram)
        self.sent_ok = sent == len(datagram)
        if self.sent_ok:
            self.last_datagram = datagram
        return sent

    def drain_outbound(self):
        pass


class _PeerState:
    def __init__(self):
        self.seen = set()
        self.connect_ack_sent = False
        self.v3_sent = False
        self.after_ack_seen = False
        self.after_v3_seen = False
        self.acked_through = None
        self.ack_sequence = 0
        self.replies = {}
        self.v3_response_record = None
        self.next_out_envelope_seq = None
        self.autonomous_started = False
        self.last_inbound_nonack = None
        self.next_ch0_seq = 1
        self.next_ch0_rel = 1
        self.next_heartbeat_at = None
        self.heartbeat_counter = None
        self.heartbeat_sent = 0
        self.pending_pings = []
        self.heartbeat_disabled = False
        self.next_self_ident_at = None
        self.self_ident_sent = False
        self.self_ident_disabled = False
        self.next_spawn_point_at = None
        self.spawn_point_sent = False
        self.spawn_point_disabled = False
        self.next_level_info_at = None
        self.level_info_sent = False
        self.level_info_disabled = False
        self.next_bundle_at = None
        self.bundle_sent = False
        self.bundle_disabled = False


class RegistrationAdapter:
    def __init__(self, events, codecs, *, decompressor=None, compression_guard=None,
                 server_version=None, heartbeat_15d=False, self_ident_default=False,
                 spawn_point_notification=False, world_activation=False, clock=None):
        if server_version is not None and server_version != OWNED_SERVER_VERSION:
            raise ValueError("unsupported server version selection")
        if self_ident_default and (not heartbeat_15d or server_version != OWNED_SERVER_VERSION):
            raise ValueError("current default actor candidate requires owned version and heartbeat")
        if spawn_point_notification and not self_ident_default:
            raise ValueError("spawn notification requires the current default actor candidate")
        if world_activation and not spawn_point_notification:
            raise ValueError("world activation requires the current spawn notification")
        self.events = events
        self.frame, self.v3_request, self.v3_response, self.wire, self.rep, self.dispatch = codecs
        self._server_version = server_version
        self._version_choice = "owned_image" if server_version is not None else "historical"
        self._heartbeat_enabled = heartbeat_15d
        self._self_ident_enabled = self_ident_default
        self._spawn_point_enabled = spawn_point_notification
        self._world_activation_enabled = world_activation
        self._clock = clock or time.monotonic
        self._heartbeat = getattr(self.dispatch, "heartbeat_15d", None)
        if heartbeat_15d and self._heartbeat is None:
            raise ValueError("pinned heartbeat codec required")
        self.peers = {}
        if (decompressor is None) != (compression_guard is None):
            raise ValueError("decompressor and compression guard must be provided together")
        self._decompressor = decompressor
        self._compression_guard = compression_guard
        self._compression_state = None
        self._compression_failure = None

    def _compression_ready(self):
        if self._compression_state is not None:
            return self._compression_state
        try:
            if self._compression_guard is not None:
                self._compression_guard()
            else:
                verify_aeternum_decoder()
        except Exception:
            self._compression_failure = "compression_source_unverified"
            self._compression_state = False
            return False
        try:
            if self._decompressor is None:
                if package_metadata.version("lz4") != "4.4.5":
                    raise ValueError("lz4 version mismatch")
                self._decompressor = importlib.import_module("lz4.block")
        except Exception:
            self._compression_failure = "compression_dependency_unavailable"
            self._compression_state = False
            return False
        self._compression_state = True
        return True

    def _emit(self, event, peer, **metadata):
        self.events.emit(event, connection_id=peer.id, **metadata)

    @staticmethod
    def _out_envelope(state, inbound_sequence):
        return (state.next_out_envelope_seq if state.autonomous_started
                else inbound_sequence)

    @staticmethod
    def _note_out_envelope(state, sequence):
        state.next_out_envelope_seq = (sequence + 1) & 0xFFFF

    def on_app(self, peer, plaintext):
        if peer.id not in self.peers:
            if len(self.peers) >= MAX_PEERS:
                self._emit("CARRIER_REJECTED", peer, reason="peer_limit")
                return
            self.peers[peer.id] = _PeerState()
        state = self.peers[peer.id]
        try:
            self._handle(peer, state, plaintext)
        except (ValueError, TypeError, IndexError):
            self._emit("CARRIER_REJECTED", peer, reason="invalid_frame_or_response")
        except Exception:
            self._emit("CARRIER_REJECTED", peer, reason="adapter_failure")

    def _ack(self, peer, state, sequence):
        ack = self.rep.build_sm_ct_acks_record(state.ack_sequence, sequence,
                                                state.acked_through)
        outbound_sequence = self._out_envelope(state, sequence)
        datagram = (b"\x80\x01" + outbound_sequence.to_bytes(2, "big") + ack
                    if ack is not None else None)
        if datagram is not None and peer.send_app(datagram) == len(datagram):
            state.ack_sequence = (state.ack_sequence + 1) & 0xFFFF
            state.acked_through = sequence
            self._note_out_envelope(state, outbound_sequence)
            state.replies.setdefault(sequence, []).append(datagram)
            self._emit("CARRIER_ACK_SENT", peer, envelope_sequence=outbound_sequence,
                       inbound_envelope_sequence=sequence)

    def _heartbeat_ack(self, payload):
        if not self._heartbeat_enabled:
            return None
        variants = [("raw", payload)]
        for prefix_length in range(1, 6):
            remaining = len(payload) - prefix_length
            if remaining == 36 and payload[:prefix_length] == self.wire.encode_vlq32(remaining):
                variants.append(("canonical_length_prefix", payload[prefix_length:]))
                break
        try:
            _, declared_size, _, inner = self.wire.parse_cs_envelope(payload)
            if declared_size == len(payload) - 8 and self.wire.verify_cs_crc32(payload):
                variants.append(("verified_cs_wrapper", inner))
        except ValueError:
            pass
        for normalization, body in variants:
            if len(body) != 36:
                continue
            try:
                decoded = self._heartbeat.decode_ack(body)
                echoed = (decoded.echoed_ping.counter, decoded.echoed_ping.nonce)
                del decoded
                return normalization, echoed
            except ValueError:
                continue
        return None

    def on_tick(self, peer, now):
        if not self._heartbeat_enabled:
            return
        state = self.peers.get(peer.id)
        if (self._self_ident_enabled and state is not None and state.v3_sent and
                not state.self_ident_sent and not state.self_ident_disabled and
                state.next_self_ident_at is not None and now >= state.next_self_ident_at):
            state.self_ident_sent = self._send_fixed_actor_message(
                peer, state, current_self_ident_default.encode_default(),
                current_self_ident_default.TYPE_ID, "SELF_IDENT_DEFAULT")
            state.self_ident_disabled = not state.self_ident_sent
            if state.self_ident_sent and self._spawn_point_enabled:
                state.next_spawn_point_at = now + 1.0
        if (self._spawn_point_enabled and state is not None and state.self_ident_sent and
                not state.spawn_point_sent and not state.spawn_point_disabled and
                state.next_spawn_point_at is not None and now >= state.next_spawn_point_at):
            state.spawn_point_sent = self._send_fixed_actor_message(
                peer, state, current_spawn_point.encode_notification(),
                current_spawn_point.TYPE_ID, "SPAWN_POINT_NOTIFICATION")
            state.spawn_point_disabled = not state.spawn_point_sent
            if state.spawn_point_sent and self._world_activation_enabled:
                state.next_level_info_at = now + 1.0
        if (self._world_activation_enabled and state is not None and state.spawn_point_sent and
                not state.level_info_sent and not state.level_info_disabled and
                state.next_level_info_at is not None and now >= state.next_level_info_at):
            state.level_info_sent = self._send_fixed_actor_message(
                peer, state, current_world_activation.encode_level_info_candidate(),
                current_world_activation.LEVEL_INFO_TYPE_ID, "LEVEL_INFO_CANDIDATE",
                header_bytes=len(current_world_activation.LEVEL_INFO_HEADER), body_kind="candidate")
            state.level_info_disabled = not state.level_info_sent
            if state.level_info_sent:
                state.next_bundle_at = now + 1.0
        if (self._world_activation_enabled and state is not None and state.level_info_sent and
                not state.bundle_sent and not state.bundle_disabled and
                state.next_bundle_at is not None and now >= state.next_bundle_at):
            state.bundle_sent = self._send_fixed_actor_message(
                peer, state, current_world_activation.encode_empty_bundle(),
                current_world_activation.BUNDLE_TYPE_ID, "EMPTY_STATE_BUNDLE",
                header_bytes=len(current_world_activation.BUNDLE_HEADER))
            state.bundle_disabled = not state.bundle_sent
        if (state is None or not state.v3_sent or state.heartbeat_disabled or
                state.next_heartbeat_at is None or now < state.next_heartbeat_at or
                state.heartbeat_sent >= MAX_HEARTBEATS_PER_PEER):
            return
        if state.heartbeat_counter is None:
            state.heartbeat_counter = secrets.randbits(32)
        counter = state.heartbeat_counter
        nonce = secrets.randbits(32)
        ping = self._heartbeat.HeartbeatPing15D(counter=counter, nonce=nonce)
        body = self._heartbeat.encode_ping(ping)
        if len(body) != 12 or state.next_out_envelope_seq is None:
            state.heartbeat_disabled = True
            self._emit("HEARTBEAT_15D_REJECTED", peer, reason="codec_or_cursor")
            return
        record = self.frame.MessageRecord(
            channel=0, payload=self.wire.encode_vlq32(len(body)) + body,
            sequence=state.next_ch0_seq, reliable_sequence=state.next_ch0_rel,
            reliable=True, flags_override=0x21)
        record_bytes = self.frame.marshal_datagram([record])
        ack = self.rep.build_sm_ct_acks_record(state.ack_sequence,
                                                state.last_inbound_nonack,
                                                state.acked_through)
        envelope_sequence = state.next_out_envelope_seq
        datagram = (b"\x80\x01" + envelope_sequence.to_bytes(2, "big") +
                    record_bytes + (ack or b""))
        if peer.send_app(datagram) != len(datagram):
            state.heartbeat_disabled = True
            self._emit("HEARTBEAT_15D_REJECTED", peer, reason="send_failed")
            return
        state.autonomous_started = True
        self._note_out_envelope(state, envelope_sequence)
        state.next_ch0_seq = (state.next_ch0_seq + 1) & 0xFFFF
        state.next_ch0_rel = (state.next_ch0_rel + 1) & 0xFFFF
        if ack is not None:
            state.ack_sequence = (state.ack_sequence + 1) & 0xFFFF
            state.acked_through = state.last_inbound_nonack
        state.heartbeat_counter = (counter + 1) & 0xFFFFFFFF
        state.heartbeat_sent += 1
        state.next_heartbeat_at = now + 0.5
        state.pending_pings.append((counter, nonce))
        if len(state.pending_pings) > 8:
            state.pending_pings.pop(0)
        self._emit("HEARTBEAT_15D_SENT", peer, envelope_sequence=envelope_sequence,
                   record_sequence=record.sequence, reliable_sequence=record.reliable_sequence,
                   body_bytes=len(body), count=state.heartbeat_sent,
                   client_acceptance_proven=False)

    def _send_fixed_actor_message(self, peer, state, body, type_id, event_prefix,
                                  *, header_bytes=4, body_kind="default"):
        if state.next_out_envelope_seq is None:
            self._emit(event_prefix + "_REJECTED", peer, reason="cursor_unavailable")
            return False
        record = self.frame.MessageRecord(
            channel=0, payload=self.wire.encode_vlq32(len(body)) + body,
            sequence=state.next_ch0_seq, reliable_sequence=state.next_ch0_rel,
            reliable=True, flags_override=0x21)
        ack = self.rep.build_sm_ct_acks_record(state.ack_sequence,
                                               state.last_inbound_nonack,
                                               state.acked_through)
        envelope_sequence = state.next_out_envelope_seq
        datagram = (b"\x80\x01" + envelope_sequence.to_bytes(2, "big") +
                    self.frame.marshal_datagram([record]) + (ack or b""))
        if peer.send_app(datagram) != len(datagram):
            self._emit(event_prefix + "_REJECTED", peer, reason="send_failed")
            return False
        state.autonomous_started = True
        self._note_out_envelope(state, envelope_sequence)
        state.next_ch0_seq = (state.next_ch0_seq + 1) & 0xFFFF
        state.next_ch0_rel = (state.next_ch0_rel + 1) & 0xFFFF
        if ack is not None:
            state.ack_sequence = (state.ack_sequence + 1) & 0xFFFF
            state.acked_through = state.last_inbound_nonack
        self._emit(event_prefix + "_SENT", peer, envelope_sequence=envelope_sequence,
                   record_sequence=record.sequence, reliable_sequence=record.reliable_sequence,
                   type_id=type_id, typed_bytes=len(body),
                   **{body_kind + "_body_bytes": len(body) - header_bytes},
                   client_acceptance_proven=False, world_entry_proven=False)
        return True

    def _typed_id(self, payload):
        """Trust a typed ID only after validating the pinned C→S wrapper."""
        try:
            _, declared_size, _, inner = self.wire.parse_cs_envelope(payload)
            if declared_size != len(payload) - 8 or not self.wire.verify_cs_crc32(payload):
                return None
        except ValueError:
            return None
        if len(inner) < 4 or inner[:2] != b"\x00\x01" or not inner[2] & 0x80:
            return None
        return (inner[2] & 0x3F) | (inner[3] << 6)

    def _registration_schema(self, payload):
        """Raw or one canonical source-encoded VLQ wrapper; no offset search."""
        variants = [("raw", payload)]
        for prefix_length in range(1, 6):
            remaining = len(payload) - prefix_length
            if remaining > 0 and payload[:prefix_length] == self.wire.encode_vlq32(remaining):
                variants.append(("canonical_length_prefix", payload[prefix_length:]))
                break
        for normalization, body in variants:
            if len(body) == 832:
                try:
                    parsed = self.v3_request.parse_v3_request(body)
                    del parsed
                    return "strict", normalization, len(body)
                except (ValueError, IndexError):
                    pass
            try:
                parsed = self.v3_request.parse_v3_request_retry(body)
                if parsed is not None:
                    del parsed
                    return "structured_retry", normalization, len(body)
            except (ValueError, IndexError):
                pass
        return "unresolved", "none", 0

    def _handle(self, peer, state, plaintext):
        if not isinstance(plaintext, bytes) or not 4 <= len(plaintext) <= MAX_PLAINTEXT_BYTES:
            self._emit("CARRIER_REJECTED", peer, reason="input_limit")
            return
        try:
            envelope, body = self.frame.parse_envelope(plaintext)
        except ValueError:
            self._emit("CARRIER_REJECTED", peer, reason="invalid_envelope")
            return
        if envelope.type_byte == 0x81 and envelope.is_compressed:
            if not self._compression_ready():
                self._emit("CARRIER_REJECTED", peer, reason=self._compression_failure)
                return
            expanded = None
            used_hint = None
            for hint in LZ4_HINTS:
                try:
                    expanded = self._decompressor.decompress(body, uncompressed_size=hint)
                    used_hint = hint
                    break
                except self._decompressor.LZ4BlockError:
                    continue
            if expanded is None:
                self._emit("CARRIER_REJECTED", peer,
                           reason="compressed_invalid_or_output_limit")
                return
            if not isinstance(expanded, bytes) or len(expanded) > MAX_EXPANDED_BYTES:
                self._emit("CARRIER_REJECTED", peer, reason="expanded_limit")
                return
            self._emit("CARRIER_DECOMPRESSED", peer, envelope_sequence=envelope.sequence,
                       compressed_bytes=len(body), expanded_bytes=len(expanded),
                       size_hint=used_hint)
            body = expanded
        elif envelope.type_byte != 0x80 or envelope.is_compressed:
            self._emit("CARRIER_REJECTED", peer, reason="unsupported_mode")
            return
        result = self.frame.parse_datagram(body)
        if result.error or result.trailing_bits or not result.messages or len(result.messages) > 32:
            self._emit("CARRIER_REJECTED", peer, reason="invalid_records")
            return
        sequence = envelope.sequence
        if sequence in state.seen:
            cached = state.replies.get(sequence, ())
            for datagram in cached:
                if peer.send_app(datagram) != len(datagram):
                    self._emit("CARRIER_REJECTED", peer, reason="reply_resend_failed")
                    return
            self._emit("CARRIER_DUPLICATE", peer, envelope_sequence=sequence,
                       locally_generated_replies_resent=len(cached))
            return
        if len(state.seen) >= MAX_SEQUENCES_PER_PEER:
            self._emit("CARRIER_REJECTED", peer, reason="sequence_limit")
            return
        state.seen.add(sequence)
        self._emit("CARRIER_PARSED", peer, envelope_sequence=sequence,
                   record_count=len(result.messages), plaintext_bytes=len(plaintext))
        non_ack = False
        connect_request = False
        v3_candidates = []
        data_records = []
        for record in result.messages:
            system_id = record.system_msg_id if record.channel == 3 else None
            typed_id = self._typed_id(record.payload) if record.channel != 3 else None
            self._emit("CARRIER_RECORD", peer, envelope_sequence=sequence, flags=record.flags,
                       channel=record.channel, system_id=system_id, typed_id=typed_id,
                       payload_bytes=len(record.payload))
            if (record.channel == 3 and record.flags == 0x20 and system_id == 6 and
                    len(record.payload) == 6 and record.payload[0] == 0x40 and
                    record.payload[-1] == 0x06):
                self._emit("CLIENT_CARRIER_ACK_RANGE", peer, envelope_sequence=sequence,
                           last_to_ack=int.from_bytes(record.payload[1:3], "big"),
                           first_to_ack=int.from_bytes(record.payload[3:5], "big"))
            if system_id == 1:
                connect_request = True
            elif system_id != 6:
                non_ack = True
            if record.channel != 3 and record.flags & 0x40:
                v3_candidates.append(record)
            if record.channel != 3:
                data_records.append(record)
        prior_connect_ack = state.connect_ack_sent
        if non_ack:
            state.last_inbound_nonack = sequence
        if connect_request:
            outbound_sequence = self._out_envelope(state, sequence)
            facade = _ConnectAckFacade(
                peer, sequence,
                outgoing_envelope_seq=outbound_sequence if state.autonomous_started else None)
            self.rep.PeerSession.send_connect_ack(facade)
            if not facade.sent_ok:
                self._emit("CARRIER_REJECTED", peer, reason="connect_ack_send_failed")
                return
            state.connect_ack_sent = True
            state.acked_through = sequence
            state.ack_sequence = max(state.ack_sequence, 2)
            self._note_out_envelope(state, outbound_sequence)
            state.replies.setdefault(sequence, []).append(facade.last_datagram)
            self._emit("CONNECT_ACK_SENT", peer, envelope_sequence=sequence,
                       outbound_envelope_sequence=outbound_sequence,
                       source="pinned_peer_session")
        if (prior_connect_ack and not connect_request and data_records and
                not state.after_ack_seen):
            state.after_ack_seen = True
            self._emit("CLIENT_DATA_AFTER_CONNECT_ACK", peer, envelope_sequence=sequence,
                       data_class="non_system_data", client_acceptance_proven=False)
        post_types = [self._typed_id(record.payload)
                      for record in result.messages
                      if record.channel != 3]
        known_types = self.dispatch.supported_type_ids()
        non_registration_types = [type_id for record, type_id in zip(
            [record for record in result.messages if record.channel != 3], post_types)
            if not record.flags & 0x40 and type_id is not None and type_id != 0x13
            and type_id in known_types]
        if state.v3_sent and non_registration_types and not state.after_v3_seen:
            state.after_v3_seen = True
            self._emit("POST_REGISTRATION_CLIENT_DATA", peer, envelope_sequence=sequence,
                       typed_id=non_registration_types[0], client_acceptance_proven=False)
        if len(v3_candidates) > 1:
            self._emit("V3_REJECTED", peer, reason="ambiguous_candidates")
            self._ack(peer, state, sequence)
            return
        candidate_context = (prior_connect_ack and not connect_request and
                             len(data_records) == 1 and data_records[0].channel == 0)
        if (candidate_context and state.v3_sent and
                data_records[0].flags == 0x21):
            heartbeat_ack = self._heartbeat_ack(data_records[0].payload)
            if heartbeat_ack is not None:
                normalization, echoed = heartbeat_ack
                matched = echoed in state.pending_pings
                if matched:
                    state.pending_pings.remove(echoed)
                self._emit("HEARTBEAT_15D_ACK", peer, envelope_sequence=sequence,
                           body_bytes=36, normalization=normalization, type_id=0x15d,
                           matched_local_ping=matched, client_acceptance_proven=False)
                self._ack(peer, state, sequence)
                return
        if v3_candidates and not candidate_context:
            self._emit("V3_REJECTED", peer, reason="candidate_context_gate")
            self._ack(peer, state, sequence)
            return
        reliable_single = (candidate_context and not v3_candidates and
                           data_records[0].flags == 0x21)
        if v3_candidates or reliable_single:
            v3_record = v3_candidates[0] if v3_candidates else data_records[0]
            basis = "no_length_flag" if v3_candidates else "schema_compatibility"
            parse_mode, normalization, normalized_bytes = self._registration_schema(v3_record.payload)
            self._emit("REGISTRATION_SCHEMA_RESULT", peer, envelope_sequence=sequence,
                       parse_mode=parse_mode, normalization=normalization,
                       normalized_bytes=normalized_bytes, type_unproven=True)
            if parse_mode == "unresolved":
                self._emit("V3_REJECTED", peer, reason="schema_unresolved")
                self._ack(peer, state, sequence)
                return
            self._emit("V3_CANDIDATE", peer, envelope_sequence=sequence,
                       payload_bytes=len(v3_record.payload), recognition_basis=basis,
                       type_unproven=True)
            if not 0 < len(v3_record.payload) <= 4096:
                self._emit("V3_REJECTED", peer, reason="sequence_or_size_gate")
                self._ack(peer, state, sequence)
                return
            if state.v3_sent:
                body_out = state.v3_response_record
                ack = self.rep.build_sm_ct_acks_record(state.ack_sequence, sequence,
                                                        state.acked_through)
                if ack is not None:
                    body_out += ack
                outbound_sequence = self._out_envelope(state, sequence)
                datagram = b"\x80\x01" + outbound_sequence.to_bytes(2, "big") + body_out
                if peer.send_app(datagram) != len(datagram):
                    self._emit("V3_REJECTED", peer, reason="response_resend_failed")
                    return
                if ack is not None:
                    state.ack_sequence = (state.ack_sequence + 1) & 0xFFFF
                    state.acked_through = sequence
                state.replies.setdefault(sequence, []).append(datagram)
                self._note_out_envelope(state, outbound_sequence)
                self._emit("V3_RESPONSE_RESENT", peer, envelope_sequence=sequence)
                return
            self._emit("V3_PARSER_RESULT", peer, envelope_sequence=sequence,
                       parse_mode=parse_mode, normalization=normalization,
                       exact_request_type_known=False)
            response_fields = {"session_token": self.v3_response.make_session_token()}
            if self._server_version is not None:
                response_fields["server_version"] = self._server_version
            response = self.v3_response.encode(
                self.v3_response.V3RegistrationResponse(**response_fields))
            payload = self.wire.encode_vlq32(len(response)) + response
            record = self.frame.MessageRecord(channel=0, payload=payload, sequence=0,
                                              reliable_sequence=0, reliable=True,
                                              flags_override=0x21)
            response_record_bytes = self.frame.marshal_datagram([record])
            body_out = response_record_bytes
            ack = self.rep.build_sm_ct_acks_record(state.ack_sequence, sequence,
                                                    state.acked_through)
            if ack is not None:
                body_out += ack
            outbound_sequence = self._out_envelope(state, sequence)
            datagram = b"\x80\x01" + outbound_sequence.to_bytes(2, "big") + body_out
            if peer.send_app(datagram) != len(datagram):
                self._emit("V3_REJECTED", peer, reason="send_failed")
                return
            state.v3_sent = True
            state.v3_response_record = response_record_bytes
            self._note_out_envelope(state, outbound_sequence)
            if self._heartbeat_enabled:
                state.next_heartbeat_at = self._clock() + 0.5
            if self._self_ident_enabled:
                state.next_self_ident_at = self._clock() + 1.0
            if ack is not None:
                state.ack_sequence = (state.ack_sequence + 1) & 0xFFFF
                state.acked_through = sequence
            state.replies.setdefault(sequence, []).append(datagram)
            self._emit("V3_RESPONSE_SENT", peer, envelope_sequence=outbound_sequence,
                       inbound_envelope_sequence=sequence,
                       response_type_id=0x03, response_body_bytes=len(response),
                       response_record_sequence=0, response_reliable_sequence=0,
                       version_choice=self._version_choice,
                       client_acceptance_proven=False)
        elif non_ack and not connect_request:
            self._ack(peer, state, sequence)


def parse_options(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--port", type=int, default=64003)
    parser.add_argument("--duration", type=int, default=300)
    parser.add_argument("--chain", choices=("full", "leaf"), default="full")
    parser.add_argument("--first-light", type=Path, required=True)
    parser.add_argument("--server-version", choices=(OWNED_SERVER_VERSION,))
    parser.add_argument("--heartbeat-15d", action="store_true")
    parser.add_argument("--self-ident-default", action="store_true")
    parser.add_argument("--spawn-point-notification", action="store_true")
    parser.add_argument("--world-activation", action="store_true")
    options = parser.parse_args(argv)
    if not 1 <= options.port <= 65535 or not 1 <= options.duration <= 600:
        parser.error("Port 1..65535 and duration 1..600 required")
    if options.self_ident_default and (not options.heartbeat_15d or
                                      options.server_version != OWNED_SERVER_VERSION):
        parser.error("Default actor candidate requires owned version and heartbeat")
    if options.spawn_point_notification and not options.self_ident_default:
        parser.error("Spawn notification requires the current default actor candidate")
    if options.world_activation and not options.spawn_point_notification:
        parser.error("World activation requires the current spawn notification")
    return options


def main(argv=None):
    options = parse_options(argv)
    reference = verify_reference(options.first_light)
    codecs = load_codecs(reference)
    from dtls_transport_probe import Responder
    from connectivity_probe import EventLog, private_directory

    directory = private_directory(options.certificates)
    path = private_directory(options.log)
    path.parent.mkdir(parents=True, exist_ok=True)
    events = EventLog(path)
    try:
        adapter = RegistrationAdapter(events, codecs, server_version=options.server_version,
                                      heartbeat_15d=options.heartbeat_15d,
                                      self_ident_default=options.self_ident_default,
                                      spawn_point_notification=options.spawn_point_notification,
                                      world_activation=options.world_activation)
        Responder(directory, events, port=options.port, chain=options.chain,
                  on_app=adapter.on_app,
                  on_tick=adapter.on_tick if options.heartbeat_15d else None,
                  max_datagrams=4096,
                  max_peer_datagrams=2048).run(options.duration)
    finally:
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
