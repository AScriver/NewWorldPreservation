"""Bounded IPv4 loopback DTLS diagnostic; no game authentication or responses.

The server does not authenticate client certificates. A completed server handshake
does not prove that a client accepted this server or entered a world.
"""
import argparse
import json
import socket
import threading
import time
import uuid
from pathlib import Path

from OpenSSL import SSL
from cryptography import x509
from cryptography.hazmat.primitives import hashes

from connectivity_probe import EventLog, private_directory
from udp_handoff_probe import header_metadata
from windows_udp_owner import owner_of_bound_port


MAX_PEERS = 8
MAX_DATAGRAMS = 512
MAX_PEER_DATAGRAMS = 128
MAX_HANDSHAKE_SECONDS = 20
MAX_IDLE_SECONDS = 30
MAX_APP_BYTES = 4096
ALERTS = {0: "close_notify", 20: "bad_record_mac", 40: "handshake_failure",
          42: "bad_certificate", 43: "unsupported_certificate", 44: "certificate_revoked",
          45: "certificate_expired", 46: "certificate_unknown", 47: "illegal_parameter",
          48: "unknown_ca", 49: "access_denied", 70: "protocol_version",
          71: "insufficient_security", 80: "internal_error", 90: "user_canceled",
          100: "no_renegotiation", 112: "unrecognized_name"}
REASONS = {"unknown ca", "certificate verify failed", "bad certificate", "handshake failure",
           "unsupported protocol", "no shared cipher", "wrong version number", "unexpected message",
           "decryption failed or bad record mac", "bad record mac"}


def _failure(error):
    kind = type(error).__name__
    if kind not in {"Error", "SysCallError", "ZeroReturnError", "WantReadError", "WantWriteError"}:
        kind = "other"
    reasons = set()
    for item in getattr(error, "args", ()):
        if isinstance(item, (list, tuple)):
            for detail in item:
                if isinstance(detail, (list, tuple)) and detail and isinstance(detail[-1], str):
                    reasons.add(detail[-1].lower())
    return kind, next(iter(sorted(reasons & REASONS)), "other")


def _state_class(value):
    state = value.decode("ascii", errors="ignore").lower()
    for word in ("client hello", "server hello", "certificate", "key exchange", "finished"):
        if word in state:
            return word.replace(" ", "_")
    return "other"


def _socket_error(error):
    kind = type(error).__name__
    code = getattr(error, "winerror", None)
    if not isinstance(code, int):
        code = getattr(error, "errno", None)
    return {"error_class": kind if kind in {"ConnectionResetError", "OSError"} else "other",
            "error_code": code if isinstance(code, int) else None}


class Peer:
    def __init__(self, server, address):
        self.server, self.address = server, address
        self.id = str(uuid.uuid4())
        self.connection = SSL.Connection(server.context, None)
        self.connection.set_accept_state()
        self.created = self.last_seen = time.monotonic()
        self.packets = 0
        self.established = False
        self.state = None

    def send_app(self, data):
        """Send a caller-provided inert application message after negotiation."""
        if not self.established or not isinstance(data, bytes) or not 0 < len(data) <= MAX_APP_BYTES:
            raise ValueError("Established peer and bounded bytes required")
        sent = self.connection.send(data)
        return sent if self.server._drain(self) else 0


class Responder:
    def __init__(self, certificates, events, *, port=64003, chain="full",
                 lookup=owner_of_bound_port, on_app=None, on_tick=None,
                 max_datagrams=MAX_DATAGRAMS, max_peer_datagrams=MAX_PEER_DATAGRAMS,
                 max_lifetime_peers=None):
        if not 0 <= port <= 65535 or chain not in ("full", "leaf"):
            raise ValueError("Invalid port or chain mode")
        if (type(max_datagrams) is not int or not 1 <= max_datagrams <= 4096 or
                type(max_peer_datagrams) is not int or not 1 <= max_peer_datagrams <= 2048 or
                max_peer_datagrams > max_datagrams):
            raise ValueError("Invalid bounded datagram limits")
        if (max_lifetime_peers is not None and
                (type(max_lifetime_peers) is not int or not 1 <= max_lifetime_peers <= MAX_PEERS)):
            raise ValueError("Invalid lifetime peer admission limit")
        self.max_datagrams, self.max_peer_datagrams = max_datagrams, max_peer_datagrams
        self.max_lifetime_peers = max_lifetime_peers
        self.lifetime_peer_admissions = 0
        directory = Path(certificates)
        manifest = json.loads((directory / "certificate-manifest.json").read_text(encoding="utf-8"))
        leaf = x509.load_pem_x509_certificate((directory / "server.pem").read_bytes())
        root = x509.load_pem_x509_certificate((directory / "ca.pem").read_bytes())
        self.leaf_fingerprint = leaf.fingerprint(hashes.SHA256()).hex()
        self.root_fingerprint = root.fingerprint(hashes.SHA256()).hex()
        if (self.leaf_fingerprint != manifest["leaf_sha256"] or
                self.root_fingerprint != manifest["ca_sha256"]):
            raise ValueError("Certificate manifest fingerprint mismatch")
        self.allowed_names = {name.encode("ascii").lower() for name in manifest["dns_sans"]}
        self.context = SSL.Context(SSL.DTLS_SERVER_METHOD)
        self.context.use_certificate_file(str(directory / "server.pem"))
        self.context.use_privatekey_file(str(directory / "server.key"))
        self.context.check_privatekey()
        self.context.set_cipher_list(b"ECDHE-RSA-AES256-GCM-SHA384")
        self.context.set_verify(SSL.VERIFY_NONE, lambda *_: True)
        if chain == "full":
            self.context.add_extra_chain_cert(root)
        self.context.set_info_callback(self._info)
        self.context.set_tlsext_servername_callback(self._sni)
        self.events, self.lookup, self.on_app, self.on_tick = events, lookup, on_app, on_tick
        self.chain = chain
        self.peers = {}
        self.by_connection = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind(("127.0.0.1", port))
        except BaseException:
            self.socket.close()
            raise
        self.address = self.socket.getsockname()

    def _info(self, connection, where, result):
        peer = self.by_connection.get(connection)
        if peer is None:
            return
        if where & SSL.SSL_CB_ALERT:
            self.events.emit("DTLS_ALERT", connection_id=peer.id,
                             direction="read" if where & SSL.SSL_CB_READ else "write",
                             level={1: "warning", 2: "fatal"}.get((result >> 8) & 255, "other"),
                             description=ALERTS.get(result & 255, "other"))
        if where & (SSL.SSL_CB_LOOP | SSL.SSL_CB_HANDSHAKE_START | SSL.SSL_CB_HANDSHAKE_DONE):
            state = connection.get_state_string()
            if state != peer.state:
                peer.state = state
                self.events.emit("DTLS_HANDSHAKE_STATE", connection_id=peer.id,
                                 state_class=_state_class(state))

    def _sni(self, connection):
        peer = self.by_connection.get(connection)
        if peer is None:
            return
        name = connection.get_servername()
        self.events.emit("DTLS_SNI", connection_id=peer.id, present=name is not None,
                         name_class="allowlisted" if name and name.lower() in self.allowed_names else "other")

    def _drain(self, peer):
        while True:
            try:
                output = peer.connection.bio_read(65535)
            except SSL.WantReadError:
                return True
            if not output:
                return True
            try:
                self.socket.sendto(output, peer.address)
            except OSError as error:
                self.events.emit("DTLS_SOCKET_FAILURE", connection_id=peer.id,
                                 direction="send", peer_attributed=True, **_socket_error(error))
                self._close_peer(peer, "send_failure")
                return False
            self.events.emit("DTLS_SERVER_OUTPUT", connection_id=peer.id, datagram_bytes=len(output))

    def _close_peer(self, peer, reason):
        if self.peers.pop(peer.address, None) is None:
            return
        self.by_connection.pop(peer.connection, None)
        self.events.emit("DTLS_PEER_CLOSED", connection_id=peer.id, reason=reason,
                         handshake_established=peer.established)

    def _advance(self, peer):
        connection = peer.connection
        try:
            if not peer.established:
                connection.do_handshake()
                peer.established = True
                self.events.emit("DTLS_HANDSHAKE_ESTABLISHED", connection_id=peer.id,
                                 cipher=connection.get_cipher_name(),
                                 protocol=connection.get_protocol_version_name(),
                                 client_acceptance_proven=False, client_certificate_authenticated=False)
            if peer.established:
                while True:
                    try:
                        plaintext = connection.recv(MAX_APP_BYTES)
                    except SSL.WantReadError:
                        break
                    if not plaintext:
                        self._close_peer(peer, "remote_close")
                        break
                    self.events.emit("DTLS_APPLICATION_DISCARDED", connection_id=peer.id,
                                     plaintext_bytes=len(plaintext))
                    if self.on_app is not None:
                        self.on_app(peer, plaintext)
        except (SSL.WantReadError, SSL.WantWriteError):
            pass
        except (SSL.Error, SSL.SysCallError, SSL.ZeroReturnError) as error:
            kind, reason = _failure(error)
            self.events.emit("DTLS_FAILURE", connection_id=peer.id, error_class=kind, openssl_reason=reason)
            self._close_peer(peer, "openssl_failure")
        finally:
            self._drain(peer)

    def run(self, seconds, stop=None):
        if not 0 < seconds <= 600:
            self.socket.close()
            raise ValueError("Duration must be 1..600 seconds")
        stop = stop if stop is not None else threading.Event()
        deadline = time.monotonic() + seconds
        count = 0
        self.events.emit("DTLS_PROBE_LISTENING", bind=self.address[0], port=self.address[1],
                         chain=self.chain, configured_leaf_sha256=self.leaf_fingerprint,
                         configured_chain_root_sha256=self.root_fingerprint if self.chain == "full" else None,
                         client_certificate_authenticated=False, game_authentication=False,
                         world_entry=False, max_datagrams=self.max_datagrams,
                         max_peer_datagrams=self.max_peer_datagrams)
        try:
            while not stop.is_set() and time.monotonic() < deadline and count < self.max_datagrams:
                now = time.monotonic()
                for peer in list(self.peers.values()):
                    if now - peer.created >= MAX_HANDSHAKE_SECONDS and not peer.established:
                        self._close_peer(peer, "handshake_deadline")
                    elif now - peer.last_seen >= MAX_IDLE_SECONDS:
                        self._close_peer(peer, "idle_deadline")
                    else:
                        timeout = peer.connection.DTLSv1_get_timeout()
                        if timeout is not None and timeout <= 0:
                            try:
                                fired = peer.connection.DTLSv1_handle_timeout()
                                self.events.emit("DTLS_TIMER", connection_id=peer.id, retransmitted=fired)
                                self._drain(peer)
                            except SSL.Error as error:
                                kind, reason = _failure(error)
                                self.events.emit("DTLS_FAILURE", connection_id=peer.id,
                                                 error_class=kind, openssl_reason=reason)
                                self._close_peer(peer, "timer_failure")
                    if (peer.established and self.on_tick is not None and
                            self.peers.get(peer.address) is peer):
                        try:
                            self.on_tick(peer, now)
                        except Exception:
                            self.events.emit("DTLS_TICK_FAILURE", connection_id=peer.id,
                                             reason="application_tick_failure")
                            self._close_peer(peer, "tick_failure")
                try:
                    self.socket.settimeout(min(0.05, max(0.001, deadline - time.monotonic())))
                    data, address = self.socket.recvfrom(65535)
                except socket.timeout:
                    continue
                except ConnectionResetError as error:
                    self.events.emit("DTLS_SOCKET_FAILURE", direction="receive",
                                     peer_attributed=False, recoverable=True, **_socket_error(error))
                    continue
                except OSError as error:
                    self.events.emit("DTLS_SOCKET_FAILURE", direction="receive",
                                     peer_attributed=False, recoverable=False, **_socket_error(error))
                    break
                if address[0] != "127.0.0.1":
                    continue
                count += 1
                peer = self.peers.get(address)
                metadata = header_metadata(data)
                if peer is None:
                    if (metadata["datagram_class"] != "dtls_client_hello_header" or
                            len(self.peers) >= MAX_PEERS or
                            (self.max_lifetime_peers is not None and
                             self.lifetime_peer_admissions >= self.max_lifetime_peers)):
                        self.events.emit("DTLS_DATAGRAM_REFUSED", reason="unclassified_or_capacity",
                                         datagram_bytes=len(data))
                        continue
                    peer = Peer(self, address)
                    self.lifetime_peer_admissions += 1
                    self.peers[address] = peer
                    self.by_connection[peer.connection] = peer
                    self.events.emit("DTLS_PEER_OPENED", connection_id=peer.id,
                                     peer={"address":address[0], "port":address[1]})
                peer.packets += 1
                peer.last_seen = time.monotonic()
                self.events.emit("DTLS_DATAGRAM_RECEIVED", connection_id=peer.id,
                                 datagram_bytes=len(data), process_id=self.lookup(*address),
                                 owner_basis="IPv4_bound_endpoint_owner_not_exact_flow", **metadata)
                if peer.packets > self.max_peer_datagrams:
                    self._close_peer(peer, "packet_limit")
                    continue
                try:
                    if peer.connection.bio_write(data) != len(data):
                        raise ValueError("Incomplete BIO write")
                    self._advance(peer)
                except (SSL.Error, ValueError) as error:
                    kind, reason = _failure(error)
                    self.events.emit("DTLS_FAILURE", connection_id=peer.id,
                                     error_class=kind, openssl_reason=reason)
                    self._close_peer(peer, "bio_failure")
        finally:
            for peer in list(self.peers.values()):
                self._close_peer(peer, "probe_stopped")
            self.socket.close()
            self.events.emit("DTLS_PROBE_STOPPED", received_datagrams=count,
                             sockets_closed=True, remaining_peers=len(self.peers))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--port", type=int, default=64003)
    parser.add_argument("--duration", type=int, default=600)
    parser.add_argument("--chain", choices=("full", "leaf"), default="full")
    options = parser.parse_args()
    if not 1 <= options.port <= 65535 or not 1 <= options.duration <= 600:
        parser.error("Port 1..65535 and duration 1..600 required")
    directory = private_directory(options.certificates)
    path = private_directory(options.log)
    path.parent.mkdir(parents=True, exist_ok=True)
    events = EventLog(path)
    try:
        Responder(directory, events, port=options.port, chain=options.chain).run(options.duration)
    finally:
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
