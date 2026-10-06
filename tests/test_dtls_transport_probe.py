import json
import socket
import sys
import threading
import time
from types import SimpleNamespace
import warnings
from pathlib import Path
from unittest.mock import Mock

import pytest
from OpenSSL import SSL

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from connectivity_probe import EventLog, generate_certificates
from dtls_transport_probe import MAX_PEERS, Responder


@pytest.fixture
def certdir(tmp_path):
    directory = tmp_path / "certificates"
    generate_certificates(directory, ["localhost"])
    return directory


def _client(certdir, wrong_ca=None):
    context = SSL.Context(SSL.DTLS_CLIENT_METHOD)
    context.set_cipher_list(b"ECDHE-RSA-AES256-GCM-SHA384")
    context.load_verify_locations(str((wrong_ca or certdir) / "ca.pem"))
    context.set_verify(SSL.VERIFY_PEER, lambda _conn, _cert, _errno, _depth, okay: okay)
    connection = SSL.Connection(context, None)
    connection.set_connect_state()
    connection.set_tlsext_host_name(b"localhost")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    sock.setblocking(False)
    return sock, connection, context


def _drain(connection, sock, destination):
    while True:
        try:
            wire = connection.bio_read(65535)
        except SSL.WantReadError:
            return
        sock.sendto(wire, destination)


def _exchange(clients, destination, *, payload=None, limit=5):
    complete = set()
    rejected = set()
    received = {}
    sent = set()
    deadline = time.monotonic() + limit
    while time.monotonic() < deadline:
        for index, (sock, connection, _context) in enumerate(clients):
            if index not in complete | rejected:
                try:
                    connection.do_handshake()
                    complete.add(index)
                except SSL.WantReadError:
                    pass
                except SSL.Error:
                    rejected.add(index)
            if index in complete and payload is not None and index not in sent:
                connection.send(payload + bytes([index]))
                sent.add(index)
            _drain(connection, sock, destination)
            while True:
                try:
                    wire, _ = sock.recvfrom(65535)
                except BlockingIOError:
                    break
                connection.bio_write(wire)
                if index in complete:
                    try:
                        received[index] = connection.recv(4096)
                    except SSL.WantReadError:
                        pass
                    except SSL.Error:
                        rejected.add(index)
            _drain(connection, sock, destination)
        if (len(complete) + len(rejected) == len(clients) and
                (payload is None or len(received) + len(rejected) == len(clients))):
            break
        time.sleep(0.002)
    return complete, rejected, received


def _run(tmp_path, certdir, *, trusted=True, peers=1, payload=None, chain="full"):
    path = tmp_path / "events.jsonl"
    events = EventLog(path)
    stop = threading.Event()
    server = Responder(certdir, events, port=0, chain=chain, lookup=lambda *_: 4321,
                       on_app=(lambda peer, data: peer.send_app(b"reply:" + data)) if payload else None)
    thread = threading.Thread(target=server.run, args=(6, stop))
    wrong_ca = None
    if not trusted:
        wrong_ca = tmp_path / "unrelated-ca"
        generate_certificates(wrong_ca, ["unrelated.example"])
    clients = [_client(certdir, wrong_ca) for _ in range(peers)]
    thread.start()
    try:
        outcome = _exchange(clients, server.address, payload=payload)
        if not trusted:
            deadline = time.monotonic() + 1
            while '"state": "DTLS_ALERT"' not in path.read_text() and time.monotonic() < deadline:
                time.sleep(0.005)
    finally:
        stop.set()
        thread.join(timeout=3)
        for sock, _, _ in clients:
            sock.close()
        events.close()
    assert not thread.is_alive()
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert records[-1]["state"] == "DTLS_PROBE_STOPPED"
    assert records[-1]["remaining_peers"] == 0 and server.socket.fileno() == -1
    return outcome, records


def test_two_independent_verified_peers_exchange_and_discard_secret(tmp_path, certdir):
    secret = b"SYNTHETIC-SECRET-DO-NOT-RETAIN"
    (complete, rejected, received), records = _run(tmp_path, certdir, peers=2, payload=secret)
    assert complete == {0, 1} and not rejected
    assert received == {0: b"reply:" + secret + b"\x00",
                        1: b"reply:" + secret + b"\x01"}
    established = [item for item in records if item["state"] == "DTLS_HANDSHAKE_ESTABLISHED"]
    assert len(established) == 2 and len({item["connection_id"] for item in established}) == 2
    assert all(item["client_acceptance_proven"] is False for item in established)
    assert sum(item["plaintext_bytes"] for item in records
               if item["state"] == "DTLS_APPLICATION_DISCARDED") == 2 * (len(secret) + 1)
    assert secret.decode() not in json.dumps(records)
    assert any(item["state"] == "DTLS_SNI" and item["name_class"] == "allowlisted"
               for item in records)
    assert "localhost" not in json.dumps(records)
    assert all(item["owner_basis"] == "IPv4_bound_endpoint_owner_not_exact_flow"
               for item in records if item["state"] == "DTLS_DATAGRAM_RECEIVED")


def test_established_peer_tick_runs_without_inbound_datagrams_on_fake_clock(
        tmp_path, certdir, monkeypatch):
    import dtls_transport_probe as probe_module

    clock = [0.0]
    monkeypatch.setattr(probe_module.time, "monotonic", lambda: clock[0])
    stop = threading.Event()
    ticks = []

    def on_tick(peer, now):
        ticks.append((peer.id, now))
        clock[0] += 0.5
        if len(ticks) == 3:
            stop.set()

    path = tmp_path / "tick-events.jsonl"
    events = EventLog(path)
    server = Responder(certdir, events, port=0, on_tick=on_tick)
    real_socket = server.socket
    real_socket.close()
    fake_socket = Mock()
    fake_socket.recvfrom.side_effect = socket.timeout
    server.socket = fake_socket
    connection = Mock()
    connection.DTLSv1_get_timeout.return_value = None
    peer = SimpleNamespace(id="owned-synthetic", address=("127.0.0.1", 10001),
                           connection=connection, established=True, created=0.0,
                           last_seen=0.0)
    server.peers[peer.address] = peer
    server.by_connection[connection] = peer
    server.run(5, stop)
    events.close()
    assert ticks == [("owned-synthetic", 0.0), ("owned-synthetic", 0.5),
                     ("owned-synthetic", 1.0)]
    assert fake_socket.recvfrom.call_count == 3 and not server.peers
    assert "DTLS_TICK_FAILURE" not in path.read_text()


def test_wrong_ca_client_rejects_and_no_application_exchange(tmp_path, certdir):
    (complete, rejected, received), records = _run(tmp_path, certdir, trusted=False)
    assert rejected == {0} and not complete and not received
    assert not any(item["state"] == "DTLS_APPLICATION_DISCARDED" for item in records)
    assert any(item["state"] == "DTLS_ALERT" and item["direction"] == "read"
               and item["level"] == "fatal"
               and item["description"] == "unknown_ca" for item in records)
    assert "-----BEGIN" not in json.dumps(records) and "localhost" not in json.dumps(records)


def test_leaf_chain_mode_and_refused_non_hello(tmp_path, certdir):
    path = tmp_path / "events.jsonl"
    events = EventLog(path)
    server = Responder(certdir, events, port=0, chain="leaf", lookup=lambda *_: None)
    stop = threading.Event()
    thread = threading.Thread(target=server.run, args=(3, stop))
    thread.start()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(b"SYNTHETIC-SECRET-DO-NOT-RETAIN", server.address)
        time.sleep(0.1)
    finally:
        stop.set()
        thread.join(timeout=3)
        events.close()
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert any(item["state"] == "DTLS_DATAGRAM_REFUSED" for item in records)
    listening = next(item for item in records if item["state"] == "DTLS_PROBE_LISTENING")
    assert listening["configured_leaf_sha256"] == json.loads(
        (certdir / "certificate-manifest.json").read_text())["leaf_sha256"]
    assert listening["configured_chain_root_sha256"] is None
    assert "SYNTHETIC-SECRET" not in json.dumps(records)


def test_bounds_and_fixed_loopback_bind(tmp_path, certdir):
    events = EventLog(tmp_path / "events.jsonl")
    try:
        with pytest.raises(ValueError):
            Responder(certdir, events, port=-1)
        with pytest.raises(ValueError):
            Responder(certdir, events, port=0, chain="invalid")
        for total, per_peer in ((0, 1), (4097, 1), (4096, 2049), (1, 2), (True, 1)):
            with pytest.raises(ValueError):
                Responder(certdir, events, port=0, max_datagrams=total,
                          max_peer_datagrams=per_peer)
        for lifetime_cap in (0, MAX_PEERS + 1, True, 1.0):
            with pytest.raises(ValueError, match="lifetime"):
                Responder(certdir, events, port=0, max_lifetime_peers=lifetime_cap)
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            server = Responder(certdir, events, port=0)
        assert server.address[0] == "127.0.0.1"
        assert server.max_lifetime_peers is None
        with pytest.raises(ValueError):
            server.run(601)
        assert server.socket.fileno() == -1
    finally:
        events.close()
    assert MAX_PEERS == 8


def test_selected_datagram_budget_stops_and_closes_socket(tmp_path, certdir):
    path = tmp_path / "budget.jsonl"
    events = EventLog(path)
    server = Responder(certdir, events, port=0, max_datagrams=3, max_peer_datagrams=2)
    thread = threading.Thread(target=server.run, args=(3,))
    thread.start()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            for _ in range(3):
                sock.sendto(b"SYNTHETIC-SECRET-DO-NOT-RETAIN", server.address)
        thread.join(timeout=3)
        assert not thread.is_alive()
    finally:
        thread.join(timeout=4)
        events.close()
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert records[0]["max_datagrams"] == 3
    assert records[0]["max_peer_datagrams"] == 2
    assert records[-1]["received_datagrams"] == 3
    assert records[-1]["sockets_closed"] and server.socket.fileno() == -1
    assert "SYNTHETIC-SECRET" not in path.read_text()


def test_retransmission_timer_and_peer_capacity(tmp_path, certdir):
    path = tmp_path / "events.jsonl"
    events = EventLog(path)
    server = Responder(certdir, events, port=0, lookup=lambda *_: None)
    stop = threading.Event()
    thread = threading.Thread(target=server.run, args=(4, stop))
    clients = [_client(certdir) for _ in range(MAX_PEERS + 1)]
    thread.start()
    try:
        for sock, connection, _context in clients:
            with pytest.raises(SSL.WantReadError):
                connection.do_handshake()
            _drain(connection, sock, server.address)
        # Ignore server flights so each incomplete handshake needs its timer.
        time.sleep(1.3)
    finally:
        stop.set()
        thread.join(timeout=3)
        for sock, _, _ in clients:
            sock.close()
        events.close()
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert len([item for item in records if item["state"] == "DTLS_PEER_OPENED"]) == MAX_PEERS
    assert any(item["state"] == "DTLS_DATAGRAM_REFUSED" for item in records)
    assert any(item["state"] == "DTLS_TIMER" and item["retransmitted"] for item in records)
    assert records[-1]["remaining_peers"] == 0 and server.socket.fileno() == -1


def test_one_lifetime_peer_refuses_later_client_hello_after_close(tmp_path, certdir):
    path = tmp_path / "lifetime-events.jsonl"
    events = EventLog(path)
    server = Responder(certdir, events, port=0, max_lifetime_peers=1,
                       lookup=lambda *_: None)
    stop = threading.Event()
    thread = threading.Thread(target=server.run, args=(3, stop))
    first = _client(certdir)
    second = _client(certdir)
    thread.start()
    try:
        complete, _, _ = _exchange([first], server.address, limit=2)
        assert complete == {0}
        assert server.lifetime_peer_admissions == 1
        admitted = next(iter(server.peers.values()))
        server._close_peer(admitted, "synthetic_test_close")
        assert not server.peers
        complete_again, _, _ = _exchange([second], server.address, limit=0.5)
        assert not complete_again
        assert server.lifetime_peer_admissions == 1
    finally:
        stop.set()
        thread.join(timeout=3)
        first[0].close()
        second[0].close()
        events.close()
    assert not thread.is_alive() and server.socket.fileno() == -1
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert len([row for row in records if row["state"] == "DTLS_PEER_OPENED"]) == 1
    assert any(row["state"] == "DTLS_DATAGRAM_REFUSED" for row in records)


def test_receive_reset_is_unattributed_then_fatal_socket_error_stops_cleanly(tmp_path, certdir):
    path = tmp_path / "events.jsonl"
    events = EventLog(path)
    server = Responder(certdir, events, port=0)
    actual_socket = server.socket
    server.socket = Mock(wraps=actual_socket)
    server.socket.recvfrom.side_effect = [ConnectionResetError(10054, "SECRET-RESET"),
                                         OSError(10055, "SECRET-FATAL")]
    try:
        server.run(2)
    finally:
        events.close()
    records = [json.loads(line) for line in path.read_text().splitlines()]
    failures = [item for item in records if item["state"] == "DTLS_SOCKET_FAILURE"]
    assert [(item["error_code"], item["recoverable"], item["peer_attributed"])
            for item in failures] == [(10054, True, False), (10055, False, False)]
    assert all(item["connection_id"] is None and item["direction"] == "receive" for item in failures)
    assert actual_socket.fileno() == -1 and records[-1]["state"] == "DTLS_PROBE_STOPPED"
    assert "SECRET-" not in json.dumps(records)


def test_send_error_closes_only_affected_peer_and_cleans_up(tmp_path, certdir):
    path = tmp_path / "events.jsonl"
    events = EventLog(path)
    server = Responder(certdir, events, port=0)
    actual_socket = server.socket
    server.socket = Mock(wraps=actual_socket)
    stop = threading.Event()
    thread = threading.Thread(target=server.run, args=(3, stop))
    bad_sock, bad_connection, _context = _client(certdir)
    good_client = _client(certdir)

    def sendto(data, destination):
        if destination == bad_sock.getsockname():
            raise OSError(10055, "SECRET-SEND")
        return actual_socket.sendto(data, destination)

    server.socket.sendto.side_effect = sendto
    thread.start()
    try:
        with pytest.raises(SSL.WantReadError):
            bad_connection.do_handshake()
        _drain(bad_connection, bad_sock, server.address)
        deadline = time.monotonic() + 1
        while '"reason": "send_failure"' not in path.read_text() and time.monotonic() < deadline:
            time.sleep(0.005)
        complete, rejected, _ = _exchange([good_client], server.address, limit=2)
    finally:
        stop.set()
        thread.join(timeout=3)
        bad_sock.close()
        good_client[0].close()
        events.close()
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert complete == {0} and not rejected
    failure = next(item for item in records if item["state"] == "DTLS_SOCKET_FAILURE")
    assert failure["direction"] == "send" and failure["peer_attributed"]
    assert failure["connection_id"] and failure["error_code"] == 10055
    assert any(item["state"] == "DTLS_PEER_CLOSED" and item["reason"] == "send_failure"
               and item["connection_id"] == failure["connection_id"] for item in records)
    assert any(item["state"] == "DTLS_HANDSHAKE_ESTABLISHED"
               and item["connection_id"] != failure["connection_id"] for item in records)
    assert actual_socket.fileno() == -1 and records[-1]["remaining_peers"] == 0
    assert "SECRET-SEND" not in json.dumps(records)
