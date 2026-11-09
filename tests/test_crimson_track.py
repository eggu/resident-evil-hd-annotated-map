"""Compile the real death-room tracker: a death in the current room's table is recorded; a save load
(many records at once) and IDs outside the room table are not; INI section round-trips."""
import subprocess
import tempfile
from pathlib import Path

s = (Path(__file__).resolve().parents[1] / 'src/re1_mapnames.c').read_text()
code = s[s.index('static volatile int death_room[1024];'):s.index('/* ---- Enemy markers from real spawns')]
prog = '''#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef unsigned U32; typedef unsigned char BYTE;
#define EXE_CRIMSON 0x10
#define EXE_ROOMSTATE 0x20
static BYTE image[0x40], obj[0xc0c0], rs[0x28], *exe = image;
static const int stage_first[7] = {0, 0, 37, 72, 104, 129, 154};
static char ini_path[4], ini[4096];
static int writes;
static U32 u32(const void *p) { U32 v; memcpy(&v, p, 4); return v; }
static int readable(const void *p, U32 n) { return p != 0; }
static void log_line(const char *s) {}
static int lstrlenA(const char *s) { return (int)strlen(s); }
#define wsprintfA sprintf
static void WritePrivateProfileStringA(const char *sec, const char *k, const char *v, const char *f) {
    writes++; char *e = ini; while (*e) e += strlen(e) + 1; sprintf(e, "%s=%s", k, v); }
static unsigned GetPrivateProfileSectionA(const char *sec, char *buf, unsigned n, const char *f) {
    memcpy(buf, ini, sizeof ini); return 0; }
static void revive(U32 id, float t) { memcpy(obj + 0x40 + id * 0x30 + 0x2c, &t, 4); }
static void room(U32 stage, U32 r) { memcpy(rs + 0x20, &stage, 4); memcpy(rs + 0x24, &r, 4); }
''' + code + '''
int main(void) {
    BYTE *o = obj, *r = rs; memcpy(image + EXE_CRIMSON, &o, sizeof o); memcpy(image + EXE_ROOMSTATE, &r, sizeof r);
    U32 table[3] = {384, 385, 0}; memcpy(obj + 0xc040, table, sizeof table);
    load_death_rooms(); assert(death_room[384] == -1);
    room(1, 1); track_deaths();                        /* prime */
    revive(384, 9000); track_deaths(); assert(death_room[384] == 1 && writes == 1);
    room(2, 0x1d); revive(384, 12000); track_deaths(); assert(death_room[384] == 66); /* re-killed upstairs */
    revive(500, 5000); track_deaths(); assert(death_room[500] == -1);               /* not in this room */
    for (U32 i = 0; i < 6; i++) revive(385 + i, 7000);  /* load: many at once */
    track_deaths(); assert(death_room[385] == -1);
    load_death_rooms(); assert(death_room[384] == 66 && death_room[500] == -1);      /* INI: last write wins */
    return 0;
}
'''
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 't.c', Path(d) / 't'
    c.write_text(prog)
    subprocess.run(['clang', '-w', str(c), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
print('PASS: death room recorded for current-room IDs, re-kill moves it, loads and foreign IDs ignored, INI round-trip')
