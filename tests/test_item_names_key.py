"""The real poll_keys, compiled on the host with scripted keys (user decision 2026-11-08, the shared numbering): 1 rooms, 2 locks,
3 key items, 4 files/maps, 5 puzzles, 6 events, 7 common items, 8 enemies (hold: minutes), 9 scope, 0 all, backslash language. H cycles item names all -> no common -> off (RE0 HD, user decision 2026-11-08); nothing else touches
them (the Aim hold was removed, user decision 2026-11-07); one press toggles once inside the rest; the map draws names only for
'item_names' (marks.h: 2 leaves out the ordinary items)."""
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / 'src/re1_mapnames.c').read_text()
cut = lambda a, b: s[s.index(a):s.index(b)]
assert 'marks_layout(marks, nmarks, occ, nocc, MAXOCC, is, item_names, W, H)' in s  # what build() passes as `names`

PROG = r'''
#include <assert.h>
#include <string.h>
typedef unsigned U32; typedef long LONG; typedef unsigned char BYTE; typedef unsigned long DWORD;
#define VK_SHIFT 0x10
#define VK_RBUTTON 2
#define VK_SUBTRACT 0x6d
#define VK_ADD 0x6b
#define VK_OEM_3 0xc0
#define VK_OEM_MINUS 0xbd
#define VK_OEM_PLUS 0xbb
#define VK_OEM_4 0xdb
#define VK_OEM_6 0xdd
#define VK_OEM_5 0xdc
static volatile LONG hidden, language, all_off, visibility, crimson_time, legend_open = 1, name_size = 100, name_opacity = 70, icon_size = 100, icon_opacity = 80;
static volatile LONG item_names, modifier_vk = VK_SHIFT;
#define CRIMSON_KIND 8
#define GROUPS 7
#define EVENT_KIND 6
static const int toggle_kind[GROUPS] = {0, 1, 4, 5, 2, 6, 7};
#define InterlockedXor(p, v) (*(p) ^= (v))
static int map_is_open = 1, front = 1, saves; static DWORD now; static int down[256];
static int map_open(void) { return map_is_open; }
static int game_in_front(void) { return front; }
static void save_settings(void) { saves++; }
static short GetAsyncKeyState(int k) { return down[k] ? (short)0x8000 : 0; }
static DWORD GetTickCount(void) { return now; }
#include "hold_key.h"
''' + cut('static int step_by(', '/* 2x view.') + r'''
static void tap(int key) { down[key] = 1; poll_keys(); down[key] = 0; poll_keys(); now += 400; }
int main(void) {
    assert(!item_names);                                  /* hidden at first */
    tap('H');         assert(item_names == 1 && saves == 1);   /* all */
    tap('H');         assert(item_names == 2 && saves == 2);   /* all except ordinary items */
    tap('H');         assert(item_names == 0 && saves == 3);   /* hidden */
    tap('H');         assert(item_names == 1);                  /* and around again */
    down[VK_RBUTTON] = 1; poll_keys();                    /* the right mouse button (the old Aim) changes nothing */
    assert(item_names == 1); down[VK_RBUTTON] = 0; poll_keys(); assert(item_names == 1);
    int before = saves; down['H'] = 1; poll_keys(); now += 50; poll_keys(); now += 100; poll_keys();   /* one held press: one step */
    assert(item_names == 2 && saves == before + 1); down['H'] = 0; poll_keys();
    now += 400; item_names = 1; map_is_open = 0; tap('H'); assert(item_names == 1);   /* map closed: ignored */
    map_is_open = 1; front = 0; tap('H'); assert(item_names == 1);                    /* game not in front: ignored */
    /* the numbering: key -> HiddenKinds bit, one toggle per press */
    map_is_open = 1; front = 1; now += 400; hidden = 0;
    static const struct { int key, bit; } groups[] = {{'1', 1}, {'2', 2}, {'3', 16}, {'4', 32}, {'5', 4}, {'6', 64}, {'7', 128}, {'8', 256}};
    for (int i = 0; i < 8; i++) { tap(groups[i].key); assert(hidden == groups[i].bit); tap(groups[i].key); assert(hidden == 0); }
    assert(!crimson_time);                                  /* a tap never touches the minutes */
    hidden = 0; down['8'] = 1; poll_keys(); now += 600; poll_keys(); down['8'] = 0; poll_keys(); now += 400;
    assert(crimson_time == 1 && hidden == 0);               /* a long press of 8 with enemies on: the minutes left */
    hidden = 256; down['8'] = 1; poll_keys(); now += 600; poll_keys(); down['8'] = 0; poll_keys(); now += 400;
    assert(crimson_time == 1);                              /* enemies off: the long press does nothing */
    hidden = 0;
    assert(visibility == 0); tap('9'); assert(visibility == 1); tap('9'); assert(visibility == 2); tap('9'); assert(visibility == 0);   /* 9 is the scope */
    assert(language == 0); tap(VK_OEM_5); assert(language == 1); tap(VK_OEM_5); assert(language == 2); tap(VK_OEM_5); assert(language == 0); /* backslash: English -> Korean -> Chinese */
    tap('0'); assert(all_off == 1); tap('0'); assert(all_off == 0);
    for (int old = 0; old < 1; old++) { visibility = 0; tap('8'); assert(visibility == 0 && hidden == 256); tap('8'); }               /* 8 no longer changes the scope */
    hidden = 0; language = 1; tap('9'); assert(language == 1);                                                                          /* 9 no longer changes the language */
    return 0;
}
'''
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 'keys.c', Path(d) / 'keys'
    c.write_text(PROG)
    subprocess.run(['clang', '-w', '-I', str(ROOT / 'src'), str(c), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
print('PASS: the 1-9, 0, backslash and H keys of the shared numbering; H cycles item names all / no common / off; one press toggles once; ignored when the map is closed')
