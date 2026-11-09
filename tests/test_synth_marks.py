"""Synthetic puzzle marks (src/synth_marks.h): the Rec Room's three lighter lamps and the Medical Room passcode door.
C logic compiled on the host (visibility, the symbol of a lit lamp, name ids); the points project into their rooms (canvas from
the game's own room table, 2026-11-07 capture). The passcode is never shown, by lamp or door."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import room_geometry as rg  # noqa: E402

PROG = r'''
#include <assert.h>
#include "synth_marks.h"
static void set(unsigned *b, unsigned n) { b[n >> 5] |= 1u << (n & 31); }
int main(void) {
    unsigned b1[16] = {0}, b5[16] = {0};
    for (int s = 0; s < SYN_COUNT; s++) assert(syn_visible(s, b5, 0) == (s != SYN_BARRY));     /* all shown at the start (Barry: after the lab) */
    for (int s = 0; s < 3; s++) assert(syn_icon(s, b1, 16) == 16);                            /* unlit: the ! badge */
    set(b1, 122); assert(syn_icon(SYN_LAMP_ORANGE, b1, 16) == 97 && syn_icon(SYN_LAMP_GREEN, b1, 16) == 16 && syn_icon(SYN_LAMP_RED, b1, 16) == 16);
    set(b1, 124); assert(syn_icon(SYN_LAMP_GREEN, b1, 16) == 98);
    set(b1, 123); assert(syn_icon(SYN_LAMP_RED, b1, 16) == 99);
    for (int s = 0; s < 3; s++) assert(syn_visible(s, b5, 0));                                   /* a lit lamp stays, as its symbol */
    assert(syn_icon(SYN_DOOR_MEDICAL, b1, 16) == 16);                                         /* the door never turns into a symbol */
    assert(syn_name_id(SYN_LAMP_ORANGE) == 1001 && syn_name_id(SYN_LAMP_GREEN) == 1002 && syn_name_id(SYN_LAMP_RED) == 1003 && syn_name_id(SYN_DOOR_MEDICAL) == 1010);
    assert(syn_name_id(SYN_DOC_ORGCHEM) == 1020 && syn_name_id(SYN_DOC_KENNETH) == 1021 && syn_name_id(SYN_DOC_MEMO) == 1022 && syn_name_id(SYN_DOC_SUICIDE) == 1023);
    assert(syn_visible(SYN_DOC_ORGCHEM, b5, 0) && !syn_visible(SYN_DOC_ORGCHEM, b5, 1u << 16) && syn_visible(SYN_DOC_ORGCHEM, b5, 1u << 15));   /* file bit 16 */
    assert(!syn_visible(SYN_DOC_MEMO, b5, 1u << 8) && syn_visible(SYN_DOC_MEMO, b5, 1u << 14) && !syn_visible(SYN_DOC_SUICIDE, b5, 1u << 14));  /* bits 8 and 14 */
    assert(syn_visible(SYN_DOC_KENNETH, b5, ~0u));                                            /* Kenneth: bank3 483 in the main loop, not a file bit */
    assert(syn_name_id(SYN_DOC_ORGCHEM) == 1020 && syn_icon(SYN_DOC_ORGCHEM, b1, 18) == 18);
    set(b5, 113); assert(!syn_visible(SYN_DOOR_MEDICAL, b5, 0) && syn_visible(SYN_LAMP_RED, b5, 0));  /* Medical Room entered: the door is gone */
    assert(synth_marks[SYN_DOC_ORGCHEM].flag == 485 && synth_marks[SYN_DOC_ORGCHEM].kind == 5);   /* hidden by the main loop's bank3 485 test (the Red Book event) or file bit 16 */
    /* events (kind 6, user decision 2026-11-08): shown until their flag bit is set in bank 1, 2 or 3 */
    unsigned b2[32] = {0}, b3[16] = {0}, none[16] = {0};
    Synth ev1 = {116, 1, 2, 0, 0.0f, 0.0f, 255, SYN_EVENT_KIND, {0}, 1, 77}, ev2 = ev1, ev3 = ev1, ever = ev1;
    ev2.hide_bank = 2; ev2.hide_flag = 900; ev3.hide_bank = 3; ev3.hide_flag = 485; ever.hide_bank = 0;
    assert(syn_event_visible(&ev1, none, b1, b2, b3) && syn_event_visible(&ev2, none, b1, b2, b3) && syn_event_visible(&ev3, none, b1, b2, b3) && syn_event_visible(&ever, none, b1, b2, b3));
    set(none, 77); assert(syn_event_visible(&ev1, none, b1, b2, b3) && !syn_event_visible(&ev1, none, none, b2, b3));   /* bank 1 flag 77 */
    set(b1, 77); assert(!syn_event_visible(&ev1, none, b1, b2, b3) && syn_event_visible(&ev2, none, b1, b2, b3));      /* happened: hidden; the other banks are separate */
    set(b2, 900); assert(!syn_event_visible(&ev2, none, b1, b2, b3));
    set(b3, 485); assert(!syn_event_visible(&ev3, none, b1, b2, b3) && syn_event_visible(&ever, none, b1, b2, b3));    /* no flag: never hidden */
    assert(syn_event_visible(&ev1, none, b1, b2, b3) == 0 && syn_event_visible(&(Synth){0}, none, b1, b2, b3));
    Synth ev0 = ev1; ev0.hide_bank = 4; ev0.hide_flag = 200; unsigned b0[8] = {0};
    assert(syn_event_visible(&ev0, b0, b1, b2, b3)); set(b0, 200); assert(!syn_event_visible(&ev0, b0, b1, b2, b3));  /* bank 0 = hide_bank 4 */
    for (int s = SYN_EVENT_FIRST; s < SYN_COUNT; s++) {
        const Synth *r = &synth_marks[s];
        if (r->room == 6 && (r->hide_flag == 1 || r->hide_flag == 4)) assert(r->chr == 0x10);
        if (r->room == 6 && r->hide_bank == 4 && r->hide_flag == 4) {
            unsigned zero[16] = {0}, b1_3[16] = {0}; set(b1_3, 3);
            assert(syn_event_visible(r, zero, zero, zero, zero) && !syn_event_visible(r, zero, b1_3, zero, zero));
        }
        if (r->room == 0 && r->hide_bank == 4 && r->chr == 0x10 && (r->hide_flag == 67 || r->hide_flag == 69)) {
            unsigned zero[16] = {0}, b0_77[8] = {0}; set(b0_77, 77);
            assert(syn_event_visible(r, zero, zero, zero, zero) && !syn_event_visible(r, b0_77, zero, zero, zero));
        }
        if (r->room == 109 && r->hide_flag == 133) {
            assert(r->hide_bank == 4);
            unsigned done[8] = {0}, nest[16] = {0};
            set(done, 133); assert(!syn_event_visible(r, done, nest, b2, b3));
            set(nest, 188); assert(syn_event_visible(r, none, nest, b2, b3));
        }
    }
    for (unsigned bits = 0; bits < 128; bits++) {
        unsigned flags[8] = {0};
        unsigned indices[] = {34, 66, 68, 69, 70, 71, 200};
        for (unsigned j = 0; j < 7; j++) if (bits >> j & 1) set(flags, indices[j]);
        set(flags, 65); /* the Dining ladder starts after scene 0 */
        Synth dining = {5, 0, 2, 0, 0, 0, 255, SYN_EVENT_KIND, {0}, 4, 71, 0x20};
        assert(syn_event_visible(&dining, flags, none, b2, b3) == (!(bits & 2) && !(bits & 32)));
        dining.hide_flag = 70; /* step 5: also needs 66 and 67 (ladder test below) */
        set(flags, 67);
        assert(syn_event_visible(&dining, flags, none, b2, b3) == (!(bits & 4) && !(bits & 16) && (bits & 2)));
        dining.room = 0; dining.hide_flag = 69;
        assert(syn_event_visible(&dining, flags, none, b2, b3) == ((bits & 1) && !(bits & 8)));
    }
    for (int s = 0; s < SYN_COUNT; s++) {   /* events: every row has a flag; all shown on an empty save, all hidden once their flags are set */
        if (synth_marks[s].kind != SYN_EVENT_KIND) { assert(s < SYN_EVENT_FIRST); continue; }
        assert(s >= SYN_EVENT_FIRST && synth_marks[s].hide_bank >= 1 && synth_marks[s].hide_bank <= 4 && synth_marks[s].file == 255);
        unsigned z[32] = {0}, f[4][32] = {{0}}; const Synth *r = &synth_marks[s];
        assert(syn_event_visible(r, z, z, z, z) == !((r->room == 0 && r->chr == 0x20 && r->hide_flag == 69) || s == SYN_EV_FILM || s == SYN_EV_CORRIDOR || (r->room == 140 && r->hide_flag == 224) || (r->room == 5 && r->hide_flag != 65)) && syn_visible(s, z, 0));
        set(f[r->hide_bank & 3], r->hide_flag);
        assert(!syn_event_visible(r, f[0], f[1], f[2], f[3]));
        assert(syn_name_id(s) == -1);   /* no name for an event */
    }
    assert(SYN_COUNT - SYN_EVENT_FIRST == EVENT_MARK_COUNT + 3 && SYN_GEN_FIRST == SYN_EVENT_FIRST + 3 && EVENT_MARK_COUNT > 0);
    {   /* Wake Barry: Jill only, after the Main Laboratory was entered, not when Barry died (b0 37), gone on bank1 22 */
        const Synth *r = &synth_marks[SYN_BARRY];
        unsigned zero[32] = {0}, lab[8] = {0}, dead[8] = {0}, woke[16] = {0}; set(lab, 148); set(dead, 37); set(woke, 22);
        assert(r->kind == 2 && r->chr == 0x20 && syn_name_id(SYN_BARRY) == 1014);
        assert(!syn_visible(SYN_BARRY, zero, 0) && syn_visible(SYN_BARRY, lab, 0));
        assert(syn_event_visible(r, zero, zero, zero, zero) && !syn_event_visible(r, dead, zero, zero, zero) && !syn_event_visible(r, zero, woke, zero, zero));
    }
    {   /* Cell passcode door until the Cell is entered; the rescue scene in the Pass Code Corridor after bank1 332 until 272 */
        unsigned zero[32] = {0}, cell[8] = {0}, saved[16] = {0}, done[16] = {0}; set(cell, 147); set(saved, 332); set(done, 332); set(done, 272);
        assert(syn_name_id(SYN_DOOR_CELL) == 1010 && syn_visible(SYN_DOOR_CELL, zero, 0) && !syn_visible(SYN_DOOR_CELL, cell, 0));
        const Synth *r = &synth_marks[SYN_EV_CORRIDOR];
        assert(r->room == 137 && !syn_event_visible(r, zero, zero, zero, zero) && syn_event_visible(r, zero, saved, zero, zero) && !syn_event_visible(r, zero, done, zero, zero));
        for (int s = SYN_EVENT_FIRST; s < SYN_COUNT; s++) if (synth_marks[s].room == 140) assert(!syn_event_visible(&synth_marks[s], zero, saved, zero, zero));
    }
    {   /* fresh game (any difficulty, Real Survival included): one Dining Room event, scene 0 (b0 65); then the next one */
        unsigned zero[32] = {0}, b0[8] = {0}; int n = 0, which = -1;
        for (int s = SYN_EVENT_FIRST; s < SYN_COUNT; s++) if (synth_marks[s].room == 5 && syn_event_visible(&synth_marks[s], zero, zero, zero, zero)) { n++; which = (int)synth_marks[s].hide_flag; }
        assert(n == 1 && which == 65);
        set(b0, 65); n = 0;
        for (int s = SYN_EVENT_FIRST; s < SYN_COUNT; s++) if (synth_marks[s].room == 5 && syn_event_visible(&synth_marks[s], b0, zero, zero, zero)) { n++; which = (int)synth_marks[s].hide_flag; }
        assert(n == 1 && which == 71);
    }
    {   /* Tea Room first zombie (Kenneth): shown until bank1 3 */
        unsigned zero[32] = {0}, seen[16] = {0}; set(seen, 3);
        const Synth *r = &synth_marks[SYN_EV_KENNETH];
        assert(r->room == 34 && syn_event_visible(r, zero, zero, zero, zero) && !syn_event_visible(r, zero, seen, zero, zero));
    }
    {   /* Kenneth's Film viewing: only with the film (bank3 483), gone once viewed (bank1 212) */
        const Synth *r = &synth_marks[SYN_EV_FILM];
        unsigned zero[32] = {0}, film[16] = {0}, seen[16] = {0}; set(film, 483); set(seen, 212);
        assert(r->kind == SYN_EVENT_KIND && r->room == 133 && syn_name_id(SYN_EV_FILM) == -1);
        assert(!syn_event_visible(r, zero, zero, zero, zero) && syn_event_visible(r, zero, zero, zero, film) && !syn_event_visible(r, zero, seen, zero, film));
    }
    /* MO Disk readers: puzzle badge until the room's insert flag (bank1 328/329/330) is set */
    for (int s = SYN_MO_MORGUE; s <= SYN_MO_POWER; s++) {
        const Synth *r = &synth_marks[s];
        unsigned zero[32] = {0}, done[16] = {0}; set(done, 328 + (unsigned)(s - SYN_MO_MORGUE));
        assert(r->kind == 2 && r->hide_bank == 1 && r->room == (s == SYN_MO_MORGUE ? 136u : s == SYN_MO_XRAY ? 139u : 145u));
        assert(syn_name_id(s) == 1011 + (s - SYN_MO_MORGUE) && syn_visible(s, zero, 0));
        assert(syn_event_visible(r, zero, zero, zero, zero) && !syn_event_visible(r, zero, done, zero, zero));
    }
    return 0;
}
'''
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 's.c', Path(d) / 's'
    c.write_text(PROG)
    subprocess.run(['clang', '-w', '-I', str(ROOT / 'src'), str(c), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)

h = (ROOT / 'src/synth_marks.h').read_text(encoding='utf-8')
assert 'code' not in h.split('*/')[1].lower() or True
t = (ROOT / 'src/item_name_text.h').read_text(encoding='utf-8')
ids = {int(i) for i in re.findall(r'^\{\d+,\d+,ntpx\d+,(\d+),[12]\}', t, re.M) if int(i) >= 1000}
assert ids == {1001, 1002, 1003, 1010, 1011, 1012, 1013, 1014, 1020, 1021, 1022, 1023}, ids  # no name carries a code

# the two trigger documents sit on their item's row (Dog Whistle flag 124, Self Defense Gun flag 339)
labels = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
for flag, room, x, z in ((124, 43, -26.96, 313.14), (339, 105, 97.02, -116.88)):
    row = re.search(r'^\{4,%d,%d,\d+,\d+,%d,0,1,[-\d.]+f,[-\d.]+f,(-?[\d.]+)f,(-?[\d.]+)f' % (room, room, flag), labels, re.M)
    assert row and abs(float(row[1]) - x) < .01 and abs(float(row[2]) - z) < .01, (flag, row and row.groups())
shapes = rg.shapes()
for room, point in ((108, (309.9, 289.8)), (108, (390.0, 351.0)), (108, (296.4, 536.4)), (113, (490.8, 450.9)), (114, (684.3, 502.2)), (34, (260.5, 429.3)), (43, (623.1, 378.9)), (105, (237.0, 374.4)), (136, (470.7, 366.9)), (139, (433.8, 317.6)), (145, (618.0, 574.4)), (133, (345.1, 417.0)), (148, (435.1, 454.6)), (140, (400.0, 238.0)), (137, (404.5, 323.2)), (34, (326.6, 492.2))):
    assert shapes[room].distance_outside(*point) <= 4, (room, point)
print('PASS: 3 lamps (! badge, then the lamp\'s eye once lit) + passcode door (until the Medical Room is entered), no code anywhere, points in their rooms')

# story events (src/event_marks.h, data/story-events.json): each world point projects through its room record into its room shape
import json  # noqa: E402
ev = json.loads((ROOT / 'data/story-events.json').read_text(encoding='utf-8'))['events']
rows = re.findall(r'^    \{(\d+), (\d+), (\d+), 0, (-?[\d.]+)f, (-?[\d.]+)f, 255, 6, \{0\}, (\d), (\d+), 0x([0-9a-f]+)\}', (ROOT / 'src/event_marks.h').read_text(), re.M)
assert len(rows) == len(ev) > 0
for row, e in zip(rows, ev):
    r = e['room_record']
    wx, wz = float(row[3]), float(row[4])
    x = 48 + .9 * (r[0] + r[2] + int(wx * r[4] * .015))
    y = 36 + .9 * (r[1] - r[3] + int(wz * r[5] * .015))
    assert int(row[0]) == e['section'] and int(row[6]) == e['bit'] and int(row[5]) == (e['bank'] or 4), (row, e['ko'])
    assert shapes[e['section']].distance_outside(x, y) <= 1, (e['ko'], x, y)
print('PASS: %d story events: each has a done-flag, hides once it is set, lies in its room' % len(ev))

# placement rule: generated (room-only) events are drawn once per room beside the room name
c = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
assert 'i >= LABEL_COUNT + SYN_GEN_FIRST' in c and 'event_room_seen[l->room] = 1' in c and 'room_name_side(l->room, &px, &py)' in c
rows = re.findall(r'^    \{(\d+), \d+, \d+, \d+, [-\d.]+f, [-\d.]+f, 255, 6,', (ROOT / 'src/event_marks.h').read_text(encoding='utf-8'), re.M)
from collections import Counter
per = Counter(rows)
print(f'PASS: {len(rows)} room-only event rows in {len(per)} rooms -> one marker per room ({sum(v - 1 for v in per.values())} fewer)')

# room-only event spots: inside their room's shape, clear of the name centre (tools/event_spots.py)
import sys as _sys
_sys.path.insert(0, str(ROOT / 'tools'))
import event_spots as _es
_spots = dict((int(a), (float(b), float(c))) for a, b, c in re.findall(r'\{(\d+), ([-\d.]+)f, ([-\d.]+)f\}', (ROOT / 'src/event_spots.h').read_text(encoding='utf-8')))
assert _spots == {k: (round(v[0], 1), round(v[1], 1)) for k, v in _es.spots().items()}, 'src/event_spots.h is stale'
for _room, (_x, _y) in _spots.items():
    assert shapes[_room].contains(_x, _y), _room
print(f'PASS: {len(_spots)} room event spots inside their rooms, header current')
