"""Room names (tools/layout_room_names.py): the committed rows and rasters are what the generator makes from the committed
inputs (reproducible), its standalone check passes, and the check catches broken layouts. Restated here: every anchor in
its room, leaders axis-aligned and at most LEADER_MAX, the 150% wrap rule, no two names of a floor overlapping."""
from pathlib import Path
import copy
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import layout_room_names as L  # noqa: E402
import room_geometry as rg  # noqa: E402

text = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
rows = L.read_rows(text)
names, shapes, exclusive = L.layout(rows, rg.load())
assert len(names) == 288 and not L.check(names, shapes, exclusive)

# reproducible: rows, rasters and data/room_names.json are what the generator writes
lines = text.split('\n')
arrays = dict(re.findall(r'static const unsigned char (px\d+)\[\]=\{([^}]*)\};', text))
saved = {(n['room'], n['lang']): n for n in json.loads((ROOT / 'data/room_names.json').read_text(encoding='utf-8'))['names']}
for n in names:
    m = L.ROW.match(lines[n['row']])
    im, ax, ay = L.raster(n)
    assert (int(m['w']), int(m['h'])) == im.size and arrays[m['px']] == ','.join(map(str, im.tobytes())), n['text']
    assert abs(float(m['x']) - n['anchor'][0]) < .01 and abs(float(m['y']) - n['anchor'][1]) < .01
    assert abs(float(m['ax']) - ax) < .01 and abs(float(m['ay']) - ay) < .01 and m['text'] == ' / '.join(n['lines'])
    s = saved[(n['room'], n['lang'])]
    assert s['box'] == list(n['box']) and s['lines'] == n['lines'] and (s['leader'] is None) == (n['leader'] is None)

# the rules, restated
for n in names:
    assert shapes[n['room']].contains(*n['anchor']), n['text']
    if n['leader']:
        (x0, y0), (x1, y1) = n['leader']
        assert (x0 == x1 or y0 == y1) and abs(x1 - x0) + abs(y1 - y0) <= L.LEADER_MAX + 1, n['text']
    room_w = L.Mask(shapes[n['room']]).width if len(n['lines']) > 1 or ' ' in n['text'] else None
    one_line = L.text_size([n['text']], L.SIZE[n['lang_id']])[0] / L.RASTER
    if len(n['lines']) > 1:
        assert ' ' in n['text'] and one_line > L.WRAP * room_w and len(n['lines']) == 2, n['text']
    elif room_w is not None:
        assert one_line <= L.WRAP * room_w, n['text']
for a in names:
    for b in names:
        if a['row'] < b['row'] and (a['area'], a['floor'], a['lang']) == (b['area'], b['floor'], b['lang']) and (a['room'], b['room']) not in exclusive:
            assert not L.hit(a['box'], b['box']), (a['text'], b['text'])

# the check catches what it must
broken = copy.deepcopy(names)
broken[0]['anchor'] = (0.5, 0.5)
assert any('anchor outside' in e for e in L.check(broken, shapes, exclusive))
broken = copy.deepcopy(names)
a = next(n for n in broken if not n['leader'])
b = next(n for n in broken if n is not a and (n['area'], n['floor'], n['lang']) == (a['area'], a['floor'], a['lang']) and (a['room'], n['room']) not in exclusive)
b['box'] = a['box']
assert any('overlaps' in e for e in L.check(broken, shapes, exclusive))
broken = copy.deepcopy(names)
c = next(n for n in broken if n['leader'])
(x0, y0), _ = c['leader']
c['leader'] = [(x0, y0), (x0 + L.LEADER_MAX + 10, y0)]
assert any('too long' in e for e in L.check(broken, shapes, exclusive))

# the runtime draws a room name from its anchor
src = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
assert 'float x = cx - l->ax * tk, y = cy - l->ay * tk;' in src
print('PASS: %d room names reproducible; anchors in rooms, %d leaders <= %d, 150%% wrap, no overlaps; check catches 3 mutants'
      % (len(names), sum(1 for n in names if n['leader']), L.LEADER_MAX))
