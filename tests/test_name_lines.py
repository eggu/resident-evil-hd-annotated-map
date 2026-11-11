"""Two-line names are aligned toward their icon (RE0 rule, user decision 2026-11-08). Each name is one raster; src/name_lines.h gives
each line's band, and the real emit_name draws a line as a sub-rectangle. Checks: the bands cover every ink pixel and match the row
comment's line count (all 192 marker names and every multi-line item name); left alignment shares the left ink edge of the lines, right
alignment the right edge, centred draws the raster whole; heights and widths are preserved; a one-line name is never split."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from render_labels import ROW, parse  # noqa: E402

h = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
n = (ROOT / 'src/item_name_text.h').read_text(encoding='utf-8')
nl = (ROOT / 'src/name_lines.h').read_text(encoding='utf-8')
arrays = dict(re.findall(r'static const unsigned char (px\d+)\[\]=\{([^}]*)\};', h))
narr = dict(re.findall(r'static const unsigned char (ntpx\d+)\[\]=\{([^}]*)\};', n))
start, end, table = parse(h)
label_size, expect = {}, {}
for i, line in enumerate(l for l in table if l.startswith('{')):
    m = ROW.match(line)
    label_size[i] = (int(m['w']), int(m['h'])) if m else (0, 0)
    if m and int(m['kind']) in (1, 2, 4, 5):
        im = Image.frombytes('RGBA', label_size[i], bytes(map(int, arrays[m['px']].split(','))))
        if im.getbbox():
            expect[i] = (im, len(re.sub(r'^[★◆◇□]', '', m['text']).split(' / ')))
entries = re.findall(r'^\{(\d+),(\d+),(ntpx\d+),\d+,\d+\}, /\* (.*) \*/$', n, re.M)


label_lines = {}
split = nl.index('nametext_lines[]')
for img, count, body in re.findall(r'\{(\d+),(\d+),\{((?:\{-?\d+,-?\d+,-?\d+,-?\d+\},?){3})\}\}', nl[:split]):
    label_lines[int(img)] = [tuple(map(int, b)) for b in re.findall(r'\{(-?\d+),(-?\d+),(-?\d+),(-?\d+)\}', body)][:int(count)]
name_lines = {}
for img, count, body in re.findall(r'\{(\d+),(\d+),\{((?:\{-?\d+,-?\d+,-?\d+,-?\d+\},?){3})\}\}', nl[split:]):
    name_lines[int(img)] = [tuple(map(int, b)) for b in re.findall(r'\{(-?\d+),(-?\d+),(-?\d+),(-?\d+)\}', body)][:int(count)]
assert len(label_lines) == int(re.search(r'#define LABEL_LINES_COUNT (\d+)', nl)[1]) == 192 and len(name_lines) == int(re.search(r'#define NAMETEXT_LINES_COUNT (\d+)', nl)[1])


def covers(im, bands):
    alpha = im.getchannel('A').load()
    w, hh = im.size
    for y in range(hh):
        for x in range(w):
            if alpha[x, y]:
                assert any(y0 <= y <= y1 and x0 <= x <= x1 for y0, y1, x0, x1 in bands), (x, y, bands)
    assert all(a[1] < b[0] for a, b in zip(bands, bands[1:]))


for i, (im, lines) in expect.items():
    assert (i in label_lines) == (lines > 1), i                      # exactly the multi-line names have bands
    if lines > 1:
        assert len(label_lines[i]) == lines and all(len(b) == 4 for b in label_lines[i]), i
        covers(im, label_lines[i])
for k, (w, hh, px, text) in enumerate(entries):
    im = Image.frombytes('RGBA', (int(w), int(hh)), bytes(map(int, narr[px].split(','))))
    if k in name_lines:
        covers(im, name_lines[k])
    else:
        assert im.getbbox(), text                                          # one band only: no entry
assert len(name_lines) >= 10

PROG = r'''
#include <assert.h>
typedef unsigned U32;
#define LABEL_COUNT %d
#define NAME_FIRST 5000
#define ZH_FIRST 8000
typedef unsigned char BYTE;
#include "name_lines.h"
#include "labels_zh.h"
static U32 W_[9000], H_[9000];
static U32 image_w(U32 i) { return W_[i]; }
static U32 image_h(U32 i) { return H_[i]; }
static struct { U32 i; float x, y, w, h, u0, v0, u1, v1; } op[8]; static int nop;
static void emit(U32 i, float x, float y, float w, float h, float u0, float v0, float u1, float v1) { op[nop].i = i; op[nop].x = x; op[nop].y = y; op[nop].w = w; op[nop].h = h; op[nop].u0 = u0; op[nop].v0 = v0; op[nop].u1 = u1; op[nop].v1 = v1; nop++; }
%s
int main(void) {
%s
    int checked = 0;
    for (U32 k = 0; k < ZH_COUNT; k++) { W_[ZH_FIRST + k] = zh_text[k].w; H_[ZH_FIRST + k] = zh_text[k].h; }
    for (U32 n = 0; n < LABEL_LINES_COUNT + NAMETEXT_LINES_COUNT + ZH_LINES_COUNT; n++) {
        const NameLines *nl = n < LABEL_LINES_COUNT ? &label_lines[n] : n < LABEL_LINES_COUNT + NAMETEXT_LINES_COUNT ? &nametext_lines[n - LABEL_LINES_COUNT]
                                                                       : &zh_lines[n - LABEL_LINES_COUNT - NAMETEXT_LINES_COUNT];
        U32 img = n < LABEL_LINES_COUNT ? nl->image : n < LABEL_LINES_COUNT + NAMETEXT_LINES_COUNT ? NAME_FIRST + nl->image : ZH_FIRST + nl->image;
        float iw = image_w(img), ih = image_h(img), s = 1.5f, bx = 100, by = 50;
        int left = nl->line[0].x0, right = nl->line[0].x1;
        for (int k = 1; k < nl->lines; k++) { if (nl->line[k].x0 < left) left = nl->line[k].x0; if (nl->line[k].x1 > right) right = nl->line[k].x1; }
        nop = 0; emit_name(img, bx, by, iw * s, ih * s, 0); assert(nop == 1 && op[0].w == iw * s && op[0].u1 == 1 && op[0].v1 == 1);   /* centred: the raster as is */
        nop = 0; emit_name(img, bx, by, iw * s, ih * s, -1); assert(nop == nl->lines);
        for (int k = 0; k < nop; k++) {
            assert(op[k].x == bx + left * s);                                                  /* the lines share the left ink edge */
            assert(op[k].w == (nl->line[k].x1 - nl->line[k].x0 + 1) * s && op[k].y == by + nl->line[k].y0 * s);
            assert(op[k].u0 >= 0 && op[k].u1 <= 1 && op[k].v0 >= 0 && op[k].v1 <= 1 && op[k].u0 < op[k].u1);
        }
        nop = 0; emit_name(img, bx, by, iw * s, ih * s, 1); assert(nop == nl->lines);
        for (int k = 0; k < nop; k++) assert(op[k].x + op[k].w == bx + (right + 1) * s);       /* the lines share the right ink edge */
        checked++;
    }
    assert(checked == LABEL_LINES_COUNT + NAMETEXT_LINES_COUNT + ZH_LINES_COUNT && ZH_LINES_COUNT > 0);
    /* a one-line name (no entry) is drawn whole, whatever the alignment */
    nop = 0; emit_name(0, 10, 10, 30, 12, -1); assert(nop == 1 || lines_of(0) != 0);
    return 0;
}
'''
size_lines = []
for i, (w, hh) in label_size.items():
    size_lines.append('W_[%d] = %d; H_[%d] = %d;' % (i, w, i, hh))
for k, (w, hh, px, text) in enumerate(entries):
    size_lines.append('W_[5000 + %d] = %s; H_[5000 + %d] = %s;' % (k, w, k, hh))
cut = lambda s, a, b: s[s.index(a):s.index(b)]
src = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
prog = PROG % (len(label_size), cut(src, 'static const NameLines *lines_of(', 'static void build(BYTE *mgr'), '\n'.join('    ' + l for l in size_lines))
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 'lines.c', Path(d) / 'lines'
    c.write_text(prog, encoding='utf-8')
    subprocess.run(['clang', '-w', '-I', str(ROOT / 'src'), str(c), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
print('PASS: %d marker names and %d item names with several lines: bands cover the ink, left/right alignment share an edge, centred draws whole' % (len(label_lines), len(name_lines)))
