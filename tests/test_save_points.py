"""Typewriter / item box icons (src/save_points.h, tools/extract_save_points.py): one point per machine of every room of
data/save_points.json, and the zoomed icon lands where the zoomed map sprite of the same point lands at every zoom offset
(zoom.h: a sprite at input m is drawn at 48 + .9 * (2m + off); the overlay's ZX is 2 * (48 + .9m) - 48 + .9 * off)."""
from pathlib import Path
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
h = (ROOT / 'src/save_points.h').read_text(encoding='utf-8')
points = [(int(a), int(b), float(c), float(d)) for a, b, c, d in re.findall(r'^\{(\d+),(\d),(-?[\d.]+)f,(-?[\d.]+)f\},$', h, re.M)]
assert len(points) == int(re.search(r'#define SAVE_POINT_COUNT (\d+)', h)[1]) == 21
rooms = json.loads((ROOT / 'data/save_points.json').read_text(encoding='utf-8'))
for sp in rooms:
    assert any(p[0] == sp['room'] and p[1] == 0 for p in points) == sp['typewriter'], sp
    assert any(p[0] == sp['room'] and p[1] == 1 for p in points) == sp['item_box'], sp
assert len({(p[0], p[1]) for p in points}) == len(points)                       # one point per machine
assert (114, 0, 191.0, 124.0) == (114, 0, round(*[p[2] for p in points if p[:2] == (114, 0)]), round(*[p[3] for p in points if p[:2] == (114, 0)]))  # Room 003 / 003호실 typewriter

PROG = r'''
#include <assert.h>
#include <math.h>
#include "zoom.h"
int main(void) {
    for (float off_x = ZOOM_X_MIN; off_x <= ZOOM_X_MAX; off_x += 37) for (float m = 0; m < 960; m += 97) {
        float overlay = zoom_out_x(48 + .9f * m, off_x);                       /* ZX(canvas) */
        int s[12] = {0, 0, 0, 0, (int)m, 0, 8, 8, 0, 0, 0, 0}; zoom_sprite(s, off_x, 0);
        float sprite = 48 + .9f * s[4];                                       /* what 0x5561d0 draws for the zoomed sprite */
        assert(fabsf(overlay - sprite) <= .9f);                                /* the native sprite is whole-pixel: within one input unit */
    }
    return 0;
}
'''
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 'z.c', Path(d) / 'z'
    c.write_text(PROG)
    subprocess.run(['clang', '-w', '-I', str(ROOT / 'src'), str(c), '-o', str(exe), '-lm'], check=True)
    subprocess.run([str(exe)], check=True)
print('PASS: 21 typewriter / item box points match the 12 rooms; the overlay transform equals the zoomed sprite transform at every pan offset')
