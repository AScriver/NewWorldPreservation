"""IPv4 UDP bind-owner lookup, NOT an exact flow/destination identity.

Microsoft GetExtendedUdpTable / MIB_UDPROW_OWNER_PID / UDP_TABLE_CLASS:
https://learn.microsoft.com/windows/win32/api/iphlpapi/nf-iphlpapi-getextendedudptable
https://learn.microsoft.com/windows/win32/api/udpmib/ns-udpmib-mib_udprow_owner_pid
https://learn.microsoft.com/windows/win32/api/iprtrmib/ne-iprtrmib-udp_table_class
Only return a unique positive PID for the exact or wildcard local binding.
"""
import ctypes
import ipaddress
import socket
import sys


def _matching_pids(table, address, port):
    if len(table) < 4:
        return None
    count = int.from_bytes(table[:4], "little")
    if count > (len(table) - 4) // 12:
        return None
    owners = set()
    for index in range(count):
        row = table[4 + index * 12:16 + index * 12]
        if row[:4] not in (address, b"\0" * 4):
            continue
        if socket.ntohs(int.from_bytes(row[4:8], "little") & 0xffff) == port:
            owners.add(int.from_bytes(row[8:12], "little"))
    return owners


def _read_table():
    if sys.platform != "win32":
        return None
    try:
        function = ctypes.WinDLL("iphlpapi").GetExtendedUdpTable
        function.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32), ctypes.c_int,
                             ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32)
        function.restype = ctypes.c_uint32
        size = ctypes.c_uint32()
        result = function(None, ctypes.byref(size), 0, socket.AF_INET, 1, 0)
        if result not in (0, 122):
            return None
        needed = max(4, size.value)
        for _ in range(3):
            if needed > 8 * 1024 * 1024:
                return None
            buffer = ctypes.create_string_buffer(needed)
            size.value = needed
            result = function(buffer, ctypes.byref(size), 0, socket.AF_INET, 1, 0)
            if result == 0:
                return buffer.raw[:size.value] if 4 <= size.value <= needed else None
            if result != 122:
                return None
            needed = max(size.value, needed * 2)
    except (AttributeError, OSError, ValueError, OverflowError, MemoryError, ctypes.ArgumentError):
        return None
    return None


def owner_of_bound_port(address, port):
    """Best-effort current IPv4 endpoint owner; ambiguous/missing data -> None."""
    try:
        local = ipaddress.ip_address(address)
        if local.version != 4 or not local.is_loopback or not 1 <= port <= 65535:
            return None
    except (ValueError, TypeError):
        return None
    table = _read_table()
    owners = None if table is None else _matching_pids(table, local.packed, port)
    return next(iter(owners)) if owners and len(owners) == 1 and next(iter(owners)) > 0 else None
