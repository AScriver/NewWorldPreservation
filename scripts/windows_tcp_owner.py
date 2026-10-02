"""Best-effort Windows TCP four-tuple to owner PID lookup (metadata only).

Layouts and table class: Microsoft GetExtendedTcpTable, MIB_TCPROW_OWNER_PID,
MIB_TCP6ROW_OWNER_PID, and TCP_TABLE_CLASS documentation:
https://learn.microsoft.com/windows/win32/api/iphlpapi/nf-iphlpapi-getextendedtcptable
https://learn.microsoft.com/windows/win32/api/tcpmib/ns-tcpmib-mib_tcprow_owner_pid
https://learn.microsoft.com/windows/win32/api/tcpmib/ns-tcpmib-mib_tcp6row_owner_pid
https://learn.microsoft.com/windows/win32/api/iprtrmib/ne-iprtrmib-tcp_table_class
"""

import ctypes
import ipaddress
import socket
import sys


_OWNER_PID_ALL = 5
_INSUFFICIENT_BUFFER = 122
_MAX_TABLE_BYTES = 8 * 1024 * 1024


class _Tcp4Row(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state", "local_address", "local_port", "remote_address", "remote_port", "pid"
    )]


class _Tcp6Row(ctypes.Structure):
    _fields_ = [
        ("local_address", ctypes.c_ubyte * 16), ("local_scope", ctypes.c_uint32),
        ("local_port", ctypes.c_uint32), ("remote_address", ctypes.c_ubyte * 16),
        ("remote_scope", ctypes.c_uint32), ("remote_port", ctypes.c_uint32),
        ("state", ctypes.c_uint32), ("pid", ctypes.c_uint32),
    ]


def _matching_pids(table, row_type, local, local_port, remote, remote_port,
                   local_scope=0, remote_scope=0):
    """Return only matching PIDs; None means the native table is malformed."""
    row_size = ctypes.sizeof(row_type)
    if len(table) < 4:
        return None
    count = int.from_bytes(table[:4], "little")
    if count > (len(table) - 4) // row_size:
        return None
    matches = set()
    for index in range(count):
        row = row_type.from_buffer_copy(table, 4 + index * row_size)
        if row_type is _Tcp4Row:
            local_bytes = int(row.local_address).to_bytes(4, "little")
            remote_bytes = int(row.remote_address).to_bytes(4, "little")
        else:
            local_bytes = bytes(row.local_address)
            remote_bytes = bytes(row.remote_address)
            if (socket.ntohl(row.local_scope) != local_scope
                    or socket.ntohl(row.remote_scope) != remote_scope):
                continue
        if (local_bytes == local and remote_bytes == remote
                and socket.ntohs(row.local_port & 0xffff) == local_port
                and socket.ntohs(row.remote_port & 0xffff) == remote_port):
            matches.add(int(row.pid))
    return matches


def _read_table(af):
    if sys.platform != "win32":
        return None
    try:
        function = ctypes.WinDLL("iphlpapi").GetExtendedTcpTable
        function.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32),
                             ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32)
        function.restype = ctypes.c_uint32
        size = ctypes.c_uint32()
        result = function(None, ctypes.byref(size), 0, af, _OWNER_PID_ALL, 0)
        if result not in (0, _INSUFFICIENT_BUFFER):
            return None
        needed = max(4, size.value)
        for _ in range(3):
            if needed > _MAX_TABLE_BYTES:
                return None
            buffer = ctypes.create_string_buffer(needed)
            size.value = needed
            result = function(buffer, ctypes.byref(size), 0, af, _OWNER_PID_ALL, 0)
            if result == 0:
                return buffer.raw[:size.value] if 4 <= size.value <= needed else None
            if result != _INSUFFICIENT_BUFFER:
                return None
            needed = max(size.value, needed * 2)
    except (AttributeError, OSError, OverflowError, ValueError, MemoryError, ctypes.ArgumentError):
        return None
    return None


def owner_of_connection(local_address, local_port, remote_address, remote_port):
    """Return one positive PID for an exact TCP tuple, else None.

    This is a momentary OS table lookup; a finished connection may disappear
    before the query. It does not prove executable identity or TLS content.
    """
    try:
        local = ipaddress.ip_address(local_address)
        remote = ipaddress.ip_address(remote_address)
        if (local.version != remote.version or not 1 <= local_port <= 65535
                or not 1 <= remote_port <= 65535):
            return None
        local_scope = int(getattr(local, "scope_id", None) or 0)
        remote_scope = int(getattr(remote, "scope_id", None) or 0)
    except (ValueError, TypeError, OverflowError):
        return None
    af = socket.AF_INET if local.version == 4 else socket.AF_INET6
    table = _read_table(af)
    if table is None:
        return None
    row_type = _Tcp4Row if local.version == 4 else _Tcp6Row
    pids = _matching_pids(table, row_type, local.packed, local_port,
                          remote.packed, remote_port, local_scope, remote_scope)
    return next(iter(pids)) if pids and len(pids) == 1 and next(iter(pids)) > 0 else None
