"""Synthetic Carrier adapter controls; never launch a client or listener."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import carrier_registration_probe as adapter_module
from dtls_transport_probe import TerminalProtocolError
from current_creation_member_body import MEMBER_UUID as CREATION_UUID
from current_player_identity_body import MEMBER_UUID as IDENTITY_UUID
from current_player_creation_candidate import OWNED_PLAYER_ASSET, compose_player_creation_candidate
from private_player_creation_trial import PreparedPlayerCreation
from private_trial_character import PrivateTrialCharacter
from current_registration_response_body import RegistrationResponseBody
from current_registration_response_record import encode_registration_response_record

CURRENT_RESPONSE = RegistrationResponseBody(0, 0, b"", b"", (False,) * 4)
CURRENT_STREAMS = json.loads((Path(__file__).resolve().parents[1] /
    "tests/fixtures/registration/current-request-stream-original.json").read_text())["vectors"]


CLI_BASE = ["--certificates", "unused", "--log", "unused", "--first-light", "unused"]
CLI_CURRENT = ["--current-request-type-index", "0", "--current-response-type-index", "0x3",
               "--current-response-body", "private/body.bin",
               "--current-response-body-sha256", "0" * 64]


@pytest.mark.parametrize("mask", range(1, 15))
def test_current_cli_requires_the_entire_explicit_profile(mask):
    supplied = [value for index in range(4) if mask & (1 << index)
                for value in CLI_CURRENT[index * 2:index * 2 + 2]]
    with pytest.raises(SystemExit) as error:
        adapter_module.parse_options(CLI_BASE + supplied)
    assert error.value.code == 2


@pytest.mark.parametrize("selector", ["-1", "4294967296", "0x100000000", "none"])
def test_current_cli_rejects_out_of_range_or_noninteger_selector(selector):
    current = CLI_CURRENT.copy()
    current[1] = selector
    with pytest.raises(SystemExit):
        adapter_module.parse_options(CLI_BASE + current)


@pytest.mark.parametrize("stage", ["--heartbeat-15d", "--self-ident-default",
    "--self-ident-current-length", "--spawn-point-notification", "--world-activation",
    "--player-creation-candidate"])
def test_current_cli_cannot_enable_trial_messages(stage):
    with pytest.raises(SystemExit):
        adapter_module.parse_options(CLI_BASE + CLI_CURRENT + [stage])


def test_current_cli_zero_selector_and_historical_default_are_distinct():
    options = adapter_module.parse_options(CLI_BASE + CLI_CURRENT)
    assert options.current_request_type_index == 0
    assert options.current_response_type_index == 3
    historical = adapter_module.parse_options(CLI_BASE)
    assert historical.current_request_type_index is None
    assert adapter_module.prepare_current_registration(historical) == {}
    with pytest.raises(SystemExit):
        adapter_module.parse_options(CLI_BASE + CLI_CURRENT +
            ["--server-version", adapter_module.OWNED_SERVER_VERSION])


@pytest.mark.parametrize("digest", ["", "0" * 63, "0" * 65, "z" * 64])
def test_current_cli_requires_a_complete_hexadecimal_digest(digest):
    current = CLI_CURRENT.copy()
    current[-1] = digest
    with pytest.raises(SystemExit):
        adapter_module.parse_options(CLI_BASE + current)


def private_body_options(tmp_path, monkeypatch, raw):
    import connectivity_probe
    monkeypatch.setattr(connectivity_probe, "WORKSPACE", tmp_path)
    path = tmp_path / "private" / "body.bin"
    path.parent.mkdir()
    path.write_bytes(raw)
    current = CLI_CURRENT.copy()
    current[5], current[7] = str(path), hashlib.sha256(raw).hexdigest().upper()
    return adapter_module.parse_options(CLI_BASE + current)


def test_current_cli_prepares_exact_caller_body_and_selectors(tmp_path, monkeypatch):
    # Original literal: zero u32/u64, two empty counted byte fields, four false flags.
    options = private_body_options(tmp_path, monkeypatch, bytes.fromhex("00" * 18))
    prepared = adapter_module.prepare_current_registration(options)
    assert prepared == {"current_request_type_index": 0, "current_response_type_index": 3,
                        "current_response_body": CURRENT_RESPONSE}


@pytest.mark.parametrize("raw", [b"", bytes(17), bytes(18) + b"tail",
    bytes(12) + b"\x80\x00" + bytes(5), bytes(17) + b"\x02", bytes(4097),
    bytes(12) + b"\xbf\x3f" + b"x" * 4095 + bytes(5)])
def test_current_cli_rejects_invalid_or_unbounded_body_privately(tmp_path, monkeypatch, raw):
    options = private_body_options(tmp_path, monkeypatch, raw)
    with pytest.raises(ValueError) as error:
        adapter_module.prepare_current_registration(options)
    assert str(error.value) == "Invalid private current registration response configuration"


def test_current_cli_hash_and_private_path_fail_before_runtime(tmp_path, monkeypatch):
    options = private_body_options(tmp_path, monkeypatch, bytes(18))
    options.current_response_body_sha256 = "0" * 64
    monkeypatch.setattr(adapter_module, "verify_reference", lambda *_: pytest.fail("runtime reached"))
    with pytest.raises(ValueError):
        adapter_module.main(CLI_BASE + ["--current-request-type-index", "0",
            "--current-response-type-index", "3", "--current-response-body",
            options.current_response_body, "--current-response-body-sha256", "0" * 64])
    outside = tmp_path / "body.bin"
    outside.write_bytes(bytes(18))
    options.current_response_body = str(outside)
    options.current_response_body_sha256 = hashlib.sha256(bytes(18)).hexdigest()
    with pytest.raises(ValueError, match="Invalid private"):
        adapter_module.prepare_current_registration(options)


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
                  spawn_point_notification=False, world_activation=False,
                  self_ident_current_length=False, prepared_creation=None, clock=None,
                  user_stop_lifetime=False, current_request_type_index=None,
                  current_response_type_index=None, current_response_body=None):
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
                                               self_ident_current_length=self_ident_current_length,
                                               spawn_point_notification=spawn_point_notification,
                                               world_activation=world_activation,
                                               prepared_creation=prepared_creation,
                                               clock=clock,
                                               user_stop_lifetime=user_stop_lifetime,
                                               current_request_type_index=current_request_type_index,
                                               current_response_type_index=current_response_type_index,
                                               current_response_body=current_response_body), events, frame, response


@pytest.mark.parametrize("value", [1, "true", None])
def test_manual_adapter_selection_requires_explicit_boolean(value):
    with pytest.raises(ValueError, match="explicit boolean"):
        setup_adapter(user_stop_lifetime=value)


def current_adapter(request_index=19, response_index=3, body=CURRENT_RESPONSE, **kwargs):
    return setup_adapter(current_request_type_index=request_index,
        current_response_type_index=response_index, current_response_body=body, **kwargs)


def current_stream(vector):
    return bytes.fromhex(vector["crc_be32"] + vector["count_be32"] + vector["payload"])


@pytest.mark.parametrize("vector", CURRENT_STREAMS, ids=lambda row: row["name"])
@pytest.mark.parametrize("response_index", [0, 3, 300])
def test_current_literal_request_routes_exact_caller_response(vector, response_index):
    adapter, events, frame, historical = current_adapter(vector["type_index"], response_index)
    peer = Peer("current-synthetic")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0x21, payload=current_stream(vector))]
    adapter.on_app(peer, b"\x02current")
    assert frame.marshaled[-1].payload == encode_registration_response_record(
        CURRENT_RESPONSE, type_index=response_index)
    assert historical.tokens == [] and historical.versions == []
    assert adapter.peers[peer.id].v3_sent
    schema = next(row for row in events.rows if row["event"] == "REGISTRATION_SCHEMA_RESULT")
    assert schema["parse_mode"] == "current_physical" and schema["normalization"] == "raw"
    sent = next(row for row in events.rows if row["event"] == "V3_RESPONSE_SENT")
    assert sent["response_type_id"] == response_index
    assert sent["response_body_bytes"] == 18 and sent["version_choice"] == "caller_current_body"
    assert sent["client_acceptance_proven"] is False
    # A later ordinary retry reuses the exact cached record/cursor machinery.
    adapter.on_app(peer, b"\x03retry")
    assert len(frame.marshaled) == 1
    assert any(row["event"] == "V3_RESPONSE_RESENT" for row in events.rows)


@pytest.mark.parametrize("missing", ["current_request_type_index", "current_response_type_index", "current_response_body"])
def test_current_profile_requires_all_three_values(missing):
    values = dict(current_request_type_index=19, current_response_type_index=3,
                  current_response_body=CURRENT_RESPONSE)
    values[missing] = None
    with pytest.raises(ValueError, match="both type selectors and response BODY"):
        setup_adapter(**values)


@pytest.mark.parametrize("value", [True, False, -1, 1 << 32, "19", 19.0])
@pytest.mark.parametrize("selector", ["request", "response"])
def test_current_profile_rejects_invalid_selectors(selector, value):
    with pytest.raises(ValueError):
        current_adapter(**{selector + "_index": value})


@pytest.mark.parametrize("body", [b"", {}, object()])
def test_current_profile_requires_current_immutable_body(body):
    with pytest.raises(TypeError):
        current_adapter(body=body)


def test_current_response_cap_includes_record_prefix_before_peer_resources():
    allowed = RegistrationResponseBody(0, 0, b"x" * 4072, b"", (False,) * 4)
    adapter, _, _, _ = current_adapter(body=allowed)
    assert len(adapter._current_response_payload) == 4096
    oversized = RegistrationResponseBody(0, 0, b"x" * 4073, b"", (False,) * 4)
    with pytest.raises(ValueError, match="adapter byte limit"):
        current_adapter(body=oversized)


@pytest.mark.parametrize("kind", ["checksum", "count", "outer-uuid", "flags", "presence", "selector", "suffix", "prefix", "body-tail", "over-cap"])
def test_current_profile_rejects_malformed_stream_without_legacy_fallback(kind, monkeypatch):
    import zlib
    vector = next(row for row in CURRENT_STREAMS if row["type_index"] == 19 and row["flags"] == 0)
    value = current_stream(vector)
    if kind in ("outer-uuid", "flags", "presence", "selector", "body-tail"):
        payload = bytearray(value[8:])
        if kind == "body-tail":
            payload += b"private-tail"
        else:
            payload[{"outer-uuid": 0, "flags": 16, "presence": 17, "selector": 18}[kind]] ^= 0x7F
        value = zlib.crc32(payload).to_bytes(4, "big") + len(payload).to_bytes(4, "big") + payload
        value = bytes(value)
    elif kind == "checksum":
        value = bytes([value[0] ^ 1]) + value[1:]
    elif kind == "count":
        value = value[:4] + (0xFFFFFFFF).to_bytes(4, "big") + value[8:]
    elif kind == "suffix":
        value += b"private-suffix"
    elif kind == "prefix":
        value = bytes([len(value)]) + value
    else:
        value = b"private-limit" * 400
    adapter, events, frame, historical = current_adapter()
    monkeypatch.setattr(adapter.v3_request, "parse_v3_request", lambda _: pytest.fail("legacy fallback"))
    monkeypatch.setattr(adapter.v3_request, "parse_v3_request_retry", lambda _: pytest.fail("legacy fallback"))
    peer = Peer("rejected-current")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0x21, payload=value)]
    adapter.on_app(peer, b"\x02current")
    assert frame.marshaled == [] and historical.tokens == []
    assert not adapter.peers[peer.id].v3_sent
    assert any(row.get("reason") == "schema_unresolved" for row in events.rows)
    assert "private-" not in str(events.rows)


def test_current_retry_type_is_not_post_registration_progress(monkeypatch):
    vector = next(row for row in CURRENT_STREAMS if row["type_index"] == 128 and row["flags"] == 0)
    adapter, events, frame, _ = current_adapter(request_index=128)
    monkeypatch.setattr(adapter, "_typed_id", lambda _: 128)
    adapter.dispatch.supported_type_ids = lambda: {128}
    peer = Peer("current-type-policy")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0x21, payload=current_stream(vector))]
    adapter.on_app(peer, b"\x02current")
    adapter.on_app(peer, b"\x03current")
    assert any(row["event"] == "V3_RESPONSE_RESENT" for row in events.rows)
    assert not any(row["event"] == "POST_REGISTRATION_CLIENT_DATA" for row in events.rows)


@pytest.mark.parametrize("string_bytes,expected_size,accepted", [(3999, 4096, True), (4000, 4097, False)])
def test_current_request_schema_cap_includes_physical_header(string_bytes, expected_size, accepted):
    from dataclasses import replace
    from current_registration_request_body import decode_body
    from current_registration_request_stream import encode_registration_request_stream
    vector = next(row for row in CURRENT_STREAMS if row["type_index"] == 19 and row["flags"] == 0)
    body, _ = decode_body(bytes.fromhex(vector["body"]))
    value = encode_registration_request_stream(replace(body, field_a0=b"x" * string_bytes), type_index=19)
    assert len(value) == expected_size
    adapter, _, _, _ = current_adapter()
    result = adapter._registration_schema(value)
    assert result == (("current_physical", "raw", expected_size) if accepted else ("unresolved", "none", 0))


def test_current_valid_request_fields_are_not_logged_or_retained_in_peer_state():
    from dataclasses import replace
    from current_registration_request_body import decode_body
    from current_registration_request_stream import encode_registration_request_stream
    vector = next(row for row in CURRENT_STREAMS if row["type_index"] == 19 and row["flags"] == 0)
    body, _ = decode_body(bytes.fromhex(vector["body"]))
    sentinel = b"original-private-request-sentinel"
    value = encode_registration_request_stream(replace(body, field_a0=sentinel), type_index=19)
    adapter, events, frame, historical = current_adapter()
    peer = Peer("current-data-discard")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, flags=0x21, payload=value)]
    adapter.on_app(peer, b"\x02current")
    state = adapter.peers[peer.id]
    assert state.v3_sent and historical.tokens == []
    assert sentinel.decode() not in str(events.rows)
    assert sentinel.decode() not in str(vars(state))
    assert all(sentinel not in sent for sent in peer.sent)
    # The caller owns input buffers; discarding decoded fields is not secure erasure.


def test_current_partial_reply_does_not_advance_send_state():
    vector = next(row for row in CURRENT_STREAMS if row["type_index"] == 19 and row["flags"] == 0)
    adapter, events, frame, _ = current_adapter()
    peer = Peer("current-partial")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    state = adapter.peers[peer.id]
    previous_ack = (state.ack_sequence, state.acked_through)
    peer.partial = True
    frame.records = [Record(channel=0, flags=0x21, payload=current_stream(vector))]
    adapter.on_app(peer, b"\x02current")
    assert not state.v3_sent and state.v3_response_record is None
    assert (state.ack_sequence, state.acked_through) == previous_ack
    assert not any(row["event"] == "V3_RESPONSE_SENT" for row in events.rows)


def test_manual_heartbeat_continues_past_old_total_with_bounded_pending():
    adapter, events, frame, _ = setup_adapter(
        heartbeat_15d=True, user_stop_lifetime=True, clock=lambda: 0.0)
    peer = Peer("manual-heartbeat")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, system_id=None, flags=0xE0, payload=b"registration")]
    adapter.on_app(peer, b"\x02registration")
    for index in range(1201):
        adapter.on_tick(peer, 0.5 * (index + 1))
    state = adapter.peers[peer.id]
    assert state.heartbeat_sent == 1201
    assert len(state.pending_pings) == 8
    assert state.next_ch0_seq == state.next_ch0_rel == 1202
    assert not state.terminal_error
    assert len([row for row in events.rows if row["event"] == "HEARTBEAT_15D_SENT"]) == 1201


def test_manual_full_namespace_normalized_replay_and_conflict():
    class Decoder:
        class LZ4BlockError(Exception):
            pass

        def decompress(self, _body, *, uncompressed_size):
            return b"same-record-stream" if self.same else b"different-record-stream"

    decoder = Decoder()
    decoder.same = True
    adapter, events, frame, _ = setup_adapter(
        decompressor=decoder, compression_guard=lambda: None, user_stop_lifetime=True)
    peer = Peer("manual-replay")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01same-record-stream")
    initial = list(peer.sent)
    frame.compressed = True
    adapter.on_app(peer, b"\x01compressed")
    assert peer.sent == initial * 2
    assert adapter.peers[peer.id].seen_digests[1] == hashlib.sha256(b"same-record-stream").digest()
    decoder.same = False
    with pytest.raises(TerminalProtocolError, match="content_conflict"):
        adapter.on_app(peer, b"\x01compressed")
    assert peer.sent == initial * 2
    with pytest.raises(TerminalProtocolError):
        adapter.on_app(peer, b"\x02later")
    with pytest.raises(TerminalProtocolError):
        adapter.on_tick(peer, 1.0)
    assert peer.sent == initial * 2
    assert events.rows[-1]["reason"] == "inbound_sequence_content_conflict"


def test_manual_retains_more_than_old_inbound_total_and_rejects_lower_new_sequence():
    adapter, _events, frame, _ = setup_adapter(user_stop_lifetime=True)
    peer = Peer("manual-sequences")
    frame.records = [Record(system_id=6, flags=0x20)]
    frame.parse_envelope = lambda plaintext: (
        SimpleNamespace(sequence=int.from_bytes(plaintext[:2], "big"),
                        is_compressed=False, type_byte=0x80), plaintext[2:])
    for sequence in range(2051):
        if sequence == 2048:
            continue
        adapter.on_app(peer, sequence.to_bytes(2, "big") + b"stream")
    state = adapter.peers[peer.id]
    assert len(state.seen) == len(state.seen_digests) == 2050
    before = (len(peer.sent), len(state.seen), state.last_inbound_nonack,
              state.acked_through, state.ack_sequence)
    with pytest.raises(TerminalProtocolError, match="unsupported_lower"):
        adapter.on_app(peer, (2048).to_bytes(2, "big") + b"new-stream")
    assert (len(peer.sent), len(state.seen), state.last_inbound_nonack,
            state.acked_through, state.ack_sequence) == before


@pytest.mark.parametrize("cursor", ["next_out_envelope_seq", "next_ch0_seq",
                                    "next_ch0_rel", "ack_sequence"])
def test_manual_fresh_cursor_exhaustion_is_terminal_before_send(cursor):
    adapter, events, frame, _ = setup_adapter(
        heartbeat_15d=True, user_stop_lifetime=True, clock=lambda: 0.0)
    peer = Peer("manual-cursor")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, system_id=None, flags=0xE0, payload=b"registration")]
    adapter.on_app(peer, b"\x02registration")
    state = adapter.peers[peer.id]
    setattr(state, cursor, 65536)
    before = (len(peer.sent), state.next_out_envelope_seq,
              state.next_ch0_seq, state.next_ch0_rel, state.ack_sequence)
    with pytest.raises(TerminalProtocolError, match="namespace_exhausted"):
        adapter.on_tick(peer, 0.5)
    assert (len(peer.sent), state.next_out_envelope_seq,
            state.next_ch0_seq, state.next_ch0_rel, state.ack_sequence) == before
    with pytest.raises(TerminalProtocolError):
        adapter.on_tick(peer, 1.0)
    assert len(peer.sent) == before[0]
    assert events.rows[-1]["event"] == "CARRIER_TERMINAL_FAILURE"


@pytest.mark.parametrize("send_path", ["connect", "v3_initial", "v3_resend", "ack"])
def test_manual_app_send_paths_reject_unsafe_fresh_cursors_before_send(send_path):
    adapter, _events, frame, _ = setup_adapter(user_stop_lifetime=True)
    peer = Peer("manual-app-cursor")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    if send_path == "connect":
        adapter.on_app(peer, b"\x01connect")
        state = adapter.peers[peer.id]
        frame.records = [Record(system_id=1, payload=b"\x01")]
        incoming = b"\x02connect-again"
    else:
        adapter.on_app(peer, b"\x01connect")
        state = adapter.peers[peer.id]
        if send_path == "v3_resend":
            frame.records = [Record(channel=0, system_id=None, flags=0xE0,
                                    payload=b"registration")]
            adapter.on_app(peer, b"\x02registration")
            incoming = b"\x03new-registration"
        elif send_path == "v3_initial":
            frame.records = [Record(channel=0, system_id=None, flags=0xE0,
                                    payload=b"registration")]
            incoming = b"\x02registration"
        else:
            frame.records = [Record(system_id=8, payload=b"other-system")]
            incoming = b"\x02other"
    state.next_out_envelope_seq = 65536
    before = len(peer.sent)
    with pytest.raises(TerminalProtocolError):
        adapter.on_app(peer, incoming)
    assert len(peer.sent) == before


def test_manual_fresh_connect_retry_and_duplicate_preserve_distinct_cursors():
    adapter, events, frame, _ = setup_adapter(user_stop_lifetime=True)
    peer = Peer("manual-connect-retry")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01first-connect")
    adapter.on_app(peer, b"\x02changed-connect-body")
    state = adapter.peers[peer.id]
    assert peer.sent == [b"connect-ack", b"connect-ack"]
    assert (state.acked_through, state.ack_sequence, state.next_out_envelope_seq,
            state.outgoing_sequences) == (2, 2, 3, {1, 2})
    assert len([row for row in events.rows if row["event"] == "CONNECT_ACK_SENT"]) == 2

    before = (len(peer.sent), state.acked_through, state.ack_sequence,
              state.next_out_envelope_seq, set(state.outgoing_sequences))
    adapter.on_app(peer, b"\x02changed-connect-body")
    assert peer.sent[-1] == b"connect-ack"
    assert (len(peer.sent), state.acked_through, state.ack_sequence,
            state.next_out_envelope_seq, state.outgoing_sequences) == (
                before[0] + 1, *before[1:])
    assert events.rows[-1]["locally_generated_replies_resent"] == 1
    with pytest.raises(TerminalProtocolError, match="inbound_sequence_content_conflict"):
        adapter.on_app(peer, b"\x02same-envelope-different-body")
    assert len(peer.sent) == before[0] + 1


def test_manual_fresh_connect_after_autonomous_send_keeps_outbound_allocation():
    adapter, events, frame, _ = setup_adapter(
        heartbeat_15d=True, user_stop_lifetime=True, clock=lambda: 0.0)
    peer = Peer("manual-autonomous-retry")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01first-connect")
    frame.records = [Record(channel=0, flags=0xE0, payload=b"registration")]
    adapter.on_app(peer, b"\x02registration")
    adapter.on_tick(peer, 0.5)
    state = adapter.peers[peer.id]
    assert state.autonomous_started and state.next_out_envelope_seq == 4
    before_ack = state.ack_sequence
    frame.records = [Record(system_id=1, payload=b"\x02new-request")]
    adapter.on_app(peer, b"\x05different-connect-length")
    assert state.next_out_envelope_seq == 5
    assert state.acked_through == 5 and state.ack_sequence == before_ack
    assert state.outgoing_sequences == {1, 2, 3, 4}
    assert events.rows[-1]["event"] == "CONNECT_ACK_SENT"
    assert events.rows[-1]["outbound_envelope_sequence"] == 4
    assert len(peer.sent) == 4


def test_manual_fresh_connect_checks_ack_namespace_after_real_ack_send():
    adapter, _events, frame, _ = setup_adapter(user_stop_lifetime=True)
    peer = Peer("manual-ack-exhaustion")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    state = adapter.peers[peer.id]
    state.ack_sequence = 65535
    frame.records = [Record(system_id=8, payload=b"other")]
    adapter.on_app(peer, b"\x02other")
    assert state.ack_sequence == 65536 and state.next_out_envelope_seq == 3
    sent = len(peer.sent)
    frame.records = [Record(system_id=1, payload=b"\x02")]
    with pytest.raises(TerminalProtocolError, match="outgoing_ack_namespace_exhausted"):
        adapter.on_app(peer, b"\x03fresh-connect")
    assert len(peer.sent) == sent


def test_manual_fresh_connect_rejects_exhausted_envelope_after_success():
    adapter, _events, frame, _ = setup_adapter(user_stop_lifetime=True)
    peer = Peer("manual-envelope-exhaustion")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    state = adapter.peers[peer.id]
    state.autonomous_started = True
    state.next_out_envelope_seq = 65535
    adapter.on_app(peer, b"\x02fresh-connect")
    assert state.next_out_envelope_seq == 65536
    sent = len(peer.sent)
    with pytest.raises(TerminalProtocolError, match="outgoing_envelope_namespace_exhausted"):
        adapter.on_app(peer, b"\x03fresh-again")
    assert len(peer.sent) == sent


def test_manual_partial_second_connect_latches_terminal_failure():
    adapter, _events, frame, _ = setup_adapter(user_stop_lifetime=True)
    peer = Peer("manual-connect-partial")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01first")
    state = adapter.peers[peer.id]
    prior = (state.acked_through, state.ack_sequence, state.next_out_envelope_seq)
    peer.partial = True
    with pytest.raises(TerminalProtocolError, match="connect_ack_send_failed"):
        adapter.on_app(peer, b"\x02second")
    assert (state.acked_through, state.ack_sequence,
            state.next_out_envelope_seq) == prior
    peer.partial = False
    with pytest.raises(TerminalProtocolError, match="connect_ack_send_failed"):
        adapter.on_app(peer, b"\x03third")
    assert len(peer.sent) == 2


def test_manual_fixed_actor_send_checks_shared_reliable_cursor():
    adapter, _events, frame, _ = setup_adapter(
        server_version=adapter_module.OWNED_SERVER_VERSION, heartbeat_15d=True,
        self_ident_default=True, user_stop_lifetime=True, clock=lambda: 0.0)
    peer = Peer("manual-actor-cursor")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, system_id=None, flags=0xE0, payload=b"registration")]
    adapter.on_app(peer, b"\x02registration")
    state = adapter.peers[peer.id]
    state.next_ch0_rel = 65536
    before = len(peer.sent)
    with pytest.raises(TerminalProtocolError, match="record_namespace_exhausted"):
        adapter.on_tick(peer, 1.0)
    assert len(peer.sent) == before
    assert not state.self_ident_sent


def test_manual_partial_send_latches_terminal_failure():
    adapter, _events, frame, _ = setup_adapter(
        heartbeat_15d=True, user_stop_lifetime=True, clock=lambda: 0.0)
    peer = Peer("manual-partial")
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, system_id=None, flags=0xE0, payload=b"registration")]
    adapter.on_app(peer, b"\x02registration")
    peer.partial = True
    with pytest.raises(TerminalProtocolError, match="heartbeat_send_failed"):
        adapter.on_tick(peer, 0.5)
    sent = len(peer.sent)
    peer.partial = False
    with pytest.raises(TerminalProtocolError):
        adapter.on_tick(peer, 1.0)
    with pytest.raises(TerminalProtocolError):
        adapter.on_app(peer, b"\x03later")
    assert len(peer.sent) == sent


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


def _ready_current_actor_candidate(*, spawn_point_notification=False, world_activation=False,
                                   self_ident_current_length=False, prepared_creation=None):
    adapter, events, frame, _response = setup_adapter(
        server_version=adapter_module.OWNED_SERVER_VERSION,
        heartbeat_15d=True, self_ident_default=True,
        spawn_point_notification=spawn_point_notification,
        world_activation=world_activation, self_ident_current_length=self_ident_current_length,
        prepared_creation=prepared_creation,
        clock=lambda: 0.0)
    peer = Peer("actor-candidate")
    adapter.on_tick(peer, 2.0)
    assert not peer.sent
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(peer, b"\x01connect")
    frame.records = [Record(channel=0, payload=b"private-registration")]
    adapter.on_app(peer, b"\x02registration")
    return adapter, events, frame, peer


def test_current_length_option_is_default_off_and_requires_current_actor():
    arguments = ["--certificates", "private/certs", "--log", "private/events", "--first-light", "reference"]
    assert adapter_module.parse_options(arguments).self_ident_current_length is False
    with pytest.raises(SystemExit):
        adapter_module.parse_options(arguments + ["--self-ident-current-length"])
    with pytest.raises(ValueError, match="current default actor"):
        setup_adapter(self_ident_current_length=True)
    options = adapter_module.parse_options(arguments + ["--self-ident-current-length", "--self-ident-default",
        "--heartbeat-15d", "--server-version", adapter_module.OWNED_SERVER_VERSION])
    assert options.self_ident_current_length is True


def test_current_length_candidate_preserves_body_and_smaller_stage_prefixes():
    adapter, events, frame, peer = _ready_current_actor_candidate(
        spawn_point_notification=True, world_activation=True, self_ident_current_length=True)
    for tick in (1.0, 2.0, 3.0, 4.0):
        adapter.on_tick(peer, tick)
    fixed = [record for record in frame.marshaled if record.payload[2:6] == b"\x00\x01\x9c\x19"]
    assert len(fixed) == 1 and fixed[0].payload == b"\x83\x02" + adapter_module.current_self_ident_default.encode_default()
    candidates = [row for row in events.rows if row["event"].endswith("_SENT") and "length_prefix_variant" in row]
    assert [row["length_prefix_variant"] for row in candidates] == [
        "owned_compact_131_candidate", "pinned_leb128", "pinned_leb128", "pinned_leb128"]


@pytest.mark.parametrize("body", [bytes(131), b"\x00\x01\x9c\x19" + bytes(126),
    b"\x00\x01\x9c\x19" + bytes(126) + b"\x01"])
def test_current_length_candidate_rejects_non_default_body_without_advancing_cursors(body):
    adapter, events, _frame, peer = _ready_current_actor_candidate(self_ident_current_length=True)
    state = adapter.peers[peer.id]
    before = dict(state.__dict__)
    sent_before = len(peer.sent)
    assert adapter._send_fixed_actor_message(peer, state, body, 1628, "SELF_IDENT_DEFAULT") is False
    assert state.__dict__ == before and len(peer.sent) == sent_before
    assert events.rows[-1]["reason"] == "length_candidate_body_mismatch"


def test_current_length_candidate_does_not_apply_to_another_type_of_same_size():
    adapter, _events, frame, peer = _ready_current_actor_candidate(self_ident_current_length=True)
    state = adapter.peers[peer.id]
    body = adapter_module.current_self_ident_default.encode_default()
    assert adapter._send_fixed_actor_message(peer, state, body, 1, "OTHER_CANDIDATE") is True
    assert frame.marshaled[-1].payload == b"\x83\x01" + body


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


def _synthetic_prepared_creation():
    record = PrivateTrialCharacter(
        "11000000-0000-4000-8000-000000000001",
        "22000000-0000-4000-8000-000000000002",
        "33000000-0000-4000-8000-000000000003",
        "44000000-0000-4000-8000-000000000004",
        "Preservation", "2026-10-06T22:00:00Z",
        bytes.fromhex("0200000001000000aabbccddeeff1122"))
    table = [bytes(16)] * 3936
    table[10], table[3935] = CREATION_UUID, IDENTITY_UUID
    identity = record.identity_body()
    candidate = compose_player_creation_candidate(
        slot=0, creation_key=0, identity_key=9,
        creation_class_index=10, identity_class_index=3935,
        class_table=tuple(table), asset_id=OWNED_PLAYER_ASSET,
        assigned_gde_ref=record.gde_ref, occupied_keys=frozenset(),
        character_id=identity.character_id, character_name=identity.character_name,
        delivery_mode="resource-index")
    return PreparedPlayerCreation(record, candidate.typed_bytes,
                                  hashlib.sha256(candidate.typed_bytes).hexdigest())


def test_player_creation_is_once_after_empty_bundle_with_shared_cursors():
    prepared = _synthetic_prepared_creation()
    adapter, events, frame, peer = _ready_current_actor_candidate(
        spawn_point_notification=True, world_activation=True,
        self_ident_current_length=True, prepared_creation=prepared)
    for tick in (1.0, 2.0, 3.0, 4.0, 4.99):
        adapter.on_tick(peer, tick)
    assert not any(row["event"] == "PLAYER_CREATION_CANDIDATE_SENT" for row in events.rows)
    adapter.on_tick(peer, 5.0)
    sent = [row for row in events.rows if row["event"] == "PLAYER_CREATION_CANDIDATE_SENT"]
    assert len(sent) == 1
    assert (sent[0]["type_id"], sent[0]["typed_bytes"], sent[0]["candidate_body_bytes"]) == (
        8, len(prepared.typed_bytes), len(prepared.typed_bytes) - 3)
    state = adapter.peers[peer.id]
    assert state.creation_attempted and state.creation_sent and not state.creation_disabled
    assert frame.marshaled[-1].payload == bytes((len(prepared.typed_bytes),)) + prepared.typed_bytes
    assert frame.marshaled[-1].channel == 0 and frame.marshaled[-1].reliable
    sent_before = len(peer.sent)
    adapter.on_tick(peer, 60.0)
    assert len([row for row in events.rows if row["event"] == "PLAYER_CREATION_CANDIDATE_SENT"]) == 1
    assert all(prepared.trial_character.character_id not in str(row) for row in events.rows)
    assert len(peer.sent) >= sent_before  # Heartbeat may continue, candidate does not.
    assert not state.replies.get(5)


@pytest.mark.parametrize("corruption", ("typed_bytes", "typed_sha256"))
def test_player_creation_final_digest_guard_is_terminal_before_send(corruption):
    prepared = _synthetic_prepared_creation()
    adapter, events, frame, peer = _ready_current_actor_candidate(
        spawn_point_notification=True, world_activation=True,
        self_ident_current_length=True, prepared_creation=prepared)
    for tick in (1.0, 2.0, 3.0, 4.0):
        adapter.on_tick(peer, tick)
    state = adapter.peers[peer.id]
    assert state.bundle_sent and not state.creation_attempted
    state.next_heartbeat_at = 100.0
    before_cursors = (state.next_out_envelope_seq, state.next_ch0_seq,
                      state.next_ch0_rel, state.ack_sequence, state.acked_through)
    before_replies = {key: tuple(value) for key, value in state.replies.items()}
    before_sends, before_records = len(peer.sent), len(frame.marshaled)
    if corruption == "typed_bytes":
        changed = prepared.typed_bytes[:-1] + bytes((prepared.typed_bytes[-1] ^ 1,))
        object.__setattr__(prepared, "typed_bytes", changed)
    else:
        object.__setattr__(prepared, "typed_sha256", "0" * 64)
    for tick in (5.0, 6.0):
        adapter.on_tick(peer, tick)
    assert state.creation_attempted and state.creation_disabled and not state.creation_sent
    assert (state.next_out_envelope_seq, state.next_ch0_seq, state.next_ch0_rel,
            state.ack_sequence, state.acked_through) == before_cursors
    assert {key: tuple(value) for key, value in state.replies.items()} == before_replies
    assert len(peer.sent) == before_sends and len(frame.marshaled) == before_records
    assert [row for row in events.rows if row["event"] == "PLAYER_CREATION_CANDIDATE_REJECTED"] == [
        {"event": "PLAYER_CREATION_CANDIDATE_REJECTED", "connection_id": peer.id,
         "reason": "typed_boundary"}]
    assert not any(row["event"] == "PLAYER_CREATION_CANDIDATE_SENT" for row in events.rows)


def test_player_creation_predecessor_failure_and_exception_never_retry(monkeypatch):
    prepared = _synthetic_prepared_creation()
    adapter, events, _frame, peer = _ready_current_actor_candidate(
        spawn_point_notification=True, world_activation=True,
        self_ident_current_length=True, prepared_creation=prepared)
    for tick in (1.0, 2.0, 3.0):
        adapter.on_tick(peer, tick)
    peer.partial = True
    adapter.on_tick(peer, 4.0)
    state = adapter.peers[peer.id]
    assert state.bundle_disabled and state.creation_attempted and state.creation_disabled
    peer.partial = False
    adapter.on_tick(peer, 5.0)
    assert not any(row["event"] == "PLAYER_CREATION_CANDIDATE_SENT" for row in events.rows)

    adapter, events, _frame, peer = _ready_current_actor_candidate(
        spawn_point_notification=True, world_activation=True,
        self_ident_current_length=True, prepared_creation=prepared)
    for tick in (1.0, 2.0, 3.0, 4.0):
        adapter.on_tick(peer, tick)
    original = adapter._send_fixed_actor_message
    def fail_after_attempt(*args, **kwargs):
        if args[4] == "PLAYER_CREATION_CANDIDATE":
            raise RuntimeError("synthetic private data must not appear in logs")
        return original(*args, **kwargs)
    monkeypatch.setattr(adapter, "_send_fixed_actor_message", fail_after_attempt)
    adapter.on_tick(peer, 5.0)
    adapter.on_tick(peer, 6.0)
    assert adapter.peers[peer.id].creation_attempted
    assert len([row for row in events.rows if row["event"] == "PLAYER_CREATION_CANDIDATE_REJECTED"]) == 1
    assert "synthetic private data" not in str(events.rows)


def test_player_creation_peer_object_and_option_guards():
    prepared = _synthetic_prepared_creation()
    with pytest.raises(ValueError, match="complete current guarded"):
        setup_adapter(prepared_creation=prepared)
    adapter, events, frame, first = _ready_current_actor_candidate(
        spawn_point_notification=True, world_activation=True,
        self_ident_current_length=True, prepared_creation=prepared)
    second = Peer(first.id)
    frame.records = [Record(system_id=1, payload=b"\x01")]
    adapter.on_app(second, b"\x03connect")
    adapter.on_tick(second, 100.0)
    assert adapter._creation_peer is first and second.sent == []
    assert not adapter.peers[first.id].creation_attempted
    assert any(row["event"] == "CARRIER_REJECTED" and
               row["reason"] == "creation_lifetime_peer_limit" for row in events.rows)


def test_player_creation_cli_options_are_default_off_and_coupled():
    base = ["--certificates", "private/certs", "--log", "private/events",
            "--first-light", "reference"]
    assert adapter_module.parse_options(base).player_creation_candidate is False
    with pytest.raises(SystemExit):
        adapter_module.parse_options(base + ["--trial-character", "private/character.json"])
    required = ["--player-creation-candidate", "--server-version",
                adapter_module.OWNED_SERVER_VERSION, "--heartbeat-15d", "--self-ident-default",
                "--self-ident-current-length", "--spawn-point-notification",
                "--world-activation", "--trial-character", "private/character.json",
                "--trial-character-sha256", "0" * 64, "--type-index", "private/typeindex.json",
                "--delivery-mode", "resource-index", "--trial-known-empty-occupancy"]
    assert adapter_module.parse_options(base + required).player_creation_candidate is True
    with pytest.raises(SystemExit):
        adapter_module.parse_options(base + [value for value in required if value != "--world-activation"])
    with pytest.raises(SystemExit):
        adapter_module.parse_options(base + required[:-1])
