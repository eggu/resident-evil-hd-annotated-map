"""Apply the shared map-mod naming rules (RE0 HD wiki 02, user decision 2026-11-07) to the comments of src/labels.h.

- Marker names (kinds 1-5): a trailing count goes to line 2; otherwise a name of 8 or more characters (spaces included)
  wraps at the space nearest its middle; a single word is never split; at most two lines. Lines are joined by ' / '.
- Korean names drop the particle '의' unless verification/korean-particle-keep.json keeps it.
- Weapons are key items: each ordinary (kind 7) weapon row becomes a Korean and an English kind 4 row with an icon.
- Legend wording: '[ · ]' and '- · +' without outer brackets, '[7] ... (Hold: Time)'.

Only comments, kinds and icon tables change here; run tools/render_labels.py --kinds 1-6 afterwards to redraw the text.
Running it again changes nothing."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
MARKS = '★◆◇□'
KEEP = json.loads((ROOT / 'verification/korean-particle-keep.json').read_text(encoding='utf-8'))['keep']
WEAPONS = (3, 4, 6, 7, 10, 11, 12, 13, 15)  # item ids, data/item_names.json
COUNT = re.compile(r'^(.*?) (x\d+|\d+%)$')


def drop_particle(text):
    """'A의 B' -> 'A B' for every '의' that ends a word, unless the word is on the keep list."""
    return re.sub(r'(\S+)의(?= )', lambda m: m[0] if m[0] in KEEP else m[1], text)


def wrap(text):
    """Display text (no line breaks) -> lines."""
    m = COUNT.match(text)
    if m:
        return [m[1], m[2]]
    if len(text) < 8 or ' ' not in text:
        return [text]
    middle = len(text) / 2
    at = min((i for i, c in enumerate(text) if c == ' '), key=lambda i: abs(i - middle))
    return [text[:at], text[at + 1:]]


def name_comment(comment, korean):
    mark = re.match(r'^[%s]? *' % MARKS, comment)[0]  # '◆ Shield Key' keeps its space
    text = ' '.join(comment[len(mark):].split(' / '))
    if korean:
        text = drop_particle(text)
    return mark + ' / '.join(wrap(text))


def main():
    path = ROOT / 'src/labels.h'
    h = path.read_text(encoding='utf-8')
    names = json.loads((ROOT / 'data/item_names.json').read_text(encoding='utf-8'))
    out, extra_px, new_icons, icon_of = [], [], [], {}
    icon_count = int(re.search(r'#define ICON_COUNT (\d+)', h)[1])
    key = re.search(r'^\{4,(?:[^,]*,){11}(\d+),(\d+),(px\d+)[^\n]*/\* ◇', h, re.M)  # a key-item raster: colour source
    key_wh, key_px = key[1] + ',' + key[2], key[3]
    px_arrays = dict(re.findall(r'static const unsigned char (px\d+)\[\]=\{([^}]*)\};', h))
    next_px = max(int(k[2:]) for k in px_arrays) + 1
    for line in h.split('\n'):
        m = re.match(r'^\{(\d+),(.*)\}, /\* (.*) \*/$', line)
        if not m:
            out.append(line)
            continue
        kind, comment = int(m[1]), m[3]
        if kind == 6:
            fixed = re.sub(r'^legend \[\[·\]\] ', 'legend [ · ] ', comment)
            fixed = re.sub(r'^legend \[-·\+\] ', 'legend - · + ', fixed)
            fixed = fixed.replace('[7] 적 · 길게: 시간', '[7] 적 (길게: 시간)').replace('[7] Enemies · Hold: Time', '[7] Enemies (Hold: Time)')
            out.append(line.replace('/* ' + comment + ' */', '/* ' + fixed + ' */'))
        elif 1 <= kind <= 5:
            korean = re.search('[가-힣]', comment) is not None
            out.append(line.replace('/* ' + comment + ' */', '/* ' + name_comment(comment, korean) + ' */'))
        elif kind == 7 and int(comment.split()[-1]) in WEAPONS:
            item = int(comment.split()[-1])
            f = m[2].split(',')  # room, room2, area, floor, flag, chr, lang, x, y, x2, y2, w, h, px, reward, step, ax, ay, visits...
            if item not in icon_of:
                icon_of[item] = icon_count + len(new_icons) + 1
                new_icons.append(f[13])
            icon = icon_of[item]
            visits = ','.join(f[18:])
            for lang, text in ((1, names[str(item)][1]), (2, names[str(item)][0])):
                px = 'px%d' % next_px
                next_px += 1
                extra_px.append('static const unsigned char %s[]={%s};' % (px, px_arrays[key_px]))
                head = ','.join(['4'] + f[:6] + [str(lang)] + f[7:11])
                out.append('{%s,%s,%s,0,0,0.00f,0.00f,%s,%d}, /* %s */' % (head, key_wh, px, visits, icon, name_comment('◇' + text, lang == 1)))
        else:
            out.append(line)
    h = '\n'.join(out)
    if new_icons:
        icon_px = ''.join('static const unsigned char icpx%d[]={%s};\n' % (icon_count + n, px_arrays[p]) for n, p in enumerate(new_icons))
        h = h.replace('static const struct { U32 w, h; const BYTE *px; } icons[]={',
                      '\n'.join(extra_px) + '\n' + icon_px + 'static const struct { U32 w, h; const BYTE *px; } icons[]={', 1)
        h = re.sub(r'(icons\[\]=\{.*?)\};', lambda g: g[1] + ''.join(',{32,32,icpx%d}' % (icon_count + n) for n in range(len(new_icons))) + '};', h, count=1, flags=re.S)
        h = h.replace('#define ICON_COUNT %d' % icon_count, '#define ICON_COUNT %d' % (icon_count + len(new_icons)))
        count = len(re.findall(r'^\{\d+,[^\n]*\}, /\* .* \*/$', h, re.M))
        h = re.sub(r'#define LABEL_COUNT \d+', '#define LABEL_COUNT %d' % count, h)
        rows = re.findall(r'^\{(\d+),[^\n]*\}, /\* .* \*/$', h, re.M)
        h = re.sub(r'#define LEGEND_FIRST \d+', '#define LEGEND_FIRST %d' % rows.index('6'), h)
    path.write_text(h, encoding='utf-8')


if __name__ == '__main__':
    main()
