import importlib.util
import ipaddress
import os
import socket
import struct
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


spec = importlib.util.spec_from_file_location(
    "windows_tcp_owner", Path(__file__).parents[1] / "scripts/windows_tcp_owner.py"
)
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)


def row4(local, local_port, remote, remote_port, pid):
    return struct.pack(
        "<6I", 5, int.from_bytes(ipaddress.ip_address(local).packed, "little"),
        socket.htons(local_port), int.from_bytes(ipaddress.ip_address(remote).packed, "little"),
        socket.htons(remote_port), pid,
    )


def row6(local, local_port, remote, remote_port, pid, local_scope=0, remote_scope=0):
    return struct.pack(
        "<16sII16sIIII", ipaddress.ip_address(local).packed, socket.htonl(local_scope),
        socket.htons(local_port), ipaddress.ip_address(remote).packed, socket.htonl(remote_scope),
        socket.htons(remote_port), 5, pid,
    )


def table(*rows):
    return struct.pack("<I", len(rows)) + b"".join(rows)


def test_ipv4_exact_tuple_and_network_order_ports():
    data = table(
        row4("127.0.0.1", 49152, "127.0.0.1", 443, 10340),
        row4("127.0.0.1", 49153, "127.0.0.1", 443, 20202),
    )
    with patch.object(owner, "_read_table", return_value=data) as read:
        assert owner.owner_of_connection("127.0.0.1", 49152, "127.0.0.1", 443) == 10340
        assert owner.owner_of_connection("127.0.0.1", 443, "127.0.0.1", 49152) is None
        read.assert_called_with(socket.AF_INET)


def test_ipv6_exact_tuple():
    data = table(row6("::1", 49152, "::1", 443, 10340))
    with patch.object(owner, "_read_table", return_value=data) as read:
        assert owner.owner_of_connection("::1", 49152, "::1", 443) == 10340
        read.assert_called_once_with(socket.AF_INET6)


def test_ipv6_scope_is_part_of_exact_address():
    data = table(row6("fe80::1", 49152, "fe80::2", 443, 10340, 7, 7))
    with patch.object(owner, "_read_table", return_value=data):
        assert owner.owner_of_connection("fe80::1%7", 49152, "fe80::2%7", 443) == 10340
        assert owner.owner_of_connection("fe80::1", 49152, "fe80::2", 443) is None


def test_malformed_ambiguous_or_missing_owner_fails_closed():
    matching = row4("127.0.0.1", 49152, "127.0.0.1", 443, 10340)
    other = row4("127.0.0.1", 49152, "127.0.0.1", 443, 20202)
    for data in (b"\x01", struct.pack("<I", 2) + matching,
                 table(matching, other), table(matching, matching[:-4] + b"\0\0\0\0")):
        with patch.object(owner, "_read_table", return_value=data):
            assert owner.owner_of_connection("127.0.0.1", 49152, "127.0.0.1", 443) is None
    with patch.object(owner, "_read_table", return_value=None):
        assert owner.owner_of_connection("127.0.0.1", 49152, "127.0.0.1", 443) is None


@pytest.mark.parametrize("family,address", [(socket.AF_INET, "127.0.0.1"),
                                            (socket.AF_INET6, "::1")])
def test_native_owner_of_held_ephemeral_loopback_connection(family, address):
    if sys.platform != "win32":
        pytest.skip("GetExtendedTcpTable is Windows-only")
    with socket.socket(family, socket.SOCK_STREAM) as listener, \
         socket.socket(family, socket.SOCK_STREAM) as client:
        listener.bind((address, 0))
        listener.listen(1)
        client.connect(listener.getsockname())
        accepted, _ = listener.accept()
        with accepted:
            local = client.getsockname()
            remote = client.getpeername()
            assert owner.owner_of_connection(local[0], local[1], remote[0], remote[1]) == os.getpid()
