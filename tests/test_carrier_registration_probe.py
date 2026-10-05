"""Synthetic Carrier adapter controls; never launch a client or listener."""
import hashlib
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import carrier_registration_probe as adapter_module


class Events:
    def __init__(self):
        self.rows = []

    def emit(self, event, **fields):
        self.rows.append({"event": event, **fields})


class Peer:
    def __init__(self, identity, *, partial=False):
        self.id = identity
        self.sent = []
        self.partial = partial

    def send_app(self, value):
        self.sent.append(value)
        return len(value) - 1 if self.partial else len(value)


class Record:
    def __init__(self, *, channel=3, system_id=None, payload=b"", flags=0x21):
        self.channel = channel
        self.system_msg_id = system_id
        self.payload = payload
        self.flags = flags


class FakeFrame:
    MessageRecord = SimpleNamespace

    def __init__(self):
        self.records = []
        self.compressed = False
        self.error = None
        self.last_body = None
        self.marshaled = []

    def parse_envelope(self, plaintext):
        return SimpleNamespace(sequence=plaintext[0], is_compressed=self.compressed,
                               type_byte=0x81 if self.compressed else 0x80), plaintext[1:]

    def parse_datagram(self, _body):
        self.last_body = _body
        return SimpleNamespace(messages=self.records, trailing_bits=0, error=self.error)

    def marshal_datagram(self, records):
        assert len(records) == 1 and records[0].flags_override == 0x21
        self.marshaled.append(records[0])
        return b"encoded-response" if records[0].sequence == 0 else b"encoded-heartbeat"


class FakeRep:
    class PeerSession:
        @staticmethod
        def send_connect_ack(facade):
            facade.send_app(b"connect-ack")

    @staticmethod
    def build_sm_ct_acks_record(_out_seq, last, through):
        return b"ack" if through != last else None


class FakeRequest:
    def __init__(self, fail_strict=False, fail_fallback=False):
        self.fail_strict = fail_strict
        self.fail_fallback = fail_fallback

    def parse_v3_request(self, _body):
        if self.fail_strict:
            raise ValueError("secret request data")
        return object()

    def parse_v3_request_retry(self, _body):
        if self.fail_fallback:
            raise ValueError("secret request data")
        return object()


class FakeResponse:
    def __init__(self):
        self.tokens = []
        self.versions = []

    def make_session_token(self):
        token = b"R" * 32
        self.tokens.append(token)
        return token

    def V3RegistrationResponse(self, *, session_token, server_version=None):
        self.versions.append(server_version)
        return SimpleNamespace(session_token=session_token, server_version=server_version)

    def encode(self, response):
        assert response.session_token == b"R" * 32
        return b"response-body"


class FakeHeartbeat:
    HeartbeatPing15D = SimpleNamespace

    @staticmethod
    def encode_ping(ping):
        return b"\x00\x01\x9d\x05" + ping.counter.to_bytes(4, "big") + ping.nonce.to_bytes(4, "big")

    @staticmethod
    def decode_ack(body):
        if (len(body) != 36 or body[4:8] != b"\x00\x00\x00\x1c" or
                body[8:24] != b"\x00" * 16 or body[24:28] != b"\x00\x01\x9d\x05"):
            raise ValueError("private ack body")
        return SimpleNamespace(client_hash=body[:4], echoed_ping=SimpleNamespace(
            counter=int.from_bytes(body[28:32], "big"),
            nonce=int.from_bytes(body[32:36], "big")))


def setup_adapter(request=None, *, decompressor=None, compression_guard=None,
                  server_version=None, heartbeat_15d=False, self_ident_default=False,
                  spawn_point_notification=False, world_activation=False, clock=None):
    events, frame, response = Events(), FakeFrame(), FakeResponse()
    class FakeWire:
        @staticmethod
        def encode_vlq32(size):
            result = bytearray()
            while True:
                chunk = size & 0x7f
                size >>= 7
                result.append(chunk | 0x80 if size else chunk)
                if not size:
                    return bytes(result)

        @staticmethod
        def parse_cs_envelope(payload):
            if not payload.startswith(b"framed:"):
                raise ValueError("secret input")
            return 0, len(payload) - 8, b"0" * 16, payload[7:]

        @staticmethod
        def verify_cs_crc32(payload):
            return payload.startswith(b"framed:")

    codecs = (frame, request or FakeRequest(), response,
              FakeWire(), FakeRep(), SimpleNamespace(supported_type_ids=lambda: {5},
                                                    heartbeat_15d=FakeHeartbeat))
    return adapter_module.RegistrationAdapter(events, codecs, decompressor=decompressor,
                                               compression_guard=compression_guard,
                                               server_version=server_version,
                                               heartbeat_15d=heartbeat_15d,
                                               self_ident_default=self_ident_default,
                                               spawn_point_notification=spawn_point_notification,
                                               world_activation=world_activation,
                                               clock=clock), events, frame, response


def test_connect_then_registration_then_post_data_metadata_only():
    adapter, events, frame, response = setup_adapter()
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01secret-connect")
    assert peer.sent == [b"connect-ack"]
    assert "CONNECT_ACK_SENT" in [row["event"] for row in events.rows]
    frame.records = [Record(channel=0, system_id=None, flags=0xE0,
                            payload=b"secret-auth-blob")]
    adapter.on_app(peer, b"\x02secret-registration")
    assert response.tokens == [b"R" * 32]
    assert peer.sent[-1] == b"\x80\x01\x00\x02encoded-responseack"
    names = [row["event"] for row in events.rows]
    assert "CLIENT_DATA_AFTER_CONNECT_ACK" in names
    assert "V3_PARSER_RESULT" in names
    assert "V3_RESPONSE_SENT" in names
    assert response.versions == [None]
    assert {"event": "V3_RESPONSE_SENT", "connection_id": "peer-a",
            "envelope_sequence": 2, "inbound_envelope_sequence": 2,
            "response_type_id": 3,
            "response_body_bytes": len(b"response-body"),
            "response_record_sequence": 0, "response_reliable_sequence": 0,
            "version_choice": "historical", "client_acceptance_proven": False} in events.rows
    assert "POST_REGISTRATION_CLIENT_DATA" not in names
    frame.records = [Record(channel=0, system_id=None,
                            payload=b"framed:\x00\x01\x85\x00secret-next")]
    adapter.on_app(peer, b"\x03secret-next")
    assert "POST_REGISTRATION_CLIENT_DATA" in [row["event"] for row in events.rows]
    assert "secret" not in str(events.rows)


def test_candidate_before_connect_is_acked_but_not_registered():
    adapter, events, frame, _response = setup_adapter()
    peer = Peer("peer-a")
    frame.records = [Record(channel=0, flags=0xE0, payload=b"unknown secret")]
    adapter.on_app(peer, b"\x01private")
    assert peer.sent == [b"\x80\x01\x00\x01ack"]
    names = [row["event"] for row in events.rows]
    assert "V3_CANDIDATE" not in names and "V3_REJECTED" in names
    assert "V3_RESPONSE_SENT" not in names
    assert {"event": "V3_REJECTED", "connection_id": "peer-a",
            "reason": "candidate_context_gate"} in events.rows


def test_unresolved_no_length_candidate_is_only_acked_without_leaking_body():
    adapter, events, frame, _response = setup_adapter(FakeRequest(True, True))
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0xE0,
                            payload=b"secret identity")]
    adapter.on_app(peer, b"\x02private")
    assert peer.sent[-1] == b"\x80\x01\x00\x02ack"
    assert {"event": "V3_REJECTED", "connection_id": "peer-a",
            "reason": "schema_unresolved"} in events.rows
    assert "V3_RESPONSE_SENT" not in [row["event"] for row in events.rows]
    assert "secret" not in str(events.rows)


def test_duplicate_v3_resends_cached_reply_and_retry_is_not_progress():
    adapter, events, frame, response = setup_adapter()
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0xE0, payload=b"secret registration")]
    adapter.on_app(peer, b"\x02registration")
    original = peer.sent[-1]
    adapter.on_app(peer, b"\x02registration")
    assert peer.sent[-1] == original
    adapter.on_app(peer, b"\x03retry")
    assert peer.sent[-1][:4] == b"\x80\x01\x00\x03"
    assert response.tokens == [b"R" * 32]
    assert "POST_REGISTRATION_CLIENT_DATA" not in [row["event"] for row in events.rows]
    assert "V3_RESPONSE_RESENT" in [row["event"] for row in events.rows]


def test_partial_send_cannot_claim_connect_ack():
    adapter, events, frame, _response = setup_adapter()
    peer = Peer("peer-a", partial=True)
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    assert "CONNECT_ACK_SENT" not in [row["event"] for row in events.rows]
    assert {"event": "CARRIER_REJECTED", "connection_id": "peer-a",
            "reason": "connect_ack_send_failed"} in events.rows


def test_partial_v3_send_does_not_advance_response_or_ack_state():
    adapter, events, frame, _response = setup_adapter()
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    peer.partial = True
    frame.records = [Record(channel=0, flags=0xE0, payload=b"opaque")]
    adapter.on_app(peer, b"\x02candidate")
    state = adapter.peers[peer.id]
    assert not state.v3_sent and state.acked_through == 1 and state.v3_response_record is None
    assert "V3_RESPONSE_SENT" not in [row["event"] for row in events.rows]


def test_two_candidate_records_reject_ambiguity():
    adapter, events, frame, _response = setup_adapter()
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0xE0, payload=b"first"),
                     Record(channel=0, flags=0xE0, payload=b"second")]
    adapter.on_app(peer, b"\x02candidates")
    assert {"event": "V3_REJECTED", "connection_id": "peer-a",
            "reason": "ambiguous_candidates"} in events.rows
    assert "V3_RESPONSE_SENT" not in [row["event"] for row in events.rows]


@pytest.mark.parametrize("records", [
    [Record(channel=1, flags=0xE0, payload=b"x" * 75)],
    [Record(channel=0, flags=0xE0, payload=b"x" * 75),
     Record(channel=0, flags=0x21, payload=b"other")],
])
def test_good_schema_no_length_record_requires_sole_channel_zero_data(records):
    request = FixtureRequest(b"x" * 75, "retry")
    adapter, events, frame, response = setup_adapter(request)
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = records
    adapter.on_app(peer, b"\x02inadmissible")
    assert request.seen == [] and response.tokens == []
    assert peer.sent[-1] == b"\x80\x01\x00\x02ack"
    assert {"event": "V3_REJECTED", "connection_id": "peer-a",
            "reason": "candidate_context_gate"} in events.rows
    assert "V3_RESPONSE_SENT" not in [row["event"] for row in events.rows]


def test_same_datagram_connect_and_good_schema_cannot_use_new_ack_as_prior_state():
    request = FixtureRequest(b"x" * 75, "retry")
    adapter, events, frame, response = setup_adapter(request)
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01"),
                     Record(channel=0, flags=0xE0, payload=b"x" * 75)]
    adapter.on_app(peer, b"\x01mixed")
    assert peer.sent == [b"connect-ack"]
    assert request.seen == [] and response.tokens == []
    assert {"event": "V3_REJECTED", "connection_id": "peer-a",
            "reason": "candidate_context_gate"} in events.rows


def test_two_unknown_reliable_records_cannot_be_schema_candidates():
    request = FixtureRequest(b"x" * 75, "retry")
    adapter, events, frame, response = setup_adapter(request)
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0x21, payload=b"x" * 75),
                     Record(channel=0, flags=0x21, payload=b"x" * 75)]
    adapter.on_app(peer, b"\x02multiple")
    assert request.seen == [] and response.tokens == []
    assert peer.sent[-1] == b"\x80\x01\x00\x02ack"
    assert "V3_CANDIDATE" not in [row["event"] for row in events.rows]


def test_ack_only_does_not_pingpong_and_state_is_per_connection():
    adapter, events, frame, _response = setup_adapter()
    first, second = Peer("first"), Peer("second")
    frame.records = [Record(system_id=6, payload=b"\x06")]
    adapter.on_app(first, b"\x01ack")
    assert not first.sent
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(second, b"\x01connect")
    assert second.sent == [b"connect-ack"]
    adapter.on_app(second, b"\x01connect")
    assert second.sent == [b"connect-ack", b"connect-ack"]
    assert "CARRIER_DUPLICATE" in [row["event"] for row in events.rows]


def test_exact_client_ack_range_shape_records_numbers_only():
    adapter, events, frame, _response = setup_adapter()
    peer = Peer("peer-a")
    frame.records = [Record(channel=3, system_id=6, flags=0x20,
                            payload=b"\x40\x12\x34\x00\x02\x06")]
    adapter.on_app(peer, b"\x01ack")
    assert {"event": "CLIENT_CARRIER_ACK_RANGE", "connection_id": "peer-a",
            "envelope_sequence": 1, "last_to_ack": 0x1234,
            "first_to_ack": 2} in events.rows
    assert not peer.sent
    assert "\x40" not in str(events.rows)


@pytest.mark.parametrize("flags,payload", [
    (0x21, b"\x40\x00\x01\x00\x01\x06"),
    (0x20, b"\x41\x00\x01\x00\x01\x06"),
    (0x20, b"\x40\x00\x01\x00\x01\x06\x06"),
    (0x20, b"\x40\x00\x01\x00\x01\x05"),
])
def test_nonmatching_ack_shape_has_no_range_event(flags, payload):
    adapter, events, frame, _response = setup_adapter()
    frame.records = [Record(channel=3, system_id=6, flags=flags, payload=payload)]
    adapter.on_app(Peer("peer-a"), b"\x01ack")
    assert "CLIENT_CARRIER_ACK_RANGE" not in [row["event"] for row in events.rows]


def test_owned_version_option_is_one_field_and_only_exact_marker_is_allowed():
    marker = adapter_module.OWNED_SERVER_VERSION
    adapter, events, frame, response = setup_adapter(server_version=marker)
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0xE0, payload=b"opaque")]
    adapter.on_app(peer, b"\x02registration")
    assert response.versions == [marker]
    assert any(row["event"] == "V3_RESPONSE_SENT" and
               row["version_choice"] == "owned_image" for row in events.rows)
    assert marker not in str(events.rows)
    with pytest.raises(ValueError, match="unsupported server version"):
        setup_adapter(server_version="anything else")
    arguments = ["--certificates", "unused", "--log", "unused", "--first-light", "unused"]
    assert adapter_module.parse_options(arguments).server_version is None
    assert adapter_module.parse_options(arguments).heartbeat_15d is False
    assert adapter_module.parse_options(arguments + ["--heartbeat-15d"]).heartbeat_15d is True
    assert adapter_module.parse_options(arguments + ["--server-version", marker]).server_version == marker
    with pytest.raises(SystemExit) as error:
        adapter_module.parse_options(arguments + ["--server-version", "anything else"])
    assert error.value.code == 2


def test_opt_in_heartbeat_fake_clock_cursor_and_private_echo():
    now = [0.0]
    adapter, events, frame, _response = setup_adapter(
        heartbeat_15d=True, clock=lambda: now[0])
    peer = Peer("peer-a")
    adapter.on_tick(peer, 0.0)
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    assert adapter.peers[peer.id].ack_sequence == 2  # MN connect uses ch3 IDs 0 and 1.
    frame.records = [Record(channel=0, flags=0xE0, payload=b"opaque")]
    adapter.on_app(peer, b"\x02registration")
    assert adapter.peers[peer.id].ack_sequence == 3
    original_response = peer.sent[-1]
    adapter.on_tick(peer, 0.49)
    assert peer.sent[-1] == original_response
    adapter.on_tick(peer, 0.5)
    first_ping = adapter.peers[peer.id].pending_pings[0]
    assert peer.sent[-1] == b"\x80\x01\x00\x03encoded-heartbeat"
    assert (frame.marshaled[-1].sequence, frame.marshaled[-1].reliable_sequence) == (1, 1)
    adapter.on_tick(peer, 0.99)
    assert len(adapter.peers[peer.id].pending_pings) == 1
    adapter.on_tick(peer, 1.0)
    assert peer.sent[-1] == b"\x80\x01\x00\x04encoded-heartbeat"
    assert (frame.marshaled[-1].sequence, frame.marshaled[-1].reliable_sequence) == (2, 2)
    adapter.on_app(peer, b"\x02duplicate")
    assert peer.sent[-1] == original_response  # Cached retransmission keeps its old envelope.
    frame.records = [Record(channel=0, flags=0x20, payload=b"unknown")]
    adapter.on_app(peer, b"\x03unknown")
    assert peer.sent[-1] == b"\x80\x01\x00\x05ack"
    assert adapter.peers[peer.id].ack_sequence == 4
    echo = (b"SECR" + b"\x00\x00\x00\x1c" + bytes(16) + b"\x00\x01\x9d\x05" +
            first_ping[0].to_bytes(4, "big") + first_ping[1].to_bytes(4, "big"))
    frame.records = [Record(channel=0, flags=0x21, payload=echo)]
    adapter.on_app(peer, b"\x04heartbeat-ack")
    assert peer.sent[-1] == b"\x80\x01\x00\x06ack"
    assert first_ping not in adapter.peers[peer.id].pending_pings
    assert any(row["event"] == "HEARTBEAT_15D_ACK" and row["matched_local_ping"] is True
               and row["type_id"] == 0x15d for row in events.rows)
    assert "SECR" not in str(events.rows)


def test_heartbeat_send_failure_and_budget_do_not_advance_owned_cursors():
    adapter, events, frame, _response = setup_adapter(heartbeat_15d=True, clock=lambda: 0.0)
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0xE0, payload=b"opaque")]
    adapter.on_app(peer, b"\x02registration")
    state = adapter.peers[peer.id]
    cursor = state.next_out_envelope_seq
    peer.partial = True
    adapter.on_tick(peer, 0.5)
    assert state.heartbeat_disabled and not state.pending_pings
    assert state.next_out_envelope_seq == cursor and state.next_ch0_seq == 1
    assert not any(row["event"] == "HEARTBEAT_15D_SENT" for row in events.rows)
    peer.partial = False
    adapter.on_tick(peer, 1.0)
    assert state.heartbeat_sent == 0
    state.heartbeat_disabled = False
    state.heartbeat_sent = adapter_module.MAX_HEARTBEATS_PER_PEER
    adapter.on_tick(peer, 1.0)
    assert state.heartbeat_sent == adapter_module.MAX_HEARTBEATS_PER_PEER


def test_compressed_or_invalid_frame_fails_closed():
    adapter, events, frame, _response = setup_adapter(
        decompressor=FakeLz4(fail=True), compression_guard=lambda: True)
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"secret")]
    frame.compressed = True
    adapter.on_app(peer, b"\x01whole-block")
    frame.compressed = False
    frame.error = "secret parser detail"
    adapter.on_app(peer, b"\x02secret")
    assert not peer.sent
    assert [row["reason"] for row in events.rows if row["event"] == "CARRIER_REJECTED"] == [
        "compressed_invalid_or_output_limit", "invalid_records"]
    assert "secret" not in str(events.rows)


class FakeLz4:
    class LZ4BlockError(Exception):
        pass

    def __init__(self, *, fail=False, overflow=False):
        self.hints = []
        self.fail = fail
        self.overflow = overflow

    def decompress(self, body, *, uncompressed_size):
        assert body == b"whole-block"
        self.hints.append(uncompressed_size)
        if self.fail or uncompressed_size < 4096:
            raise self.LZ4BlockError("private malformed bytes")
        return b"x" * (262145 if self.overflow else 12)


def test_bounded_compression_uses_full_body_and_only_records_lengths():
    decoder = FakeLz4()
    adapter, events, frame, _response = setup_adapter(
        decompressor=decoder, compression_guard=lambda: True)
    frame.compressed = True
    frame.records = [Record(system_id=6, payload=b"\x06")]
    adapter.on_app(Peer("peer-a"), b"\x01whole-block")
    assert decoder.hints == [256, 1024, 4096]
    assert frame.last_body == b"x" * 12
    assert {"event": "CARRIER_DECOMPRESSED", "connection_id": "peer-a",
            "envelope_sequence": 1, "compressed_bytes": 11,
            "expanded_bytes": 12, "size_hint": 4096} in events.rows
    assert "whole-block" not in str(events.rows)


@pytest.mark.parametrize("fail,overflow,reason", [
    (True, False, "compressed_invalid_or_output_limit"), (False, True, "expanded_limit")])
def test_compression_rejects_invalid_or_expanded_overflow(fail, overflow, reason):
    decoder = FakeLz4(fail=fail, overflow=overflow)
    adapter, events, frame, _response = setup_adapter(
        decompressor=decoder, compression_guard=lambda: True)
    frame.compressed = True
    frame.records = [Record(system_id=1, payload=b"\x01")]
    peer = Peer("peer-a")
    adapter.on_app(peer, b"\x01whole-block")
    assert not peer.sent
    assert {"event": "CARRIER_REJECTED", "connection_id": "peer-a",
            "reason": reason} in events.rows
    assert max(decoder.hints) <= 262144


def test_compression_source_guard_and_input_limit_fail_before_decoder():
    decoder = FakeLz4()

    def denied_source():
        raise ValueError("private path detail")

    adapter, events, frame, _response = setup_adapter(
        decompressor=decoder, compression_guard=denied_source)
    frame.compressed = True
    peer = Peer("peer-a")
    adapter.on_app(peer, b"\x01whole-block")
    adapter.on_app(peer, b"\x02" + b"x" * 4096)
    assert decoder.hints == [] and not peer.sent
    assert [row["reason"] for row in events.rows if row["event"] == "CARRIER_REJECTED"] == [
        "compression_source_unverified", "input_limit"]
    assert "private path detail" not in str(events.rows)


def test_system_only_after_connect_cannot_claim_new_client_data():
    adapter, events, frame, _response = setup_adapter()
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    for sequence, system_id in ((2, 3), (3, 4), (4, 6)):
        frame.records = [Record(system_id=system_id, payload=bytes([system_id]))]
        adapter.on_app(peer, bytes([sequence]) + b"system")
    assert "CLIENT_DATA_AFTER_CONNECT_ACK" not in [row["event"] for row in events.rows]
    frame.records = [Record(channel=0, flags=0xE0, payload=b"opaque")]
    adapter.on_app(peer, b"\x05candidate")
    assert {"event": "CLIENT_DATA_AFTER_CONNECT_ACK", "connection_id": "peer-a",
            "envelope_sequence": 5, "data_class": "non_system_data",
            "client_acceptance_proven": False} in events.rows


def test_unknown_reliable_860_byte_data_is_progress_only_and_acked():
    adapter, events, frame, response = setup_adapter(FakeRequest(True, True))
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=3, system_id=6, flags=0x20, payload=b"\x06"),
                     Record(channel=0, flags=0x21, payload=b"private" * 122 + b"abcdef")]
    assert len(frame.records[1].payload) == 860
    adapter.on_app(peer, b"\x02unknown")
    assert peer.sent[-1] == b"\x80\x01\x00\x02ack"
    assert response.tokens == []
    assert {"event": "CLIENT_DATA_AFTER_CONNECT_ACK", "connection_id": "peer-a",
            "envelope_sequence": 2, "data_class": "non_system_data",
            "client_acceptance_proven": False} in events.rows
    assert {"event": "REGISTRATION_SCHEMA_RESULT", "connection_id": "peer-a",
            "envelope_sequence": 2, "parse_mode": "unresolved", "normalization": "none",
            "normalized_bytes": 0, "type_unproven": True} in events.rows
    assert "V3_RESPONSE_SENT" not in [row["event"] for row in events.rows]
    assert "private" not in str(events.rows)


class FixtureRequest:
    def __init__(self, expected, mode):
        self.expected = expected
        self.mode = mode
        self.seen = []

    def parse_v3_request(self, body):
        self.seen.append(("strict", len(body)))
        if self.mode == "strict" and body == self.expected:
            return object()
        raise ValueError("private parser details")

    def parse_v3_request_retry(self, body):
        self.seen.append(("retry", len(body)))
        return object() if self.mode == "retry" and body == self.expected else None


@pytest.mark.parametrize("mode,length", [("strict", 832), ("retry", 75)])
def test_schema_compatibility_on_canonical_length_prefix_only(mode, length):
    fixture = bytes([0x5a]) * length
    request = FixtureRequest(fixture, mode)
    adapter, events, frame, response = setup_adapter(request)
    peer = Peer("peer-a")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    prefix = adapter.wire.encode_vlq32(len(fixture))
    frame.records = [Record(channel=0, flags=0x21, payload=prefix + fixture)]
    adapter.on_app(peer, b"\x02synthetic")
    assert response.tokens == [b"R" * 32]
    assert {"event": "REGISTRATION_SCHEMA_RESULT", "connection_id": "peer-a",
            "envelope_sequence": 2, "parse_mode": "strict" if mode == "strict" else "structured_retry",
            "normalization": "canonical_length_prefix", "normalized_bytes": length,
            "type_unproven": True} in events.rows
    assert {"event": "V3_CANDIDATE", "connection_id": "peer-a",
            "envelope_sequence": 2, "payload_bytes": len(prefix) + length,
            "recognition_basis": "schema_compatibility", "type_unproven": True} in events.rows
    assert "private" not in str(events.rows)


def test_reference_admission_rejects_wrong_path_dirty_tree_and_hash(tmp_path, monkeypatch):
    reference = tmp_path / "first-light"
    reference.mkdir()
    selected = reference / "server" / "javelin" / "frame.py"
    selected.parent.mkdir(parents=True)
    selected.write_bytes(b"pinned synthetic source")
    digest = hashlib.sha256(selected.read_bytes()).hexdigest()
    monkeypatch.setattr(adapter_module, "REFERENCE", reference)
    monkeypatch.setattr(adapter_module, "SOURCE_HASHES", {"server/javelin/frame.py": digest})
    monkeypatch.setattr(adapter_module, "_git", lambda _reference, *args: (
        str(reference) if args == ("rev-parse", "--show-toplevel") else
        adapter_module.COMMIT if args == ("rev-parse", "HEAD") else ""))
    assert adapter_module.verify_reference(reference) == reference
    with pytest.raises(ValueError, match="exact local checkout"):
        adapter_module.verify_reference(tmp_path)
    selected.write_bytes(b"changed")
    with pytest.raises(ValueError, match="source hash mismatch"):
        adapter_module.verify_reference(reference)
    selected.write_bytes(b"pinned synthetic source")
    monkeypatch.setattr(adapter_module, "_git", lambda _reference, *args: "dirty"
                        if args == ("status", "--porcelain") else
                        str(reference) if args == ("rev-parse", "--show-toplevel") else
                        adapter_module.COMMIT)
    with pytest.raises(ValueError, match="not clean"):
        adapter_module.verify_reference(reference)


def _ready_current_actor_candidate(*, spawn_point_notification=False, world_activation=False):
    adapter, events, frame, _response = setup_adapter(
        server_version=adapter_module.OWNED_SERVER_VERSION,
        heartbeat_15d=True, self_ident_default=True,
        spawn_point_notification=spawn_point_notification,
        world_activation=world_activation, clock=lambda: 0.0)
    peer = Peer("actor-candidate")
    adapter.on_tick(peer, 2.0)
    assert not peer.sent
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, payload=b"private-registration")]
    adapter.on_app(peer, b"\x02registration")
    return adapter, events, frame, peer


def test_world_activation_stages_once_and_preserves_shared_cursors():
    adapter, events, frame, peer = _ready_current_actor_candidate(
        spawn_point_notification=True, world_activation=True)
    for tick in (1.0, 2.0, 2.99):
        adapter.on_tick(peer, tick)
    assert not any(row["event"] == "LEVEL_INFO_CANDIDATE_SENT" for row in events.rows)
    adapter.on_tick(peer, 3.0)
    level = next(row for row in events.rows if row["event"] == "LEVEL_INFO_CANDIDATE_SENT")
    assert (level["type_id"], level["typed_bytes"], level["candidate_body_bytes"]) == (1635, 63, 59)
    adapter.on_tick(peer, 3.99)
    assert not any(row["event"] == "EMPTY_STATE_BUNDLE_SENT" for row in events.rows)
    adapter.on_tick(peer, 4.0)
    bundle = next(row for row in events.rows if row["event"] == "EMPTY_STATE_BUNDLE_SENT")
    assert (bundle["type_id"], bundle["typed_bytes"], bundle["default_body_bytes"]) == (8, 9, 6)
    adapter.on_tick(peer, 20.0)
    for name in ("SELF_IDENT_DEFAULT_SENT", "SPAWN_POINT_NOTIFICATION_SENT",
                 "LEVEL_INFO_CANDIDATE_SENT", "EMPTY_STATE_BUNDLE_SENT"):
        assert sum(row["event"] == name for row in events.rows) == 1
    sequences = [(record.sequence, record.reliable_sequence) for record in frame.marshaled]
    assert sequences == [(index, index) for index in range(len(sequences))]
    assert level["world_entry_proven"] is False and bundle["client_acceptance_proven"] is False
    assert "private-registration" not in str(events.rows)


def test_world_activation_delayed_tick_and_failed_level_send_do_not_send_bundle():
    adapter, events, _frame, peer = _ready_current_actor_candidate(
        spawn_point_notification=True, world_activation=True)
    adapter.on_tick(peer, 100.0)
    adapter.on_tick(peer, 101.0)
    state = adapter.peers[peer.id]
    assert state.next_level_info_at == 102.0 and not state.level_info_sent
    before = (state.next_out_envelope_seq, state.next_ch0_seq, state.next_ch0_rel, state.ack_sequence)
    peer.partial = True
    adapter.on_tick(peer, 102.0)
    assert (state.next_out_envelope_seq, state.next_ch0_seq, state.next_ch0_rel, state.ack_sequence) == before
    assert state.level_info_disabled and not state.level_info_sent
    adapter.on_tick(peer, 110.0)
    assert not any(row["event"] == "EMPTY_STATE_BUNDLE_SENT" for row in events.rows)


def test_world_activation_requires_current_spawn_option_and_defaults_off():
    with pytest.raises(ValueError, match="requires the current spawn"):
        setup_adapter(world_activation=True)
    arguments = ["--certificates", "private/certificates", "--log", "private/events.jsonl",
                 "--first-light", str(adapter_module.REFERENCE)]
    assert adapter_module.parse_options(arguments).world_activation is False
    with pytest.raises(SystemExit):
        adapter_module.parse_options(arguments + ["--world-activation"])
    options = adapter_module.parse_options(arguments + ["--world-activation", "--heartbeat-15d",
        "--self-ident-default", "--spawn-point-notification", "--server-version", adapter_module.OWNED_SERVER_VERSION])
    assert options.world_activation is True


def test_default_actor_candidate_once_after_registration_shares_heartbeat_cursors():
    adapter, events, frame, peer = _ready_current_actor_candidate()
    adapter.on_tick(peer, 0.5)
    adapter.on_tick(peer, 0.99)
    assert not any(row["event"] == "SELF_IDENT_DEFAULT_SENT" for row in events.rows)
    adapter.on_tick(peer, 1.0)
    actor = next(row for row in events.rows if row["event"] == "SELF_IDENT_DEFAULT_SENT")
    assert (actor["type_id"], actor["typed_bytes"], actor["default_body_bytes"]) == (1628, 131, 127)
    assert (actor["record_sequence"], actor["reliable_sequence"]) == (2, 2)
    assert frame.marshaled[-2].payload == adapter.wire.encode_vlq32(131) + b"\x00\x01\x9c\x19" + bytes(127)
    assert [(record.sequence, record.reliable_sequence) for record in frame.marshaled] == [(0, 0), (1, 1), (2, 2), (3, 3)]
    adapter.on_tick(peer, 3.0)
    assert sum(row["event"] == "SELF_IDENT_DEFAULT_SENT" for row in events.rows) == 1
    assert actor["client_acceptance_proven"] is False and actor["world_entry_proven"] is False
    assert "private-registration" not in str(events.rows)


def test_failed_default_actor_send_cannot_advance_shared_cursors_or_claim_delivery():
    adapter, events, _frame, peer = _ready_current_actor_candidate()
    state = adapter.peers[peer.id]
    before = (state.next_out_envelope_seq, state.next_ch0_seq, state.next_ch0_rel, state.ack_sequence)
    peer.partial = True
    adapter.on_tick(peer, 1.0)
    assert (state.next_out_envelope_seq, state.next_ch0_seq, state.next_ch0_rel, state.ack_sequence) == before
    assert state.self_ident_disabled and not state.self_ident_sent
    assert not any(row["event"] == "SELF_IDENT_DEFAULT_SENT" for row in events.rows)
    actor_rejections = [row for row in events.rows if row["event"] == "SELF_IDENT_DEFAULT_REJECTED"]
    assert actor_rejections == [{"event": "SELF_IDENT_DEFAULT_REJECTED", "connection_id": peer.id, "reason": "send_failed"}]
    sent_count = len(peer.sent)
    adapter.on_tick(peer, 2.0)
    assert len(peer.sent) == sent_count


def test_current_actor_candidate_requires_explicit_owned_configuration():
    with pytest.raises(ValueError, match="owned version and heartbeat"):
        setup_adapter(self_ident_default=True)
    with pytest.raises(ValueError, match="owned version and heartbeat"):
        setup_adapter(heartbeat_15d=True, self_ident_default=True)


def test_spawn_notification_waits_for_actual_self_ident_send_and_uses_shared_cursors():
    adapter, events, frame, peer = _ready_current_actor_candidate(spawn_point_notification=True)
    # A delayed first tick still leaves a full second between the two messages.
    adapter.on_tick(peer, 4.0)
    assert not any(row["event"] == "SPAWN_POINT_NOTIFICATION_SENT" for row in events.rows)
    adapter.on_tick(peer, 4.99)
    assert not any(row["event"] == "SPAWN_POINT_NOTIFICATION_SENT" for row in events.rows)
    adapter.on_tick(peer, 5.0)
    spawn = next(row for row in events.rows if row["event"] == "SPAWN_POINT_NOTIFICATION_SENT")
    assert (spawn["type_id"], spawn["typed_bytes"], spawn["default_body_bytes"]) == (1617, 4, 0)
    assert frame.marshaled[-1].payload == b"\x04\x00\x01\x91\x19"
    assert [(record.sequence, record.reliable_sequence) for record in frame.marshaled] == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    adapter.on_tick(peer, 7.0)
    assert sum(row["event"] == "SPAWN_POINT_NOTIFICATION_SENT" for row in events.rows) == 1


def test_failed_self_ident_send_cannot_schedule_spawn_notification():
    adapter, events, _frame, peer = _ready_current_actor_candidate(spawn_point_notification=True)
    peer.partial = True
    adapter.on_tick(peer, 1.0)
    adapter.on_tick(peer, 3.0)
    assert adapter.peers[peer.id].next_spawn_point_at is None
    assert not any(row["event"].startswith("SPAWN_POINT_NOTIFICATION") for row in events.rows)
