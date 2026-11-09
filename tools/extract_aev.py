"""Room `aev` records (area hit data) of a legally owned RE1 HD REMASTER install, read only.

nativePC/arc/room/stNN/rXXX.arc (MT ARC v7) holds `room\\aev\\rXXX`, an XFS. After the field-name strings every record is 0x74
bytes: a 24-byte prefix, 8 floats (the four world x, z corners of the hit polygon), then fields: byte 4 = mType, u16 at 14 = mNo.
mType (captured 2026-11-07): 0 look/event area, 1 area, 4 pickup area, 6 typewriter, 8 item box, 10 door/check, 11 examine object
(mNo = the item or message number, e.g. 77 = light with the Lighter). Positions go through the room record like pickups."""
from pathlib import Path
import struct
import zlib

ROOM_ARC = 'nativePC/arc/room/st%02d/r%s.arc'


def arc_entry(path, name):
    data = Path(path).read_bytes()
    magic, version, count = struct.unpack_from('<4sHH', data, 0)
    if magic != b'ARC\0' or version != 7:
        raise ValueError('not an ARC v7 file')
    for i in range(count):
        o = 8 + 80 * i
        entry = data[o:o + 64].split(b'\0')[0].decode()
        _kind, packed, _size, offset = struct.unpack_from('<IIII', data, o + 64)
        if entry == name:
            return zlib.decompress(data[offset:offset + packed])
    raise KeyError(name)


def records(room_id, game):
    """[(type, no, centre x, centre z)] of the room's aev, room_id like '40a'."""
    stage = int(room_id[0])
    data = arc_entry(Path(game) / (ROOM_ARC % (stage, room_id)), 'room\\aev\\r' + room_id)
    out, i = [], data.index(b'mPointTbl') + 10
    while i < len(data) - 32:
        pts = struct.unpack_from('<8f', data, i)
        if all(1 < abs(v) < 30000 for v in pts):
            post = data[i + 32:i + 0x74 - 24]
            out.append((post[4], struct.unpack_from('<H', post, 14)[0], sum(pts[0::2]) / 4, sum(pts[1::2]) / 4))
            i += 32
        else:
            i += 1
    return out
