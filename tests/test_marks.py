"""src/marks.h, the RE0 HD mark rules, compiled on the host: name slots by tier and weight, the second ring, the drop and badge
rules, the event beside a key, locks never moved. Data: every lock row's two points sit 22 px either side of its door, so their
midpoint (DoorKey=Center, the default) is the door."""
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
h = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
locks = 0
for r in re.findall(r'^\{1,([^\n]*?)\}, /\* ', h, re.M):
    x, y, x2, y2 = (float(v.rstrip('f')) for v in r.split(',')[7:11])
    assert (x == x2 and abs(abs(y2 - y) - 22) < .01) or (y == y2 and abs(abs(x2 - x) - 22) < .01) or (x, y) == (x2, y2), r[:40]
    locks += 1
assert locks == 72

PROG = r'''
#include <assert.h>
typedef unsigned U32;
#include "marks.h"
static Occupied occ[64]; static U32 no;
static Mark mk(int cat, float cx, float cy, float side, float nw, float nh) {
    return (Mark){0, cat, 0, {cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2}, {0, 0, 0, 0}, nw, nh, MARK_KEEP, 0}; }
int main(void) {
    const float S = 36, W = 1000, H = 800;
    /* a free key: right slot, touching the mark */
    Mark m[4] = {mk(CAT_KEY, 500, 400, S, 60, 20)};
    no = 0; no = marks_layout(m, 1, occ, no, 64, S, 1, W, H);
    assert(m[0].state == MARK_NAMED && m[0].name.l == 518 && m[0].name.t == 390 && no == 2 && occ[1].weight == 8);
    /* names off: no names, marks still weigh */
    m[0] = mk(CAT_KEY, 500, 400, S, 60, 20); no = 0; no = marks_layout(m, 1, occ, no, 64, S, 0, W, H);
    assert(m[0].state == MARK_KEEP && no == 1);
    /* right slot taken by a panel (8x): left slot; right and left taken: below */
    m[0] = mk(CAT_FILE, 500, 400, S, 60, 20); no = 0; occ[no++] = (Occupied){{518, 380, 600, 420}, 8};
    marks_layout(m, 1, occ, no, 64, S, 1, W, H); assert(m[0].name.r == 482);
    m[0] = mk(CAT_FILE, 500, 400, S, 60, 20); no = 0; occ[no++] = (Occupied){{400, 385, 600, 415}, 8};
    marks_layout(m, 1, occ, no, 64, S, 1, W, H); assert(m[0].name.t == 418 && m[0].name.l == 470);
    /* everything near taken by a room name (4x): the second ring, one name height out */
    m[0] = mk(CAT_LOCK, 500, 400, S, 60, 20); no = 0; occ[no++] = (Occupied){{470, 370, 530, 430}, 4};
    marks_layout(m, 1, occ, no, 64, S, 1, W, H); assert(m[0].ringed && !boxes_hit(m[0].name, occ[0].box));
    /* tiers: the key names first, so a document beside it takes another slot */
    m[0] = mk(CAT_FILE, 500, 400, S, 60, 20); m[1] = mk(CAT_KEY, 500, 460, S, 60, 20); no = 0;
    marks_layout(m, 2, occ, no, 64, S, 1, W, H); assert(m[1].name.l == 518 && !boxes_hit(m[0].name, m[1].name));
    /* drop rule: an item on a key core is not drawn; a centred document becomes a badge; an off-centre one is dropped; a lock stays */
    m[0] = mk(CAT_KEY, 500, 400, S, 0, 0); m[1] = mk(CAT_ITEM, 503, 402, S, 0, 0); m[2] = mk(CAT_FILE, 501, 401, S, 60, 20); m[3] = mk(CAT_LOCK, 500, 400, S, 60, 20);
    no = 0; marks_layout(m, 4, occ, no, 64, S, 0, W, H);
    assert(m[1].state == MARK_DROP && m[2].state == MARK_KEEP && m[2].mark.l == 483 + S * .6f && m[3].state == MARK_KEEP && m[3].mark.l == 482);
    m[2] = mk(CAT_FILE, 512, 400, S, 0, 0); no = 0; marks_layout(m, 3, occ, no, 64, S, 0, W, H); assert(m[2].state == MARK_DROP);
    /* the core is small: an item touching only the key's edge stays (the key is painted over it) */
    m[1] = mk(CAT_ITEM, 530, 400, S, 0, 0); no = 0; marks_layout(m, 2, occ, no, 64, S, 0, W, H); assert(m[1].state == MARK_KEEP);
    /* a key name avoids an item mark (weight 1) when a free slot exists, so both stay */
    m[0] = mk(CAT_KEY, 500, 400, S, 60, 20); m[1] = mk(CAT_ITEM, 545, 400, S, 0, 0); no = 0;
    marks_layout(m, 2, occ, no, 64, S, 1, W, H); assert(m[0].name.r == 482 && m[1].state == MARK_KEEP);
    /* name alignment follows the slot: right of the icon -> left-aligned, left -> right-aligned, below and above -> centred, corners toward the icon */
    m[0] = mk(CAT_KEY, 500, 400, S, 60, 20); no = 0; marks_layout(m, 1, occ, no, 64, S, 1, W, H); assert(m[0].slot == 0 && name_align(m[0].slot) == -1);
    m[0] = mk(CAT_FILE, 500, 400, S, 60, 20); no = 0; occ[no++] = (Occupied){{518, 380, 600, 420}, 8}; marks_layout(m, 1, occ, no, 64, S, 1, W, H); assert(m[0].slot == 1 && name_align(m[0].slot) == 1);
    m[0] = mk(CAT_FILE, 500, 400, S, 60, 20); no = 0; occ[no++] = (Occupied){{400, 385, 600, 415}, 8}; marks_layout(m, 1, occ, no, 64, S, 1, W, H); assert(m[0].slot == 2 && name_align(m[0].slot) == 0);
    int want[8] = {-1, 1, 0, 0, -1, 1, -1, 1};
    for (int s = 0; s < 8; s++) assert(name_align(s) == want[s]);
    /* an event (CAT_EVENT) is a top-tier mark with no name, is never dropped, covers nothing, and stands beside a key it overlaps */
    m[0] = mk(CAT_KEY, 500, 400, S, 60, 20); m[1] = mk(CAT_EVENT, 500, 400, S, 0, 0); m[1].event = 1; m[2] = mk(CAT_ITEM, 500, 400, S, 0, 0); no = 0;
    marks_layout(m, 3, occ, no, 64, S, 1, W, H);
    assert(m[1].state == MARK_KEEP && m[1].mark.l == m[0].mark.r && m[0].state == MARK_NAMED && m[2].state == MARK_DROP);
    m[0] = mk(CAT_EVENT, 300, 300, S, 0, 0); m[0].event = 1; m[1] = mk(CAT_PUZZLE, 300, 300, S, 40, 16); no = 0; marks_layout(m, 2, occ, no, 64, S, 1, W, H);
    assert(m[0].state == MARK_KEEP && m[1].state == MARK_NAMED);                                     /* covered by a puzzle: the event stays, it displaces nothing */
    m[0] = mk(CAT_EVENT, 300, 300, S, 60, 20); m[0].event = 1; no = 0; marks_layout(m, 1, occ, no, 64, S, 1, W, H);
    assert(m[0].state == MARK_KEEP); marks_layout(m, 1, occ, 0, 64, S, 2, W, H); assert(m[0].state == MARK_KEEP);  /* never named, whatever the H state */
    assert(top_tier(CAT_EVENT) && top_tier(CAT_KEY) && top_tier(CAT_PUZZLE) && !top_tier(CAT_ITEM));
    /* an event on a key item stands beside it (right if it fits, else left) and has no name */
    /* ordinary items are named last, beside their icon, avoiding the placed names; one covered by a key mark gets none */
    m[0] = mk(CAT_KEY, 500, 400, S, 60, 20); m[1] = mk(CAT_ITEM, 560, 400, S, 50, 18); no = 0; no = marks_layout(m, 2, occ, no, 64, S, 1, W, H);
    assert(m[0].state == MARK_NAMED && m[1].state == MARK_NAMED && !boxes_hit(m[1].name, m[0].name) && !boxes_hit(m[1].name, m[1].mark));
    assert(m[1].name.l == m[1].mark.r || m[1].name.r == m[1].mark.l || m[1].name.t == m[1].mark.b || m[1].name.b == m[1].mark.t);
    m[0] = mk(CAT_ITEM, 300, 300, S, 50, 18); no = 0; marks_layout(m, 1, occ, no, 64, S, 0, W, H); assert(m[0].state == MARK_KEEP);   /* names off */
    m[0] = mk(CAT_ITEM, 300, 300, S, 0, 0); no = 0; marks_layout(m, 1, occ, no, 64, S, 1, W, H); assert(m[0].state == MARK_KEEP);    /* no name image */
    m[0] = mk(CAT_KEY, 500, 400, S, 0, 0); m[1] = mk(CAT_ITEM, 503, 402, S, 50, 18); no = 0; marks_layout(m, 2, occ, no, 64, S, 1, W, H);
    assert(m[1].state == MARK_DROP);                                                                                               /* covered: dropped, never named */
    /* names = 2 (all except ordinary items): the key is named, the ordinary item is not */
    m[0] = mk(CAT_KEY, 500, 400, S, 60, 20); m[1] = mk(CAT_ITEM, 560, 400, S, 50, 18); no = 0; no = marks_layout(m, 2, occ, no, 64, S, 2, W, H);
    assert(m[0].state == MARK_NAMED && m[1].state == MARK_KEEP);
    m[0] = mk(CAT_FILE, 500, 400, S, 60, 20); no = 0; marks_layout(m, 1, occ, no, 64, S, 2, W, H); assert(m[0].state == MARK_NAMED);
    m[0] = mk(CAT_KEY, 500, 400, S, 60, 20); m[1] = mk(CAT_PUZZLE, 505, 400, S, 60, 20); m[1].event = 1; no = 0;
    marks_layout(m, 2, occ, no, 64, S, 1, W, H); assert(m[1].mark.l == 518 && m[1].state == MARK_KEEP);
    m[0] = mk(CAT_KEY, 980, 400, S, 0, 0); m[1] = mk(CAT_PUZZLE, 980, 400, S, 0, 0); m[1].event = 1; no = 0;
    marks_layout(m, 2, occ, no, 64, S, 0, W, H); assert(m[1].mark.r == 962);
    /* enemies and other icons drawn outside the list: on a key or puzzle core only */
    m[0] = mk(CAT_PUZZLE, 500, 400, S, 0, 0); m[0].state = MARK_KEEP;
    assert(core_covered(m, 1, 505, 400, S) && !core_covered(m, 1, 530, 400, S));
    /* names stay on screen */
    m[0] = mk(CAT_KEY, 990, 790, S, 60, 20); no = 0; marks_layout(m, 1, occ, no, 64, S, 1, W, H);
    assert(m[0].name.r <= W - 1 && m[0].name.b <= H - 1);
    return 0;
}
'''
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 'marks.c', Path(d) / 'marks'
    c.write_text(PROG)
    subprocess.run(['clang', '-w', '-I', str(ROOT / 'src'), str(c), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
print(f'PASS: mark tiers, weights, rings, drop/badge/event rules; {locks} lock rows straddle their doors')
