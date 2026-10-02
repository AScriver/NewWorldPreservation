import json
from pathlib import Path
import socket
import sys
import threading
import time

import pytest
sys.path.insert(0,str(Path(__file__).parents[1] / "scripts"))
import udp_handoff_probe as probe
from connectivity_probe import EventLog


def record(body=b"SYNTHETIC-SECRET-DO-NOT-EXPORT",version=b"\xfe\xff",offset=0,message_length=None):
    length = len(body) if message_length is None else message_length
    message = bytes([1])+length.to_bytes(3,"big")+b"\0\0"+offset.to_bytes(3,"big")+len(body).to_bytes(3,"big")+body
    return b"\x16"+version+b"\0"*8+len(message).to_bytes(2,"big")+message


@pytest.mark.parametrize("version,expected", [(b"\xfe\xff","DTLS1.0"),(b"\xfe\xfd","DTLS1.2")])
def test_standard_client_hello_header_does_not_claim_negotiation_or_export_body(version,expected):
    metadata = probe.header_metadata(record(version=version))
    assert metadata["datagram_class"] == "dtls_client_hello_header" and metadata["record_version"] == expected
    assert metadata["client_hello_complete"] and not metadata["client_hello_body_validated"]
    assert not metadata["negotiated_version_proven"] and not metadata["payload_saved"]
    assert "SYNTHETIC-SECRET" not in json.dumps(metadata)


def test_fragmented_client_hello_and_invalid_offsets_are_not_promoted_to_complete():
    metadata = probe.header_metadata(record(b"test",offset=4,message_length=8))
    assert metadata["datagram_class"] == "dtls_client_hello_header" and not metadata["client_hello_complete"]
    assert probe.header_metadata(record(b"test",offset=5,message_length=8))["datagram_class"] == "dtls_record_header"


@pytest.mark.parametrize("data", [b"",b"secret",record(version=b"\x03\x03"),record()[:12]])
def test_unknown_or_truncated_header_does_not_export_prefix(data):
    assert probe.header_metadata(data) == {"datagram_class":"unclassified","payload_saved":False}


def test_truncated_record_and_encrypted_epoch_do_not_claim_client_hello():
    truncated = probe.header_metadata(record()[:-1])
    assert truncated["datagram_class"] == "dtls_record_header" and not truncated["first_record_complete"]
    encrypted = bytearray(record())
    encrypted[4] = 1
    assert probe.header_metadata(encrypted)["datagram_class"] == "dtls_record_header"


def test_real_loopback_receive_logs_metadata_and_owner_only_never_replies(tmp_path):
    path = tmp_path / "events.jsonl"
    events = EventLog(path)
    stop = threading.Event()
    observer = probe.Observer("127.0.0.1",0,events,lookup=lambda address,port:123)
    thread = threading.Thread(target=observer.run,args=(3,stop))
    thread.start()
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sender:
            sender.settimeout(0.15)
            sender.sendto(record(),observer.address)
            with pytest.raises(socket.timeout):
                sender.recvfrom(65536)
        deadline = time.monotonic()+2
        while "GAME_TRANSPORT_DATAGRAM_OBSERVED" not in path.read_text() and time.monotonic() < deadline:
            time.sleep(0.01)
    finally:
        stop.set()
        thread.join(timeout=3)
        events.close()
    assert not thread.is_alive()
    records = [json.loads(line) for line in path.read_text().splitlines()]
    datagram = next(item for item in records if item["state"] == "GAME_TRANSPORT_DATAGRAM_OBSERVED")
    assert datagram["process_id"] == 123 and not datagram["handshake_established"]
    assert not datagram["payload_saved"] and "SYNTHETIC-SECRET" not in json.dumps(records)
    assert records[-1]["state"] == "UDP_HANDOFF_OBSERVER_STOPPED"
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as check:
        check.bind(observer.address)


def test_non_loopback_observer_refused_before_bind():
    with pytest.raises(ValueError):
        probe.Observer("0.0.0.0",0,None)
