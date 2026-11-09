"""data/room_shapes.json (tools/extract_room_shapes.py) and the canvas transform.

The transform is proven twice, and both proofs must fail on a wrong one: (1) the 440 item markers (canvas positions from
the game's own projection) lie in or within 2 units of their room at the transform, and 5 units of offset either way or a
5% smaller scale loses that; (2) distinct rooms of a floor tile: the overlap between rooms that are not variants of one
another (section_rules.h, same map position) at least doubles when either scale is 5% larger. The extractor's hole filling
and run encoding are checked on a synthetic mask."""
from pathlib import Path
import itertools
import json
import re
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import room_geometry as rg  # noqa: E402
from extract_room_shapes import filled, runs  # noqa: E402

data = rg.load()
assert len(data['rooms']) == 154 and sum('runs' in r for r in data['rooms']) == 148
assert set(data['sources']) == {'bhd.exe'} | {'nativePC/arc/id/e_rom/subscr/map_st%02d.arc' % s for s in range(1, 6)}
snapshot = json.loads((ROOT / 'verification/source-snapshot.json').read_text())
assert data['sources']['bhd.exe'] == snapshot['game_exe_sha256']
for r in data['rooms']:
    if 'runs' in r:
        assert len(r['runs']) == r['rect'][3] and all(0 <= v <= r['rect'][2] for row in r['runs'] for v in row)

h = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
rows = [f.split(',') for f in re.findall(r'^\{([^\n]*?)\}, /\* ', h, re.M)]
markers = [(int(f[1]), float(f[8].rstrip('f')), float(f[9].rstrip('f'))) for f in rows if f[0] in ('4', '5', '7')]


def near(perturb):
    shapes = rg.shapes(data, perturb)
    pts = [(r, x, y) for r, x, y in markers if r in shapes]
    return sum(shapes[r].distance_outside(x, y, limit=2, step=1) <= 2 for r, x, y in pts) / len(pts)


base = near((0, 0, 1, 1))
assert base >= .95, base
for p in ((5, 0, 1, 1), (-5, 0, 1, 1), (0, 5, 1, 1), (0, -5, 1, 1), (0, 0, .95, 1), (0, 0, 1, .95)):
    assert near(p) <= .93, (p, near(p))

pairs = {(int(a), int(b)) for a, b in re.findall(r'\{(\d+),(\d+)\}', (ROOT / 'src/section_rules.h').read_text())}
pairs |= {(b, a) for a, b in pairs}


def overlap(perturb):
    shapes = rg.shapes(data, perturb)
    cells = {}
    for r, s in shapes.items():
        x0, y0, x1, y1 = s.bounds()
        cells[r] = {(x, y) for y in range(int(y0), int(y1) + 1) for x in range(int(x0), int(x1) + 1) if s.contains(x + .5, y + .5)}
    pos = {r['room']: tuple(r['map']) for r in data['rooms']}
    total = 0
    for a, b in itertools.combinations(sorted(shapes), 2):
        sa, sb = shapes[a], shapes[b]
        if (sa.area, sa.floor) == (sb.area, sb.floor) and (a, b) not in pairs and pos[a] != pos[b]:
            total += len(cells[a] & cells[b])
    return total


o = overlap((0, 0, 1, 1))
assert overlap((0, 0, 1.05, 1)) >= 2 * o and overlap((0, 0, 1, 1.05)) >= 2 * o, o

mask = Image.new('L', (7, 5))
for x, y in [(x, y) for x in range(1, 6) for y in (1, 3)] + [(1, 2), (5, 2)]:
    mask.putpixel((x, y), 255)  # a ring with a hole at (2..4, 2)
assert runs(filled(mask)) == [[], [1, 6], [1, 6], [1, 6], []]
print('PASS: 148 room shapes; markers %.1f%% in or within 2 units, offset/shrink fail; tiling overlap %d, doubles at +5%% scale' % (100 * base, o))
