/* Mark and item-name placement: the RE0 HD map mod's rules (its wiki page 03), the default for every map mod since the
 * user's decision of 2026-11-07. Pure arithmetic on screen boxes, so tests compile it on the host.
 *
 * - Weights while names choose a slot: key and puzzle marks and the panels 8, room names 4, everything else 1;
 *   a placed key or puzzle name 8, other placed names 2.
 * - Names by tier: key items, puzzles, locks, documents, ordinary items (names = 1; names = 2 leaves out the ordinary items). Slots touch the mark: right, left, below, above, then the four
 *   corners; the first slot with no overlap wins, else the least; still overlapping, a second ring one name height out.
 * - A lower-priority icon whose core (its middle 7/18 of the side) touches a key or puzzle core, or a key name that was not
 *   pushed out, is not drawn; a document centred on one moves down and right as a badge. Locks stay on their doors.
 * - An event (a story scene, a rescue marker) that overlaps a key-item mark stands beside it. Events have no name, displace nothing and are
 *   never dropped.
 * - A name's lines are aligned toward its icon (RE0 rule, user decision 2026-11-08): left-aligned in the slots that start at the icon's
 *   right or left edge, right-aligned in the ones that end there, centred above and below. */
typedef struct { float l, t, r, b; } Box;
typedef struct { Box box; U32 weight; } Occupied;
enum { CAT_LOCK, CAT_KEY, CAT_FILE, CAT_PUZZLE, CAT_ITEM, CAT_ENEMY, CAT_EVENT };
enum { MARK_DROP, MARK_KEEP, MARK_NAMED };
typedef struct { U32 label; int cat, event; Box mark, name; float nw, nh; int state, ringed, slot; } Mark; /* slot: the name_candidates index chosen */
/* Line alignment of a name in slot `slot`: -1 left, 0 centred, 1 right (toward the icon). */
static int name_align(int slot) { return slot == 0 || slot == 4 || slot == 6 ? -1 : slot == 1 || slot == 5 || slot == 7 ? 1 : 0; }

static int boxes_hit(Box a, Box b) { return a.l < b.r && b.l < a.r && a.t < b.b && b.t < a.b; }
static int top_tier(int cat) { return cat == CAT_KEY || cat == CAT_PUZZLE || cat == CAT_EVENT; }
static float overlap_score(Box b, const Occupied *o, U32 n, U32 min_weight) {
    float s = 0;
    for (U32 i = 0; i < n; i++) if (o[i].weight >= min_weight) {
        float w = (b.r < o[i].box.r ? b.r : o[i].box.r) - (b.l > o[i].box.l ? b.l : o[i].box.l);
        float h = (b.b < o[i].box.b ? b.b : o[i].box.b) - (b.t > o[i].box.t ? b.t : o[i].box.t);
        if (w > 0 && h > 0) s += w * h * (float)o[i].weight;
    }
    return s;
}
static void name_candidates(Box m, float w, float h, Box out[8]) {
    float cx = (m.l + m.r) * .5f, cy = (m.t + m.b) * .5f;
    const float x[8] = {m.r, m.l - w, cx - w * .5f, cx - w * .5f, m.l, m.r - w, m.l, m.r - w};
    const float y[8] = {cy - h * .5f, cy - h * .5f, m.b, m.t - h, m.b, m.b, m.t - h, m.t - h};
    for (int i = 0; i < 8; i++) out[i] = (Box){x[i], y[i], x[i] + w, y[i] + h};
}
static float mark_core(float side) { return side * 7.0f / 36.0f; } /* half the core's side */
/* A mark's core touches a key or puzzle mark's core (enemies and other icons drawn outside the list use this). */
static int core_covered(const Mark *m, U32 count, float cx, float cy, float side) {
    float c = mark_core(side);
    Box mi = {cx - c, cy - c, cx + c, cy + c};
    for (U32 j = 0; j < count; j++) if (top_tier(m[j].cat) && !m[j].event && m[j].state != MARK_DROP) {
        float jx = (m[j].mark.l + m[j].mark.r) * .5f, jy = (m[j].mark.t + m[j].mark.b) * .5f;
        if (boxes_hit(mi, (Box){jx - c, jy - c, jx + c, jy + c})) return 1;
    }
    return 0;
}
/* occ holds the panels, room names and other drawn icons; the marks are added here. Returns the new occupied count. */
static U32 marks_layout(Mark *m, U32 count, Occupied *occ, U32 no, U32 cap, float side, int names, float W, float H) {
    U32 first = no;
    for (U32 i = 0; i < count && no < cap; i++) { m[i].state = MARK_KEEP; m[i].ringed = 0; m[i].slot = 0; occ[no++] = (Occupied){m[i].mark, top_tier(m[i].cat) ? 8u : 1u}; }
    for (U32 i = 0; i < count; i++) if (m[i].event)
        for (U32 j = 0; j < count; j++) if (m[j].cat == CAT_KEY && boxes_hit(m[i].mark, m[j].mark)) {
            float ew = m[i].mark.r - m[i].mark.l, left = m[j].mark.r + ew <= W ? m[j].mark.r : m[j].mark.l - ew;
            m[i].mark = (Box){left, m[j].mark.t, left + ew, m[j].mark.b};
            if (first + i < cap) occ[first + i].box = m[i].mark;
            break;
        }
    static const int tiers[5] = {CAT_KEY, CAT_PUZZLE, CAT_LOCK, CAT_FILE, CAT_ITEM};
    if (names) for (int t = 0; t < 5; t++) for (U32 i = 0; i < count; i++) if (m[i].cat == tiers[t] && !m[i].event) {
        if (t == 4) { /* ordinary items: named only with a name image, not in state 2 (names = 2: all but ordinary items), and not when a key or puzzle mark covers them */
            if (names == 2) continue;
            float cx = (m[i].mark.l + m[i].mark.r) * .5f, cy = (m[i].mark.t + m[i].mark.b) * .5f;
            if (m[i].nw <= 0 || core_covered(m, count, cx, cy, m[i].mark.r - m[i].mark.l)) continue;
        }
        float w = m[i].nw, h = m[i].nh, least = -1;
        Box c[8], best = {0, 0, 0, 0};
        int pick = 0;
        name_candidates(m[i].mark, w, h, c);
        for (int j = 0; j < 8; j++) {
            Box b = c[j]; /* pulled back on screen */
            if (b.l < 1) { b.r += 1 - b.l; b.l = 1; }
            if (b.r > W - 1) { b.l -= b.r - (W - 1); b.r = W - 1; }
            if (b.t < 1) { b.b += 1 - b.t; b.t = 1; }
            if (b.b > H - 1) { b.t -= b.b - (H - 1); b.b = H - 1; }
            float a = overlap_score(b, occ, no, 1);
            if (least < 0 || a < least) { least = a; best = b; pick = j; }
            if (a == 0) break;
        }
        if (least > 0) {
            Box wide = {m[i].mark.l - h, m[i].mark.t - h, m[i].mark.r + h, m[i].mark.b + h};
            name_candidates(wide, w, h, c);
            for (int j = 0; j < 8 && least > 0; j++) {
                Box b = c[j];
                if (b.l < 1 || b.t < 1 || b.r > W - 1 || b.b > H - 1) continue;
                float a = overlap_score(b, occ, no, 1);
                if (a < least) { least = a; best = b; pick = j; m[i].ringed = 1; }
            }
        }
        m[i].name = best; m[i].state = MARK_NAMED; m[i].slot = pick;
        if (no < cap) occ[no++] = (Occupied){best, t < 2 ? 8u : 2u};
    }
    float c = mark_core(side);
    for (U32 i = 0; i < count; i++) if (!top_tier(m[i].cat) && m[i].cat != CAT_LOCK) {
        int covered = 0, centred = 0;
        float cx = (m[i].mark.l + m[i].mark.r) * .5f, cy = (m[i].mark.t + m[i].mark.b) * .5f;
        Box mi = {cx - c, cy - c, cx + c, cy + c};
        for (U32 j = 0; j < count; j++) if (top_tier(m[j].cat) && !m[j].event) {
            float jx = (m[j].mark.l + m[j].mark.r) * .5f, jy = (m[j].mark.t + m[j].mark.b) * .5f, dx = cx - jx, dy = cy - jy;
            if (boxes_hit(mi, (Box){jx - c, jy - c, jx + c, jy + c})) { covered = 1; if (dx > -c && dx < c && dy > -c && dy < c) centred = 1; }
            if (m[j].state == MARK_NAMED && !m[j].ringed && m[j].cat == CAT_KEY && boxes_hit(mi, m[j].name)) covered = 1;
        }
        if (!covered) continue;
        if (m[i].cat != CAT_FILE || !centred) { m[i].state = MARK_DROP; continue; }
        float d = side * .6f;
        m[i].mark = (Box){m[i].mark.l + d, m[i].mark.t + d, m[i].mark.r + d, m[i].mark.b + d};
        if (m[i].state == MARK_NAMED) m[i].name = (Box){m[i].name.l + d, m[i].name.t + d, m[i].name.r + d, m[i].name.b + d};
    }
    return no;
}
