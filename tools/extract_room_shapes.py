"""Extract every map room's filled shape from a legally owned RE1 HD REMASTER install (read only) into data/room_shapes.json.

Sources (both checked by hash against verification/source-snapshot.json and data/room_shapes.json):
- bhd.exe: the static room table at RVA 0x8c8e00, 154 records of 96 bytes (the runtime's EXE_ROOMS). Fields used:
  +0x00/+0x04 map position, +0x18/+0x1c area and floor, +0x48 texture page, +0x50..+0x5c the room's rectangle in the page.
- nativePC/arc/id/e_rom/subscr/map_st0N.arc: MT Framework ARC v7, zlib entries; the textures stNN_1P_ID_HQ (TEX v0x9d,
  BC3) hold the rooms as flat silhouettes, page P. The _0P twins are the same shapes with detail drawn in.

A room's shape is the alpha (> 127) of its rectangle with interior holes filled (flood fill from the border), stored as
row runs in texture pixels. Canvas (game pixels at 1280x720, the labels.h space) = 48 + 0.9 * (map + texel * (SX, SY)),
see TRANSFORM; tests/test_room_shapes.py proves it against the markers and rejects perturbed constants.

Usage: python tools/extract_room_shapes.py "<game folder>" [--dump local/room-shapes]
Writes data/room_shapes.json; --dump also writes the decoded pages as PNGs under local/ (ignored, never committed)."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import struct
import zlib
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ROOM_TABLE_RVA, ROOM_SIZE, ROOMS = 0x8c8e00, 96, 154
STAGE_FIRST = (0, 37, 72, 104, 129, 154)  # first room index per stage (runtime stage_first)
TRANSFORM = {'origin': [48, 36], 'gui_scale': 0.9, 'texel': [0.9375, 0.8035]}  # 0x5561d0's 0.9 and (48,36); runtime save icons


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_offset(exe, rva):
    pe = struct.unpack_from('<I', exe, 0x3c)[0]
    count, opt = struct.unpack_from('<H', exe, pe + 6)[0], struct.unpack_from('<H', exe, pe + 20)[0]
    for i in range(count):
        o = pe + 24 + opt + 40 * i
        size, va, raw_size, raw = struct.unpack_from('<IIII', exe, o + 8)
        if va <= rva < va + raw_size:
            return raw + rva - va
    raise ValueError('RVA %#x is not in the file' % rva)


def room_table(exe):
    o = file_offset(exe, ROOM_TABLE_RVA)
    return [struct.unpack_from('<24i', exe, o + ROOM_SIZE * r) for r in range(ROOMS)]


def arc_entries(data):
    magic, version, count = struct.unpack_from('<4sHH', data, 0)
    if magic != b'ARC\0' or version != 7:
        raise ValueError('not an ARC v7 file')
    for i in range(count):
        o = 8 + 80 * i
        name = data[o:o + 64].split(b'\0')[0].decode()
        kind, packed, _size, offset = struct.unpack_from('<IIII', data, o + 64)
        yield name, kind, zlib.decompress(data[offset:offset + packed])


def decode_tex(data):
    if data[:4] != b'TEX\0' or data[4] != 0x9d:
        raise ValueError('not a TEX v0x9d file')
    d2, d3 = struct.unpack_from('<II', data, 8)
    w, h, fmt = (d2 >> 6) & 0x1fff, (d2 >> 19) & 0x1fff, (d3 >> 8) & 0xff
    if fmt != 0x2b or len(data) - 20 != w * h:
        raise ValueError('unexpected texture format %#x %dx%d' % (fmt, w, h))
    return Image.frombytes('RGBA', (w, h), data[20:], 'bcn', 3)


def filled(alpha):
    """Alpha mask -> rows of 0/1 with holes filled: anything not reachable from the border through transparent pixels is in."""
    w, h = alpha.size
    px = alpha.load()
    solid = [[px[x, y] > 127 for x in range(w)] for y in range(h)]
    outside = [[False] * w for _ in range(h)]
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if 0 <= x < w and 0 <= y < h and not outside[y][x] and not solid[y][x]:
            outside[y][x] = True
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [[0 if outside[y][x] else 1 for x in range(w)] for y in range(h)]


def runs(rows):
    """Row-run encoding: per row, [start, end) pairs."""
    out = []
    for row in rows:
        r, x = [], 0
        while x < len(row):
            if row[x]:
                s = x
                while x < len(row) and row[x]:
                    x += 1
                r += [s, x]
            else:
                x += 1
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('game')
    ap.add_argument('--dump')
    a = ap.parse_args()
    game = Path(a.game)
    exe = (game / 'bhd.exe').read_bytes()
    snapshot = json.loads((ROOT / 'verification/source-snapshot.json').read_text())
    if sha256(exe) != snapshot['game_exe_sha256']:
        raise SystemExit('bhd.exe is not the supported build')
    sources = {'bhd.exe': sha256(exe)}
    pages = {}
    for stage in range(1, 6):
        rel = 'nativePC/arc/id/e_rom/subscr/map_st%02d.arc' % stage
        data = (game / rel).read_bytes()
        sources[rel] = sha256(data)
        for name, _kind, body in arc_entries(data):
            leaf = name.rsplit('\\', 1)[-1]  # stNN_SP_ID_HQ: S 0 detail, 1 flat; P page
            tex = decode_tex(body)
            pages[leaf[:7]] = tex
            if a.dump:
                Path(a.dump).mkdir(parents=True, exist_ok=True)
                tex.save(Path(a.dump) / (leaf + '.png'))
    rooms = []
    for i, r in enumerate(room_table(exe)):
        stage = next(s for s in range(5) if STAGE_FIRST[s] <= i < STAGE_FIRST[s + 1]) + 1
        u, v, w, h = r[20:24]
        room = {'room': i, 'stage': stage, 'area': r[6], 'floor': r[7], 'map': [r[0], r[1]], 'page': r[18], 'rect': [u, v, w, h]}
        if w > 0 and h > 0:
            alpha = pages['st%02d_1%d' % (stage, r[18])].getchannel('A').crop((u, v, u + w, v + h))
            room['runs'] = runs(filled(alpha))
        rooms.append(room)
    out = {'_source': 'tools/extract_room_shapes.py from a legally owned game; derived silhouettes only, no game images.',
           'as_of': datetime.date.today().isoformat(), 'sources': sources, 'transform': TRANSFORM, 'rooms': rooms}
    (ROOT / 'data/room_shapes.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print('%d rooms, %d with shapes' % (len(rooms), sum('runs' in r for r in rooms)))


if __name__ == '__main__':
    main()
