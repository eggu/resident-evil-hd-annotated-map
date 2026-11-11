"""Category colours (user decisions 2026-11-07 and 2026-11-08): the common-item colour is the cool grey #B8BCC4, a disabled legend row is
the darker grey #6A6A6A, every colour comes from the table in src/colors.h (INI [Colors], one key per category), and every marker name,
legend row and item name raster is white with a dark outline so the draw state (colour = texture x vertex diffuse) can tint it.
Contrast figures are CIE76 distances and WCAG ratios against the legend panel (14,14,18 at ~81%)."""
from pathlib import Path
import math
import re
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from render_labels import ROW, LEGEND_ROW, old_style, parse  # noqa: E402

colors = (ROOT / 'src/colors.h').read_text(encoding='utf-8')
keys = re.findall(r'"(\w+)"', re.search(r'color_keys\[COL_COUNT\] = \{(.*?)\};', colors, re.S)[1])
default = [int(v, 16) for v in re.findall(r'0x([0-9a-f]{6})', re.search(r'color_default\[COL_COUNT\] = \{(.*?)\};', colors, re.S)[1])]
assert keys == ['Rooms', 'Locks', 'KeyItems', 'Files', 'Puzzles', 'Events', 'CommonItems', 'Enemies'] and len(default) == 8
rgb = dict(zip(keys, [((v >> 16) & 255, (v >> 8) & 255, v & 255) for v in default]))
assert rgb['CommonItems'] == (0xb8, 0xbc, 0xc4)                           # cool grey (user decision 2026-11-08)
assert rgb['Puzzles'] == (255, 150, 40) and rgb['Events'] == (0xb0, 0x70, 0xff) and rgb['Locks'] == (255, 205, 70)   # RE0's puzzle orange and event purple
assert re.search(r'#define COLOR_OFF\s+0x6a6a6a', colors) and re.search(r'#define COLOR_READOUT\s+0x8c8c8c', colors)


def lab(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    r, g, b = map(f, c)
    x, y, z = (.4124 * r + .3576 * g + .1805 * b) / .95047, .2126 * r + .7152 * g + .0722 * b, (.0193 * r + .1192 * g + .9505 * b) / 1.08883
    t = lambda q: q ** (1 / 3) if q > .008856 else 7.787 * q + 16 / 116
    return 116 * t(y) - 16, 500 * (t(x) - t(y)), 200 * (t(y) - t(z))


def lum(c):
    lin = [v / 255 / 12.92 if v / 255 <= .04045 else ((v / 255 + .055) / 1.055) ** 2.4 for v in c]
    return .2126 * lin[0] + .7152 * lin[1] + .0722 * lin[2]


delta = lambda a, b: math.dist(lab(a), lab(b))
panel = (11, 11, 15)  # (14, 14, 18) at ~81% over a black map
for a in keys:
    for b in keys:
        if a < b:
            assert delta(rgb[a], rgb[b]) > 20, (a, b, delta(rgb[a], rgb[b]))
assert delta(rgb['CommonItems'], rgb['Puzzles']) > 60 and delta(rgb['CommonItems'], rgb['Events']) > 35
off, readout = (0x6a,) * 3, (0x8c,) * 3
assert delta(off, readout) > 10 and delta(off, rgb['CommonItems']) > 30                       # disabled stays apart from a readout and from the common colour
worst = (58, 58, 62)                                                                           # the panel over a white map
for name, c in list(rgb.items()) + [('off', off)]:
    on_black, on_white = (lum(c) + .05) / (lum(panel) + .05), (lum(c) + .05) / (lum(worst) + .05)
    assert on_black > (3.5 if name == "off" else 4.5) and on_white > (2.0 if name == "off" else 2.8), (name, on_black, on_white)   # the disabled grey only has to stay readable

# every name, legend row and item name raster is white with the outline
h = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
start, end, table = parse(h)
arrays = dict(re.findall(r'static const unsigned char (px\d+)\[\]=\{([^}]*)\};', h))
checked = 0
for line in table:
    m = ROW.match(line) or LEGEND_ROW.match(line)
    if not m or m['text'].startswith('item ') or int(m['kind']) not in (0, 1, 2, 3, 4, 5, 6):
        continue
    im = Image.frombytes('RGBA', (int(m['w']), int(m['h'])), bytes(map(int, arrays[m['px']].split(','))))
    if im.getbbox():
        assert old_style(im)[0] == (255, 255, 255), m['text']
        checked += 1
assert checked > 600


def neutral_white(px):
    """Every opaque pixel is a grey between the outline and white (edge pixels blend them) and pure white is there: no colour is baked in."""
    b = list(map(int, px.split(',')))
    opaque = [(b[i], b[i + 1], b[i + 2]) for i in range(0, len(b), 4) if b[i + 3] > 240]
    return bool(opaque) and all(p[0] == p[1] == p[2] for p in opaque) and (255, 255, 255) in opaque


t = (ROOT / 'src/item_name_text.h').read_text(encoding='utf-8')
names = re.findall(r'static const unsigned char ntpx\d+\[\]=\{([^}]*)\};', t)
assert len(names) == int(re.search(r'#define NT_COUNT (\d+)', t)[1]) and all(neutral_white(px) for px in names)
lg = (ROOT / 'src/legend_text.h').read_text(encoding='utf-8')
rows = re.findall(r'static const unsigned char ltpx\d+\[\]=\{([^}]*)\};', lg)
assert len(rows) == int(re.search(r'#define LT_COUNT (\d+)', lg)[1]) == 3 * 58 and all(neutral_white(px) for px in rows)  # Korean, English, Chinese

# the runtime tints with the table: names by category, the legend rows by build_legend, MODULATE in the draw state
c = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
assert '{0,1,4},{0,2,2},{0,3,0}' in c                                                          # COLOROP MODULATE, ARG1 texture, ARG2 diffuse
assert 'emit_color = name_alpha | cat_color[COL_ROOM]' in c and 'emit_color = name_alpha | cat_color[cat_color_of(m->cat)]' in c
assert 'cat_color[row_color[r]]' in c and 'COLOR_OFF' in c and 'load_colors();' in c
print('PASS: colours from src/colors.h (common items #B8BCC4, disabled #6A6A6A), %d marker/legend rasters, all item names and legend text white, MODULATE tint in the draw state' % checked)
