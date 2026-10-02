"""Receive-only loopback handoff observer; payloads discarded, no game protocol.

DTLS header classification only: RFC6347 sections4.1/4.2.2. No negotiation,
certificate validation, credential capture, registration or gameplay response.
https://www.rfc-editor.org/rfc/rfc6347.html
"""
import argparse
import ipaddress
import socket
import threading
import time

from connectivity_probe import EventLog, private_directory
from windows_udp_owner import owner_of_bound_port


def header_metadata(data):
    result = {"datagram_class":"unclassified", "payload_saved":False}
    if len(data) < 13 or data[0] not in (20,21,22,23) or data[1:3] not in (b"\xfe\xff",b"\xfe\xfd"):
        return result
    length = int.from_bytes(data[11:13],"big")
    result.update(datagram_class="dtls_record_header", record_version="DTLS1.0" if data[2] == 255 else "DTLS1.2",
                  record_content_type={20:"change_cipher_spec",21:"alert",22:"handshake",23:"application_data"}[data[0]],
                  record_epoch=int.from_bytes(data[3:5],"big"), first_record_bytes=length,
                  first_record_complete=length <= len(data)-13, negotiated_version_proven=False)
    if data[0] != 22 or result["record_epoch"] != 0 or not 12 <= length <= 16384 or not result["first_record_complete"]:
        return result
    message = data[13:25]
    message_length = int.from_bytes(message[1:4],"big")
    fragment_offset = int.from_bytes(message[6:9],"big")
    fragment_length = int.from_bytes(message[9:12],"big")
    if message[0] == 1 and fragment_length <= length-12 and fragment_offset+fragment_length <= message_length:
        result.update(datagram_class="dtls_client_hello_header", client_hello_complete=(fragment_offset == 0 and fragment_length == message_length),
                      client_hello_body_validated=False)
    return result


class Observer:
    def __init__(self, bind, port, events, *, lookup=owner_of_bound_port):
        if bind != "127.0.0.1" or not 0 <= port <= 65535:
            raise ValueError("Only owned IPv4 loopback endpoints")
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        try:
            self.socket.bind((bind,port))
            self.socket.settimeout(0.1)
        except BaseException:
            self.socket.close()
            raise
        self.events, self.lookup = events, lookup
        self.address = self.socket.getsockname()

    def run(self, seconds, stop=None):
        if not 0 < seconds <= 600:
            self.socket.close()
            raise ValueError("Bounded observation required")
        stop = stop if stop is not None else threading.Event()
        deadline, count = time.monotonic()+seconds, 0
        self.events.emit("UDP_HANDOFF_OBSERVER_LISTENING",bind=self.address[0],port=self.address[1],receive_only=True)
        try:
            while not stop.is_set() and time.monotonic() < deadline and count < 64:
                try:
                    data, peer = self.socket.recvfrom(65536)
                except socket.timeout:
                    continue
                if not ipaddress.ip_address(peer[0]).is_loopback:
                    continue
                count += 1
                self.events.emit("GAME_TRANSPORT_DATAGRAM_OBSERVED",peer={"address":peer[0],"port":peer[1]},
                                 local={"address":self.address[0],"port":self.address[1]},datagram_bytes=len(data),
                                 process_id=self.lookup(peer[0],peer[1]),owner_basis="IPv4_bound_endpoint_owner_not_exact_flow",
                                 handshake_established=False,**header_metadata(data))
                del data
        finally:
            self.socket.close()
            self.events.emit("UDP_HANDOFF_OBSERVER_STOPPED",received_datagrams=count,handshake_established=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log",required=True)
    parser.add_argument("--port",type=int,default=64003)
    parser.add_argument("--duration",type=int,default=600)
    options = parser.parse_args()
    if not 1 <= options.port <= 65535 or not 1 <= options.duration <= 600:
        parser.error("Valid port and duration1..600 required")
    path = private_directory(options.log)
    path.parent.mkdir(parents=True,exist_ok=True)
    events = EventLog(path)
    try:
        Observer("127.0.0.1",options.port,events).run(options.duration)
    finally:
        events.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
