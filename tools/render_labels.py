"""Redraw every text raster in src/labels.h and src/crimson_data.h with Pretendard Medium.

The headers stay the build inputs. Text comes from each row's comment. Marker names and legend rows are drawn white with a
dark outline: the run time multiplies them by the category colour (INI [Colors]). The Crimson Head digits keep their own colours. Room names (kind 0) are placed and drawn by tools/layout_room_names.py, not here. Needs Pillow only."""
from collections import Counter
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'fonts/Pretendard-Medium.otf'
FONT_BOLD = ROOT / 'fonts/Pretendard-Bold.otf'
OUTLINE = (8, 8, 8)
WHITE = (255, 255, 255)
HINT = (170, 170, 170)  # legend key hints, in both languages
KEY_HINT = re.compile(r'^(?:(?P<mod>Shift|Ctrl) \+ )?(?P<keys>\[ · \]|- · \+)')
HINT_ROW = re.compile(r'^\[(공격|Attack)\]')
STROKE = 2
LINE_GAP = 4
ROW = re.compile(r'^(?P<head>\{(?P<kind>[0-57]),.*?,)(?P<w>\d+),(?P<h>\d+),(?P<px>px\d+)(?P<tail>,.*/\* (?P<text>.*) \*/)$')
LEGEND_ROW = re.compile(r'^(?P<head>\{(?P<kind>6),.*?,)(?P<w>\d+),(?P<h>\d+),(?P<px>px\d+)(?P<tail>\}, /\* (?P<text>.*) \*/)$')
_fonts = {}


def font(px):
    return _fonts.setdefault(px, ImageFont.truetype(str(FONT), px))


def clean(comment):
    """Row comment -> drawn lines: drop the category mark; ' / ' separates lines except in the one-line legend."""
    if comment.startswith('legend '):
        return [comment[len('legend '):]]
    return re.sub(r'^[★◆◇□]', '', comment).split(' / ')


def legend_row(line, px, color):
    """A legend row on a canvas of one fixed height per size, so all rows share a baseline. In '[ · ] ...', '- · + ...' and the
    same after 'Shift + ' or 'Ctrl + ', the keys are bold white and ' · ' (between alternatives) and ' + ' (a combination) are in the
    row colour (RE0 HD legend, user decision 2026-11-07: no outer brackets); the words after the keys start at the same x in rows
    with the same modifier."""
    regular, bold, small = font(px), ImageFont.truetype(str(FONT_BOLD), px), font(round(px * .7))

    def key_runs(modifier, first, second):
        head = [(modifier, WHITE, bold), (' + ', color, regular)] if modifier else []
        return head + [(first, WHITE, bold), (' · ', color, regular), (second, WHITE, bold)]

    def run_width(runs):
        return sum(f.getlength(text) for text, _, f in runs)

    keys = KEY_HINT.match(line)
    head, rest, start, text_x = [], line, 0, 0
    if keys:
        modifier, pair = keys['mod'], keys['keys']
        head = key_runs(modifier, pair[0], pair[-1])
        rest = line[keys.end():]
        column = max(run_width(key_runs(modifier, '[', ']')), run_width(key_runs(modifier, '-', '+')))
        start, text_x = (column - run_width(head)) / 2, column
    ref = regular.getbbox('[', anchor='ls')

    def lift(f):  # centre a smaller run on the bracket height of the row's own font
        box = f.getbbox('[', anchor='ls')
        return round(((ref[1] + ref[3]) - (box[1] + box[3])) / 2) if f is small else 0

    ascent, descent = regular.getmetrics()
    canvas = Image.new('RGBA', (int(text_x + regular.getlength(rest)) + 2 * STROKE + 3, ascent + descent + 2 * STROKE + 2))
    d = ImageDraw.Draw(canvas)
    baseline = ascent + STROKE + 1
    for stroke in (True, False):
        paint = (OUTLINE, OUTLINE) if stroke else (None, None)
        width = STROKE if stroke else 0
        x = STROKE + 1 + start
        for text, fill, f in head:
            d.text((x, baseline + lift(f)), text, font=f, anchor='ls', fill=(paint[0] or fill) + (255,), stroke_width=width, stroke_fill=OUTLINE + (255,))
            x += f.getlength(text)
        d.text((STROKE + 1 + text_x, baseline), rest, font=regular, anchor='ls', fill=(paint[0] or color) + (255,), stroke_width=width, stroke_fill=OUTLINE + (255,))
    return canvas


def block_size(lines, px):
    f = font(px)
    boxes = [f.getbbox(line, stroke_width=STROKE) for line in lines]
    return max(b[2] - b[0] for b in boxes), sum(b[3] - b[1] for b in boxes) + LINE_GAP * (len(lines) - 1)


def draw_block(canvas, lines, cx, cy, px, color):
    f = font(px)
    d = ImageDraw.Draw(canvas)
    y = cy - block_size(lines, px)[1] / 2
    for line in lines:
        l, t, r, b = f.getbbox(line, stroke_width=STROKE)
        d.text((round(cx - (r - l) / 2 - l), round(y - t)), line, font=f, fill=color + (255,),
               stroke_width=STROKE, stroke_fill=OUTLINE + (255,))
        y += b - t + LINE_GAP


def old_style(im):
    """(fill colour, text centre, leader-only layer) of an old raster."""
    px = im.load()
    w, h = im.size
    dark = {(x, y) for y in range(h) for x in range(w) if px[x, y][3] > 200 and sum(px[x, y][:3]) < 60}
    near = {(x + i, y + j) for x, y in dark for i in range(-3, 4) for j in range(-3, 4)}
    fill = Counter(px[x, y][:3] for x, y in near if 0 <= x < w and 0 <= y < h and px[x, y][3] > 240 and sum(px[x, y][:3]) > 60)
    xs, ys = [p[0] for p in dark], [p[1] for p in dark]
    leader = Image.new('RGBA', im.size)
    lp = leader.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] and (x, y) not in near:
                lp[x, y] = px[x, y]
    return fill.most_common(1)[0][0], ((min(xs) + max(xs) + 1) / 2, (min(ys) + max(ys) + 1) / 2), leader


def parse(text):
    start = text.index('static const Label labels[]={')
    end = text.index('};', start)
    return start, end, text[start:end].split('\n')


# Font size per marker kind and language, fitted once to the previous rasters so names keep their on-screen size.
SIZES = {(0, 'ko'): 23, (0, 'en'): 21, (1, 'ko'): 19, (1, 'en'): 17, (3, 'ko'): 19, (3, 'en'): 16, (2, 'ko'): 18, (2, 'en'): 17,
         (4, 'ko'): 19, (4, 'en'): 17, (5, 'ko'): 19, (5, 'en'): 17, ('legend', 'ko'): 20, ('legend-small', 'ko'): 16,
         ('legend', 'en'): 19, ('legend-small', 'en'): 15}


def rewrite_labels(kinds=None):
    path = ROOT / 'src/labels.h'
    text = path.read_text(encoding='utf-8')
    start, end, table = parse(text)
    arrays = dict(re.findall(r'static const unsigned char (px\d+)\[\]=\{([^}]*)\};', text))
    parsed = []
    for i, line in enumerate(table):
        m = ROW.match(line) or LEGEND_ROW.match(line)
        if not m or m['text'].startswith('item '):
            continue
        old = Image.frombytes('RGBA', (int(m['w']), int(m['h'])), bytes(map(int, arrays[m['px']].split(','))))
        if not old.getbbox():  # blank placeholder rows
            continue
        lines = clean(m['text'])
        lang = 'ko' if re.search('[가-힣]', m['text']) else 'en'
        kind = int(m['kind'])
        if kind == 0 or (kinds and kind not in kinds):  # room names: tools/layout_room_names.py
            continue
        cls = ('legend-small' if int(m['h']) < 22 else 'legend') if kind == 6 else kind
        parsed.append((i, m, cls, lang, lines, old))
    for i, m, cls, lang, lines, old in parsed:
        color = WHITE[::-1]  # white rasters: the run time tints them by category (INI [Colors]); stored B,G,R like the old fills
        px = SIZES[cls, lang]
        if int(m['kind']) == 6:
            canvas = legend_row(lines[0], px, color)
        else:  # marker names are placed at run time: the box is the text, so the collision box is too
            w, h = block_size(lines, px)
            canvas = Image.new('RGBA', (w + 2, h + 2))
            draw_block(canvas, lines, (w + 2) / 2, (h + 2) / 2, px, color)
        arrays[m['px']] = ','.join(map(str, canvas.tobytes()))
        table[i] = m.expand(r'\g<head>') + '%d,%d,%s' % (canvas.width, canvas.height, m['px']) + m['tail']
    text = text[:start] + '\n'.join(table) + text[end:]
    text = re.sub(r'(static const unsigned char (px\d+)\[\]=\{)[^}]*(\};)', lambda g: g[1] + arrays[g[2]] + g[3], text)
    path.write_text(text, encoding='utf-8')


def rewrite_crimson():
    path = ROOT / 'src/crimson_data.h'
    text = path.read_text(encoding='utf-8')
    w = int(re.search(r'CRIMSON_ATLAS_W (\d+)', text)[1])
    h = int(re.search(r'CRIMSON_ATLAS_H (\d+)', text)[1])
    row_h = int(re.search(r'CRIMSON_ROW_H (\d+)', text)[1])
    pad = int(re.search(r'CRIMSON_PAD (\d+)', text)[1])
    atlas = Image.frombytes('RGBA', (w, h), bytes(map(int, re.search(r'crimson_atlas\[\]=\{([^}]*)\}', text)[1].split(','))))
    rects = [tuple(map(int, r)) for r in re.findall(r'\{(\d+),(\d+),(\d+),(\d+),(\d+)\}', re.search(r'crimson_digit\[10\] = \{(.*?)\};', text)[1])]
    rects += [tuple(map(int, r)) for r in re.findall(r'\{(\d+),(\d+),(\d+),(\d+),(\d+)\}', re.search(r'crimson_unit\[2\] = \{(.*?)\};', text)[1])]
    glyphs = '0123456789분m'
    f = font(19)
    for row in range(h // row_h):
        for glyph, (x, _, cw, ch, _adv) in zip(glyphs, rects):
            box = (x, row * row_h, x + cw, row * row_h + ch)
            color, centre, _leader = old_style(atlas.crop(box))
            cell = Image.new('RGBA', (cw, ch))
            l, t, r, b = f.getbbox(glyph, stroke_width=STROKE)
            ImageDraw.Draw(cell).text((round((cw - (r - l)) / 2 - l), round(centre[1] - (b - t) / 2 - t)), glyph, font=f, fill=color + (255,),
                                      stroke_width=STROKE, stroke_fill=OUTLINE + (255,))
            atlas.paste(cell, box[:2])
    data = ','.join(map(str, atlas.tobytes()))
    text = re.sub(r'(crimson_atlas\[\]=\{)[^}]*(\})', lambda g: g[1] + data + g[2], text)
    path.write_text(text, encoding='utf-8')
    return pad


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kinds', help='only these row kinds, e.g. 1-6 (room names, kind 0, belong to layout_room_names.py)')
    a = ap.parse_args()
    if a.kinds:
        lo, _, hi = a.kinds.partition('-')
        rewrite_labels(set(range(int(lo), int(hi or lo) + 1)))
    else:
        rewrite_labels()
        rewrite_crimson()
