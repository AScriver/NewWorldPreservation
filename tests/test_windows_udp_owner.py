import ipaddress
import os
import socket
import struct
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
sys.path.insert(0,str(Path(__file__).parents[1] / "scripts"))
import windows_udp_owner as owner


def row(address, port, pid):
    return struct.pack("<4sII",ipaddress.ip_address(address).packed,socket.htons(port),pid)


def table(*rows):
    return struct.pack("<I",len(rows)) + b"".join(rows)


def test_exact_and_wildcard_binding_but_not_wrong_port_or_address():
    for address in ("127.0.0.1","0.0.0.0"):
        with patch.object(owner,"_read_table",return_value=table(row(address,49152,123))):
            assert owner.owner_of_bound_port("127.0.0.1",49152) == 123
            assert owner.owner_of_bound_port("127.0.0.1",49153) is None
    with patch.object(owner,"_read_table",return_value=table(row("192.0.2.1",49152,123))):
        assert owner.owner_of_bound_port("127.0.0.1",49152) is None


@pytest.mark.parametrize("data", [b"",b"\x01",struct.pack("<I",2)+row("127.0.0.1",49152,123),
    table(row("127.0.0.1",49152,123),row("0.0.0.0",49152,456)),table(row("127.0.0.1",49152,0)),None])
def test_missing_malformed_or_ambiguous_owner_fails_closed(data):
    with patch.object(owner,"_read_table",return_value=data):
        assert owner.owner_of_bound_port("127.0.0.1",49152) is None


@pytest.mark.parametrize("address,port", [("::1",123),("192.0.2.1",123),("invalid",123),("127.0.0.1",0)])
def test_only_loopback_ipv4_valid_ports_are_queried(address,port):
    with patch.object(owner,"_read_table") as read:
        assert owner.owner_of_bound_port(address,port) is None
        read.assert_not_called()


@pytest.mark.parametrize("address", ["127.0.0.1","0.0.0.0"])
def test_actual_native_owner_of_held_ephemeral_udp_binding(address):
    if sys.platform != "win32":
        pytest.skip("Windows UDP table only")
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as held:
        held.bind((address,0))
        assert owner.owner_of_bound_port("127.0.0.1",held.getsockname()[1]) == os.getpid()
