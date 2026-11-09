"""Compile the actual capture and snapshot blocks; verify one scan per opening."""
from pathlib import Path
import subprocess
import tempfile
s = (Path(__file__).resolve().parents[1] / 'src/re1_mapnames.c').read_text()
capture = s[s.index('void __cdecl capture_map'):s.index('/* thunk i:')].replace('__cdecl ', '')
a = s.index('    static Live live[MAXU];', s.index('static void draw('))
b = s.index('    view.dev = dev;', a)
block = s[a:b]
assert s.count('nlive = live_units(cur, live);') == 1
program = '''#include <assert.h>
#include <string.h>
typedef unsigned int U32;
typedef unsigned char BYTE;
#define MAXU 128
#define EXE_ROOMSTATE 0x100
static BYTE storage[512], room[40], map[0x62a0], other[0x62a0];
static BYTE *exe=storage;
static void *map_object;
static U32 frame,map_frame,map_session;
static const int stage_first[7]={0,0,37,72,104,129,154};
typedef struct { U32 flag; float x,y; } Live;
static int scans;
static float position=1;
static U32 u32(const void *p) { U32 n; memcpy(&n,p,4); return n; }
static int readable(void *p, int n) { return p!=0; }
static U32 live_units(U32 room, Live *out) { scans++; out[0].x=position; return 1; }
''' + capture + '\nstatic float snapshot(void) {\n' + block + '''
 return nlive ? live[0].x : -1;
}
int main(void) {
 BYTE *r=room; memcpy(storage+EXE_ROOMSTATE,&r,sizeof r);
 *(U32 *)(room+0x20)=1; *(U32 *)(room+0x24)=5;
 capture_map(map); assert(snapshot()==1 && scans==1);
 *(U32 *)(map+0x60ac)=1;
 position=2;
 for(int i=0;i<100;i++){ frame++; capture_map(map); assert(snapshot()==1); }
 assert(scans==1);
 *(U32 *)(map+0x629c)=1; frame++; capture_map(map);
 *(U32 *)(map+0x629c)=2; frame++; capture_map(map);
 *(U32 *)(map+0x629c)=0; frame++; capture_map(map);
 assert(snapshot()==1 && scans==1);
 frame+=10; capture_map(map); assert(snapshot()==2 && scans==2);
 position=3; *(U32 *)(map+0x60ac)=0; frame++; capture_map(map);
 assert(snapshot()==3 && scans==3);
 position=4; capture_map(other); assert(snapshot()==4 && scans==4);
 position=5; for(int i=0;i<50;i++){ frame++; capture_map(other); assert(snapshot()==4); } /* state 0 held: one session */
 assert(scans==4);
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d); (p/'snapshot.c').write_text(program)
 subprocess.run(['clang',str(p/'snapshot.c'),'-o',str(p/'snapshot')],check=True)
 subprocess.run([str(p/'snapshot')],check=True)
print('PASS: frozen across 100 frames and box subviews; refresh on reopen/init/new map; state 0 held for 50 frames = one session')
