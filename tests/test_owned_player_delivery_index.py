"""Original synthetic ObjectStream controls only; never read client assets."""
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import owned_player_delivery_index as target

def element(type_id,children=b'',name=None,value=None,extra=None,version=None):
    flags=8 | (64 if name is not None else 0) | (128 if version is not None else 0)
    header=bytearray()
    if name is not None:header.extend(name.to_bytes(4,'big'))
    if version is not None:header.append(version)
    header.extend(type_id)
    if value is not None:
        flags|=16
        if extra is None:flags|=len(value)
        else:flags|=32|extra;header.extend(len(value).to_bytes(extra,'big'))
        header.extend(value)
    return bytes([flags])+header+children+b'\0'

def fixture(*,index=7,field_type=target.INDEX_UUID,width=4,name=target.INDEX_NAME_CRC,duplicate=False,extra=None):
    leaf=element(field_type,name=name,value=index.to_bytes(width,'big'),extra=extra)
    base=element(target.FACETED_UUID,leaf+(leaf if duplicate else b''),version=1)
    player=element(target.PLAYER_UUID,base)
    return b'\0\0\0\0\3'+element(target.ENTITY_UUID,player)+b'\0'

def test_literal_untouched_big_endian_scalar_and_offsets():
    # Independent literal: Entity →Player →Faceted →named u32(7), close each +stream.
    literal=(b'\0\0\0\0\3\x08'+target.ENTITY_UUID+b'\x08'+target.PLAYER_UUID+
             b'\x88\x01'+target.FACETED_UUID+b'\x5c\x81\xe5\x98\xc5'+target.INDEX_UUID+
             b'\0\0\0\7'+bytes(5))
    result=target.parse_player_delivery_index(literal)
    assert result.resource_index==7 and result.player_offset==22
    assert result.field_offset==57 and result.value_offset==78 and result.parsed_nodes==4

@pytest.mark.parametrize('index',[0,1,9,0x100,0xffffffff])
@pytest.mark.parametrize('extra',[None,1,2,4])
def test_value_and_size_field_boundaries(index,extra):
    assert target.parse_player_delivery_index(fixture(index=index,extra=extra)).resource_index==index

@pytest.mark.parametrize('cut',[0,1,4,5,6,20,50,60,80,85,86])
def test_truncation_never_returns_a_candidate(cut):
    with pytest.raises(ValueError):target.parse_player_delivery_index(fixture()[:cut])

@pytest.mark.parametrize('options',[{'field_type':bytes(16)},{'width':3},{'width':5},{'name':0x4024b7c1},{'duplicate':True}])
def test_wrong_field_identity_width_and_duplicate_refused(options):
    with pytest.raises(ValueError):target.parse_player_delivery_index(fixture(**options))

def test_wrong_missing_and_duplicate_players_or_bases_refused():
    for blob in [fixture().replace(target.PLAYER_UUID,bytes(16)),fixture().replace(target.FACETED_UUID,bytes(16)),
                 b'\0\0\0\0\3'+element(target.ENTITY_UUID,element(target.PLAYER_UUID)*2)+b'\0',
                 b'\0\0\0\0\3'+element(target.ENTITY_UUID,element(target.PLAYER_UUID,element(target.FACETED_UUID)*2))+b'\0']:
        with pytest.raises(ValueError):target.parse_player_delivery_index(blob)

@pytest.mark.parametrize('blob',[b'\0\0\0\0\2',fixture()+b'\0',fixture().replace(target.ENTITY_UUID,bytes(16)),
                               b'\0\0\0\0\3\x01',b'\0\0\0\0\3\x29'+target.ENTITY_UUID,
                               b'\0\0\0\0\3\x3b'+target.ENTITY_UUID+b'\0\0\0'])
def test_version_root_trailing_and_unsupported_flags_refused(blob):
    with pytest.raises(ValueError):target.parse_player_delivery_index(blob)

def test_tree_bounds_and_mutable_input_refused(monkeypatch):
    for attr,limit in [('MAX_NODES',3),('MAX_DEPTH',3),('MAX_BYTES',10)]:
        with monkeypatch.context() as scoped:
            scoped.setattr(target,attr,limit)
            with pytest.raises(ValueError):target.parse_player_delivery_index(fixture())
    with pytest.raises(ValueError):target.parse_player_delivery_index(bytearray(fixture()))

def test_pinned_reader_refuses_outside_ignored_and_wrong_identity(tmp_path,monkeypatch):
    monkeypatch.setattr(target,'__file__',str(tmp_path/'scripts/owned_player_delivery_index.py'))
    outside=tmp_path/'outside.bin';outside.write_bytes(fixture())
    with pytest.raises(ValueError,match='ignored space'):target.read_pinned_player_delivery_index(outside)
    ignored=tmp_path/'private';ignored.mkdir()
    path=ignored/'original.bin';path.write_bytes(fixture())
    with pytest.raises(ValueError,match='identity mismatch'):target.read_pinned_player_delivery_index(path)
