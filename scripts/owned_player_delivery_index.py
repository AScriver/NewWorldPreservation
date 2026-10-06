"""Original bounded ObjectStream-v3 metadata reader, not native asset loading.

Public reference grammar interprets the selected scalar as BE32. Current image
joins class/field identity; its primitive loader and runtime mode stay separate.
No decompressor, client, listener or mutation is invoked by this module.
"""
from dataclasses import dataclass
import hashlib
from pathlib import Path

ENTITY_UUID = bytes.fromhex('756516588663478d90902432dfcafa44')
PLAYER_UUID = bytes.fromhex('d50340cfa0824b9099338c42387c0c77')
FACETED_UUID = bytes.fromhex('65cd8f3e73aa43e98d9ab5ae43f624f9')
INDEX_UUID = bytes.fromhex('43da906b7def4ca89790854106d3f983')
INDEX_NAME_CRC = 0x81E598C5
DECODED_BYTES = 367528
DECODED_SHA256 = '513e5f9bc3f8ca9896fdea164c9889dfbf2bd9587d7273f19395b1b83b3af377'
MAX_BYTES, MAX_NODES, MAX_DEPTH = 400000, 25000, 128


@dataclass(frozen=True)
class PlayerDeliveryIndex:
    resource_index: int
    player_offset: int
    field_offset: int
    value_offset: int
    parsed_nodes: int


def parse_player_delivery_index(data: bytes) -> PlayerDeliveryIndex:
    """Read one exact selected metadata field; accept original controls too.

    Reject ambiguity, other stream versions, unsupported flags and malformed
    tree/extent/type/width. This strict subset is not a native reader emulator.
    A resource index, including zero, is returned without choosing runtime mode.
    """
    if type(data) is not bytes or not 6 <= len(data) <= MAX_BYTES:
        raise ValueError('requires bounded immutable ObjectStream bytes')
    if data[:5] != b'\0\0\0\0\3':
        raise ValueError('requires binary ObjectStream version3')
    cursor, nodes, stack, roots, ended = 5, [], [], [], False

    def read(count: int) -> bytes:
        nonlocal cursor
        if not 0 <= count <= len(data) - cursor:
            raise ValueError('truncated ObjectStream element')
        result = data[cursor:cursor+count]
        cursor += count
        return result

    while cursor < len(data):
        offset, flags = cursor, read(1)[0]
        if flags == 0:
            if stack:
                stack.pop()
                continue
            if cursor != len(data):
                raise ValueError('trailing ObjectStream bytes')
            ended = True
            break
        if (not flags & 8 or (not flags & 16 and flags & 0x27)):
            raise ValueError('unsupported ObjectStream flags')
        if len(nodes) >= MAX_NODES or len(stack) >= MAX_DEPTH:
            raise ValueError('ObjectStream tree bound exceeded')
        name = int.from_bytes(read(4), 'big') if flags & 64 else None
        if flags & 128:
            read(1)  # Skip class version; this metadata reader does not instantiate classes.
        type_id, size = read(16), 0
        if flags & 16:
            size = flags & 7
            if flags & 32:
                if size not in (1, 2, 4):
                    raise ValueError('unsupported ObjectStream size width')
                size = int.from_bytes(read(size), 'big')
        value_offset, value = cursor, read(size)
        parent = stack[-1] if stack else None
        node = (type_id, name, parent, offset, value_offset, value)
        index = len(nodes)
        nodes.append(node)
        if parent is None:
            roots.append(index)
        stack.append(index)
    if not ended or stack or len(roots) != 1 or nodes[roots[0]][0] != ENTITY_UUID:
        raise ValueError('requires one complete Entity root')
    players = [i for i, n in enumerate(nodes) if n[0] == PLAYER_UUID]
    if len(players) != 1:
        raise ValueError('requires exactly one PlayerComponent')
    bases = [i for i, n in enumerate(nodes) if n[2] == players[0] and n[0] == FACETED_UUID]
    if len(bases) != 1:
        raise ValueError('requires one direct FacetedComponent base')
    fields = [n for n in nodes if n[2] == bases[0] and n[1] == INDEX_NAME_CRC]
    if len(fields) != 1 or fields[0][0] != INDEX_UUID or len(fields[0][5]) != 4:
        raise ValueError('requires one typed four-byte replication index')
    field = fields[0]
    return PlayerDeliveryIndex(int.from_bytes(field[5], 'big'), nodes[players[0]][3],
                               field[3], field[4], len(nodes))


def read_pinned_player_delivery_index(decoded_path: Path) -> PlayerDeliveryIndex:
    """Read only the hash-pinned decoded artifact in this project's ignored space.

    Producing that artifact and verifying the owned package/CRC are separate
    file-only procedures. This API executes neither an external decoder nor
    native client code and does not establish current runtime configuration.
    """
    root = Path(__file__).resolve().parents[1]
    path = Path(decoded_path).resolve()
    if not any(path.is_relative_to(root / folder) for folder in ('.scratch', 'private')):
        raise ValueError('decoded asset must remain in project ignored space')
    with path.open('rb') as stream:
        data = stream.read(DECODED_BYTES + 1)
    if len(data) != DECODED_BYTES or hashlib.sha256(data).hexdigest() != DECODED_SHA256:
        raise ValueError('decoded owned player identity mismatch')
    return parse_player_delivery_index(data)
