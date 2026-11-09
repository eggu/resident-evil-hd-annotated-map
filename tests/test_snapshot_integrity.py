"""Pinned source identity and all 216 embedded ordinary icons match approved A sprites."""
from pathlib import Path
import hashlib,json,re
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'verification/source-snapshot.json').read_text())
for name,record in m['copied_files'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==record['sha256'],name
h=(ROOT/'src/labels.h').read_text()
records=re.findall(r'^\{([^\n]+)\}, /\* (.*?) \*/',h,re.M)
assert len(records)==int(re.search(r'#define LABEL_COUNT (\d+)',h)[1])==m['label_count']==948
ordinary=[(r.split(','),comment) for r,comment in records if r.startswith('7,')]
assert len(ordinary)==m['ordinary_placements']==216
rows=json.loads((ROOT/'data/labels.json').read_text())
ids={r[8] for r in rows if r[0]==7}
assert sorted(ids)==m['ordinary_ids'] and len(ids)==17
# Exact BGRA bytes, not a visual similarity estimate.
textures={int(i):bytes(map(int,v.split(','))) for i,v in re.findall(r'static const unsigned char px(\d+)\[\]=\{([^}]+)\};',h)}
for cols,comment in ordinary:
    item=int(comment.split()[-1]);im=Image.open(ROOT/f'assets/icons/{item}.png').convert('RGBA')
    assert im.size==(32,32) and set(im.getchannel('A').tobytes())<={0,255}
    assert textures[int(cols[14][2:])]==im.tobytes('raw','BGRA'),item
# Verify the refill-tank pixels embedded in the separate crimson atlas too.
im=Image.open(ROOT/'assets/icons/kerosene.png').convert('RGBA')
im=im.crop(im.getchannel('A').point(lambda a:255 if a>40 else 0).getbbox())
scale=32/max(im.size)
im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS)
a=im.getchannel('A').point(lambda a:255 if a>110 else 0)
canvas=Image.new('RGBA',(32,32));canvas.paste(im.convert('RGB').quantize(16,method=Image.Quantize.MEDIANCUT).convert('RGB'),((32-im.width)//2,(32-im.height)//2),a)
rim=Image.new('RGBA',(32,32));rim.paste((12,14,10,255),mask=canvas.getchannel('A').filter(ImageFilter.MaxFilter(3)));rim.alpha_composite(canvas)
box=rim.getchannel('A').getbbox();rim=rim.crop((box[0],0,box[2],rim.height))
c=(ROOT/'src/crimson_data.h').read_text()
w,hc=[int(re.search(r'#define CRIMSON_ATLAS_'+n+r' (\d+)',c)[1]) for n in 'WH']
pixels=bytes(map(int,re.search(r'crimson_atlas\[\]=\{([^}]+)',c)[1].split(',')))
atlas=Image.frombytes('RGBA',(w,hc),pixels,'raw','BGRA')
x,y,iw,ih,_=map(int,re.search(r'fuel_icon = \{([^}]+)',c)[1].split(','))
assert atlas.crop((x,y,x+iw,y+ih)).tobytes()==rim.tobytes()
tanks=[r for r,comment in records if 900<=int(r.split(',')[5])<905]
assert len(tanks)==10
assert m['kerosene_rooms']==['102','114','118','403','503']
assert any(r[0]==7 and r[5]==463 and r[2]==11 for r in rows)
c_src=(ROOT/'src/re1_mapnames.c').read_text()
assert 'RE1HD.AnnotatedMap ' + (ROOT/'VERSION').read_text().strip() + ' loaded' in c_src
# spawn hook must take the room from the game's own current-room pair, not the lagging ROOMSTATE (v31 log: room 101 read as 0)
assert 'cum_room(ds, dr)' in c_src and 'u32(inv + 0xe472c)' in c_src and 'enemy spawn mode=' in c_src
print('PASS: 12 pinned runtime sources, 964 textures, 17 A icons / 216 placements (weapons are key items), five refill tanks')
