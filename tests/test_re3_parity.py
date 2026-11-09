"""Real runtime fragments, compiled on the host: settings (clamps, legacy TextSize, the Version 3 and 4 migrations, the new key numbering
of HiddenKinds, [Colors], the atomic save that leaves [Colors] and the comments alone) and the all-scope flag-test hook against a fake image. Name placement is tests/test_marks.py."""
import subprocess
import tempfile
from pathlib import Path

s = (Path(__file__).resolve().parents[1] / 'src/re1_mapnames.c').read_text()
cut = lambda a, b: s[s.index(a):s.index(b)]

SETTINGS = r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned U32; typedef long LONG; typedef unsigned char BYTE;
#define MAX_PATH 260
#define VK_SHIFT 0x10
#define VK_CONTROL 0x11
#define FALSE 0
#define ERROR_FILE_NOT_FOUND 2
#define MOVEFILE_REPLACE_EXISTING 1
#define MOVEFILE_WRITE_THROUGH 8
#define wsprintfA sprintf
#define EVENT_KIND 6
#include "colors.h"
static const char *fake[16][2]; static int nfake; static char written[32][2][16], written_sec[32][16]; static int nwritten, fail_write, moved, deleted, logged;
static char write_file[MAX_PATH], moved_from[MAX_PATH], moved_to[MAX_PATH];
static const char *lookup(const char *k) { for (int i = 0; i < nfake; i++) if (!strcmp(fake[i][0], k)) return fake[i][1]; return 0; }
static int GetPrivateProfileIntA(const char *sec, const char *k, int d, const char *f) { const char *v = lookup(k); return v ? atoi(v) : d; }
static void GetPrivateProfileStringA(const char *sec, const char *k, const char *d, char *o, unsigned n, const char *f) { const char *v = lookup(k); strcpy(o, v ? v : d); }
static int WritePrivateProfileStringA(const char *sec, const char *k, const char *v, const char *f) {
    if (fail_write && !strcmp(k, "HiddenKinds")) return 0;
    strcpy(write_file, f); strcpy(written_sec[nwritten], sec); strcpy(written[nwritten][0], k); strcpy(written[nwritten][1], v); nwritten++; return 1; }
static int CopyFileA(const char *a, const char *b, int fail) { return 1; }
static unsigned GetLastError(void) { return 0; }
static int MoveFileExA(const char *a, const char *b, unsigned f) { moved++; strcpy(moved_from, a); strcpy(moved_to, b); return f == (MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH); }
static int DeleteFileA(const char *a) { deleted++; return 1; }
static void log_line(const char *s) { logged++; }
static int map_open(void) { return 0; }
static int game_in_front(void) { return 0; }
''' + cut('static volatile LONG hidden;', 'static void log_line(const char *s) {') + r'''
static int ini(const char *k1, const char *v1, const char *k2, const char *v2) {
    nfake = 0; if (k1) { fake[nfake][0] = k1; fake[nfake++][1] = v1; } if (k2) { fake[nfake][0] = k2; fake[nfake++][1] = v2; }
    return load_settings(); }
static const char *saved(const char *k) { for (int i = 0; i < nwritten; i++) if (!strcmp(written[i][0], k)) return written[i][1]; return 0; }
int main(void) {
    strcpy(ini_path, "x.ini");
    assert(ini(0, 0, 0, 0) == 1);          assert(name_size == 100 && name_opacity == 70);        /* defaults; no Version: migrate */
    assert(icon_size == 100 && icon_opacity == 80 && !item_names && legend_open && modifier_vk == VK_SHIFT && !door_key_unvisited);
    assert(hidden == 502);                                                                      /* rooms only; events (spoilers) hidden too */
    assert(ini("Version", "4", 0, 0) == 0);                                                     /* migrated once */
    assert(ini("Version", "3", "HiddenKinds", "0") == 1 && hidden == 64);                         /* v3 had no events group: hidden after the migration */
    assert(ini("Version", "3", "HiddenKinds", "438") == 1 && hidden == (438 | 64));
    assert(ini("Version", "4", "HiddenKinds", "0") == 0 && hidden == 0);                          /* v4: kept as saved */
    assert(ini("Version", "4", "HiddenKinds", "438") == 0 && hidden == 438);
    assert(ini("Version", "4", "HiddenKinds", "1023") == 0 && hidden == 0x1ff);                   /* only the nine group bits */
    assert(ini("Version", "2", "ItemNames", "1") == 1 && item_names == 1);                               /* v2 on -> all */
    ini("Version", "2", "ItemNames", "0"); assert(item_names == 0);                               /* v2 off -> hidden */
    ini("Version", "2", "ItemNames", "2"); assert(item_names == 1);                               /* v2 only knew on/off: non-zero is on */
    ini("Version", "3", "ItemNames", "2"); assert(item_names == 2);                               /* v3: no common */
    ini("Version", "3", "ItemNames", "1"); assert(item_names == 1);
    ini("Version", "3", "ItemNames", "0"); assert(item_names == 0);
    ini("Version", "3", "ItemNames", "7"); assert(item_names == 0);                               /* out of range: hidden */
    ini("Version", "3", "ItemNames", "-1"); assert(item_names == 0);
    ini("TextSize", "80", 0, 0);           assert(name_size == 80);                              /* v30 INI migrates */
    ini("TextSize", "85", 0, 0);           assert(name_size == 90);                              /* snapped to 10 */
    ini("TextSize", "300", 0, 0);          assert(name_size == 150);                             /* upper clamp */
    ini("TextSize", "10", 0, 0);           assert(name_size == 50);                              /* lower clamp */
    ini("NameSize", "60", "TextSize", "120"); assert(name_size == 60);                           /* new key wins */
    ini("NameSize", "0", 0, 0);            assert(name_size == 50);                              /* 0 is a value, not "missing" */
    ini("NameOpacity", "5", 0, 0);         assert(name_opacity == 10);
    ini("NameOpacity", "0", 0, 0);         assert(name_opacity == 10);
    ini("NameOpacity", "130", 0, 0);       assert(name_opacity == 100);
    ini("NameOpacity", "74", 0, 0);        assert(name_opacity == 70);
    ini("IconSize", "260", "IconOpacity", "3"); assert(icon_size == 200 && icon_opacity == 10);
    ini("Modifier", "Ctrl", "DoorKey", "Unvisited"); assert(modifier_vk == VK_CONTROL && door_key_unvisited);
    ini("Modifier", "shift", "DoorKey", "Center"); assert(modifier_vk == VK_SHIFT && !door_key_unvisited);
    ini("ItemNames", "1", "Legend", "0");  assert(item_names && !legend_open);
    assert(step10(-3, 50, 150, 100) == 100);
    name_size = 70; name_opacity = 40; nwritten = 0; moved = deleted = 0; save_settings();
    assert(!strcmp(write_file, "x.ini.tmp") && moved == 1 && !strcmp(moved_from, "x.ini.tmp") && !strcmp(moved_to, "x.ini"));
    assert(!strcmp(saved("NameSize"), "70") && !saved("TextSize") && !strcmp(saved("Version"), "4"));  /* legacy key never written back */
    for (int i = 0; i < nwritten; i++) assert(!strcmp(written_sec[i], "AnnotatedMap"));        /* [Colors], [CrimsonRooms] and every comment stay as the user left them */
    for (int i = 0; i < nwritten; i++) for (int c = 0; c < COL_COUNT; c++) assert(strcmp(written[i][0], color_keys[c]));
    assert(!strcmp(saved("ItemNames"), "1") && !strcmp(saved("Legend"), "0") && !strcmp(saved("Modifier"), "Shift") && !strcmp(saved("DoorKey"), "Center"));
    item_names = 2; nwritten = 0; save_settings(); assert(!strcmp(saved("ItemNames"), "2"));       /* the state is saved as is */
    /* [Colors]: defaults, #RRGGBB (with or without #, any case), an unreadable value keeps the default and logs once */
    nfake = 0; logged = 0; load_colors();
    for (int c = 0; c < COL_COUNT; c++) assert(cat_color[c] == color_default[c]);
    assert(color_default[COL_COMMON] == 0xb8bcc4 && color_default[COL_EVENT] == 0xb070ff && color_default[COL_PUZZLE] == 0xff9628 && logged == 0);
    ini("KeyItems", "#123456", "Events", "AbCdEf"); load_colors(); assert(cat_color[COL_KEY] == 0x123456 && cat_color[COL_EVENT] == 0xabcdef && cat_color[COL_LOCK] == color_default[COL_LOCK]);
    ini("Rooms", "#12345", "Files", "#GG0000"); logged = 0; load_colors(); assert(cat_color[COL_ROOM] == color_default[COL_ROOM] && cat_color[COL_FILE] == color_default[COL_FILE] && logged == 2);
    ini("Enemies", "#ff00ff00", 0, 0); load_colors(); assert(cat_color[COL_ENEMY] == color_default[COL_ENEMY]);   /* eight digits are not a colour */
    ini("CommonItems", " #010203 ", 0, 0); load_colors(); assert(cat_color[COL_COMMON] == 0x010203);
    ini(0, 0, 0, 0); load_colors(); assert(cat_color[COL_KEY] == color_default[COL_KEY]);                          /* removed from the INI: default again */
    fail_write = 1; nwritten = 0; moved = deleted = logged = 0; save_settings();
    assert(moved == 0 && deleted == 1 && logged == 1);                                           /* a failed write keeps the INI */
    return 0;
}
'''

HOOK = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
typedef unsigned U32; typedef unsigned char BYTE; typedef unsigned DWORD; typedef long LONG;
#define WINAPI
#define PAGE_EXECUTE_READWRITE 0x40
static BYTE *exe;
static volatile LONG all_off, visibility;
static int logged; static char last_log[64];
static void log_line(const char *m) { logged++; strncpy(last_log, m, 63); }
static int readable(const void *p, U32 n) { return p != 0; }
static int VirtualProtect(void *p, size_t n, DWORD a, DWORD *old) { *old = 0; return 1; }
static int FlushInstructionCache(void *h, void *p, size_t n) { return 1; }
static void *GetCurrentProcess(void) { return 0; }
''' + cut('#define EXE_FLAG_TEST', 'static DWORD WINAPI install') + r'''
static unsigned char fake_orig(void *m, void *e, U32 bank, U32 idx) { return 0x5a; }
static const BYTE ctx[8] = {0x6a, 0x07, 0x81, 0xc1, 0xf8, 0x01, 0x00, 0x00};
static const BYTE head[16] = {0x8b, 0x44, 0x24, 0x04, 0x56, 0x8b, 0xf1, 0x83, 0xf8, 0x07, 0x0f, 0x87, 0x06, 0x01, 0x00, 0x00};
#define SIZE 0x160000
/* a fake image mapped within +-2GB of the wrapper so the 32-bit displacement is exact, as in the 32-bit game */
static BYTE *make_image(void) {
    uintptr_t hint = ((uintptr_t)flag_all_scope & ~(uintptr_t)0xfff) + 0x10000000;
    BYTE *b = mmap((void *)hint, SIZE, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    assert(b != MAP_FAILED && (intptr_t)((BYTE *)flag_all_scope - b) < 0x7ff00000);
    memcpy(b + EXE_FLAG_TEST, head, 16);
    for (int i = 0; i < 2; i++) {
        BYTE *p = b + bank7_sites[i]; memcpy(p - 8, ctx, 8); p[0] = 0xe8;
        int rel = (int)((b + EXE_FLAG_TEST) - (p + 5)); memcpy(p + 1, &rel, 4);
    }
    return b;
}
static int patched(BYTE *b, int i) {
    BYTE *p = b + bank7_sites[i]; int rel; memcpy(&rel, p + 1, 4);
    return p[0] == 0xe8 && p + 5 + rel == (BYTE *)flag_all_scope;
}
static int untouched(BYTE *b, int i) {
    BYTE *p = b + bank7_sites[i]; int rel; memcpy(&rel, p + 1, 4);
    return p + 5 + rel == b + EXE_FLAG_TEST;
}
int main(void) {
    exe = make_image(); hook_all_scope();                                   /* every byte matches */
    for (int i = 0; i < 2; i++) assert(patched(exe, i));
    flag_test = fake_orig;                                                  /* wrapper behaviour */
    visibility = 2; all_off = 0;
    assert(flag_all_scope(0, 0, 7, 5) == 1 && flag_all_scope(0, 0, 5, 5) == 0x5a && flag_all_scope(0, 0, 7, 154) == 0x5a);
    visibility = 1; assert(flag_all_scope(0, 0, 7, 5) == 0x5a);             /* other scopes keep the native answer */
    visibility = 2; all_off = 1; assert(flag_all_scope(0, 0, 7, 5) == 0x5a);

    for (int bad = 0; bad < 5; bad++) {                                     /* any mismatch: nothing is patched */
        BYTE *b = make_image(); exe = b;
        if (bad == 0) b[bank7_sites[1] - 3] ^= 1;                           /* context bytes before one site */
        if (bad == 1) b[EXE_FLAG_TEST + 4] ^= 1;                            /* flag test prologue changed */
        if (bad == 2) b[bank7_sites[1]] = 0xe9;                             /* not a call */
        if (bad == 3) b[bank7_sites[0] + 1] ^= 0x10;                        /* call goes elsewhere */
        if (bad == 4) b[bank7_sites[1] - 8] ^= 1;
        logged = 0; hook_all_scope();
        for (int i = 0; i < 2; i++) assert(!patched(b, i) && (bad == 3 || untouched(b, i) || (bad == 2 && i == 1)));
        assert(logged == 1 && strstr(last_log, "mismatch"));
    }
    return 0;
}
'''

for name, prog in (('settings', SETTINGS), ('hook', HOOK)):
    with tempfile.TemporaryDirectory() as d:
        c, exe = Path(d) / f'{name}.c', Path(d) / name
        c.write_text(prog)
        subprocess.run(['clang', '-w', '-I', str(Path(__file__).resolve().parents[1] / 'src'), str(c), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)
print('PASS: settings clamps, TextSize and Version 2 migration, new keys, atomic save; all-scope hook validation')
