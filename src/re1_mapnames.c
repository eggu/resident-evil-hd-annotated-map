/* RE1HD.AnnotatedMap.asi — Annotated Map: Survivor's Notes (주석 달린 지도: 생존자의 메모).
 * Korean room names, key doors, puzzles, key items and documents on the HD Remaster map.
 * Standalone: hooks map object vtable 0xc3d0f8 slots 0..9 (captures the map object each frame it is used)
 * and the game's IDirect3DDevice9::EndScene (device found inside the renderer object [0xd5a048]).
 */
#include <windows.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned int U32;
/* kind: 0 room name, 1 key door, 2 puzzle, 3 rescue, 4 key item, 5 document/map, 7 ordinary.
 * room is the visual/visited map section; room2 is the physical source for kinds4/5/7.
 * kinds 4/5: flag = bank3 "taken" bit. chr = spawn mask (0 = all; 0x20 Jill / 0x10 Chris,
 * low bits = difficulties; no low bits = every difficulty). */
/* lang: 0 both, 1 Korean, 2 English */
typedef struct { int kind, room, room2; U32 area, floor, flag, chr, lang; float x, y, x2, y2; U32 w, h; const BYTE *px; U32 reward, step; float ax, ay; U32 key_visits[5]; U32 icon; } Label; /* icon: 1-based index into icons[] (kinds 1-5), 0 = none */
typedef struct { U32 format, type, usage, pool, ms, msq, w, h; } SurfaceDesc;
typedef struct { int pitch; BYTE *bits; } Locked;
typedef struct { float x, y, z, rhw; U32 color; float u, v; } Vertex; /* FVF XYZRHW|DIFFUSE|TEX1 */
#include "rescue_state.h"
#include "item_state.h"
#include "reward_state.h"
#include "reward_rules.h"
#include "labels.h"
#include "section_rules.h"
#include "crimson_data.h"
#include "enemy_rec.h"
#include "zoom.h"
#include "hold_key.h"
#include "marks.h"
#include "legend_text.h"
#include "item_name_text.h"
#include "synth_marks.h"
#include "event_spots.h"
#include "save_points.h"
#include "name_lines.h"
#include "colors.h"

#define EXE_MAP_VTABLE   0x83d0f8 /* map object class vtable; slots 0..9 hooked */
#define EXE_ROOMS        0x8c8e00 /* 154 records x 96 bytes */
#define EXE_BANKS        0x8f2fc8 /* manager: bank4 +0x31c, bank5 +0x33c, bank7 +0x37c */
#define EXE_RENDERER     0x95a048 /* renderer dims +0xb8/+0xbc */
#define EXE_INVENTORY    0x8f2f28 /* +0x5110 == 1 Jill, +0x24 difficulty (spawn mask filter 0x481d40) */
#define EXE_ROOMSTATE    0x8f3068 /* +0x20 stage, +0x24 room */
#define EXE_ITEM_CTOR    0x27e990 /* uItem base ctor 0x67e990: push esi; push 0x3e8 */
/* Crimson Heads: [0xcf2df4]+0x40 + id*0x30 death records (0x4ea1d0): +0x10/+0x18 world x/z, +0x2c revive
 * time (0 = never); clock [INV+0xe4738] in 1/30 s; dead = bank2[id]. Revive check 0x4ea3a0. */
#define EXE_CRIMSON      0x8f2df4
#define EXE_REVIVE_JBE   0x0ea3fc /* 0x4ea3fc jbe; RE1.DeadShallNotRise NOPs it (90 90) */
#define CRIMSON_KIND     8        /* HiddenKinds bit, key 8 */
#define KEROSENE_FLAG 900 /* gen_labels.KEROSENE_FLAG */
#define CRIMSON_MINUTE   1800.0f
#define CRIMSON_GAP      2        /* texture px between marker and minutes */
static const int stage_first[7] = {0, 0, 37, 72, 104, 129, 154}; /* cumulative room index per stage */
#define ZX(v) (zoom_on ? zoom_out_x((float)(v), zoom_x) : (float)(v))
#define ZY(v) (zoom_on ? zoom_out_y((float)(v), zoom_y) : (float)(v))

static BYTE *exe;
/* original EndScene per device vtable: never call one object's original through another's vtable */
static struct { void **vt; int (WINAPI *fn)(void *); } chain[4];
static void *volatile map_object;
static volatile U32 frame, map_frame, map_session, map_opening;
void *map_orig[10];
void __cdecl capture_map(BYTE *p) {
    /* Native map state 0 initializes each opening; box subviews keep the same session. Count only the
     * entry into state 0: it can stay 0 for many frames, which re-snapshotted and rebuilt every frame. */
    static U32 prev_state = 1;
    U32 state = *(U32 *)(p + 0x60ac);
    if (map_object != p || frame - map_frame > 3 || (state == 0 && prev_state != 0)) map_session++;
    prev_state = state;
    map_object = p;
    map_frame = frame;
}
/* thunk i: save everything, record ECX, continue into the original slot */
#define THUNK(i) ".globl _map_thunk" #i "\n_map_thunk" #i ":\n pushal\n pushfl\n pushl %ecx\n" \
    " call _capture_map\n addl $4, %esp\n popfl\n popal\n jmp *_map_orig+" #i "*4\n"
__asm__(THUNK(0) THUNK(1) THUNK(2) THUNK(3) THUNK(4) THUNK(5) THUNK(6) THUNK(7) THUNK(8) THUNK(9));
void map_thunk0(void), map_thunk1(void), map_thunk2(void), map_thunk3(void), map_thunk4(void),
     map_thunk5(void), map_thunk6(void), map_thunk7(void), map_thunk8(void), map_thunk9(void);
static void (*const map_thunks[10])(void) = {map_thunk0, map_thunk1, map_thunk2, map_thunk3, map_thunk4,
    map_thunk5, map_thunk6, map_thunk7, map_thunk8, map_thunk9};
/* The uItem ctor records candidates; each map opening snapshots their projected positions. */
#define MAXU 128
static void *volatile units[MAXU];
static volatile LONG unit_next;
void __cdecl record_unit(void *p) { units[(InterlockedIncrement(&unit_next) - 1) & (MAXU - 1)] = p; }
__asm__(".globl _ctor_stub\n_ctor_stub:\n pushal\n pushfl\n pushl %ecx\n call _record_unit\n addl $4, %esp\n"
        " popfl\n popal\n pushl %esi\n pushl $0x3e8\n jmp *_ctor_back\n");
void ctor_stub(void);
void *ctor_back = (void *)0x67e996;
static HANDLE log_file;
/* Keys while the map is open (user decision 2026-11-08, the shared numbering): 1 rooms, 2 locks, 3 key items, 4 files/maps, 5 puzzles,
 * 6 events, 7 common items, 8 enemies (hold: the minutes left of Crimson Heads), 9 scope, 0 everything on/off, H item names, \ language
 * (VK_OEM_5; Korean keyboards print it as the won sign), ~ legend. 5 also toggles the Rebecca rescue marker. Name size: - / =
 * (also numpad -,+) 50..150% step 10; [ ] name opacity; with the modifier icon size and opacity.
 * State persists in RE1HD.AnnotatedMap.ini. */
#define GROUPS 7 /* keys 1..7 */
static const int toggle_kind[GROUPS] = {0, 1, 4, 5, 2, 6, 7}; /* HiddenKinds bit: room, lock, key item, file, puzzle, event, common item */
#define EVENT_KIND 6    /* HiddenKinds bit 64: events; kind 6 of a mark (labels use kind 6 for legend rows only, which are never drawn as marks) */
#define ITEM_ICON_PX 36 /* ordinary item icon size at 1440p (sprites are 32px); user: 90% of 40 */
static volatile LONG hidden;       /* bit per kind */
static volatile LONG english = 1;  /* default English */
static volatile LONG all_off;      /* key 0: hide every marker, keep the legend */
static volatile LONG visibility; /* 0 visited, 1 revealed, 2 all */
static volatile LONG crimson_time; /* show minutes left beside Crimson Heads; hold key 7 */
static volatile LONG name_size = 100;    /* 50..150, step 10 */
static volatile LONG name_opacity = 70;  /* 10..100, step 10 */
/* RE0 HD controls, user decision 2026-11-07: icon size and opacity on the modifier with - + [ ], H item names, ~ legend */
static volatile LONG icon_size = 100;    /* 50..200, step 10 */
static volatile LONG icon_opacity = 80;  /* 10..100, step 10 */
static volatile LONG item_names;         /* item names beside marks: 0 hidden (default, as in RE0 HD), 1 all, 2 all except ordinary items; [H] cycles 1, 2, 0 */
static volatile LONG legend_open = 1;    /* ~ folds the legend to one line and hides the readout */
static volatile LONG modifier_vk = VK_SHIFT; /* INI Modifier=Shift|Ctrl */
static volatile LONG door_key_unvisited; /* INI DoorKey=Unvisited: a lock's key on its unvisited side (1.0.0); default the door centre */
#define SETTINGS_VERSION 4 /* 1.0.0 had no Version key; 3: ItemNames is the 3-state value; 4: events are hidden group 64 (key 6), language moves to the backslash key */
static volatile float legend_top = 572; /* 1280x720 units; the note row moves it */
static volatile LONG zoom_on;
static float zoom_x, zoom_y; /* zoom.h off, game thread */
static char ini_path[MAX_PATH];
static void log_line(const char *s);
/* Atomic: edit a copy, then replace the INI with it, so a failed write keeps the old file (comments and [CrimsonRooms] too). */
static void save_settings(void) {
    char tmp[MAX_PATH + 8], v[16];
    int ok = 1;
    wsprintfA(tmp, "%s.tmp", ini_path);
    if (!CopyFileA(ini_path, tmp, FALSE) && GetLastError() != ERROR_FILE_NOT_FOUND) { log_line("settings copy failed; previous INI kept\r\n"); return; }
#define PUT_INT(key, value) (wsprintfA(v, "%d", (int)(value)), ok &= WritePrivateProfileStringA("AnnotatedMap", key, v, tmp) != 0)
#define PUT_STR(key, value) (ok &= WritePrivateProfileStringA("AnnotatedMap", key, value, tmp) != 0)
    PUT_INT("Version", SETTINGS_VERSION);
    PUT_INT("NameSize", name_size);
    PUT_INT("NameOpacity", name_opacity);
    PUT_INT("IconSize", icon_size);
    PUT_INT("IconOpacity", icon_opacity);
    PUT_INT("ItemNames", item_names);
    PUT_INT("Legend", legend_open != 0);
    PUT_INT("Visibility", visibility);
    PUT_INT("HiddenKinds", hidden);
    PUT_STR("Language", english ? "en" : "ko");
    PUT_STR("Enabled", all_off ? "0" : "1");
    PUT_STR("CrimsonTime", crimson_time ? "1" : "0");
    PUT_STR("Modifier", modifier_vk == VK_CONTROL ? "Ctrl" : "Shift");
    PUT_STR("DoorKey", door_key_unvisited ? "Unvisited" : "Center");
    /* [Colors] is never written here: the copy keeps the user's colours and every comment */
#undef PUT_INT
#undef PUT_STR
    if (!ok || !MoveFileExA(tmp, ini_path, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
        DeleteFileA(tmp);
        log_line("settings save failed; previous INI kept\r\n");
    }
}
/* clamp to [lo, hi], snapped to the nearest 10 (hand-edited INI values) */
static int step10(int v, int lo, int hi, int dflt) {
    if (v < 0) return dflt;
    v = (v + 5) / 10 * 10;
    return v < lo ? lo : v > hi ? hi : v;
}
/* Returns 1 for an INI from before the current Version: the caller rewrites it once, with the new keys and Version. */
static int load_settings(void) {
    char v[16];
    int version = GetPrivateProfileIntA("AnnotatedMap", "Version", 0, ini_path);
    name_size = GetPrivateProfileIntA("AnnotatedMap", "NameSize", -1, ini_path);
    if (name_size < 0) name_size = GetPrivateProfileIntA("AnnotatedMap", "TextSize", 100, ini_path); /* legacy v30 key */
    name_size = step10(name_size, 50, 150, 100);
    name_opacity = step10(GetPrivateProfileIntA("AnnotatedMap", "NameOpacity", 70, ini_path), 10, 100, 70);
    icon_size = step10(GetPrivateProfileIntA("AnnotatedMap", "IconSize", 100, ini_path), 50, 200, 100);
    icon_opacity = step10(GetPrivateProfileIntA("AnnotatedMap", "IconOpacity", 80, ini_path), 10, 100, 80);
    item_names = GetPrivateProfileIntA("AnnotatedMap", "ItemNames", 0, ini_path);
    /* Before Version 3 ItemNames was on/off: on -> all, off -> hidden. Now 0 hidden, 1 all, 2 no common; anything else is hidden. */
    item_names = version < 3 ? item_names != 0 : item_names >= 0 && item_names <= 2 ? item_names : 0;
    legend_open = GetPrivateProfileIntA("AnnotatedMap", "Legend", 1, ini_path) != 0;
    visibility = GetPrivateProfileIntA("AnnotatedMap", "Visibility", 0, ini_path);
    if (visibility < 0 || visibility > 2) visibility = 0;
    hidden = GetPrivateProfileIntA("AnnotatedMap", "HiddenKinds", (1<<1)|(1<<2)|(1<<4)|(1<<5)|(1<<6)|(1<<7)|(1<<8), ini_path) & 0x1ff;
    /* Before Version 4 there was no events group (bit 64 was never set): events are spoilers, so a migrated INI starts with them hidden. The other
     * bits are kinds, not key numbers, so the new numbering needs no change of the saved toggles. */
    if (version < 4) hidden |= 1 << EVENT_KIND;
    GetPrivateProfileStringA("AnnotatedMap", "Language", "en", v, sizeof v, ini_path);
    english = !(v[0] == 'k' && v[1] == 'o');
    all_off = !GetPrivateProfileIntA("AnnotatedMap", "Enabled", 1, ini_path);
    crimson_time = GetPrivateProfileIntA("AnnotatedMap", "CrimsonTime", 0, ini_path) != 0;
    GetPrivateProfileStringA("AnnotatedMap", "Modifier", "Shift", v, sizeof v, ini_path);
    modifier_vk = (v[0] == 'C' || v[0] == 'c') ? VK_CONTROL : VK_SHIFT;
    GetPrivateProfileStringA("AnnotatedMap", "DoorKey", "Center", v, sizeof v, ini_path);
    door_key_unvisited = v[0] == 'U' || v[0] == 'u';
    return version < SETTINGS_VERSION;
}

/* [Colors]: one #RRGGBB per category (colors.h). A missing key keeps the default; an unreadable value keeps the default and logs once. */
static void load_colors(void) {
    for (int i = 0; i < COL_COUNT; i++) {
        char v[32];
        cat_color[i] = color_default[i];
        GetPrivateProfileStringA("Colors", color_keys[i], "", v, sizeof v, ini_path);
        unsigned rgb;
        if (!v[0]) continue;
        if (color_parse(v, &rgb)) cat_color[i] = rgb;
        else { char line[96]; wsprintfA(line, "Colors: %s is not #RRGGBB; default kept\r\n", color_keys[i]); log_line(line); }
    }
}
static void log_line(const char *s) {
    static DWORD total; /* 2 MB cap: per-spawn lines must not grow the log without bound */
    DWORD n = (DWORD)lstrlenA(s), w;
    if (log_file == INVALID_HANDLE_VALUE || total + n > (2u << 20)) return;
    total += n;
    WriteFile(log_file, s, n, &w, 0);
}
/* Once per failure class: enough evidence without a per-frame log or altered draw guards. */
static void draw_trace(U32 code, U32 a, U32 b, U32 c, U32 d) {
    static U32 seen;
    if (code >= 32 || (seen & (1u << code))) return;
    seen |= 1u << code;
    char line[160];
    wsprintfA(line, "draw[%u] %u %u %u %u\r\n", code, a, b, c, d);
    log_line(line);
}
static int readable(const void *p, U32 n) {
    MEMORY_BASIC_INFORMATION m;
    UINT_PTR at = (UINT_PTR)p, end = at + n;
    if (at < 65536 || end < at) return 0;
    while (at < end) {
        if (!VirtualQuery((void *)at, &m, sizeof m) || m.State != MEM_COMMIT ||
            (m.Protect & (PAGE_GUARD | PAGE_NOACCESS))) return 0;
        at = (UINT_PTR)m.BaseAddress + m.RegionSize;
    }
    return 1;
}
static U32 u32(const void *p) { return *(const U32 *)p; }
static void *method(void *p, int i) { return (*(void ***)p)[i]; }
static void release(void *p) { if (p) ((ULONG (WINAPI *)(void *))method(p, 2))(p); }
/* bounds: room/lock banks 256 bits, bank3 512; anything else (e.g. room2 = -1) reads as clear */
static int bitn(const U32 *bank, U32 i, U32 n) { return i < n && (bank[i >> 5] >> (i & 31)) & 1; }
static int bit(const U32 *bank, U32 i) { return bitn(bank, i, 256); }

static int key_visited(const U32 *visited, const Label *l) {
    for (U32 i = 0; i < 5; i++) if (visited[i] & l->key_visits[i]) return 1;
    return 0;
}

static int explored(const U32 *bank, const Label *l) {
    for (U32 i=0;i<5;i++) if (l->key_visits[i]) return key_visited(bank,l);
    int shown = bit(bank, l->room);
    return shown;
}

static int name_replaced(const Label *l,const U32 *visited,const U32 *revealed,int scope) {
    if (l->kind != 0) return 0;
    for (U32 i=0;i<sizeof section_replacements/sizeof *section_replacements;i++) {
        const unsigned *pair=section_replacements[i];
        if (pair[0]==(U32)l->room && (scope==2 || bit(visited,pair[1]) || (scope==1 && bit(revealed,pair[1])))) return 1;
    }
    return 0;
}

static U32 pickup_section(const Label *l,const U32 *visited,const U32 *revealed,int scope) {
    U32 section=l->room;
    if (l->kind!=4 && l->kind!=5 && l->kind!=7) return section;
    for (int pass=0;pass<3;pass++)
        for (U32 i=0;i<sizeof section_replacements/sizeof *section_replacements;i++) {
            const unsigned *p=section_replacements[i];
            if (p[0]==section && bit(l->key_visits,p[1]) &&
                (scope==2 || bit(visited,p[1]) || (scope==1 && bit(revealed,p[1])))) section=p[1];
        }
    return section;
}
static void project_pickup(U32 section,float wx,float wz,float *x,float *y) {
    const int *r=(const int *)(exe+EXE_ROOMS+96*section);
    *x=48+.9f*(r[0]+r[2]+(int)(wx*((const float *)r)[4]*.015f));
    *y=36+.9f*(r[1]-r[3]+(int)(wz*((const float *)r)[5]*.015f));
}

/* live unit -> its class name starts with "uIT" (vtable +0x10 = mov eax, dti; ret; dti +4 = name) */
static int is_item_unit(BYTE *u) {
    BYTE *vt, *fn, *dti; const char *name;
    if (!readable(u, 0x14c0) || !readable(vt = *(BYTE **)u, 0x14)) return 0;
    fn = *(BYTE **)(vt + 0x10);
    if (!readable(fn, 6) || fn[0] != 0xb8 || fn[5] != 0xc3) return 0;
    dti = *(BYTE **)(fn + 1);
    return readable(dti, 8) && readable(name = *(const char **)(dti + 4), 4) &&
           name[0] == 'u' && name[1] == 'I' && name[2] == 'T';
}
typedef struct { U32 flag; float x, y; } Live;
/* Freeze world X/Z once; each label projects through its own native map section. */
static U32 live_units(U32 room, Live *out) {
    U32 n = 0;
    for (U32 i = 0; i < MAXU; i++) {
        BYTE *u = units[i];
        if (!u || !is_item_unit(u)) continue;
        float x = *(float *)(u + 0x40), z = *(float *)(u + 0x48);
        if (!(x > -1e5f && x < 1e5f && z > -1e5f && z < 1e5f)) continue;
        out[n].flag = u32(u + 0x14b8);
        out[n].x = x;
        out[n].y = z;
        n++;
    }
    return n;
}

/* Every label image plus the crimson glyph sheet (image LABEL_COUNT) shares a few atlas pages, so a
 * frame is one DrawPrimitiveUP per page instead of one SetTexture+draw per label. */
#define PAGE      2048
#define MAXPAGES  4
#define ATLAS_PAD 2   /* transparent texels between images: no bilinear bleed when scaled */
#define PANEL_IMAGE (LABEL_COUNT + 1) /* 4x4 opaque dark texels: legend panel, alpha from vertex diffuse */
#define ICON_FIRST (LABEL_COUNT + 2) /* icons[0..ICON_COUNT): sprites shared by name-with-icon labels */
#define TEXT_FIRST (LABEL_COUNT + 2 + ICON_COUNT) /* legend_text[]: legend and readout rows of legend_text.h */
#define NAME_FIRST (TEXT_FIRST + LT_COUNT) /* item_name_text[]: ordinary item names of item_name_text.h */
#define IMAGES    (NAME_FIRST + NT_COUNT)
#define MAXV      (6 * 1536)
#define LAYERS    3 /* 0 markers, 1 legend panel, 2 legend text: panel and text may sit on different pages */
static struct { U32 page, x, y; } slot[IMAGES];
static U32 npages;
static void *pages[MAXPAGES], *page_device;
static Vertex verts[LAYERS][MAXPAGES][MAXV];
static U32 nverts[LAYERS][MAXPAGES];
static U32 layer, emit_color = 0xffffffff; /* destination layer and vertex diffuse (alpha) for emit() */
#define PX_ 14,14,18,255
static const BYTE panel_px[4 * 4 * 4] = {PX_,PX_,PX_,PX_,PX_,PX_,PX_,PX_,PX_,PX_,PX_,PX_,PX_,PX_,PX_,PX_};
static U32 image_w(U32 i) { return i < LABEL_COUNT ? labels[i].w : i == PANEL_IMAGE ? 4 : i >= NAME_FIRST ? item_name_text[i - NAME_FIRST].w : i >= TEXT_FIRST ? legend_text[i - TEXT_FIRST].w : i >= ICON_FIRST ? icons[i - ICON_FIRST].w : CRIMSON_ATLAS_W; }
static U32 image_h(U32 i) { return i < LABEL_COUNT ? labels[i].h : i == PANEL_IMAGE ? 4 : i >= NAME_FIRST ? item_name_text[i - NAME_FIRST].h : i >= TEXT_FIRST ? legend_text[i - TEXT_FIRST].h : i >= ICON_FIRST ? icons[i - ICON_FIRST].h : CRIMSON_ATLAS_H; }
static const BYTE *image_px(U32 i) { return i < LABEL_COUNT ? labels[i].px : i == PANEL_IMAGE ? panel_px : i >= NAME_FIRST ? item_name_text[i - NAME_FIRST].px : i >= TEXT_FIRST ? legend_text[i - TEXT_FIRST].px : i >= ICON_FIRST ? icons[i - ICON_FIRST].px : crimson_atlas; }
static int taller(const void *a, const void *b) {
    return (int)image_h(*(const U32 *)b) - (int)image_h(*(const U32 *)a);
}
/* ponytail: shelf packing by descending height (~2 pages today); MAXRECTS if pages ever run out. */
static void pack(void) {
    static U32 order[IMAGES];
    U32 x = 0, y = 0, row = 0, page = 0;
    for (U32 i = 0; i < IMAGES; i++) order[i] = i;
    qsort(order, IMAGES, sizeof *order, taller);
    for (U32 n = 0; n < IMAGES; n++) {
        U32 i = order[n], w = image_w(i) + ATLAS_PAD, h = image_h(i) + ATLAS_PAD;
        if (x + w > PAGE) { x = 0; y += row; row = 0; }
        if (y + h > PAGE) { x = y = row = 0; page++; }
        slot[i].page = page; slot[i].x = x; slot[i].y = y; /* page >= MAXPAGES: never drawn */
        x += w;
        if (h > row) row = h;
    }
    npages = page < MAXPAGES ? page + 1 : MAXPAGES;
}
/* The game draws a 16:9 picture centred in any back buffer (any display mode, also Fusion Fix's). Layout stays in
 * game pixels; vertices are fitted to the back buffer here. */
static float shift_x, shift_y, fit = 1;
static void fit_screen(U32 bw, U32 bh, U32 W, U32 H) {
    float fw = (float)bw / W, fh = (float)bh / H;
    fit = fw < fh ? fw : fh;
    if (fit > 1) fit = 1; /* extra back buffer is pillars or letterbox, not a bigger picture */
    shift_x = (float)(int)((bw - W * fit) / 2); shift_y = (float)(int)((bh - H * fit) / 2);
}
static int make_pages(void *dev) {
    if (!npages) pack();
    if (page_device == dev) return pages[npages - 1] != 0;
    for (U32 p = 0; p < MAXPAGES; p++) { release(pages[p]); pages[p] = 0; }
    page_device = dev;
    for (U32 p = 0; p < npages; p++) {
        void *t = 0; Locked lk;
        HRESULT created = ((HRESULT (WINAPI *)(void *, U32, U32, U32, U32, U32, U32, void **, void *))method(dev, 23))
                (dev, PAGE, PAGE, 1, 0, 21 /*A8R8G8B8*/, 1 /*MANAGED*/, &t, 0);
        if (created < 0 || !t) { draw_trace(9, created, p, PAGE, 0); return 0; }
        if (((HRESULT (WINAPI *)(void *, U32, Locked *, void *, U32))method(t, 19))(t, 0, &lk, 0, 0) < 0) {
            draw_trace(10, p, 0, 0, 0); release(t); return 0;
        }
        for (U32 y = 0; y < PAGE; y++) ZeroMemory(lk.bits + y * lk.pitch, PAGE * 4);
        for (U32 i = 0; i < IMAGES; i++) {
            if (slot[i].page != p) continue;
            U32 w = image_w(i);
            for (U32 y = 0; y < image_h(i); y++)
                CopyMemory(lk.bits + (slot[i].y + y) * lk.pitch + slot[i].x * 4, image_px(i) + y * w * 4, w * 4);
        }
        ((HRESULT (WINAPI *)(void *, U32))method(t, 20))(t, 0);
        pages[p] = t;
    }
    return 1;
}

static void set_states(void *dev) {
    static const U32 rs[][2] = {{7,0},{14,0},{22,1},{27,1},{19,5},{20,6},{137,0},{15,0},{174,0},
                                {194,0},{168,15},{28,0},{52,0}};
    /* alpha = texture * vertex diffuse alpha (name opacity); colour = texture * vertex diffuse RGB (the category colour; the rasters are white) */
    static const U32 ts[][3] = {{0,1,4},{0,2,2},{0,3,0},{0,4,4},{0,5,2},{0,6,0},{1,1,1}};
    static const U32 ss[][2] = {{1,3},{2,3},{5,2},{6,2},{11,0}};
    ((HRESULT (WINAPI *)(void *, void *))method(dev, 92))(dev, 0);
    ((HRESULT (WINAPI *)(void *, void *))method(dev, 107))(dev, 0);
    ((HRESULT (WINAPI *)(void *, U32))method(dev, 89))(dev, 0x144 /*XYZRHW|DIFFUSE|TEX1*/);
    for (U32 i = 0; i < sizeof rs / sizeof *rs; i++)
        ((HRESULT (WINAPI *)(void *, U32, U32))method(dev, 57))(dev, rs[i][0], rs[i][1]);
    for (U32 i = 0; i < sizeof ts / sizeof *ts; i++)
        ((HRESULT (WINAPI *)(void *, U32, U32, U32))method(dev, 67))(dev, ts[i][0], ts[i][1], ts[i][2]);
    for (U32 i = 0; i < sizeof ss / sizeof *ss; i++)
        ((HRESULT (WINAPI *)(void *, U32, U32, U32))method(dev, 69))(dev, 0, ss[i][0], ss[i][1]);
}

/* Queue image i's sub-rectangle (u/v in 0..1 of that image) as two triangles on its page. */
static void emit(U32 i, float x, float y, float w, float h, float u0, float v0, float u1, float v1) {
    U32 p = slot[i].page;
    if (p >= MAXPAGES || nverts[layer][p] + 6 > MAXV) return;
    float iw = image_w(i), ih = image_h(i);
    u0 = (slot[i].x + u0 * iw) / PAGE; u1 = (slot[i].x + u1 * iw) / PAGE;
    v0 = (slot[i].y + v0 * ih) / PAGE; v1 = (slot[i].y + v1 * ih) / PAGE;
    x = x * fit + shift_x - .5f; y = y * fit + shift_y - .5f; w *= fit; h *= fit;
    U32 q = emit_color;
    Vertex a = {x, y, 0, 1, q, u0, v0}, b = {x + w, y, 0, 1, q, u1, v0}, c = {x, y + h, 0, 1, q, u0, v1}, d = {x + w, y + h, 0, 1, q, u1, v1};
    Vertex *v = verts[layer][p] + nverts[layer][p];
    v[0] = a; v[1] = b; v[2] = c; v[3] = c; v[4] = b; v[5] = d;
    nverts[layer][p] += 6;
}

/* Occupied screen rects this build: legend, room names, icons, crimson/kerosene markers, then placed item names.
 * ponytail: linear scan per candidate slot, O(names x occupied) ~ 10^4-10^5 rect tests per rebuild (a rebuild
 * only runs when the view changes); use a uniform grid if a profile ever shows it. */
#define MAXOCC 2048
static Occupied occ[MAXOCC];
static U32 nocc;
static void reserve_w(float x, float y, float w, float h, U32 weight) {
    if (nocc < MAXOCC) occ[nocc++] = (Occupied){{x, y, x + w, y + h}, weight};
}
static void reserve(float x, float y, float w, float h) { reserve_w(x, y, w, h, 1); }
static float icon_side;            /* this build's icon size in game pixels (user %) */
static U32 icon_alpha = 0xffffffff; /* icon opacity in the vertex alpha */

/* Room of a corpse on this map floor: the only candidate on (area, floor), else the one whose
 * room-name anchor is nearest to the projected point (8 IDs listed by two rooms). */
static int crimson_room(const CrimsonEnemy *e, float wx, float wz, U32 area, U32 floor, float *px, float *py) {
    int best = -1; float bd = 0;
    for (int c = 0; c < 2; c++) {
        int room = c ? e->room2 : e->room;
        if (room < 0 || room >= 154) continue;
        const int *r = (const int *)(exe + EXE_ROOMS + 96 * room);
        if ((U32)r[6] != area || (U32)r[7] != floor) continue;
        float x, y, ax = c ? e->ax2 : e->ax, ay = c ? e->ay2 : e->ay;
        project_pickup(room, wx, wz, &x, &y);
        float d = (x - ax) * (x - ax) + (y - ay) * (y - ay);
        if (best < 0 || d < bd) { best = room; bd = d; *px = x; *py = y; }
    }
    return best;
}

/* The death record holds no room, and static tables share IDs between rooms (384: 101 and 203) or miss
 * rooms (21d). So watch deaths: a record whose revive time changes while its ID is in the current room's
 * table (obj+0xc040, 32 slots, filled by 0x4ea330) died here. Persisted in the INI as [CrimsonRooms] id=room.
 * ponytail: one map for every save; a reloaded older playthrough keeps the newest kill's room per ID. */
static volatile int death_room[1024];
static void load_death_rooms(void) {
    static char buf[16384];
    for (U32 i = 0; i < 1024; i++) death_room[i] = -1;
    GetPrivateProfileSectionA("CrimsonRooms", buf, sizeof buf, ini_path);
    for (const char *k = buf; *k; k += lstrlenA(k) + 1) {
        int id = 0, room = 0; const char *v = k;
        while (*v >= '0' && *v <= '9') id = id * 10 + *v++ - '0';
        if (*v++ != '=') continue;
        while (*v >= '0' && *v <= '9') room = room * 10 + *v++ - '0';
        if (id < 1024 && room < 154) death_room[id] = room;
    }
}
static void track_deaths(void) {
    static float last[1024];
    static int primed;
    BYTE *obj = *(BYTE **)(exe + EXE_CRIMSON), *rs = *(BYTE **)(exe + EXE_ROOMSTATE);
    if (!readable(obj, 0xc0c0) || !readable(rs, 0x28)) return;
    U32 stage = u32(rs + 0x20), room = u32(rs + 0x24), changed = 0;
    int cur = stage < 7 && room < 64 ? stage_first[stage] + (int)room : -1;
    static U32 hit[1024];
    for (U32 id = 0; id < 1024; id++) {
        float r = *(const float *)(obj + 0x40 + id * 0x30 + 0x2c);
        if (r != last[id] && changed < 1024) hit[changed++] = id;
        last[id] = r;
    }
    /* a save load rewrites many records at once: no room can be inferred from that */
    if (!primed || !changed || changed > 4 || cur < 0 || cur >= 154) { primed = 1; return; }
    const U32 *table = (const U32 *)(obj + 0xc040);
    for (U32 n = 0; n < changed; n++)
        for (U32 i = 0; i < 32; i++) {
            U32 id = hit[n];
            if (table[i] != id || !(last[id] > 0) || death_room[id] == cur) continue;
            char key[8], value[8], line[64];
            death_room[id] = cur;
            wsprintfA(key, "%u", id); wsprintfA(value, "%d", cur);
            WritePrivateProfileStringA("CrimsonRooms", key, value, ini_path);
            wsprintfA(line, "crimson death id=%u room=%d\r\n", id, cur);
            log_line(line);
        }
}


/* ---- Enemy markers from real spawns -------------------------------------------------------------------
 * Spawn core 0x47f500 (cdecl-ish: [esp+4] enemy object, [esp+8] ems data row, [esp+0xc] mode 0 alive / 1 dead body /
 * 2 revived; called by 0x47efe0, 0x47f180, 0x47f340). Object: +0x156c global id, +0x1460 em id, +0x1568 row index+1.
 * Row: +0x10/+0x18 world x/z. Only mode 0 is recorded. Prologue (9 bytes) is displaced into the stub.
 * Records live in enemy_rec.h; file RE1HD.AnnotatedMap.enemies.dat beside the ASI. Design/evidence: enemies-runtime/NOTES.md. */
#define EXE_SPAWN_CORE 0x07f500
static CRITICAL_SECTION enemy_cs;
static char enemy_path[MAX_PATH];
static volatile LONG enemy_dirty;
static DWORD enemy_dirty_tick;
static float clock_last;
static int spawn_room = -2;
static float spawn_stamp;

/* Cumulative room index of a (stage 1..6, room) pair, -1 if out of range. */
static int cum_room(U32 stage, U32 r) {
    return stage < 7 && r < 64 && stage_first[stage] + (int)r < 154 ? stage_first[stage] + (int)r : -1;
}
/* Game clock [INV+0xe4738] (1/30 s), else -1 (title: zero / stale not trusted). Needs no room object. */
static float clock_now(void) {
    BYTE *inv = *(BYTE **)(exe + EXE_INVENTORY);
    if (!readable(inv, 0xe473c)) return -1;
    float now = *(float *)(inv + 0xe4738);
    return now > 0 && now < 1e9f ? now : -1;
}
/* Clock on a valid in-game room state (ROOMSTATE settled), else -1. Install-thread watch only. */
static float game_clock(void) {
    BYTE *rs = *(BYTE **)(exe + EXE_ROOMSTATE);
    if (!readable(rs, 0x28) || cum_room(u32(rs + 0x20), u32(rs + 0x24)) < 0) return -1;
    return clock_now();
}
/* Room entry from the load destination (polled): see enemy_stale. */
static void track_room_entry(void) {
    static int last = -1;
    BYTE *inv = *(BYTE **)(exe + EXE_INVENTORY);
    if (!readable(inv, 0xe4764)) return;
    int room = cum_room(u32(inv + 0xe472c), u32(inv + 0xe4730));
    float now = clock_now();
    if (room < 0 || now <= 0 || room == last) return;
    last = room;
    EnterCriticalSection(&enemy_cs);
    enemy_enter(room, now);
    LeaveCriticalSection(&enemy_cs);
}
static void enemy_mark_dirty(void) { enemy_dirty = 1; enemy_dirty_tick = GetTickCount(); }
/* Older save loaded = clock moved back: drop records stamped after it. Caller holds enemy_cs. */
static void enemy_clock_check(float now) {
    if (clock_last > 0 && now + ENEMY_REGRESS < clock_last) {
        int n = enemy_purge_after(now);
        enemy_enter_reset(); /* entry clocks of the newer timeline mean nothing */
        char line[96];
        wsprintfA(line, "enemy clock regression %d -> %d: purged %d records\r\n", (int)clock_last, (int)now, n);
        log_line(line);
        if (n) enemy_mark_dirty();
    }
    clock_last = now;
}
/* Room at spawn time: ROOMSTATE (+0x20/+0x24) still holds the PREVIOUS room while a room loads (v31 log: gid 389 of
 * room 101 = index 1 was recorded as room 0). The game's own spawn code reads INV+0xe472c/+0xe4730 (stage<<8|room, set
 * by 0x48d350 at the door/load, tested by 0x47f0c9/0x47f293 against 0x202 etc.), so that pair is the room. INV+0xe4750/
 * +0xe4754 (set by 0x4ef400 during the room load) is the fallback. All three are logged per spawn to prove which is right. */
void __cdecl record_spawn(BYTE *obj, BYTE *row, U32 mode) {
    BYTE *inv = *(BYTE **)(exe + EXE_INVENTORY), *rs = *(BYTE **)(exe + EXE_ROOMSTATE);
    if (!readable(inv, 0xe4764) || !readable(obj, 0x1570)) return;
    U32 ds = u32(inv + 0xe472c), dr = u32(inv + 0xe4730), qs = u32(inv + 0xe4750), qr = u32(inv + 0xe4754);
    U32 ss = ~0u, sr = ~0u;
    if (readable(rs, 0x28)) { ss = u32(rs + 0x20); sr = u32(rs + 0x24); }
    int room = cum_room(ds, dr);
    if (room < 0) room = cum_room(qs, qr);
    float now = clock_now();
    int ok_row = readable(row, 0x34);
    EnemyRec r = {room, *(const BYTE *)(obj + 0x1568), u32(obj + 0x1460), u32(obj + 0x156c),
                  u32(inv + 0x5110) == 1, enemy_diff_class(u32(inv + 0x24)),
                  ok_row ? *(const float *)(row + 0x10) : 0, ok_row ? *(const float *)(row + 0x18) : 0, now};
    const char *why = mode != 0 ? "mode" : now < 0 ? "clock" : room < 0 ? "room" : !ok_row ? "row" :
        r.em >= 64 || !(r.x > -1e5f && r.x < 1e5f && r.z > -1e5f && r.z < 1e5f) ? "values" : 0;
    char line[240];
    wsprintfA(line, "enemy spawn mode=%u room=%d dest=%u/%u req=%u/%u state=%u/%u slot=%u em=%u gid=%u x=%d z=%d t=%d %s\r\n",
              mode, room, ds, dr, qs, qr, ss, sr, r.slot, r.em, r.gid, (int)r.x, (int)r.z, (int)now, why ? why : "recorded");
    log_line(line);
    if (why) return;
    if (r.gid >= 1024) r.gid = 0; /* table slot not filled for this room: no kill flag */
    EnterCriticalSection(&enemy_cs);
    enemy_clock_check(now);
    if (room != spawn_room || now < spawn_stamp) { /* first spawn of a room load: replace that room's records */
        int cleared = enemy_clear_room(room);
        wsprintfA(line, "enemy room load room=%d (replaced %d records)\r\n", room, cleared);
        log_line(line);
    }
    spawn_room = room; spawn_stamp = now;
    if (enemy_add(&r)) enemy_mark_dirty();
    LeaveCriticalSection(&enemy_cs);
}
__asm__(".globl _spawn_stub\n_spawn_stub:\n pushal\n pushfl\n pushl 48(%esp)\n pushl 48(%esp)\n pushl 48(%esp)\n"
        " call _record_spawn\n addl $12, %esp\n popfl\n popal\n"
        " pushl %ebp\n movl %esp, %ebp\n andl $-16, %esp\n subl $0x58, %esp\n jmp *_spawn_back\n");
void spawn_stub(void);
void *spawn_back = (void *)0x47f509;
static void hook_spawn(void) {
    static const BYTE head[14] = {0x55, 0x8b, 0xec, 0x83, 0xe4, 0xf0, 0x83, 0xec, 0x58, 0x56, 0x57, 0x8b, 0x7d, 0x0c};
    BYTE *p = exe + EXE_SPAWN_CORE; DWORD old;
    int ok = readable(p, 14);
    for (int i = 0; ok && i < 14; i++) ok = p[i] == head[i];
    if (!ok || !VirtualProtect(p, 9, PAGE_EXECUTE_READWRITE, &old)) { log_line("spawn core mismatch; enemy markers off\r\n"); return; }
    p[0] = 0xe9; *(int *)(p + 1) = (int)((BYTE *)spawn_stub - (p + 5));
    p[5] = p[6] = p[7] = p[8] = 0x90;
    VirtualProtect(p, 9, old, &old);
    FlushInstructionCache(GetCurrentProcess(), p, 9);
    log_line("spawn core hooked\r\n");
}
static void enemy_load_file(void) {
    static char buf[ENEMY_MAX * 81 + 16];
    DWORD n = 0;
    HANDLE f = CreateFileA(enemy_path, GENERIC_READ, FILE_SHARE_READ, 0, OPEN_EXISTING, 0, 0);
    enemy_n = 0;
    if (f == INVALID_HANDLE_VALUE) return;
    if (ReadFile(f, buf, sizeof buf, &n, 0)) enemy_load_text(buf, (int)n);
    CloseHandle(f);
}
/* install thread: clock regression watch + write the file shortly after a change (tmp + rename) */
static void enemy_service(void) {
    static char buf[ENEMY_MAX * 81 + 16];
    float now = game_clock();
    int len = -1;
    EnterCriticalSection(&enemy_cs);
    if (now >= 0) enemy_clock_check(now);
    if (enemy_dirty && GetTickCount() - enemy_dirty_tick > 500) { len = enemy_serialize(buf, sizeof buf); enemy_dirty = 0; }
    LeaveCriticalSection(&enemy_cs);
    if (len < 0) return;
    char tmp[MAX_PATH + 8]; DWORD w;
    lstrcpyA(tmp, enemy_path); lstrcatA(tmp, ".tmp");
    HANDLE f = CreateFileA(tmp, GENERIC_WRITE, 0, 0, CREATE_ALWAYS, 0, 0);
    if (f == INVALID_HANDLE_VALUE) return;
    int ok = WriteFile(f, buf, len, &w, 0) && w == (DWORD)len;
    CloseHandle(f);
    if (ok) MoveFileExA(tmp, enemy_path, MOVEFILE_REPLACE_EXISTING);
}

/* Bosses the game spawns by script (never through the recorded spawn call), known from game data: shown until their defeat flag
 * is set, in every room the scope shows. Plant 42 (em 17) in the Residence Plant 42 Room / 식물 42 방 (room 116): defeated =
 * bank1 62 (the room code spawns the Helmet Key only then, item_state.h). The point is the Helmet Key's floor spot, the room's
 * far side: ems carries no position for it, so it is approximate. */
/* under_name: drawn centred under the room's name (user decision 2026-11-08: Plant 42 sits below the name of its room); wx, wz is the fallback. */
typedef struct { U32 room, em, flag; float wx, wz; int under_name; } StaticEnemy;
static const StaticEnemy static_enemies[] = {{116, 17, 62, 578.0f, 169.0f, 1}};
/* Canvas point of a room's single room-only event marker: beside its name, inside its shape (tools/event_spots.py). */
static void room_name_side(int room, float *px, float *py) {
    for (U32 i = 0; i < sizeof event_spots / sizeof *event_spots; i++)
        if (event_spots[i].room == room) { *px = event_spots[i].x; *py = event_spots[i].y; return; }
}
/* Centre x and bottom y (screen px) of the room name drawn for `room` in the current language; 0 when the room has none. */
static int room_name_spot(U32 room, float ox, float oy, float sx, float sy, float tk, float *cx, float *bottom) {
    for (U32 i = 0; i < LABEL_COUNT; i++) {
        const Label *l = &labels[i];
        if (l->kind != 0 || (U32)l->room != room || l->flag >= KEROSENE_FLAG || (l->lang && l->lang != (english ? 2u : 1u))) continue;
        float x = ((int)(ZX(l->x) + ox)) * sx, y = ((int)(ZY(l->y) + oy)) * sy;
        *cx = x - l->ax * tk + l->w * tk / 2;
        *bottom = y - l->ay * tk + l->h * tk;
        return 1;
    }
    return 0;
}
static void build_enemies(const U32 *b1, const U32 *b2, const U32 *b5, const U32 *b7, U32 area, U32 floor, float ox, float oy, float sx, float sy, float tk, const Mark *marks, U32 nmarks, U32 W, U32 H) {
    BYTE *inv = *(BYTE **)(exe + EXE_INVENTORY);
    if (!readable(inv, 0xe473c)) return;
    unsigned chr = u32(inv + 0x5110) == 1, diff = enemy_diff_class(u32(inv + 0x24));
    float now = *(float *)(inv + 0xe4738), is = icon_side;
    static const float spread[9][2] = {{0, 0}, {1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, 1}, {-1, -1}, {1, -1}, {-1, 1}};
    static float placed[MAXOCC / 4][2];
    U32 np = 0;
    EnterCriticalSection(&enemy_cs);
    for (int i = 0; i < enemy_n; i++) {
        const EnemyRec *e = &enemy_recs[i];
        U32 icon = enemy_icon_of_em[e->em];
        if (icon == 255 || enemy_stale(e) || enemy_wasp_gone(e, bit(b1, WASP_NEST_FLAG)) || enemy_tyrant_gone(e, bit(b1, BARRY_WOKEN_FLAG)) || enemy_room_cleared(e->room, bit(b1, LAB_CLEARED_FLAG)) || !enemy_shown(e, chr, diff, now, bit(b5, (U32)e->room), e->gid && bitn(b2, e->gid, 1024))) continue;
        const int *r = (const int *)(exe + EXE_ROOMS + 96 * e->room);
        if ((U32)r[6] != area || (U32)r[7] != floor) continue;
        float px, py;
        project_pickup(e->room, e->x, e->z, &px, &py);
        float cx = ((int)(ZX(px) + ox)) * sx, cy = ((int)(ZY(py) + oy)) * sy;
        U32 j = 0; /* deterministic spread: n-th icon on the same spot moves to the n-th ring offset */
        for (U32 q = 0; q < np; q++) {
            float dx = placed[q][0] - cx, dy = placed[q][1] - cy;
            if (dx * dx + dy * dy < (is * .4f) * (is * .4f)) j++;
        }
        if (np < sizeof placed / sizeof *placed) { placed[np][0] = cx; placed[np][1] = cy; np++; }
        cx += spread[j % 9][0] * is * .45f; cy += spread[j % 9][1] * is * .45f;
        if (cx - is / 2 < 0 || cy - is / 2 < 0 || cx + is / 2 > W || cy + is / 2 > H) continue;
        if (core_covered(marks, nmarks, cx, cy, is)) continue; /* a common icon on a key or puzzle mark is not drawn */
        emit_color = icon_alpha;
        emit(ICON_FIRST + icon, cx - is / 2, cy - is / 2, is, is, 0, 0, 1, 1);
        reserve(cx - is / 2, cy - is / 2, is, is);
    }
    LeaveCriticalSection(&enemy_cs);
    for (U32 n = 0; n < sizeof static_enemies / sizeof *static_enemies; n++) {
        const StaticEnemy *e = &static_enemies[n];
        U32 icon = enemy_icon_of_em[e->em];
        const int *r = (const int *)(exe + EXE_ROOMS + 96 * e->room);
        if (icon == 255 || bit(b1, e->flag) || (U32)r[6] != area || (U32)r[7] != floor) continue;
        if (!(visibility == 2 || bit(b5, e->room) || (visibility == 1 && bit(b7, e->room)))) continue;
        float px, py;
        project_pickup(e->room, e->wx, e->wz, &px, &py);
        float cx = ((int)(ZX(px) + ox)) * sx, cy = ((int)(ZY(py) + oy)) * sy, bottom;
        if (e->under_name && room_name_spot(e->room, ox, oy, sx, sy, tk, &cx, &bottom)) cy = bottom + is / 2 + 2 * tk;
        if (cx - is / 2 < 0 || cy - is / 2 < 0 || cx + is / 2 > W || cy + is / 2 > H) continue;
        if (core_covered(marks, nmarks, cx, cy, is)) continue;
        emit_color = icon_alpha;
        emit(ICON_FIRST + icon, cx - is / 2, cy - is / 2, is, is, 0, 0, 1, 1);
        reserve(cx - is / 2, cy - is / 2, is, is);
    }
}

/* row 0 crimson, row 1 grey copy */
static float crimson_glyph(const CrimsonRect *r, int row, float pen, float y, float s) {
    int v = r->y + row * CRIMSON_ROW_H;
    emit(LABEL_COUNT, pen - CRIMSON_PAD * s, y, r->w * s, r->h * s, (float)r->x / CRIMSON_ATLAS_W,
         (float)v / CRIMSON_ATLAS_H, (float)(r->x + r->w) / CRIMSON_ATLAS_W, (float)(v + r->h) / CRIMSON_ATLAS_H);
    return pen + r->adv * s;
}

/* Dormant corpses: marker + minutes left; marker only once the revive time has passed. Grey while
 * revival is not unlocked (bank1 0x2f, set by scripted events 100/101; 0x4ea3a0 returns 0 without it). */
static void build_crimson(BYTE *mgr, U32 area, U32 floor, float ox, float oy, float sx, float sy, float s, U32 W, U32 H) {
    BYTE *obj = *(BYTE **)(exe + EXE_CRIMSON), *inv = *(BYTE **)(exe + EXE_INVENTORY);
    const BYTE *jbe = exe + EXE_REVIVE_JBE;
    if (jbe[0] == 0x90 && jbe[1] == 0x90) return; /* DeadShallNotRise: corpses never revive */
    if (!readable(obj, 0x40 + 1024 * 0x30) || !readable(inv, 0xe473c)) return;
    const U32 *b2 = (const U32 *)(mgr + 0x25c); /* bank2 at mgr+0x1f8+0x64, 1024 bits */
    float now = *(float *)(inv + 0xe4738);
    int idle = !bitn((const U32 *)(mgr + 0x21c), 0x2f, 512); /* bank1 */
    static U32 logged_opening;
    int log_now = logged_opening != map_opening;
    logged_opening = map_opening;
    for (U32 id = 0; id < 1024; id++) {
        const BYTE *rec = obj + 0x40 + id * 0x30;
        float revive = *(const float *)(rec + 0x2c), wx = *(const float *)(rec + 0x10), wz = *(const float *)(rec + 0x18);
        if (!bitn(b2, id, 1024) || !(revive > 0)) continue;
        if (!(wx > -1e5f && wx < 1e5f && wz > -1e5f && wz < 1e5f)) continue;
        float px, py;
        int room = death_room[id];
        if (room >= 0) { /* seen dying: exact room */
            const int *r = (const int *)(exe + EXE_ROOMS + 96 * room);
            if ((U32)r[6] != area || (U32)r[7] != floor) continue;
            project_pickup(room, wx, wz, &px, &py);
        } else { /* killed before tracking: static tables */
            const CrimsonEnemy *e = 0;
            for (U32 i = 0; i < CRIMSON_ENEMY_COUNT && !e; i++) if (crimson_enemies[i].id == id) e = &crimson_enemies[i];
            if (!e || (room = crimson_room(e, wx, wz, area, floor, &px, &py)) < 0) continue;
        }
        if (enemy_room_cleared(room, bitn((const U32 *)(mgr + 0x21c), LAB_CLEARED_FLAG, 512))) continue;
        if (log_now) {
            char line[128];
            wsprintfA(line, "crimson map id=%u room=%d%s x=%d y=%d z=%d left=%d\r\n", id, room, death_room[id] >= 0 ? "" : " (static)",
                      (int)wx, (int)*(const float *)(rec + 0x14), (int)wz, (int)((revive - now) / 30));
            log_line(line);
        }
        /* crimson-head icon at the corpse, grey while it cannot revive yet (revival locked, or its timer still running);
         * minutes left beside it when switched on with a long press of key 7 */
        float is = icon_side, cx = ((int)(ZX(px) + ox)) * sx, cy = ((int)(ZY(py) + oy)) * sy;
        float x = cx - is / 2, y = cy - is / 2, ty = cy - crimson_marker.h * s / 2;
        if (x < 0 || y < 0 || x + is > W || y + is > H) continue;
        emit_color = icon_alpha;
        emit(ICON_FIRST + (idle || revive > now ? CRIMSON_ICON_GREY : CRIMSON_ICON), x, y, is, is, 0, 0, 1, 1);
        float pen = x + is + CRIMSON_GAP * s + CRIMSON_PAD * s;
        if (revive <= now || !crimson_time) { reserve(x, y, is, is); continue; }
        int minutes = (int)((revive - now + CRIMSON_MINUTE - 1) / CRIMSON_MINUTE), d[3], n = 0;
        if (minutes > 999) minutes = 999;
        do d[n++] = minutes % 10; while ((minutes /= 10) && n < 3);
        while (n--) pen = crimson_glyph(&crimson_digit[d[n]], idle, pen, ty, s);
        pen = crimson_glyph(&crimson_unit[english != 0], idle, pen, ty, s);
        reserve(x, y, pen - x, is);
    }
}

static void build_kerosene(U32 i, float cx, float cy, float tk, U32 W, U32 H);
static void build_legend(const U32 *b1, float k, U32 W, U32 H);
/* Everything drawn on the map, as vertices. Game state is frozen while the map is open, so this runs
 * only when the view changes (opening, floor/area, scroll, settings, confirm hold), not every frame. */
/* Zoomed, the native "typewriter / item box" callouts are hidden: same rooms (room record +0x44, visited bit, native 0x5546xx),
 * each icon at its machine: the room's typewriter / item box aev area (src/save_points.h) through the pickup projection, so it
 * moves with the room at every zoom (ZX/ZY). A room missing from the table falls back to its middle (the old behaviour). */
static int save_point(U32 room, int kind, float *wx, float *wz) {
    for (U32 i = 0; i < SAVE_POINT_COUNT; i++)
        if (save_points[i].room == room && save_points[i].kind == kind) { *wx = save_points[i].wx; *wz = save_points[i].wz; return 1; }
    return 0;
}
static void build_save_icons(const U32 *b5, U32 area, U32 floor, float ox, float oy, float sx, float sy, float is, U32 W, U32 H) {
    emit_color = icon_alpha;
    for (U32 i = 0; i < 154; i++) {
        const int *r = (const int *)(exe + EXE_ROOMS + 96 * i);
        if ((U32)r[6] != area || (U32)r[7] != floor || !bit(b5, i)) continue;
        const int *extra = (const int *)(uintptr_t)r[0x44 / 4];
        int ok = extra && readable(extra, 0x18);
        float tx, tz;
        /* the room's own aev machine counts too: the Dining Room typewriter (aev type 6) has no native callout entry */
        int ntw = ok && extra[2] != -1, nbox = ok && extra[4] != -1; /* native callout exists (drawn natively when not zoomed) */
        int typewriter = zoom_on ? ntw || save_point(i, 0, &tx, &tz) : !ntw && save_point(i, 0, &tx, &tz);
        int box = zoom_on ? nbox || save_point(i, 1, &tx, &tz) : !nbox && save_point(i, 1, &tx, &tz);
        int n = typewriter + box, drawn = 0;
        if (!n) continue;
        for (int k = 0; k < 2; k++) {
            if (!(k ? box : typewriter)) continue;
            float wx, wz, px, py;
            if (save_point(i, k, &wx, &wz)) project_pickup((U32)i, wx, wz, &px, &py);
            else { px = 48 + .9f * (r[0] + r[0x58 / 4] * .9375f / 2); py = 36 + .9f * (r[1] + r[0x5c / 4] * .8035f / 2); }
            float cx = (ZX(px) + ox) * sx, cy = (ZY(py) + oy) * sy;
            float x = cx - is / 2, y = cy - is / 2;
            if (!save_point(i, k, &wx, &wz)) x = cx - n * is / 2 + drawn * is; /* fallback: the two side by side at the middle */
            drawn++;
            if (y < 0 || y + is > H || x < 0 || x + is > W) continue;
            emit(ICON_FIRST + (k ? ICON_ITEMBOX : ICON_TYPEWRITER), x, y, is, is, 0, 0, 1, 1);
            reserve(x, y, is, is);
        }
    }
}
/* The name image of an ordinary item row in the current language, -1 if it has none. */
static int item_name_image(U32 label, int lang) {
    U32 item = 0;
    for (U32 k = 0; k < ITEM_OF_LABEL_COUNT && !item; k++) if (item_of_label[k].label == label) item = item_of_label[k].item;
    for (U32 k = 0; item && k < NT_COUNT; k++) if (item_name_text[k].item == item && item_name_text[k].lang == (U32)lang) return NAME_FIRST + k;
    return -1;
}
/* The name image (item_name_text id) of a mark: ordinary items and the synthetic puzzle marks have their own, others use the label raster. */
static int item_name_by_id(U32 id, int lang) {
    for (U32 k = 0; k < NT_COUNT; k++) if (item_name_text[k].item == id && item_name_text[k].lang == (U32)lang) return NAME_FIRST + k;
    return -1;
}
/* Mark label indices LABEL_COUNT.. are the synthetic puzzle marks of synth_marks.h, as labels of kind 2 with the puzzle badge. */
static Label synth_store[SYN_COUNT];
#define PUZZLE_ICON 16 /* icons[15]: the orange ! badge every puzzle row uses */
#define DOC_ICON 18    /* icons[17]: the document badge every file row uses */
#define EVENT_ICON 15  /* icons[14]: the purple ? diamond (assets/icons/badge-event.png) */
static const Label *mark_label(U32 i) {
    if (i < LABEL_COUNT) return &labels[i];
    Label *l = &synth_store[i - LABEL_COUNT];
    const Synth *s = &synth_marks[i - LABEL_COUNT];
    l->kind = (int)s->kind; l->room = (int)s->room; l->room2 = -1; l->area = s->area; l->floor = s->floor; l->flag = s->flag; l->chr = s->chr;
    for (int k = 0; k < 5; k++) l->key_visits[k] = s->kv[k];
    l->x2 = s->wx; l->y2 = s->wz;
    return l;
}
/* The INI colour a mark category's name is drawn in. */
static int cat_color_of(int cat) {
    return cat == CAT_LOCK ? COL_LOCK : cat == CAT_KEY ? COL_KEY : cat == CAT_FILE ? COL_FILE : cat == CAT_ITEM ? COL_COMMON : cat == CAT_EVENT ? COL_EVENT : COL_PUZZLE;
}
/* Line bands of a name image (name_lines.h), 0 for a one-line name. */
static const NameLines *lines_of(U32 image) {
    if (image < LABEL_COUNT) { for (U32 n = 0; n < LABEL_LINES_COUNT; n++) if (label_lines[n].image == image) return &label_lines[n]; }
    else if (image >= NAME_FIRST) { for (U32 n = 0; n < NAMETEXT_LINES_COUNT; n++) if (nametext_lines[n].image == image - NAME_FIRST) return &nametext_lines[n]; }
    return 0;
}
/* A name in the box (x, y, w, h) with its lines aligned toward the icon: align -1 left, 1 right, 0 centred (the raster as drawn). Each line
 * is a sub-rectangle of the one raster (name_lines.h), shifted so the lines share the left or the right ink edge of the widest. */
static void emit_name(U32 i, float x, float y, float w, float h, int align) {
    const NameLines *nl = align ? lines_of(i) : 0;
    if (!nl) { emit(i, x, y, w, h, 0, 0, 1, 1); return; }
    float iw = (float)image_w(i), ih = (float)image_h(i), s = w / iw, sy = h / ih;
    int left = nl->line[0].x0, right = nl->line[0].x1;
    for (int n = 1; n < nl->lines; n++) { if (nl->line[n].x0 < left) left = nl->line[n].x0; if (nl->line[n].x1 > right) right = nl->line[n].x1; }
    for (int n = 0; n < nl->lines; n++) {
        int x0 = nl->line[n].x0, x1 = nl->line[n].x1, y0 = nl->line[n].y0, y1 = nl->line[n].y1, shift = (align < 0 ? left : right - (x1 - x0)) - x0;
        emit(i, x + (x0 + shift) * s, y + y0 * sy, (x1 - x0 + 1) * s, (y1 - y0 + 1) * sy, x0 / iw, y0 / ih, (x1 + 1) / iw, (y1 + 1) / ih);
    }
}
static void build(BYTE *mgr, U32 area, U32 floor, float ox, float oy, U32 W, U32 H, const Live *live, U32 nlive, U32 cur) {
    const U32 *b4 = (U32 *)(mgr + 0x31c), *b5 = (U32 *)(mgr + 0x33c), *b7 = (U32 *)(mgr + 0x37c);
    BYTE *inv = *(BYTE **)(exe + EXE_INVENTORY);
    U32 cbit = 0, dbit = 0, diff, files = 0;
    if (readable(inv, 0x5114)) {
        cbit = u32(inv + 0x5110) == 1 ? 0x20 : 0x10;
        diff = u32(inv + 0x24);
        files = u32(inv); /* collected-files bitset */
        dbit = diff == 1 ? 2 : diff == 2 ? 4 : 1;
    }
    const U32 *b1 = (U32 *)(mgr + 0x21c), *b2 = (U32 *)(mgr + 0x25c), *b3 = (U32 *)(mgr + 0x2dc); /* banks at mgr+0x1f8 +0x24 / +0x64 / +0xe4 */
    float sx = W / 1280.0f, sy = H / 720.0f, k = H / 1440.0f;
    float tk = k * name_size / 100.0f;
    U32 name_alpha = ((U32)(name_opacity * 255 + 50) / 100) << 24; /* name-like text: runtime opacity; the colour is ORed in per category */
    for (U32 y = 0; y < LAYERS; y++) for (U32 p = 0; p < MAXPAGES; p++) nverts[y][p] = 0;
    layer = 0;
    nocc = 0;
    icon_side = ITEM_ICON_PX * k * icon_size / 100.0f;
    icon_alpha = ((U32)(icon_opacity * 255 + 50) / 100) << 24 | 0xffffff;
    build_legend(b1, k, W, H); /* first: occ[0] legend and occ[1] readout, weight 8 */
    /* Marks (icon labels and ordinary items) are collected, laid out by marks.h and painted lowest tier first, each with its name. */
    static Mark marks[MAXOCC / 2];
    U32 nmarks = 0;
    float is = icon_side;
    static unsigned char event_room_seen[154];
    memset(event_room_seen, 0, sizeof event_room_seen);
    for (U32 i = 0; i < LABEL_COUNT + SYN_COUNT; i++) {
        const Label *l = mark_label(i);
        if (i >= LABEL_COUNT) {
            if (!syn_visible((int)(i - LABEL_COUNT), b5, files) || !syn_event_visible(&synth_marks[i - LABEL_COUNT], (const U32 *)(mgr + 0x1fc), b1, b2, b3)) continue;
            synth_store[i - LABEL_COUNT].icon = syn_icon((int)(i - LABEL_COUNT), b1, synth_marks[i - LABEL_COUNT].kind == SYN_EVENT_KIND ? EVENT_ICON : i - LABEL_COUNT >= SYN_DOC_ORGCHEM ? DOC_ICON : PUZZLE_ICON);
        }
        if (l->area != area || l->floor != floor || (l->lang && l->lang != (english ? 2u : 1u))) continue;
        if (all_off || hidden >> (l->kind == 3 ? 2 : l->kind) & 1) continue;
        int source_room = l->room2 >= 0 ? l->room2 : l->room;
        if (!placed_item_available(l->kind,l->flag,source_room,cbit==0x20,(const U32 *)(mgr+0x1fc),b1,b3)) continue;
        if (name_replaced(l,b5,b7,visibility)) continue;
        if ((l->kind == 4 || l->kind == 5 || l->kind == 7) && bitn(b3, l->flag, 512)) continue; /* picked up */
        if (l->kind == 4 && l->flag == 357 && bitn(b3, 341, 512)) continue; /* armor-key exchange finished */
        /* Cylinder Shaft is a return slot: inserted and still removable before generator completion. */
        if (l->kind == 4 && l->flag == 344 && (!bitn(b1, 160, 512) || bitn(b1, 158, 512))) continue;
        if (l->reward) {
            if (l->reward >= sizeof reward_rules / sizeof *reward_rules ||
                !reward_visible(&reward_rules[l->reward], l->kind, l->step, b1, b2, b3)) continue;
        }
        if (l->kind == 3 && (!readable(mgr, 0x498) || !rebecca_active(cbit == 0x10, (const U32 *)(mgr + 0x1fc), *(float *)(mgr + 0x494)))) continue;
        U32 m = l->chr & 0xff; /* 0x100 = vertical door (key label placement) */
        if (m && !(cbit && (m & cbit) && (!(m & 7) || (m & dbit)))) continue; /* other mode */
        if (i >= LABEL_COUNT + SYN_GEN_FIRST) { /* room-only events: one per room */
            if (event_room_seen[l->room]) continue;
            event_room_seen[l->room] = 1;
        }
        int shown = l->kind == 3 || visibility == 2 || explored(b5, l) || (visibility == 1 && explored(b7, l));
        if (l->kind == 1 && bit(b4, l->flag)) shown = 0;
        if (!shown) continue;
        if (l->kind == 0 && l->flag >= KEROSENE_FLAG && l->flag < KEROSENE_FLAG + 5) {
            build_kerosene(l->flag - KEROSENE_FLAG, ((int)(ZX(l->x) + ox)) * sx, ((int)(ZY(l->y) + oy)) * sy, tk, W, H);
            continue;
        }
        float w = l->w * tk, h = l->h * tk;
        int name_img = i >= LABEL_COUNT ? item_name_by_id(syn_name_id((int)(i - LABEL_COUNT)), english ? 2 : 1)
                                        : l->kind == 7 ? item_name_image(i, english ? 2 : 1) : -1;
        if (l->kind == 7 || i >= LABEL_COUNT) { /* the name image replaces the icon's size for the name box */
            w = name_img < 0 ? 0 : image_w(name_img) * tk; h = name_img < 0 ? 0 : image_h(name_img) * tk;
        }
        float px = l->x, py = l->y;
        U32 section=pickup_section(l,b5,b7,visibility);
        if ((int)section!=l->room || i >= LABEL_COUNT) project_pickup(section,l->x2,l->y2,&px,&py);
        if (i >= LABEL_COUNT + SYN_GEN_FIRST) room_name_side(l->room, &px, &py);
        /* Either photograph fits either board slot; use the active native slot, not an AEV centroid. */
        if (l->kind==4 && source_room==138 && (l->flag==392 || l->flag==393)) {
            unsigned first=l->flag==392?205:207;
            project_pickup(section,-243.300003f,bitn(b1,first,512)?15.0f:-115.0f,&px,&py);
        }
        /* Match physical pickup source, then project its frozen world point on the map section. */
        /* Observation Note and Master Key share Wesker's body; ignore the document's trigger centroid. */
        U32 position_flag=l->kind==5 && source_room==148 && l->flag==498 ? 405 : l->flag;
        if ((l->kind == 4 || l->kind == 5 || l->kind == 7) && (U32)source_room == cur)
            for (U32 j=0;j<nlive;j++)
                if (live[j].flag==position_flag) {
                    project_pickup(section,live[j].x,live[j].y,&px,&py);
                    break;
                }
        /* key: (x, y) lies inside room, (x2, y2) inside room2, 22 px either side of the door: its centre by default;
         * DoorKey=Unvisited labels the locked room = the one not visited yet, else the door's destination (room2) */
        if (l->kind == 1) {
            if (!door_key_unvisited) { px = (l->x + l->x2) / 2; py = (l->y + l->y2) / 2; }
            else if (!(bit(b5, l->room2) && !bit(b5, l->room))) { px = l->x2; py = l->y2; }
        }
        float cx = ((int)(ZX(px) + ox)) * sx, cy = ((int)(ZY(py) + oy)) * sy; /* marker point */
        if (l->icon || l->kind == 7) {
            Box b = {cx - is / 2, cy - is / 2, cx + is / 2, cy + is / 2};
            if (b.l < 0 || b.t < 0 || b.r > W || b.b > H || boxes_hit(b, occ[0].box) || boxes_hit(b, occ[1].box)) continue;
            int cat = l->kind == 1 ? CAT_LOCK : l->kind == 4 ? CAT_KEY : l->kind == 5 ? CAT_FILE : l->kind == 7 ? CAT_ITEM : l->kind == EVENT_KIND ? CAT_EVENT : CAT_PUZZLE, dup = 0;
            /* the same name at the same spot is one pickup listed twice; each row still decided for itself above */
            for (U32 j = 0; j < nmarks && !dup; j++) {
                const Label *o = mark_label(marks[j].label);
                dup = o->kind == l->kind && o->icon == l->icon && o->w == l->w && o->h == l->h &&
                      marks[j].mark.l - b.l < 4 && b.l - marks[j].mark.l < 4 && marks[j].mark.t - b.t < 4 && b.t - marks[j].mark.t < 4;
            }
            if (dup || nmarks >= sizeof marks / sizeof *marks) continue;
            marks[nmarks++] = (Mark){i, cat, l->kind == 3 || l->kind == EVENT_KIND, b, {0, 0, 0, 0}, w, h, MARK_KEEP, 0};
            continue;
        }
        /* room names: painted first and never moved; marks do not avoid them, names weigh them 4x. (x, y) is the anchor and
         * (ax, ay) its place in the raster: a leader's room end, or the text centre, so a resized name grows away from it */
        float x = cx - l->ax * tk, y = cy - l->ay * tk;
        if (x < 0 || y < 0 || x + w > W || y + h > H) continue;
        emit_color = name_alpha | cat_color[COL_ROOM];
        emit(i, x, y, w, h, 0, 0, 1, 1);
        reserve_w(x, y, w, h, 4);
    }
    /* Enemies, Crimson Heads and the zoomed save icons: the lowest priority, painted before the marks, weight 1. */
    if (!all_off && !(hidden >> CRIMSON_KIND & 1)) {
        build_enemies(b1, b2, (const U32 *)(mgr + 0x33c), b7, area, floor, ox, oy, sx, sy, tk, marks, nmarks, W, H);
        build_crimson(mgr, area, floor, ox, oy, sx, sy, tk, W, H);
    }
    if (!all_off) build_save_icons(b5, area, floor, ox, oy, sx, sy, is, W, H); /* zoomed: all; else only machines without a native callout */
    nocc = marks_layout(marks, nmarks, occ, nocc, MAXOCC, is, item_names, W, H);
    for (int pass = 0; pass < 2; pass++)
        for (U32 n = 0; n < nmarks; n++) {
            const Mark *m = &marks[n];
            const Label *l = mark_label(m->label);
            if (m->state == MARK_DROP || top_tier(m->cat) != pass) continue;
            emit_color = icon_alpha;
            emit(l->kind == 7 ? m->label : ICON_FIRST + l->icon - 1, m->mark.l, m->mark.t, is, is, 0, 0, 1, 1);
            if (m->state != MARK_NAMED) continue;
            emit_color = name_alpha | cat_color[cat_color_of(m->cat)];
            emit_name(m->label >= LABEL_COUNT ? item_name_by_id(syn_name_id((int)(m->label - LABEL_COUNT)), english ? 2 : 1) : l->kind == 7 ? item_name_image(m->label, english ? 2 : 1) : m->label, m->name.l, m->name.t, m->name.r - m->name.l, m->name.b - m->name.t, name_align(m->slot));
        }
    emit_color = 0xffffffff;
}

/* RE3-style legend. Per-language kind 6 rows, order must match tools/rebuild_legend.py (one white raster per row; the colour is
 * multiplied in at draw time): */
#define LG_TITLE   0
#define LG_OPACITY 1  /* 10 levels, 10..100 */
#define LG_SIZE    11 /* 11 levels, 50..150 */
#define LG_ROW     22 /* categories [0]..[8] */
#define LG_SCOPE   31 /* [9], 3 states */
#define LG_NOTE    34
#define LG_ZOOM    (LABEL_COUNT - 2) /* appended after both language blocks: Korean, English */
static void legend_quad(U32 i, float x, float y, float k, U32 rgb) {
    emit_color = 0xff000000u | rgb;
    emit(i, x, y, image_w(i) * k, image_h(i) * k, 0, 0, 1, 1);
}
static float quad_w(U32 i, float k) { return image_w(i) * k; }
static void legend_panel(float x, float y, float w, float h) {
    emit_color = 0xd0ffffff; layer = 1; /* dark panel, ~80% opaque */
    emit(PANEL_IMAGE, x, y, w, h, .25f, .25f, .75f, .75f);
    emit_color = 0xffffffff; layer = 2;
}
/* Legend bottom-left (user decision 2026-11-08, RE0 layout): title with the [~] hint beside it, then two columns top to bottom:
 * [0]..[4] and [H] item names under [4] | [5]..[8], [9] scope under [8] and [\] language under [9]; the zoom hint below. The panel is as wide
 * as the widest state of every row in either language, so it does not jump while a setting or the language changes. Readout bottom-right:
 * name opacity and size, icon opacity and size (with the INI modifier). [~] folds both to one line (RE0 HD legend). Always reserves occ[0]
 * and occ[1]. Every row is a white raster tinted here: categories by the INI [Colors], a disabled row #6A6A6A. */
static void build_legend(const U32 *b1, float k, U32 W, U32 H) {
    (void)b1;
    static const int row_kind[9] = {-1, 0, 1, 4, 5, 2, EVENT_KIND, 7, CRIMSON_KIND}; /* [0]..[8] -> hidden bit */
    static const int row_color[9] = {-1, COL_ROOM, COL_LOCK, COL_KEY, COL_FILE, COL_PUZZLE, COL_EVENT, COL_COMMON, COL_ENEMY};
    U32 base = LEGEND_FIRST + (english ? LEGEND_PER_LANG : 0), lt = TEXT_FIRST + (english ? LT_PER_LANG : 0);
    U32 mod = modifier_vk == VK_CONTROL;
    float pad = 12 * k, gap = 22 * k, lh = 30 * k, margin = 28 * k, col[2] = {0, 0}, tw = 0, th = 0, hw_hide = 0, zw = 0;
    if (!legend_open) {
        float w = 2 * pad + quad_w(lt + LT_FOLD, k), h = 2 * pad + image_h(lt + LT_FOLD) * k, x0 = margin, y0 = (float)H - margin - h;
        legend_top = y0 * 720.0f / H;
        reserve_w(x0, y0, w, h, 8);
        reserve_w(0, 0, 0, 0, 8); /* no readout while folded */
        legend_panel(x0, y0, w, h);
        legend_quad(lt + LT_FOLD, x0 + pad, y0 + pad, k, COLOR_READOUT);
        layer = 0;
        return;
    }
    for (U32 lang = 0; lang < 2; lang++) { /* widest of both languages and of every state: a stable panel */
        U32 b = LEGEND_FIRST + lang * LEGEND_PER_LANG, l = TEXT_FIRST + lang * LT_PER_LANG;
        for (U32 r = 0; r < 9; r++) { float w = labels[b + LG_ROW + r].w * k; if (w > col[r < 5 ? 0 : 1]) col[r < 5 ? 0 : 1] = w; }
        for (U32 i = 0; i < 3; i++) {
            if (labels[b + LG_SCOPE + i].w * k > col[1]) col[1] = labels[b + LG_SCOPE + i].w * k;
            if (quad_w(l + LT_ITEM_NAMES + i, k) > col[0]) col[0] = quad_w(l + LT_ITEM_NAMES + i, k);
        }
        if (quad_w(l + LT_LANG, k) > col[1]) col[1] = quad_w(l + LT_LANG, k);
        if (labels[b + LG_TITLE].w * k + quad_w(l + LT_HIDE, k) > tw + hw_hide) { tw = labels[b + LG_TITLE].w * k; hw_hide = quad_w(l + LT_HIDE, k); }
        if (quad_w(LG_ZOOM + lang, k) > zw) zw = quad_w(LG_ZOOM + lang, k);
    }
    th = labels[base + LG_TITLE].h * k;
    float hide_gap = 14 * k, hh = th + 6 * k, cw = col[0] + gap + col[1], hw = tw + hide_gap + hw_hide;
    float w = 2 * pad + (cw > hw ? cw : hw);
    U32 zoom_row = LG_ZOOM + (english ? 1 : 0);
    if (zw + 2 * pad > w) w = zw + 2 * pad;
    float h = 2 * pad + hh + 6 * lh + lh * 0.85f;
    float x0 = margin, y0 = (float)H - margin - h; /* ponytail: margins unverified against native HUD */
    legend_top = y0 * 720.0f / H;
    reserve_w(x0, y0, w, h, 8);
    legend_panel(x0, y0, w, h);
    float x = x0 + pad, y = y0 + pad, x1 = x + col[0] + gap;
    legend_quad(base + LG_TITLE, x, y, k, COLOR_WHITE);
    legend_quad(lt + LT_HIDE, x + labels[base + LG_TITLE].w * k + hide_gap, y + th - image_h(lt + LT_HIDE) * k, k, COLOR_READOUT);
    y += hh;
    for (U32 r = 0; r < 9; r++) {
        int on = !all_off && (r == 0 || !(hidden >> row_kind[r] & 1));
        legend_quad(base + LG_ROW + r, r < 5 ? x : x1, y + (r < 5 ? r : r - 5) * lh, k, !on ? COLOR_OFF : r == 0 ? COLOR_WHITE : cat_color[row_color[r]]);
    }
    legend_quad(lt + LT_ITEM_NAMES + (U32)((item_names + 2) % 3), x, y + 5 * lh, k, item_names ? COLOR_WHITE : COLOR_OFF); /* under [4]; All, No common, Off for 1, 2, 0 */
    legend_quad(base + LG_SCOPE + visibility, x1, y + 4 * lh, k, COLOR_WHITE);                                           /* [9] under [8] */
    legend_quad(lt + LT_LANG, x1, y + 5 * lh, k, COLOR_WHITE);                                                           /* [\] under [9]: the size and colour of [H] */
    y += 6 * lh;
    legend_quad(zoom_row, x, y, k, COLOR_HINT);
    /* readout: widest value of each row, so the panel does not jump while a value changes */
    U32 rows[4] = {base + LG_OPACITY + name_opacity / 10 - 1, base + LG_SIZE + (name_size - 50) / 10,
                   lt + LT_ICON_OPACITY + mod * 10 + (icon_opacity - 10) / 10, lt + LT_ICON_SIZE + mod * 16 + (icon_size - 50) / 10};
    float rw = 0, rh = 0;
    for (U32 i = 0; i < 21; i++) if (quad_w(base + LG_OPACITY + i, k) > rw) rw = quad_w(base + LG_OPACITY + i, k);
    for (U32 i = 0; i < 10; i++) if (quad_w(lt + LT_ICON_OPACITY + mod * 10 + i, k) > rw) rw = quad_w(lt + LT_ICON_OPACITY + mod * 10 + i, k);
    for (U32 i = 0; i < 16; i++) if (quad_w(lt + LT_ICON_SIZE + mod * 16 + i, k) > rw) rw = quad_w(lt + LT_ICON_SIZE + mod * 16 + i, k);
    for (U32 i = 0; i < 4; i++) rh += image_h(rows[i]) * k;
    float rx = (float)W - margin - (rw + 2 * pad), ry = (float)H - margin - (rh + 2 * pad);
    reserve_w(rx, ry, rw + 2 * pad, rh + 2 * pad, 8);
    legend_panel(rx, ry, rw + 2 * pad, rh + 2 * pad);
    y = ry + pad;
    for (U32 i = 0; i < 4; i++) { legend_quad(rows[i], rx + pad, y, k, COLOR_READOUT); y += image_h(rows[i]) * k; }
    layer = 0;
}

/* Kerosene tank i (labels flag KEROSENE_FLAG+i; 102,114,118,403,503): jerrycan icon at 80% of the item-icon
 * size, refills left over its bottom-right corner like an inventory count. Left = INV+0x50a0+i*4 (refill
 * 0x667f70 takes 2, or 1 when the canteen is not empty or 1 is left; new game sets 4 or 5 at 0x4eedeb/
 * 0x4eeee6). Grey once empty. */
#define KEROSENE_ICON 0.8f
static void build_kerosene(U32 i, float cx, float cy, float tk, U32 W, U32 H) {
    BYTE *inv = *(BYTE **)(exe + EXE_INVENTORY);
    if (!readable(inv, 0x50b4)) return;
    int left = *(const int *)(inv + 0x50a0 + 4 * i), d[2], n = 0;
    if (left < 0) left = 0;
    if (left > 99) left = 99;
    float s = KEROSENE_ICON * icon_side, iw = s * fuel_icon.w / fuel_icon.h, x = cx - iw / 2, y = cy - s / 2;
    if (x < 0 || y < 0 || x + iw > W || y + s > H) return;
    emit_color = icon_alpha; /* icon and count follow the icon opacity, not the name opacity */
    emit(LABEL_COUNT, x, y, iw, s, (float)fuel_icon.x / CRIMSON_ATLAS_W, (float)fuel_icon.y / CRIMSON_ATLAS_H,
         (float)(fuel_icon.x + fuel_icon.w) / CRIMSON_ATLAS_W, (float)(fuel_icon.y + fuel_icon.h) / CRIMSON_ATLAS_H);
    reserve(x, y, iw, s);
    int row = left ? 2 : 1;
    float tw = 0;
    do tw += crimson_digit[d[n++] = left % 10].adv; while ((left /= 10) && n < 2);
    /* digits overhang the icon's bottom-right corner by 3 px (text scale) */
    float pen = x + iw - (tw - 3) * tk, gy = y + s - (CRIMSON_ROW_H - 7) * tk;
    while (n--) pen = crimson_glyph(&crimson_digit[d[n]], row, pen, gy, tk);
}

static void draw(void *dev) {
    BYTE *map = (BYTE *)map_object, *mgr, *ren;
    void *surface = 0, *state = 0; SurfaceDesc desc;
    static struct { void *dev; U32 session, area, floor, W, H, BW, BH; float ox, oy, zx, zy; LONG zoom; LONG hidden, english, all_off, visibility, name_size, name_opacity, crimson_time, icon_size, icon_opacity, item_names, legend_open, modifier_vk; } view, seen;
    if (!map || frame - map_frame > 3) { draw_trace(1, frame, map_frame, (U32)map, 0); return; }
    if (!readable(map, 0x62a0)) { draw_trace(2, (U32)map, 0, 0, 0); return; }
    /* Native +0x629c: 0 map, 1 item-box selection/list, 2 selected box contents. */
    if (u32(map + 0x629c) != 0) return;
    U32 area = u32(map + 0x6268), floor = u32(map + 0x626c);
    float ox = *(float *)(map + 0x6090), oy = *(float *)(map + 0x6094);
    mgr = *(BYTE **)(exe + EXE_BANKS); ren = *(BYTE **)(exe + EXE_RENDERER);
    if (area >= 7 || floor >= 7 || !(ox > -4096 && ox < 4096 && oy > -4096 && oy < 4096)) {
        draw_trace(3, area, floor, u32(map + 0x6090), u32(map + 0x6094)); return;
    }
    if (!readable(mgr, 0x3a0) || !readable(ren, 0xc0)) { draw_trace(4, (U32)mgr, (U32)ren, 0, 0); return; }
    U32 W = u32(ren + 0xb8), H = u32(ren + 0xbc);
    HRESULT got = ((HRESULT (WINAPI *)(void *, U32, void **))method(dev, 38))(dev, 0, &surface);
    if (got < 0 || !surface) { draw_trace(5, got, W, H, 0); return; }
    HRESULT hr = ((HRESULT (WINAPI *)(void *, SurfaceDesc *))method(surface, 12))(surface, &desc);
    release(surface);
    if (hr < 0) { draw_trace(15, hr, W, H, 0); return; }
    if (!desc.w || !desc.h || W < 320 || H < 200) {
        draw_trace(6, W, H, desc.w, desc.h); return;
    }
    fit_screen(desc.w, desc.h, W, H);
    if (!make_pages(dev)) return;
    static U32 drawn_frame;
    if (frame - drawn_frame > 3) map_opening++; /* a new opening of the map screen (crimson log once each) */
    drawn_frame = frame;
    /* shortcut: candidate lifetime checks remain unchanged; active-list validation is separate. */
    static Live live[MAXU];
    static U32 live_session, cur = 0xffffffff, nlive;
    static int live_ready;
    if (!live_ready || live_session != map_session) {
        BYTE *rs = *(BYTE **)(exe + EXE_ROOMSTATE);
        cur = 0xffffffff;
        nlive = 0;
        if (readable(rs, 0x28) && u32(rs + 0x20) < 7 && u32(rs + 0x24) < 64) {
            cur = stage_first[u32(rs + 0x20)] + u32(rs + 0x24);
            if (cur < 154) nlive = live_units(cur, live);
        }
        live_session = map_session;
        live_ready = 1;
    }
    view.dev = dev; view.session = map_session; view.area = area; view.floor = floor; view.W = W; view.H = H; view.BW = desc.w; view.BH = desc.h; view.zoom = zoom_on; view.zx = zoom_on ? zoom_x : 0; view.zy = zoom_on ? zoom_y : 0;
    view.ox = ox; view.oy = oy; view.hidden = hidden; view.english = english; view.all_off = all_off;
    view.visibility = visibility; view.name_size = name_size; view.name_opacity = name_opacity; view.crimson_time = crimson_time;
    view.icon_size = icon_size; view.icon_opacity = icon_opacity; view.item_names = item_names; view.legend_open = legend_open; view.modifier_vk = modifier_vk;
    if (memcmp(&view, &seen, sizeof view)) { seen = view; build(mgr, area, floor, ox, oy, W, H, live, nlive, cur); }
    HRESULT saved = ((HRESULT (WINAPI *)(void *, U32, void **))method(dev, 59))(dev, 1 /*ALL*/, &state);
    if (saved < 0 || !state) { draw_trace(7, saved, W, H, 0); return; }
    draw_trace(8, W, H, area, floor);
    U32 vp[6] = {0};
    ((HRESULT (WINAPI *)(void *, U32 *))method(dev, 48))(dev, vp);
    draw_trace(16, vp[0], vp[1], vp[2], vp[3]);
    set_states(dev);
    /* Native states 2 and 3 load the next floor and draw no rooms (0x553d84); markers wait with them, the legend stays. */
    U32 map_state = u32(map + 0x60ac);
    int rooms_hidden = map_state == 2 || map_state == 3;
    /* the game's last viewport may not cover the shifted picture; the state block restores it */
    float z1 = 1; U32 full[6] = {0, 0, desc.w, desc.h, 0, *(U32 *)&z1};
    ((HRESULT (WINAPI *)(void *, const U32 *))method(dev, 47))(dev, full);
    for (U32 y = rooms_hidden ? 1 : 0; y < LAYERS; y++)
        for (U32 p = 0; p < npages; p++) {
            if (!nverts[y][p]) continue;
            ((HRESULT (WINAPI *)(void *, U32, void *))method(dev, 65))(dev, 0, pages[p]);
            HRESULT drawn = ((HRESULT (WINAPI *)(void *, U32, U32, const void *, U32))method(dev, 83))
                    (dev, 4 /*TRIANGLELIST*/, nverts[y][p] / 3, verts[y][p], sizeof(Vertex));
            draw_trace(drawn < 0 ? 11 : 14, drawn, p, nverts[y][p], 0);
        }
    ((HRESULT (WINAPI *)(void *))method(state, 5))(state);
    release(state);
}

static void zoom_title_check(void);
static int WINAPI end_scene(void *dev) {
    void **vt = *(void ***)dev;
    for (int i = 0; i < 4; i++)
        if (chain[i].vt == vt) {
            frame++;
            zoom_title_check();
            draw(dev);
            return chain[i].fn(dev);
        }
    return 0x8876086c; /* D3DERR_INVALIDCALL: unreachable, only hooked vtables land here */
}

static int map_open(void) {
    return map_object && frame - map_frame <= 3;
}
static int game_in_front(void) {
    DWORD pid = 0;
    GetWindowThreadProcessId(GetForegroundWindow(), &pid);
    return pid == GetCurrentProcessId();
}
static int step_by(LONG v, int d, int lo, int hi) { v += d; return v < lo ? lo : v > hi ? hi : (int)v; }
static void poll_keys(void) {
    /* 1-7 groups, \\ language, 0 everything, 9 scope, H item names, ~ legend; - + [ ] name size and opacity, with the INI
     * modifier (Shift by default) icon size and opacity. Every toggle rests KEY_REST_MS after it fires. */
    static const int keys[] = {'1', '2', '3', '4', '5', '6', '7', VK_OEM_5, '0', '9', 'H', VK_OEM_3, VK_OEM_MINUS, VK_SUBTRACT, VK_OEM_PLUS, VK_ADD, VK_OEM_4, VK_OEM_6};
    static KeyRest rest[sizeof keys / sizeof *keys];
    if (!map_open() || !game_in_front()) return;
    /* key 8: tap switches enemies; long press, with enemies on, switches the minutes left */
    static HoldKey eight;
    int step = hold_key_step(&eight, (GetAsyncKeyState('8') & 0x8000) != 0, GetTickCount());
    if (step == HOLD_TAP) { InterlockedXor(&hidden, 1 << CRIMSON_KIND); save_settings(); }
    if (step == HOLD_LONG && !(hidden >> CRIMSON_KIND & 1)) { InterlockedXor(&crimson_time, 1); save_settings(); }
    int mod = (GetAsyncKeyState(modifier_vk) & 0x8000) != 0;
    for (int i = 0; i < (int)(sizeof keys / sizeof *keys); i++) {
        int key = keys[i];
        if (!key_rest_step(&rest[i], (GetAsyncKeyState(key) & 0x8000) != 0, GetTickCount())) continue;
        if (i < GROUPS) InterlockedXor(&hidden, 1 << toggle_kind[i]);
        else if (key == VK_OEM_5) InterlockedXor(&english, 1);
        else if (key == '9') visibility = (visibility + 1) % 3;
        else if (key == '0') InterlockedXor(&all_off, 1);
        else if (key == 'H') item_names = item_names == 1 ? 2 : item_names == 2 ? 0 : 1; /* all -> no common -> hidden -> all */
        else if (key == VK_OEM_3) InterlockedXor(&legend_open, 1);
        else {
            int d = key == VK_OEM_MINUS || key == VK_SUBTRACT || key == VK_OEM_4 ? -10 : 10, opacity = key == VK_OEM_4 || key == VK_OEM_6;
            if (mod && opacity) icon_opacity = step_by(icon_opacity, d, 10, 100);
            else if (mod) icon_size = step_by(icon_size, d, 50, 200);
            else if (opacity) name_opacity = step_by(name_opacity, d, 10, 100);
            else name_size = step_by(name_size, d, 50, 150);
        }
        save_settings();
    }
}

/* 2x view. All 39 map calls to 0x5561d0 are sorted here; SITE_MARKER (player) keeps its size. */
#define EXE_PAD        0x9595c4 /* [0xd595c4] pad object */
#define EXE_PAD_CONFIG 0x9599e4 /* [0xd599e4] pad action masks */
#define VA_SPRITE      0x5561d0
#define VA_PAD_HELD    0x4d9230
#define VA_PAD_REPEAT  0x4d93c0
#define VA_PAD_EDGE    0x4d9550
#define SITE_MARKER    0x555286
#define SITE_PAD       0x552b1b
/* Pad masks per action in the current scheme's block at config +0xba0. Native defaults for scheme A (0xc2ea90):
 * +0x1c LT aim, +0x24 RT attack, +0x28 LB switch target, +0x14 X run, +0x34 Y status, +0x3c A investigate. */
#define SLOT_ATTACK      0x24
#define EXE_GUI          0x8f2788 /* [0xcf2788]: 0x4ddf40 returns the GUI item under the mouse, -1 for none */
#define VA_GUI_HOVER     0x4ddf40
/* rooms and door marks scale */
#define SITE_PAPER 0x5537de
/* paper art bakes in the compass, dial socket and rule; zoomed, draw a clean part of it (same 4:3 shape) */
static const int paper_uv[4] = {20, 150, 340, 430};
static const U32 zoom_sites[] = {0x554079, 0x5540ed, 0x5541f3, 0x554251, 0x554617, 0x554fb0, 0x5555d4, 0x555631};
/* Floor name: a native GUI text object, not a sprite. Zoomed it moves above the legend (game px at 1280x720). */
#define EXE_MSG_MANAGER 0x8f30d8 /* [0xcf30d8] +0x30 text unit, +0x250 floor name object, +0x80 position */
#define VA_GUI_SET_POS  0x9eee20
/* dial, compass, legend and buttons, plus the native callouts: art 0x55472a/b, typewriter 0x5547c2/e5, item box 0x5548f3/0x554911.
 * build_save_icons draws those two as icons instead. */
static const U32 hidden_sites[] = {0x553ef9, 0x553f20, 0x5547c2, 0x5547e5, 0x5548f3, 0x554911, 0x553867, 0x5538fc, 0x553985, 0x553a73, 0x553b0f, 0x553ba4, 0x553d11, 0x553d79,
    0x553e73, 0x55472a, 0x55474b, 0x554a99, 0x554b9a, 0x554c2f, 0x554cc4, 0x555769, 0x555792, 0x555819, 0x555842, 0x5558c0,
    0x55593e, 0x5559c1, 0x555a44};
#define COUNT(a) (sizeof (a) / sizeof *(a))
static volatile float marker_x, marker_y;
static volatile U32 marker_frame, zoom_session;
static void __fastcall zoom_sprite_hook(void *map, void *edx, const int *s) {
    (void)edx;
    void (__thiscall *orig)(void *, const int *) = (void *)VA_SPRITE;
    if (!zoom_on || u32((BYTE *)map + 0x629c)) { orig(map, s); return; }
    int copy[0x5c / 4];
    CopyMemory(copy, s, sizeof copy);
    zoom_sprite(copy, zoom_x, zoom_y);
    orig(map, copy);
}
static void __fastcall fixed_sprite_hook(void *map, void *edx, const int *s) {
    (void)edx;
    void (__thiscall *orig)(void *, const int *) = (void *)VA_SPRITE;
    if (!zoom_on || u32((BYTE *)map + 0x629c)) { orig(map, s); return; }
    int copy[0x5c / 4];
    CopyMemory(copy, s, sizeof copy);
    zoom_sprite_fixed(copy, zoom_x, zoom_y);
    orig(map, copy);
}
static void __fastcall paper_sprite_hook(void *map, void *edx, const int *s) {
    (void)edx;
    void (__thiscall *orig)(void *, const int *) = (void *)VA_SPRITE;
    if (!zoom_on || u32((BYTE *)map + 0x629c)) { orig(map, s); return; }
    int copy[0x5c / 4];
    CopyMemory(copy, s, sizeof copy);
    zoom_sprite(copy, zoom_x, zoom_y);
    CopyMemory(copy + 12, paper_uv, sizeof paper_uv);
    orig(map, copy);
}
/* Moves the floor name while wanted; idempotent. The saved position goes back before any other screen uses the object. */
static void zoom_title_set(int want) {
    static BYTE *moved;
    static float saved[4];
    void (__thiscall *set_pos)(void *, const float *) = (void *)VA_GUI_SET_POS;
    if (!want) {
        if (moved && readable(moved, 0x90)) set_pos(moved, saved);
        moved = 0;
        return;
    }
    if (!moved) {
        BYTE *mgr = *(BYTE **)(exe + EXE_MSG_MANAGER), *unit = readable(mgr, 0x34) ? *(BYTE **)(mgr + 0x30) : 0;
        BYTE *obj = readable(unit, 0x254) ? *(BYTE **)(unit + 0x250) : 0;
        if (!readable(obj, 0x90)) return;
        CopyMemory(saved, obj + 0x80, sizeof saved);
        moved = obj;
    }
    float pos[4] = {saved[0] + zoom_title_dx(), saved[1] + zoom_title_dy(legend_top), saved[2], saved[3]};
    set_pos(moved, pos); /* a no-op unless the legend height changed */
}
static void zoom_title_check(void) {
    BYTE *map = (BYTE *)map_object;
    if (!(zoom_on && frame - map_frame <= 3 && map && !u32(map + 0x629c))) zoom_title_set(0);
}
static void __fastcall hidden_sprite_hook(void *map, void *edx, const int *s) {
    (void)edx;
    if (zoom_on && !u32((BYTE *)map + 0x629c)) return;
    ((void (__thiscall *)(void *, const int *))VA_SPRITE)(map, s);
}
static void __fastcall marker_sprite_hook(void *map, void *edx, const int *s) {
    marker_x = s[4] + s[6] / 2.0f; marker_y = s[5] + s[7] / 2.0f;
    marker_frame = frame;
    fixed_sprite_hook(map, edx, s);
}
static void zoom_toggle_now(void) {
    if (zoom_on) { zoom_on = 0; return; }
    int on_floor = frame - marker_frame <= 3; /* player on this floor: centre there, as a map reader expects */
    zoom_x = zoom_clamp_x(on_floor ? ZOOM_CX - 2 * marker_x : -ZOOM_CX);
    zoom_y = zoom_clamp_y(on_floor ? ZOOM_CY - 2 * marker_y : -ZOOM_CY);
    zoom_on = 1;
}
/* Replaces the native repeat read in map state idle: zoomed, directions pan instead of changing floor or area. */
static U32 __fastcall pad_repeat_hook(void *pad, void *edx, int a) {
    (void)edx;
    U32 r = ((U32 (__thiscall *)(void *, int))VA_PAD_REPEAT)(pad, a);
    BYTE *map = (BYTE *)map_object;
    if (zoom_session != map_session) { zoom_session = map_session; zoom_on = 0; }
    if (!map || !readable(map, 0x62b0) || u32(map + 0x629c)) return r;
    BYTE *cfg = *(BYTE **)(exe + EXE_PAD_CONFIG);
    if (!readable(cfg, 0xcf8)) return r;
    U32 edge = ((U32 (__thiscall *)(void *, int, int))VA_PAD_EDGE)(pad, 0, 0);
    U32 scheme = u32(cfg + 0xcf4);
    const BYTE *slot = cfg + 0xba0 + (scheme < 5 ? scheme * 0x44 : 0);
    /* Attack on the pad; on the keyboard the left mouse button, as in the game's key guide. A click on a map button stays the game's. */
    static int left_was;
    int left = game_in_front() && (GetAsyncKeyState(VK_LBUTTON) & 0x8000);
    int click = left && !left_was && ((int (__thiscall *)(void *))VA_GUI_HOVER)(*(void **)(exe + EXE_GUI)) == -1;
    left_was = left;
    if ((edge & u32(slot + SLOT_ATTACK)) || click) zoom_toggle_now();
    static DWORD last;
    DWORD now = GetTickCount(), ms = now - last;
    last = now;
    if (!zoom_on) return r;
    zoom_title_set(1);
    float x = zoom_x, y = zoom_y;
    zoom_pan(((U32 (__thiscall *)(void *, int))VA_PAD_HELD)(pad, 0), ms, &x, &y);
    zoom_x = x; zoom_y = y;
    return 0;
}
/* Every site must be the expected call, or none is patched. */
static int patch_call(U32 site, U32 target, const void *to, int write) {
    BYTE *p = (BYTE *)(uintptr_t)site;
    if (!readable(p, 5) || p[0] != 0xe8 || (U32)(site + 5 + *(int *)(p + 1)) != target) return 0;
    if (!write) return 1;
    DWORD old;
    if (!VirtualProtect(p, 5, PAGE_EXECUTE_READWRITE, &old)) return 0;
    *(int *)(p + 1) = (int)((U32)(uintptr_t)to - (site + 5));
    VirtualProtect(p, 5, old, &old);
    FlushInstructionCache(GetCurrentProcess(), p, 5);
    return 1;
}
static void hook_zoom(void) {
    int ok = patch_call(SITE_PAD, VA_PAD_REPEAT, 0, 0) && patch_call(SITE_MARKER, VA_SPRITE, 0, 0);
    for (U32 i = 0; ok && i < COUNT(zoom_sites); i++) ok = patch_call(zoom_sites[i], VA_SPRITE, 0, 0);
    ok = ok && patch_call(SITE_PAPER, VA_SPRITE, 0, 0);
    for (U32 i = 0; ok && i < COUNT(hidden_sites); i++) ok = patch_call(hidden_sites[i], VA_SPRITE, 0, 0);
    if (!ok) { log_line("zoom sites mismatch; zoom off\r\n"); return; }
    for (U32 i = 0; i < COUNT(zoom_sites); i++) patch_call(zoom_sites[i], VA_SPRITE, (void *)zoom_sprite_hook, 1);
    patch_call(SITE_PAPER, VA_SPRITE, (void *)paper_sprite_hook, 1);
    for (U32 i = 0; i < COUNT(hidden_sites); i++) patch_call(hidden_sites[i], VA_SPRITE, (void *)hidden_sprite_hook, 1);
    patch_call(SITE_MARKER, VA_SPRITE, (void *)marker_sprite_hook, 1);
    patch_call(SITE_PAD, VA_PAD_REPEAT, (void *)pad_repeat_hook, 1);
    log_line("zoom hooked\r\n");
}

static int patch_slot(void **slot, void *value) {
    DWORD old;
    if (!VirtualProtect(slot, 4, PAGE_EXECUTE_READWRITE, &old)) return 0;
    InterlockedExchangePointer(slot, value);
    VirtualProtect(slot, 4, old, &old);
    return 1;
}
static int in_image(const void *p, void **base) {
    MEMORY_BASIC_INFORMATION m;
    return VirtualQuery(p, &m, sizeof m) && m.Type == MEM_IMAGE && (*base = m.AllocationBase) != 0;
}
/* A COM object whose 119-entry vtable lives in one non-game image: IDirect3DDevice9 layout. */
static int is_device(void *p) {
    void **vt, *base, *b2;
    if (!readable(p, 4) || !readable(vt = *(void ***)p, 119 * 4) || !in_image(vt, &base) || base == exe) return 0;
    for (int i = 0; i < 119; i++)
        if (!in_image(vt[i], &b2) || b2 != base) return 0;
    return 1;
}
/* the device the game itself presents with: [[0xd5a048]+0x98] (0x7c1816, 0x9de294, 0xa702d8) */
static void *find_device(void) {
    BYTE *ren = *(BYTE **)(exe + EXE_RENDERER);
    if (!readable(ren, 0x9c)) return 0;
    return is_device(*(void **)(ren + 0x98)) ? *(void **)(ren + 0x98) : 0;
}

/* Scope 3 (All rooms): native map renderers skip a room failing both bank5 (visited) and bank7 (revealed by a map
 * pickup) tests. Their bank7 calls to flag test 0x4916a0 are redirected here, so unvisited rooms are drawn in the
 * native dim "revealed" style while bank5 stays real. Read-only: no flag is written. */
#define EXE_FLAG_TEST 0x0916a0 /* 0x4916a0 thiscall (bank, idx), ret 8 */
typedef unsigned char (__fastcall *FlagTest)(void *mgr, void *edx, U32 bank, U32 idx);
static FlagTest flag_test;
static unsigned char __fastcall flag_all_scope(void *mgr, void *edx, U32 bank, U32 idx) {
    if (bank == 7 && idx < 154 && !all_off && visibility == 2) return 1;
    return flag_test(mgr, edx, bank, idx);
}
/* Each site: rva of `E8 rel32` and the 8 bytes before it (`6A 07 81 C1 F8 01 00 00`: push 7; add ecx, 0x1f8). */
static const U32 bank7_sites[2] = {
    0x155377, /* 0x5552a0 room outlines */
    0x1543b1, /* 0x5542b0 door lines of those rooms */
}; /* floor tabs (0x55255f) stay native: All scope never opens a place the player has not reached */
static void hook_all_scope(void) {
    static const BYTE ctx[8] = {0x6a, 0x07, 0x81, 0xc1, 0xf8, 0x01, 0x00, 0x00};
    static const BYTE head[16] = {0x8b, 0x44, 0x24, 0x04, 0x56, 0x8b, 0xf1, 0x83, 0xf8, 0x07, 0x0f, 0x87, 0x06, 0x01, 0x00, 0x00};
    BYTE *target = exe + EXE_FLAG_TEST;
    int ok = readable(target, 16);
    for (int i = 0; ok && i < 16; i++) ok = target[i] == head[i];
    for (int s = 0; ok && s < 2; s++) {
        BYTE *p = exe + bank7_sites[s];
        ok = readable(p - 8, 13) && p[0] == 0xe8 && p + 5 + *(int *)(p + 1) == target;
        for (int i = 0; ok && i < 8; i++) ok = p[i - 8] == ctx[i];
    }
    if (!ok) { log_line("all-scope sites mismatch; outlines unchanged\r\n"); return; }
    flag_test = (FlagTest)target;
    for (int s = 0; s < 2; s++) {
        BYTE *p = exe + bank7_sites[s]; DWORD old;
        if (!VirtualProtect(p + 1, 4, PAGE_EXECUTE_READWRITE, &old)) continue;
        *(int *)(p + 1) = (int)((BYTE *)flag_all_scope - (p + 5));
        VirtualProtect(p + 1, 4, old, &old);
        FlushInstructionCache(GetCurrentProcess(), p, 5);
    }
    log_line("all-scope outlines hooked\r\n");
}

static DWORD WINAPI install(void *unused) {
    void **vt = (void **)(exe + EXE_MAP_VTABLE);
    int map_hooked = 0;
    (void)unused;
    for (int logged = 0, tick = 0;; Sleep(50), tick++) {
        if (map_hooked) { poll_keys(); track_deaths(); track_room_entry(); enemy_service(); }
        if (tick % 10) continue;
        if (!map_hooked) {
            BYTE *r = exe + EXE_ROOMS;
            /* wait for the Steam stub to decrypt: room table + map vtable pointing into .text */
            if (!readable(r, 96) || u32(r) != 136 || u32(r + 4) != 353 || u32(r + 0x1c) != 2 || u32(r + 0x58) != 54 ||
                !readable(vt, 40) || u32(vt) < 0x401000 || u32(vt) >= 0xc19000) {
                if (tick > 600 && !logged++) log_line("bhd.exe layout mismatch; waiting\r\n");
                continue;
            }
            for (int i = 0; i < 10; i++) { map_orig[i] = vt[i]; patch_slot(&vt[i], (void *)map_thunks[i]); }
            map_hooked = 1;
            log_line("map vtable hooked\r\n");
            static const BYTE ctor_bytes[8] = {0x56, 0x68, 0xe8, 0x03, 0, 0, 0x6a, 0xff};
            BYTE *p = exe + EXE_ITEM_CTOR; DWORD old;
            int same = readable(p, 8);
            for (int i = 0; same && i < 8; i++) same = p[i] == ctor_bytes[i];
            if (same && VirtualProtect(p, 6, PAGE_EXECUTE_READWRITE, &old)) {
                p[0] = 0xe9; *(int *)(p + 1) = (int)((BYTE *)ctor_stub - (p + 5)); p[5] = 0x90;
                VirtualProtect(p, 6, old, &old);
                FlushInstructionCache(GetCurrentProcess(), p, 6);
                log_line("item ctor hooked\r\n");
            } else log_line("item ctor mismatch; live positions off\r\n");
            hook_all_scope();
            hook_spawn();
            hook_zoom();
        }
        void *dev = find_device();
        void **v = dev ? *(void ***)dev : 0;
        if (v && v[42] != (void *)end_scene) {
            /* new device vtable, or someone re-patched ours: remember its current EndScene, then hook */
            int i = 0;
            while (i < 3 && chain[i].vt && chain[i].vt != v) i++;
            chain[i].fn = v[42];
            chain[i].vt = v;
            if (patch_slot(&v[42], (void *)end_scene)) log_line("EndScene hooked\r\n");
        }
    }
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE dll, DWORD reason, void *reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        char path[MAX_PATH];
        DWORD n = GetModuleFileNameA(dll, path, MAX_PATH - 8);
        lstrcpyA(path + n - 3, "ini");
        lstrcpyA(ini_path, path);
        int migrate = load_settings();
        load_death_rooms();
        InitializeCriticalSection(&enemy_cs);
        lstrcpyA(enemy_path, path);
        lstrcpyA(enemy_path + n - 3, "enemies.dat");
        enemy_load_file();
        lstrcpyA(path + n - 3, "log");
        log_file = CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ, 0, CREATE_ALWAYS, 0, 0);
        load_colors();
        if (migrate) { save_settings(); log_line("settings: INI rewritten once with Version 4\r\n"); }
        exe = (BYTE *)GetModuleHandleA(0);
        if (exe != (BYTE *)0x400000) {
            log_line("RE1HD.AnnotatedMap 1.0.0: unsupported bhd.exe; no patch applied\r\n");
            return TRUE;
        }
        log_line("RE1HD.AnnotatedMap 1.0.0 loaded\r\n");
        CloseHandle(CreateThread(0, 0, install, 0, 0, 0));
    }
    return TRUE;
}
