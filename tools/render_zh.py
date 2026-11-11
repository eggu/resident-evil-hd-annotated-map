"""Write src/labels_zh.h: the Simplified Chinese (zh_cn) rasters of the third language slot.

zh_cn is a compatibility slot: it reuses every Korean row of src/labels.h (positions, conditions, legend layout) and only swaps the
raster. Each entry names the Korean label row it replaces (`label`); the run time draws zh_text[k] instead of that row while the
language is zh. Covered: the marker names (kinds 1-5), the Korean legend block and its zoom hint (kind 6), and the room names
(kind 0), which are placed again by tools/layout_room_names.py's search and check with the Chinese widths (anchor x, y on the
1280x720 canvas and ax, ay in the raster, like the label rows). Rows without a translation keep the Korean raster, which the
build refuses for drawn rows (see MISSING below). Line bands of multi-line names (zh_lines, by zh_text index) are found like
tools/gen_name_lines.py does.

Text: data/zh_cn.json. Font: Source Han Sans SC subsets (fonts/SourceHanSansSC-*-zh.otf, tools/subset_zh_fonts.py); every
character must be in them. Needs Pillow and fontTools.
Run after render_labels.py / layout_room_names.py whenever labels.h or data/zh_cn.json change."""
from pathlib import Path
import json
import re
from PIL import Image
import render_labels as RL
import layout_room_names as L
from gen_name_lines import entry

ROOT = RL.ROOT
LANG = 'zh'
ZH_ROOM_LANG = 3  # lang id used only inside this generator (layout groups); the runtime keeps lang 1 rows for zh
DATA = json.loads((ROOT / 'data/zh_cn.json').read_text(encoding='utf-8'))


def norm(s):
    return ' '.join(s.replace(' / ', ' ').split())


NAMES = {norm(k): v for k, v in DATA['names'].items()}
ROOMS = {norm(k): v for k, v in DATA['rooms'].items()}
LEGEND = DATA['legend']


def legend_zh(text):
    """Korean legend row text -> Chinese (the opacity and size rows carry their value)."""
    if text in LEGEND:
        return LEGEND[text]
    m = re.match(r'^(\[ · \]|- · \+) (이름 불투명도|이름 크기) (\d+%)$', text)
    if m:
        return '%s %s %s' % (m[1], LEGEND[m[2]], m[3])
    raise KeyError(text)


def labels_table(text):
    """[(line index in the file, label index, line)] of the label rows."""
    lines = text.split('\n')
    start = next(i for i, l in enumerate(lines) if l.startswith('static const Label labels[]={'))
    out, k = [], 0
    for i in range(start + 1, len(lines)):
        if lines[i].startswith('};'):
            break
        if lines[i].startswith('{'):
            out.append((i, k, lines[i]))
            k += 1
    return out


def raster_rgba(im):
    return ','.join(map(str, im.tobytes()))


def check_font():
    from fontTools.ttLib import TTFont
    chars = set(''.join(v for k, g in DATA.items() if not k.startswith('_') for v in g.values())) - set(' |/')
    chars |= set('[]·:-+%0123456789HShiftCtrl~\\')
    for path in (RL.FONT_ZH, RL.FONT_ZH_BOLD):
        cmap = TTFont(str(path)).getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        if missing:
            raise SystemExit('%s lacks %s: run tools/subset_zh_fonts.py' % (path.name, ''.join(missing)))


def main():
    check_font()
    text = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
    count = int(re.search(r'#define LABEL_COUNT (\d+)', text)[1])
    legend_first = int(re.search(r'#define LEGEND_FIRST (\d+)', text)[1])
    per_lang = int(re.search(r'#define LEGEND_PER_LANG (\d+)', text)[1])
    arrays = dict(re.findall(r'static const unsigned char (px\d+)\[\]=\{([^}]*)\};', text))
    table = labels_table(text)
    by_line = {i: k for i, k, _ in table}
    entries, missing = [], []  # (label, image, x, y, ax, ay, comment, lines or None)

    # marker names (kinds 1-5, Korean rows) and the Korean legend block + zoom hint (kind 6)
    legend_rows = set(range(legend_first, legend_first + per_lang)) | {count - 2}
    for _, k, line in table:
        m = RL.ROW.match(line) or RL.LEGEND_ROW.match(line)
        if not m:
            continue
        kind = int(m['kind'])
        if kind == 6:
            if k not in legend_rows:
                continue
            words = m['text'][len('legend '):]
            try:
                zh = legend_zh(words)
            except KeyError:
                missing.append((k, m['text']))
                continue
            cls = 'legend-small' if int(m['h']) < 22 else 'legend'
            im = RL.legend_row(zh, RL.SIZES[cls, LANG], RL.WHITE[::-1], LANG)
            entries.append((k, im, 0, 0, 0, 0, 'legend ' + zh, None))
            continue
        if kind == 0 or kind == 7:
            continue
        if not line.split(',')[7] == '1':  # Korean rows only (the zh slot reuses them)
            continue
        old = Image.frombytes('RGBA', (int(m['w']), int(m['h'])), bytes(map(int, arrays[m['px']].split(','))))
        if not old.getbbox():  # blank placeholder rows stay blank
            continue
        key = norm(re.sub(r'^[★◆◇□]', '', m['text']))
        if key not in NAMES:
            missing.append((k, m['text']))
            continue
        lines = NAMES[key].split(' / ')
        px = RL.SIZES[kind, LANG]
        w, h = RL.block_size(lines, px, LANG)
        im = Image.new('RGBA', (w + 2, h + 2))
        RL.draw_block(im, lines, (w + 2) / 2, (h + 2) / 2, px, RL.WHITE[::-1], LANG)
        entries.append((k, im, 0, 0, 0, 0, NAMES[key], lines if kind in (1, 2, 4, 5) else None))

    # room names: the layout search and check of tools/layout_room_names.py, with Chinese text and widths
    L.SIZE[ZH_ROOM_LANG] = RL.SIZES[0, LANG]
    L.font = lambda px: RL.font(px, LANG)

    def zh_wrap(text, room_width, px):
        """One line unless wider than 150% of the room; then at the '|' nearest the middle."""
        parts = text.split('|')
        one = ''.join(parts)
        if len(parts) == 1 or L.text_size([one], px)[0] / L.RASTER <= L.WRAP * room_width:
            return [one]
        cuts = [len(''.join(parts[:i])) for i in range(1, len(parts))]
        at = min(cuts, key=lambda c: (abs(c - len(one) / 2), c))
        return [one[:at], one[at:]]

    L.wrap = zh_wrap

    rows = []
    for i, m in L.read_rows(text):
        if m['lang'] != '1':
            continue
        key = norm(m['text'])
        if key not in ROOMS:
            missing.append((by_line[i], m['text']))
            continue
        rows.append((i, dict(m.groupdict(), lang=str(ZH_ROOM_LANG), text=ROOMS[key])))
    data = L.room_geometry.load()
    names, shapes, exclusive = L.layout(rows, data)
    for n in names:
        n['lang'] = LANG
    errors = L.check(names, shapes, exclusive)
    if errors:
        raise SystemExit('zh room-name layout check failed:\n' + '\n'.join(errors))
    layout_out = []
    for n in names:
        im, ax, ay = L.raster(n)
        entries.append((by_line[n['row']], im, n['anchor'][0], n['anchor'][1], ax, ay, ''.join(n['lines']), None))
        layout_out.append({'room': n['room'], 'lang': LANG, 'lines': n['lines'], 'anchor': [round(v, 2) for v in n['anchor']],
                           'box': list(n['box']), 'leader': n['leader'], 'coverage': round(n['coverage'], 3)})

    if missing:
        raise SystemExit('no zh_cn text for:\n' + '\n'.join('  label %d: %s' % km for km in missing))

    entries.sort(key=lambda e: e[0])
    images, rows_out, line_rows = [], [], []
    for z, (label, im, x, y, ax, ay, comment, lines) in enumerate(entries):
        images.append('static const unsigned char zhpx%d[]={%s};' % (z, raster_rgba(im)))
        rows_out.append('{%d,%d,%d,zhpx%d,%.2ff,%.2ff,%.2ff,%.2ff}, /* %s */' % (label, im.width, im.height, z, x, y, ax, ay, comment))
        if lines and len(lines) > 1:
            e = entry(z, im, len(lines))
            if e:
                line_rows.append(e)
    fmt = lambda rs: ','.join('{%d,%d,{%s}}' % (i, len(b), ','.join('{%d,%d,%d,%d}' % l for l in b + [(0, 0, 0, 0)] * (3 - len(b)))) for i, b in rs)
    out = ['/* Generated by tools/render_zh.py: do not edit. Simplified Chinese (zh_cn), the third language slot: each entry replaces the',
           ' * raster of the Korean label row `label` while the language is zh; room names carry their own anchor (x, y) and raster anchor',
           ' * (ax, ay). Text: data/zh_cn.json; font: Source Han Sans SC (fonts/SourceHanSansSC-*-zh.otf). Needs name_lines.h first. */',
           *images,
           'typedef struct { unsigned short label, w, h; const BYTE *px; float x, y, ax, ay; } ZhText;',
           'static const ZhText zh_text[]={', *rows_out, '};',
           '#define ZH_COUNT %d' % len(rows_out),
           '/* line bands of the multi-line zh marker names, by zh_text index (name_lines.h format) */',
           'static const NameLines zh_lines[]={%s};' % fmt(line_rows),
           '#define ZH_LINES_COUNT %d' % len(line_rows), '']
    (ROOT / 'src/labels_zh.h').write_text('\n'.join(out), encoding='utf-8')
    (ROOT / 'data/room_names_zh.json').write_text(json.dumps({'_note': 'tools/render_zh.py output: zh_cn room-name layout; canvas units (1280x720).',
                                                              'names': layout_out}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('%d zh rasters (%d room names, %d with leaders), %d multi-line' % (len(rows_out), len(layout_out),
                                                                           sum(1 for n in layout_out if n['leader']), len(line_rows)))


if __name__ == '__main__':
    main()
