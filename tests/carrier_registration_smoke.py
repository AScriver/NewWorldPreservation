"""Explicit-only pinned First Light synthetic control; excluded from default pytest."""
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import carrier_registration_probe as adapter_module


class Events:
    def __init__(self):
        self.rows = []

    def emit(self, event, **fields):
        self.rows.append({"event": event, **fields})


class Peer:
    id = "synthetic"

    def __init__(self):
        self.sent = []

    def send_app(self, value):
        self.sent.append(value)
        return len(value)


def test_pinned_carrier_self_length_candidate_changes_exactly_one_final_datagram_byte():
    if os.environ.get("CARRIER_REGISTRATION_SMOKE") != "1":
        raise RuntimeError("set CARRIER_REGISTRATION_SMOKE=1 for explicit pinned smoke")
    codecs = adapter_module.load_codecs(adapter_module.REFERENCE)
    body = adapter_module.current_self_ident_default.encode_default()

    def render(option):
        events, peer = Events(), Peer()
        kwargs = {} if option is None else {"self_ident_current_length": option}
        adapter = adapter_module.RegistrationAdapter(events, codecs,
            server_version=adapter_module.OWNED_SERVER_VERSION,
            heartbeat_15d=True, self_ident_default=True, **kwargs)
        state = adapter_module._PeerState()
        state.next_out_envelope_seq = 7
        state.next_ch0_seq = state.next_ch0_rel = 2
        state.last_inbound_nonack = 9
        state.acked_through = 4
        state.ack_sequence = 12
        assert adapter._send_fixed_actor_message(peer, state, body, 1628, "SELF_IDENT_DEFAULT") is True
        return peer.sent[0], state.__dict__, events.rows[-1]

    historical, historical_state, historical_event = render(None)
    disabled, disabled_state, _ = render(False)
    candidate, candidate_state, candidate_event = render(True)
    assert historical == disabled and historical_state == disabled_state == candidate_state
    assert len(candidate) == len(historical)
    changed = [index for index, (old, new) in enumerate(zip(historical, candidate)) if old != new]
    assert len(changed) == 1
    offset = historical.index(b"\x83\x01" + body)
    assert changed == [offset + 1] and historical[offset + 1] == 1 and candidate[offset + 1] == 2
    assert candidate[offset + 2:offset + 2 + len(body)] == body
    assert historical_event["length_prefix_variant"] == "pinned_leb128"
    assert candidate_event["length_prefix_variant"] == "owned_compact_131_candidate"


def test_pinned_code_synthetic_connect_ack_round_trip():
    if os.environ.get("CARRIER_REGISTRATION_SMOKE") != "1":
        raise RuntimeError("set CARRIER_REGISTRATION_SMOKE=1 for explicit pinned smoke")
    codecs = adapter_module.load_codecs(adapter_module.REFERENCE)
    frame = codecs[0]
    events, peer = Events(), Peer()
    adapter = adapter_module.RegistrationAdapter(events, codecs)
    request = frame.MessageRecord(channel=3, payload=b"\x00\x00\x00\x05\x01",
                                  sequence=0, reliable_sequence=0, reliable=True,
                                  flags_override=0x21)
    datagram = b"\x80\x01\x00\x07" + frame.marshal_datagram([request])
    adapter.on_app(peer, datagram)
    assert len(peer.sent) == 1
    outbound_env, outbound_body = frame.parse_envelope(peer.sent[0])
    parsed = frame.parse_datagram(outbound_body)
    assert outbound_env.sequence == 7 and parsed.error is None
    assert [record.system_msg_id for record in parsed.messages] == [2, 6]
    assert "CONNECT_ACK_SENT" in [row["event"] for row in events.rows]


def test_pinned_lz4_full_body_synthetic_round_trip():
    if os.environ.get("CARRIER_REGISTRATION_SMOKE") != "1":
        raise RuntimeError("set CARRIER_REGISTRATION_SMOKE=1 for explicit pinned smoke")
    import lz4.block

    adapter_module.verify_aeternum_decoder()
    codecs = adapter_module.load_codecs(adapter_module.REFERENCE)
    frame = codecs[0]
    events, peer = Events(), Peer()
    adapter = adapter_module.RegistrationAdapter(events, codecs)
    ack = frame.MessageRecord(channel=3, payload=b"\x40\x00\x01\x00\x01\x06",
                              sequence=0, reliable_sequence=0, flags_override=0x20)
    body = frame.marshal_datagram([ack])
    compressed = lz4.block.compress(body, store_size=False)
    adapter.on_app(peer, b"\x81\x01\x00\x08" + compressed)
    assert not peer.sent  # Bare ACK never triggers an ACK reply.
    assert any(row["event"] == "CARRIER_DECOMPRESSED" and
               row["expanded_bytes"] == len(body) for row in events.rows)
    assert any(row["event"] == "CARRIER_PARSED" for row in events.rows)


def test_pinned_structural_schema_candidates_are_type_unproven():
    if os.environ.get("CARRIER_REGISTRATION_SMOKE") != "1":
        raise RuntimeError("set CARRIER_REGISTRATION_SMOKE=1 for explicit pinned smoke")
    codecs = adapter_module.load_codecs(adapter_module.REFERENCE)
    frame, _, _, wire, _, _ = codecs
    strict = bytearray(832)
    strict[0x44] = 1  # Required nonempty sdk_version_raw field.
    strict[0x45] = 0x18
    strict[0x334:] = bytes.fromhex("00430280" + "00" * 8)
    retry = b"\x00" * 32 + b"".join(
        type_id.to_bytes(4, "big") + b"\x01x" for type_id in range(6))
    for index, (body, expected_mode) in enumerate(
            ((bytes(strict), "strict"), (retry, "structured_retry"))):
        events, peer = Events(), Peer()
        peer.id = f"synthetic-{index}"
        adapter = adapter_module.RegistrationAdapter(events, codecs)
        connect = frame.MessageRecord(channel=3, payload=b"\x00\x00\x00\x05\x01",
                                      sequence=0, reliable_sequence=0, reliable=True,
                                      flags_override=0x21)
        adapter.on_app(peer, b"\x80\x01\x00\x01" + frame.marshal_datagram([connect]))
        registration = frame.MessageRecord(channel=0,
                                           payload=wire.encode_vlq32(len(body)) + body,
                                           sequence=0, reliable_sequence=0,
                                           reliable=True, flags_override=0x21)
        adapter.on_app(peer, b"\x80\x01\x00\x02" + frame.marshal_datagram([registration]))
        assert any(row["event"] == "REGISTRATION_SCHEMA_RESULT" and
                   row["parse_mode"] == expected_mode and
                   row["normalization"] == "canonical_length_prefix" and
                   row["type_unproven"] is True for row in events.rows)
        assert any(row["event"] == "V3_RESPONSE_SENT" for row in events.rows)
        assert not any("x" in str(row.get("payload", "")) for row in events.rows)


def test_pinned_one_field_version_and_carrier_ack_shape():
    if os.environ.get("CARRIER_REGISTRATION_SMOKE") != "1":
        raise RuntimeError("set CARRIER_REGISTRATION_SMOKE=1 for explicit pinned smoke")
    codecs = adapter_module.load_codecs(adapter_module.REFERENCE)
    frame, _, v3_response, _, rep, _ = codecs
    token = b"R" * 32
    historical = v3_response.encode(v3_response.V3RegistrationResponse(session_token=token))
    owned = v3_response.encode(v3_response.V3RegistrationResponse(
        session_token=token, server_version=adapter_module.OWNED_SERVER_VERSION))
    assert len(historical) == len(owned) == 88
    assert historical[:0x31] == owned[:0x31]
    assert historical[0x54:] == owned[0x54:]
    assert owned[0x31:0x54] == adapter_module.OWNED_SERVER_VERSION.encode("ascii")
    events, peer = Events(), Peer()
    ack_record = rep.build_sm_ct_acks_record(0, 0x1234, None)
    adapter_module.RegistrationAdapter(events, codecs).on_app(
        peer, b"\x80\x01\x00\x09" + ack_record)
    assert not peer.sent
    assert {"event": "CLIENT_CARRIER_ACK_RANGE", "connection_id": "synthetic",
            "envelope_sequence": 9, "last_to_ack": 0x1234,
            "first_to_ack": 0x1234} in events.rows
    assert frame.parse_datagram(ack_record).error is None


def test_pinned_generated_heartbeat_and_local_echo_round_trip():
    if os.environ.get("CARRIER_REGISTRATION_SMOKE") != "1":
        raise RuntimeError("set CARRIER_REGISTRATION_SMOKE=1 for explicit pinned smoke")
    codecs = adapter_module.load_codecs(adapter_module.REFERENCE)
    frame, _, _, wire, _, dispatch = codecs
    heartbeat = dispatch.heartbeat_15d
    events, peer = Events(), Peer()
    adapter = adapter_module.RegistrationAdapter(
        events, codecs, heartbeat_15d=True, clock=lambda: 0.0)
    connect = frame.MessageRecord(channel=3, payload=b"\x00\x00\x00\x05\x01",
                                  sequence=0, reliable_sequence=0, reliable=True,
                                  flags_override=0x21)
    adapter.on_app(peer, b"\x80\x01\x00\x01" + frame.marshal_datagram([connect]))
    retry = b"\x00" * 32 + b"".join(
        type_id.to_bytes(4, "big") + b"\x01x" for type_id in range(6))
    registration = frame.MessageRecord(channel=0,
                                       payload=wire.encode_vlq32(len(retry)) + retry,
                                       sequence=0, reliable_sequence=0,
                                       reliable=True, flags_override=0x21)
    adapter.on_app(peer, b"\x80\x01\x00\x02" + frame.marshal_datagram([registration]))
    assert adapter.peers[peer.id].v3_sent
    adapter.on_tick(peer, 0.49)
    assert len(peer.sent) == 2
    adapter.on_tick(peer, 0.5)
    envelope, payload = frame.parse_envelope(peer.sent[-1])
    records = frame.parse_datagram(payload)
    assert envelope.sequence == 3 and records.error is None
    assert len(records.messages) == 1
    record = records.messages[0]
    assert record.channel == 0 and record.flags == 0x21
    assert (record.sequence, record.reliable_sequence) == (1, 1)
    assert record.payload[:1] == wire.encode_vlq32(12)
    ping = heartbeat.decode_ping(record.payload[1:])
    ack_body = heartbeat.encode_ack(heartbeat.make_ack_for(ping, client_hash=b"ABCD"))
    for wrapped in (ack_body, wire.encode_vlq32(len(ack_body)) + ack_body,
                    wire.serialize_cs_envelope(bytes(16), ack_body)):
        parsed_ack = adapter._heartbeat_ack(wrapped)
        assert parsed_ack is not None
        assert parsed_ack[1] == (ping.counter, ping.nonce)
    client_ack = frame.MessageRecord(channel=0, payload=ack_body, sequence=1,
                                     reliable_sequence=1, reliable=True, flags_override=0x21)
    adapter.on_app(peer, b"\x80\x01\x00\x03" + frame.marshal_datagram([client_ack]))
    assert any(row["event"] == "HEARTBEAT_15D_ACK" and
               row["matched_local_ping"] is True for row in events.rows)
    assert "ABCD" not in str(events.rows)


def test_pinned_framing_carries_current_default_actor_after_heartbeat():
    if os.environ.get("CARRIER_REGISTRATION_SMOKE") != "1":
        raise RuntimeError("set CARRIER_REGISTRATION_SMOKE=1 for explicit pinned smoke")
    codecs = adapter_module.load_codecs(adapter_module.REFERENCE)
    frame, _, _, wire, _, _ = codecs
    events, peer = Events(), Peer()
    adapter = adapter_module.RegistrationAdapter(
        events, codecs, server_version=adapter_module.OWNED_SERVER_VERSION,
        heartbeat_15d=True, self_ident_default=True,
        spawn_point_notification=True, world_activation=True, clock=lambda: 0.0)
    connect = frame.MessageRecord(channel=3, payload=b"\x00\x00\x00\x05\x01",
                                  sequence=0, reliable_sequence=0, reliable=True,
                                  flags_override=0x21)
    adapter.on_app(peer, b"\x80\x01\x00\x01" + frame.marshal_datagram([connect]))
    retry = bytes(32) + b"".join(type_id.to_bytes(4, "big") + b"\x01x" for type_id in range(6))
    registration = frame.MessageRecord(channel=0,
                                       payload=wire.encode_vlq32(len(retry)) + retry,
                                       sequence=0, reliable_sequence=0,
                                       reliable=True, flags_override=0x21)
    adapter.on_app(peer, b"\x80\x01\x00\x02" + frame.marshal_datagram([registration]))
    adapter.on_tick(peer, 0.5)
    adapter.on_tick(peer, 1.0)
    envelope, payload = frame.parse_envelope(peer.sent[-2])
    parsed = frame.parse_datagram(payload)
    assert envelope.sequence == 4 and parsed.error is None
    record = parsed.messages[0]
    assert (record.channel, record.flags, record.sequence, record.reliable_sequence) == (0, 0x21, 2, 2)
    prefix = wire.encode_vlq32(131)
    assert record.payload == prefix + b"\x00\x01\x9c\x19" + bytes(127)
    adapter.on_tick(peer, 2.0)
    spawn_envelope, spawn_payload = frame.parse_envelope(peer.sent[-2])
    spawn_parsed = frame.parse_datagram(spawn_payload)
    assert spawn_envelope.sequence == 6 and spawn_parsed.error is None
    spawn_record = spawn_parsed.messages[0]
    assert (spawn_record.channel, spawn_record.flags, spawn_record.sequence, spawn_record.reliable_sequence) == (0, 0x21, 4, 4)
    assert spawn_record.payload == wire.encode_vlq32(4) + b"\x00\x01\x91\x19"
    adapter.on_tick(peer, 3.0)
    level_envelope, level_payload = frame.parse_envelope(peer.sent[-2])
    level_parsed = frame.parse_datagram(level_payload)
    assert level_envelope.sequence == 8 and level_parsed.error is None
    level_record = level_parsed.messages[0]
    assert (level_record.channel, level_record.flags, level_record.sequence, level_record.reliable_sequence) == (0, 0x21, 6, 6)
    assert level_record.payload == wire.encode_vlq32(63) + adapter_module.current_world_activation.encode_level_info_candidate()
    adapter.on_tick(peer, 4.0)
    bundle_envelope, bundle_payload = frame.parse_envelope(peer.sent[-2])
    bundle_parsed = frame.parse_datagram(bundle_payload)
    assert bundle_envelope.sequence == 10 and bundle_parsed.error is None
    bundle_record = bundle_parsed.messages[0]
    assert (bundle_record.channel, bundle_record.flags, bundle_record.sequence, bundle_record.reliable_sequence) == (0, 0x21, 8, 8)
    assert bundle_record.payload == wire.encode_vlq32(9) + b"\x00\x01\x08" + bytes(6)
    adapter.on_tick(peer, 5.0)
    assert sum(row["event"] == "SELF_IDENT_DEFAULT_SENT" for row in events.rows) == 1
    assert sum(row["event"] == "SPAWN_POINT_NOTIFICATION_SENT" for row in events.rows) == 1
    assert sum(row["event"] == "LEVEL_INFO_CANDIDATE_SENT" for row in events.rows) == 1
    assert sum(row["event"] == "EMPTY_STATE_BUNDLE_SENT" for row in events.rows) == 1
