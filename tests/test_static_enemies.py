"""Scripted bosses without a recorded spawn (static_enemies in src/re1_mapnames.c): Plant 42 / 식물 42 방 (Residence Plant 42 Room).
Full-data check of boss rooms: the defeat flag is the one item_state.h already uses to release the Helmet Key in that room, the
point is that key's floor spot, the room and enemy exist in the data, and the icon is Plant 42's."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
c = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
table = re.search(r'static_enemies\[\] = \{(.*?)\};', c, re.S)[1]
rows = [tuple(float(v.rstrip('f')) for v in r.split(',')) for r in re.findall(r'\{([^{}]*)\}', table)]
assert rows == [(116, 17, 62, 578.0, 169.0, 1)], rows  # the last value: drawn under the room name (user decision 2026-11-08)
room, em, flag, wx, wz, under_name = rows[0]
rooms = {r['native_index']: r for r in json.loads((ROOT / 'data/rooms.json').read_text(encoding='utf-8'))}
assert rooms[116]['room_id'] == '40c' and rooms[116]['name_ko'] == '식물 42 방'
s = (ROOT / 'src/item_state.h').read_text(encoding='utf-8')
assert 'kind==4 && flag==69 && source==116) return state_bit(b1,62)' in s      # Helmet Key only once Plant 42 is dead
h = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
key = re.search(r'^\{4,116,116,2,2,69,0,2,[-\d.]+f,[-\d.]+f,(-?[\d.]+)f,(-?[\d.]+)f', h, re.M)
assert key and abs(float(key[1]) - wx) < 1 and abs(float(key[2]) - wz) < 1, key and key.groups()
icons = [int(v) for v in re.search(r'enemy_icon_of_em\[64\]=\{([^}]+)\}', h)[1].split(',')]
assert icons[17] != 255
assert 'e->under_name && room_name_spot(e->room' in c and 'cy = bottom + is / 2' in c  # centred below the room name's raster box
print('PASS: Plant 42 (em 17) in 식물 42 방 / Plant 42 Room: defeat flag bank1 62 = the Helmet Key gate, drawn under the room name, icon drawn')
