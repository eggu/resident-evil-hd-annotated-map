"""Compile the real atlas packer and emit() against today's label sizes: every image placed, inside a page, no overlap."""
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / 'src'
s = (HERE / 're1_mapnames.c').read_text()
code = s[s.index('#define PAGE '):s.index('static int make_pages(')] + s[s.index('/* Queue image i'):s.index('/* Room of a corpse')]
sizes = [(int(w), int(h)) for w, h in re.findall(r'^\{-?\d+,-?\d+,-?\d+,\d+,\d+,\d+,\d+,\d+,[^,]+,[^,]+,[^,]+,[^,]+,(\d+),(\d+),px',
                                                  (HERE / 'labels.h').read_text(), re.M)]
cw, ch = (int(re.search(rf'#define CRIMSON_ATLAS_{c} (\d+)', (HERE / 'crimson_data.h').read_text())[1]) for c in 'WH')
sizes.append((cw, ch))
icon_n = int(re.search(r'#define ICON_COUNT (\d+)', (HERE / 'labels.h').read_text())[1])
icon_sizes = [(int(w), int(h)) for w, h in re.findall(r'\{(\d+),(\d+),icpx\d+\}', (HERE / 'labels.h').read_text())]
assert len(icon_sizes) == icon_n
text_sizes = [(int(w), int(h)) for w, h in re.findall(r'^\{(\d+),(\d+),ltpx\d+\}', (HERE / 'legend_text.h').read_text(), re.M)]
assert len(text_sizes) == int(re.search(r'#define LT_COUNT (\d+)', (HERE / 'legend_text.h').read_text())[1])
name_sizes = [(int(w), int(h)) for w, h in re.findall(r'^\{(\d+),(\d+),ntpx\d+,', (HERE / 'item_name_text.h').read_text(), re.M)]
assert len(name_sizes) == int(re.search(r'#define NT_COUNT (\d+)', (HERE / 'item_name_text.h').read_text())[1])
prog = '''#include <assert.h>
#include <stdlib.h>
typedef unsigned U32; typedef unsigned char BYTE;
typedef struct { float x, y, z, rhw; U32 color; float u, v; } Vertex;
typedef struct { U32 w, h; const BYTE *px; } Label;
#define LABEL_COUNT %d
#define CRIMSON_ATLAS_W %d
#define CRIMSON_ATLAS_H %d
#define ICON_COUNT %d
#define LT_COUNT %d
#define NT_COUNT %d
typedef struct { float l, t, r, b; } Box;
typedef struct { Box box; U32 weight; } Occupied;
static const BYTE crimson_atlas[1];
static const struct { U32 w, h; const BYTE *px; } legend_text[] = {%s};
static const struct { U32 w, h; const BYTE *px; } item_name_text[] = {%s};
static const Label labels[] = {%s};
static const struct { U32 w, h; const BYTE *px; } icons[] = {%s};
''' % (len(sizes) - 1, cw, ch, icon_n, len(text_sizes), len(name_sizes), ','.join('{%d,%d,0}' % wh for wh in text_sizes), ','.join('{%d,%d,0}' % wh for wh in name_sizes), ','.join('{%d,%d,0}' % wh for wh in sizes[:-1]), ','.join('{%d,%d,0}' % wh for wh in icon_sizes)) + code + '''
int main(void) {
 pack(); assert(npages >= 1 && npages <= MAXPAGES);
 for (U32 i = 0; i < IMAGES; i++) {
  assert(slot[i].page < npages && slot[i].x + image_w(i) <= PAGE && slot[i].y + image_h(i) <= PAGE);
  for (U32 j = 0; j < i; j++) if (slot[i].page == slot[j].page)
   assert(slot[i].x + image_w(i) + ATLAS_PAD <= slot[j].x || slot[j].x + image_w(j) + ATLAS_PAD <= slot[i].x ||
          slot[i].y + image_h(i) + ATLAS_PAD <= slot[j].y || slot[j].y + image_h(j) + ATLAS_PAD <= slot[i].y);
 }
 fit_screen(3440, 1440, 2560, 1440); assert(fit == 1 && shift_x == 440 && shift_y == 0);
 fit_screen(1920, 1200, 1920, 1080); assert(fit == 1 && shift_x == 0 && shift_y == 60);
 fit_screen(1024, 768, 1024, 576); assert(fit == 1 && shift_x == 0 && shift_y == 96);
 fit_screen(3840, 2160, 3840, 2160); assert(fit == 1 && shift_x == 0 && shift_y == 0);
 fit_screen(1280, 720, 2560, 1440); assert(fit == .5f && shift_x == 0 && shift_y == 0);
 fit_screen(3440, 1440, 2560, 1440); emit(LABEL_COUNT, 10, 20, 30, 40, 0, 0, 1, 1);
 assert(verts[layer][slot[LABEL_COUNT].page][nverts[layer][slot[LABEL_COUNT].page] - 6].x == 449.5f);
 nverts[layer][slot[LABEL_COUNT].page] = 0; fit_screen(100, 100, 100, 100);
 emit(LABEL_COUNT, 10, 20, 30, 40, 0, 0, 1, 1); U32 p = slot[LABEL_COUNT].page;
 assert(nverts[0][p] == 6 && verts[0][p][0].u * PAGE == slot[LABEL_COUNT].x && verts[0][p][5].v * PAGE == slot[LABEL_COUNT].y + CRIMSON_ATLAS_H);
 assert(verts[0][p][5].x == 39.5f && verts[0][p][5].y == 59.5f);
 for (U32 i = 0; i < ICON_COUNT; i++) assert(image_w(LABEL_COUNT + 2 + i) == 32 && image_h(LABEL_COUNT + 2 + i) == 32);
 for (U32 i = 0; i < LT_COUNT; i++) assert(image_w(TEXT_FIRST + i) == legend_text[i].w && image_h(TEXT_FIRST + i) == legend_text[i].h);
 return npages;
}
'''
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 'atlas.c', Path(d) / 'atlas'
    c.write_text(prog)
    subprocess.run(['clang', '-w', str(c), '-o', str(exe)], check=True)
    pages = subprocess.run([str(exe)]).returncode
    assert 1 <= pages <= 4, pages
print(f'PASS: {len(sizes) + icon_n + len(text_sizes) + len(name_sizes) + 1} images packed on {pages} page(s) of 2048px with 2px gaps; emit maps UVs into the page')
