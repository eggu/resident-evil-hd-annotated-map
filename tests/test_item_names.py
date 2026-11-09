"""Ordinary item names (kind 7, shown with [H]): every kind 7 row has its item id, both languages draw a name in the common-item
white (the run time tints them with the CommonItems colour, #B8BCC4 by default), the names are the data/item_names.json ones, and the runtime asks for them."""
from collections import Counter
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
h = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
t = (ROOT / 'src/item_name_text.h').read_text(encoding='utf-8')
names = json.loads((ROOT / 'data/item_names.json').read_text(encoding='utf-8'))

rows = re.findall(r'^\{(-?\d+),.*?/\* (.*?) \*/$', h[h.index('static const Label labels[]={'):], re.M)[:int(re.search(r'#define LABEL_COUNT (\d+)', h)[1])]
kind7 = {i: int(c[5:]) for i, (k, c) in enumerate(rows) if k == '7'}
assert len(kind7) == 216 and all(c.startswith('item ') for k, c in rows if k == '7')
pairs = {int(a): int(b) for a, b in re.findall(r'\{(\d+),(\d+)\}', t[t.index('item_of_label[]'):])}
assert pairs == kind7, 'item_of_label does not match the labels.h rows'

arrays = dict(re.findall(r'static const unsigned char (ntpx\d+)\[\]=\{([^}]*)\};', t))
entries = re.findall(r'^\{(\d+),(\d+),(ntpx\d+),(\d+),(\d+)\}, /\* (.*?) \*/$', t, re.M)
assert len(entries) == int(re.search(r'#define NT_COUNT (\d+)', t)[1]) == 2 * len(set(kind7.values())) + 2 * 12  # + the synthetic puzzle names
for w, hh, px, item, lang, text in entries:
    if int(item) >= 1000:  # synthetic puzzle names: tests/test_synth_marks.py
        continue
    assert text == names[item][0 if lang == '2' else 1].replace('의 ', ' ') or text == names[item][0 if lang == '2' else 1], (item, text)
    b = list(map(int, arrays[px].split(',')))
    assert len(b) == int(w) * int(hh) * 4
    fill = Counter((b[i + 2], b[i + 1], b[i]) for i in range(0, len(b), 4) if b[i + 3] > 240 and sum(b[i:i + 3]) > 60)
    assert fill.most_common(1)[0][0] == (255, 255, 255), (item, lang)

c = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
assert 'l->kind == 7 ? item_name_image(m->label' in c and 'item_name_image(i, english ? 2 : 1)' in c
print(f'PASS: {len(kind7)} ordinary item rows -> {len(entries)} white names, both languages, from data/item_names.json')

# Defense weapons are exclusive even when both rows share a pickup flag (Morgue 236).
for line in (ROOT / 'src/labels.h').read_text().splitlines():
    m = re.match(r'^\{7,(.*)\}, /\* item (113|121) \*/$', line)
    if m:
        fields = m[1].split(',')
        assert int(fields[5]) & 0x30 == (0x10 if m[2] == '113' else 0x20), line

# A pickup flag holds one item per scenario: different items on one flag must not share character and difficulty bits.
groups = {}
for line in (ROOT / 'src/labels.h').read_text().splitlines():
    m = re.match(r'^\{7,(.*)\}, /\* item (\d+) \*/$', line)
    if m:
        f = m[1].split(',')
        groups.setdefault((f[0], f[4]), []).append((int(f[5]), int(m[2])))
for key, rows in groups.items():
    for i, (a, ia) in enumerate(rows):
        for b, ib in rows[i + 1:]:
            assert ia == ib or not ((a & 0x30 or 0x30) & (b & 0x30 or 0x30) and (a & 0xf or 0xf) & (b & 0xf or 0xf)), (key, a, ia, b, ib)
print(f'PASS: {len(groups)} item pickup flags, no two items share a scenario')
