"""The real build_legend, compiled on the host with the real label sizes (user decision 2026-11-08, the shared numbering). Open:
two columns under the title (the RE0 layout), [0]..[4] with [H] item names under [4] | [5]..[8] with [9] scope under [8] and [\\] language under [9],
the [~] hint beside the title, the zoom hint below, a panel as wide in every state and language as the widest, and the bottom-right readout shows name opacity and size, then icon opacity and size for the INI modifier. Folded ([~]): one
line, no readout. Rows are white rasters; categories are tinted by the INI colours, a disabled row #6A6A6A. Both languages;
everything inside its panel, nothing overlapping. Wording: '[ · ]' and '- · +' without outer brackets, '[8] ... (Hold: Time)'."""
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
h = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
t = (ROOT / 'src/legend_text.h').read_text(encoding='utf-8')
cut = lambda a, b: s[s.index(a):s.index(b)]
count = int(re.search(r'#define LABEL_COUNT (\d+)', h)[1])
rows = re.findall(r'^\{(\d+),(?:[^,]*,){11}(\d+),(\d+),px\d+[^\n]*/\* (.*?) \*/', h, re.M)
assert len(rows) == count
texts = [x for _, _, _, x in rows]
assert sum(x.startswith('legend [ · ] ') for x in texts) == 20 and sum(x.startswith('legend - · + ') for x in texts) == 22
assert not any(re.match(r'legend \[(\[|-)', x) for x in texts), 'outer brackets'
assert texts.count('legend [8] 적 (길게: 시간)') == 1 and texts.count('legend [8] Enemies (Hold: Time)') == 1
for lang, words in (('ko', ['전체', '방 이름', '잠긴 문', '핵심 아이템', '문서·지도', '퍼즐', '이벤트', '일반 아이템']), ('en', ['All', 'Rooms', 'Locks', 'Key items', 'Files/Maps', 'Puzzles', 'Events', 'Common items'])):
    for n, w in enumerate(words):
        assert texts.count('legend [%d] %s' % (n, w)) == 1, (lang, n, w)  # one white raster per category, no off raster
assert sum(re.match(r'legend \[\d\] ', x) is not None for x in texts) == 24
lt = re.findall(r'^\{(\d+),(\d+),ltpx\d+\}, /\* (.*) \*/', t, re.M)
assert lt[0][2] == 'Shift + [ · ] 아이콘 불투명도 10%' and lt[10][2] == 'Ctrl + [ · ] 아이콘 불투명도 10%'
assert lt[20][2] == 'Shift + - · + 아이콘 크기 50%' and lt[51][2] == 'Ctrl + - · + 아이콘 크기 200%'
assert [x for _, _, x in lt[52:58]] == ['[H] 아이템 이름: 모두', '[H] 아이템 이름: 일반 제외', '[H] 아이템 이름: 끔', '[~] 숨김', '[~] 범례', '[\\] 언어: 한국어']
assert [x for _, _, x in lt[110:116]] == ['[H] Item names: All', '[H] Item names: No common', '[H] Item names: Off', '[~] Hide', '[~] Legend', '[\\] LANGUAGE: ENGLISH']
sizes = ','.join('{%s,%s}' % (w, hh) for _, w, hh, _ in rows)
lt_sizes = ','.join('{%s,%s}' % (w, hh) for w, hh, _ in lt)

PROG = r'''
#include <assert.h>
typedef unsigned U32; typedef long LONG;
#define VK_SHIFT 0x10
#define VK_CONTROL 0x11
#define LABEL_COUNT %d
#define ICON_COUNT 0
#define CRIMSON_KIND 8
#define EVENT_KIND 6
#define PANEL_IMAGE (LABEL_COUNT + 1)
#define TEXT_FIRST (LABEL_COUNT + 2 + ICON_COUNT)
%s
%s
#include "colors.h"
typedef struct { U32 w, h; } Size;
typedef struct { float l, t, r, b; } Box;
typedef struct { Box box; U32 weight; } Occupied;
static const Size labels[LABEL_COUNT] = {%s};
static const Size legend_text[LT_COUNT] = {%s};
static U32 image_w(U32 i) { return i < LABEL_COUNT ? labels[i].w : i >= TEXT_FIRST ? legend_text[i - TEXT_FIRST].w : 4; }
static U32 image_h(U32 i) { return i < LABEL_COUNT ? labels[i].h : i >= TEXT_FIRST ? legend_text[i - TEXT_FIRST].h : 4; }
static LONG english, all_off, hidden, name_opacity = 70, name_size = 100, visibility, icon_size = 100, icon_opacity = 80;
static LONG item_names, legend_open = 1, modifier_vk = VK_SHIFT;
static float legend_top; static U32 layer, emit_color;
static struct { U32 i, color; float x, y, w, h; } op[64]; static int nop;
static Occupied occ[8]; static U32 nocc;
static void emit(U32 i, float x, float y, float w, float h, float u0, float v0, float u1, float v1) {
    op[nop].i = i; op[nop].color = emit_color; op[nop].x = x; op[nop].y = y; op[nop].w = w; op[nop].h = h; nop++; }
static void reserve_w(float x, float y, float w, float h, U32 weight) { occ[nocc++] = (Occupied){{x, y, x + w, y + h}, weight}; }
%s
static int find(U32 i) { for (int n = 0; n < nop; n++) if (op[n].i == i) return n; return -1; }
static int inside(int n, Box b) { return op[n].x >= b.l && op[n].y >= b.t && op[n].x + op[n].w <= b.r && op[n].y + op[n].h <= b.b; }
static U32 tint(int n) { return op[n].color & 0xffffff; }
int main(void) {
    float first_width = -1;
    for (english = 0; english < 2; english++) for (visibility = 0; visibility < 3; visibility++) for (int m = 0; m < 2; m++) {
        modifier_vk = m ? VK_CONTROL : VK_SHIFT; item_names = (visibility + 1) %% 3; icon_opacity = 10 + 30 * visibility; icon_size = 50 + 70 * visibility;
        nop = 0; nocc = 0; legend_open = 1; hidden = 0; all_off = 0; build_legend(0, 1.0f, 2560, 1440);
        U32 base = LEGEND_FIRST + (english ? LEGEND_PER_LANG : 0), lt = TEXT_FIRST + (english ? LT_PER_LANG : 0);
        assert(nocc == 2 && occ[0].weight == 8 && occ[1].weight == 8);
        assert(occ[0].box.l < 100 && occ[1].box.r > 2400 && occ[0].box.b == occ[1].box.b);       /* bottom-left, bottom-right */
        int cell[12];
        for (int r = 0; r < 9; r++) cell[r] = find(base + LG_ROW + r);                     /* every row on (all shown) */
        cell[9] = find(base + LG_SCOPE + visibility); cell[10] = find(lt + LT_ITEM_NAMES + (item_names + 2) %% 3); cell[11] = find(lt + LT_LANG);
        for (int r = 0; r < 12; r++) assert(cell[r] >= 0 && inside(cell[r], occ[0].box));
        /* two columns (RE0 layout): [0]..[4] with [H] under [4], [5]..[8] with [9] under [8] and [\\] under [9] */
        for (int r = 1; r < 5; r++) { assert(op[cell[r]].x == op[cell[0]].x); assert(op[cell[r]].y > op[cell[r - 1]].y); }
        for (int r = 6; r < 9; r++) { assert(op[cell[r]].x == op[cell[5]].x); assert(op[cell[r]].y > op[cell[r - 1]].y); }
        float lh = op[cell[1]].y - op[cell[0]].y;
        assert(op[cell[10]].x == op[cell[0]].x && op[cell[10]].y == op[cell[4]].y + lh);               /* [H] under [4] */
        assert(op[cell[9]].x == op[cell[5]].x && op[cell[9]].y == op[cell[8]].y + lh);                 /* [9] under [8] */
        assert(op[cell[11]].x == op[cell[9]].x && op[cell[11]].y == op[cell[9]].y + lh);               /* [\\] under [9] */
        assert(op[cell[11]].y == op[cell[10]].y);                                                      /* [H] and [\\] share a row */
        for (int r = 5; r < 9; r++) assert(op[cell[r]].y == op[cell[r - 5]].y);                       /* rows line up across columns */
        for (int r = 0; r < 5; r++) assert(op[cell[r]].x + op[cell[r]].w <= op[cell[5]].x);           /* no overlap */
        assert(op[cell[10]].x + op[cell[10]].w <= op[cell[11]].x);
        assert(op[cell[10]].h == op[cell[11]].h);                                                      /* [\\] is the size of [H] */
        assert(tint(cell[11]) == COLOR_WHITE && tint(cell[10]) == (item_names ? COLOR_WHITE : COLOR_OFF) && tint(cell[9]) == COLOR_WHITE && tint(cell[0]) == COLOR_WHITE);
        float width = occ[0].box.r - occ[0].box.l;                                                     /* the panel never changes width: states, languages, modifier */
        if (first_width < 0) first_width = width; assert(width == first_width);
        static const int col[9] = {-1, COL_ROOM, COL_LOCK, COL_KEY, COL_FILE, COL_PUZZLE, COL_EVENT, COL_COMMON, COL_ENEMY};
        for (int r = 1; r < 9; r++) assert(tint(cell[r]) == cat_color[col[r]]);                /* the INI colour of the category */
        int hide = find(lt + LT_HIDE), zoom = find(LG_ZOOM + english);
        assert(hide >= 0 && inside(hide, occ[0].box) && op[hide].x > op[find(base + LG_TITLE)].x + op[find(base + LG_TITLE)].w);
        assert(find(lt + LT_ITEM_NAMES + (item_names + 3) %% 3) < 0 && find(lt + LT_ITEM_NAMES + (item_names + 1) %% 3) < 0 && zoom >= 0 && op[zoom].y > op[cell[11]].y);
        int ro[4] = {find(base + LG_OPACITY + 6), find(base + LG_SIZE + 5),
                     find(lt + LT_ICON_OPACITY + m * 10 + (icon_opacity - 10) / 10), find(lt + LT_ICON_SIZE + m * 16 + (icon_size - 50) / 10)};
        for (int i = 0; i < 4; i++) { assert(ro[i] >= 0 && inside(ro[i], occ[1].box)); if (i) assert(op[ro[i]].y > op[ro[i - 1]].y); }
        for (int n = 0; n < nop; n++) if (op[n].i != PANEL_IMAGE) assert(inside(n, occ[0].box) || inside(n, occ[1].box));
        /* disabled rows: #6A6A6A; a changed INI colour follows; [H] off is grey too */
        nop = 0; nocc = 0; hidden = (1 << EVENT_KIND) | (1 << CRIMSON_KIND) | 1; cat_color[COL_KEY] = 0x123456; item_names = 0; build_legend(0, 1.0f, 2560, 1440);
        assert(tint(find(base + LG_ROW + 6)) == COLOR_OFF && tint(find(base + LG_ROW + 8)) == COLOR_OFF && tint(find(base + LG_ROW + 1)) == COLOR_OFF);
        assert(tint(find(base + LG_ROW + 3)) == 0x123456 && tint(find(base + LG_ROW + 2)) == cat_color[COL_LOCK] && tint(find(lt + LT_ITEM_NAMES + 2)) == COLOR_OFF);
        cat_color[COL_KEY] = color_default[COL_KEY];
        nop = 0; nocc = 0; hidden = 0; all_off = 1; build_legend(0, 1.0f, 2560, 1440);
        for (int r = 0; r < 9; r++) assert(tint(find(base + LG_ROW + r)) == COLOR_OFF);
        all_off = 0; hidden = 0;
        nop = 0; nocc = 0; legend_open = 0; build_legend(0, 1.0f, 2560, 1440);
        assert(nocc == 2 && occ[1].box.r == occ[1].box.l && find(lt + LT_FOLD) >= 0 && find(base + LG_TITLE) < 0 && nop == 2);
        assert(inside(find(lt + LT_FOLD), occ[0].box));
    }
    return 0;
}
'''
defines = '\n'.join(re.findall(r'^#define LEGEND_(?:FIRST|PER_LANG) \d+$', h, re.M))
lt_defines = '\n'.join(re.findall(r'^#define LT_\w+ \d+', t, re.M))
prog = PROG % (count, defines, lt_defines, sizes, lt_sizes, cut('#define LG_TITLE', '/* Kerosene tank i'))
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 'legend.c', Path(d) / 'legend'
    c.write_text(prog, encoding='utf-8')
    subprocess.run(['clang', '-w', '-I', str(ROOT / 'src'), str(c), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
print('PASS: legend in two columns ([0]-[4] [H] | [5]-[8] [9] [\\]), stable panel width, colours from the INI table, disabled #6A6A6A, readout bottom-right, fold to one line; both languages')
