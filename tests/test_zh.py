"""Simplified Chinese (zh_cn), the third language slot. src/labels_zh.h replaces only Korean label rows; every Korean row that is ever
drawn as text (marker names of kinds 1-5, the Korean legend block and zoom hint, room names with a map shape) has a Chinese raster;
item names and legend_text carry a zh block; the bundled Source Han Sans SC subsets and their OFL license are present; the
runtime cycles English -> Korean -> Chinese on the backslash key and keeps Language=zh in the INI."""
from pathlib import Path
import json
import re
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from render_labels import ROW, LEGEND_ROW, parse  # noqa: E402

h = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
z = (ROOT / 'src/labels_zh.h').read_text(encoding='utf-8')
data = json.loads((ROOT / 'data/zh_cn.json').read_text(encoding='utf-8'))
count = int(re.search(r'#define LABEL_COUNT (\d+)', h)[1])
legend_first = int(re.search(r'#define LEGEND_FIRST (\d+)', h)[1])
per_lang = int(re.search(r'#define LEGEND_PER_LANG (\d+)', h)[1])
arrays = dict(re.findall(r'static const unsigned char (px\d+)\[\]=\{([^}]*)\};', h))
_, _, table = parse(h)
rows = [l for l in table if l.startswith('{')]
assert len(rows) == count

zarr = dict(re.findall(r'static const unsigned char (zhpx\d+)\[\]=\{([^}]*)\};', z))
zh = [(int(a), int(w), int(hh), px, float(x), float(y), text) for a, w, hh, px, x, y, text in
      re.findall(r'^\{(\d+),(\d+),(\d+),(zhpx\d+),([-\d.]+)f,([-\d.]+)f,[-\d.]+f,[-\d.]+f\}, /\* (.*) \*/$', z, re.M)]
assert len(zh) == int(re.search(r'#define ZH_COUNT (\d+)', z)[1]) > 300
labels = [e[0] for e in zh]
assert len(set(labels)) == len(labels) and labels == sorted(labels), 'one zh raster per label row'

legend_rows = set(range(legend_first, legend_first + per_lang)) | {count - 2}
replaced = set(labels)
need = 0
for i, line in enumerate(rows):
    fields = line[1:].split(',')
    kind, room, flag, lang = int(fields[0]), int(fields[1]), int(fields[5]), fields[7]
    if i in replaced:
        assert lang == '1' or i in legend_rows, ('zh replaces a non-Korean row', i, line[-60:])
    m = ROW.match(line) or LEGEND_ROW.match(line)
    if kind in (1, 2, 3, 4, 5) and lang == '1':
        im = Image.frombytes('RGBA', (int(m['w']), int(m['h'])), bytes(map(int, arrays[m['px']].split(','))))
        if im.getbbox():
            need += 1
            assert i in replaced, ('no zh raster', i, m['text'])
    if kind == 6 and i in legend_rows:
        need += 1
        assert i in replaced, ('no zh legend raster', i, m['text'])
rooms_zh = json.loads((ROOT / 'data/room_names_zh.json').read_text(encoding='utf-8'))['names']
rooms_ko = [n for n in json.loads((ROOT / 'data/room_names.json').read_text(encoding='utf-8'))['names'] if n['lang'] == 'ko']
assert sorted(n['room'] for n in rooms_zh) == sorted(n['room'] for n in rooms_ko), 'every placed Korean room name has a zh one'
room_entries = [e for e in zh if rows[e[0]].startswith('{0,')]
assert len(room_entries) == len(rooms_zh) and all(0 < e[4] < 1280 and 0 < e[5] < 720 for e in room_entries)

# white rasters with a dark outline, like every other name (the run time tints them)
for a, w, hh, px, x, y, text in zh:
    b = bytes(map(int, zarr[px].split(',')))
    assert len(b) == w * hh * 4 and any(b[k + 3] > 240 and b[k] == b[k + 1] == b[k + 2] == 255 for k in range(0, len(b), 4)), text

# item names and the legend text: a zh block of the same size
t = (ROOT / 'src/item_name_text.h').read_text(encoding='utf-8')
langs = re.findall(r'^\{\d+,\d+,ntpx\d+,\d+,(\d)\}', t, re.M)
assert langs.count('3') == langs.count('1') == langs.count('2')
lt = (ROOT / 'src/legend_text.h').read_text(encoding='utf-8')
assert int(re.search(r'#define LT_COUNT (\d+)', lt)[1]) == 3 * int(re.search(r'#define LT_PER_LANG (\d+)', lt)[1])

# the Chinese font: Source Han Sans SC subsets under the SIL OFL (tools/render_zh.py checks they hold every character)
assert all((ROOT / 'fonts' / f).stat().st_size > 10000 for f in ('SourceHanSansSC-Medium-zh.otf', 'SourceHanSansSC-Bold-zh.otf'))
assert 'SIL Open Font License' in (ROOT / 'fonts/SourceHanSans-LICENSE.txt').read_text(encoding='utf-8')
chars = set(''.join(v for k, g in data.items() if not k.startswith('_') for v in g.values())) - set(' |/')

# runtime: three languages on one key, Language=zh in the INI
c = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
assert 'language = (language + 1) % 3' in c and '"zh"' in c and "v[0] == 'z' && v[1] == 'h' ? 2" in c
assert '#include "labels_zh.h"' in c and '#define IMAGES    (ZH_FIRST + ZH_COUNT)' in c
ini = (ROOT / 'packaging/RE1HD.AnnotatedMap.ini').read_text(encoding='utf-8')
assert 'zh = Simplified Chinese' in ini
print('PASS: zh_cn slot: %d rasters replace Korean rows (%d drawn rows needed, %d room names), item names and legend text in 3 blocks, '
      '%d characters, backslash cycles 3 languages' % (len(zh), need, len(room_entries), len(chars)))
