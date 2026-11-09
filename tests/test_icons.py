"""Every icons[] sprite in labels.h (badges, item icons, enemy heads) is byte-identical to its PNG in assets/icons."""
from pathlib import Path
import re
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
h = (ROOT / 'src/labels.h').read_text()
embedded = {int(i): bytes(map(int, v.split(','))) for i, v in re.findall(r'static const unsigned char icpx(\d+)\[\]=\{([^}]+)\};', h)}
n = int(re.search(r'#define ICON_COUNT (\d+)', h)[1])
assert len(embedded) == n == 99  # 87 + nine weapons (key items since 2026-11-07) + the three lamp eyes
assert re.search(r'icons\[\]=\{(?:\{32,32,icpx\d+\},?){%d}\}' % n, h)
pngs = {}
for f in sorted((ROOT / 'assets/icons').glob('*.png')):
    if f.name == 'kerosene.png': continue
    im = Image.open(f).convert('RGBA')
    assert im.size == (32, 32) and set(im.getchannel('A').tobytes()) <= {0, 255}, f.name
    pngs[f.name] = im.tobytes('raw', 'BGRA')
names = {n: [k for k, b in pngs.items() if b == px] for n, px in embedded.items()}
assert all(names.values()), [n for n, k in names.items() if not k]
for badge in ('badge-puzzle', 'badge-event', 'badge-document', 'badge-map', 'badge-typewriter', 'badge-itembox'):
    assert pngs[badge + '.png'] in embedded.values(), badge
enemy_rows = [int(v) for v in re.search(r'enemy_icon_of_em\[64\]=\{([^}]+)\}', h)[1].split(',')]
drawn = {v for v in enemy_rows if v != 255}
assert len(enemy_rows) == 64 and drawn and all(v < 85 for v in drawn)
assert all(any(k.startswith('enemy-') for k in names[v]) for v in drawn), 'enemy_icon_of_em must point at enemy heads'
assert len(list((ROOT / 'assets/icons').glob('enemy-*.png'))) == 16  # 15 approved heads + grey crimson (generated)
for macro, png in (('CRIMSON_ICON', 'enemy-crimson-head.png'), ('CRIMSON_ICON_GREY', 'enemy-crimson-head-grey.png')):
    assert png in names[int(re.search(rf'#define {macro} (\d+)', h)[1])], macro
weapons = {3, 4, 6, 7, 10, 11, 12, 13, 15}
assert all(any(k == f'{w}.png' for k in names[87 + i]) for i, w in enumerate((3, 6, 13, 7, 10, 12, 11, 4, 15))), 'weapon icons'
assert all(any(k == f'symbol-eye-{i}.png' for k in names[95 + i]) for i in (1, 2, 3)), 'lamp eye icons are icons 97-99'
print(f'PASS: {len(embedded)} embedded icons (4 badges, {len(drawn)} enemy heads) match assets/icons PNG bytes')
