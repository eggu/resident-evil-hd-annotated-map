"""Rewrite the category rows of the legend in src/labels.h (user decision 2026-11-08, legend renumbering).

Per language the block is: title, name opacity x10, name size x11, then the category rows [0]..[8] (one white raster each; the
run time picks the colour, so there is no separate off raster), the three scope rows [9], and the note row. The language row
'[\\] ...' lives in legend_text.h next to [H]. Idempotent: it removes every '[<digit>]' legend row and writes the new ones.
Needs Pillow; run before render_labels.py."""
from pathlib import Path
import re
from render_labels import ROOT, SIZES, WHITE, legend_row

CATEGORIES = {
    'ko': ['[0] 전체', '[1] 방 이름', '[2] 잠긴 문', '[3] 핵심 아이템', '[4] 문서·지도', '[5] 퍼즐', '[6] 이벤트', '[7] 일반 아이템', '[8] 적 (길게: 시간)'],
    'en': ['[0] All', '[1] Rooms', '[2] Locks', '[3] Key items', '[4] Files/Maps', '[5] Puzzles', '[6] Events', '[7] Common items', '[8] Enemies (Hold: Time)']}
SCOPE = {'ko': ['[9] 범위: 방문한 방', '[9] 범위: 공개된 방', '[9] 범위: 모든 방'],
         'en': ['[9] Scope: Visited', '[9] Scope: Revealed', '[9] Scope: All rooms']}
ROW = re.compile(r'^\{6,-1,-1,99,99,0,0,0,0\.0f,0\.0f,0\.0f,0\.0f,(\d+),(\d+),(px\d+)\}, /\* legend (.*) \*/$')
DIGIT_ROW = re.compile(r'^\[\d\] ')


def main():
    path = ROOT / 'src/labels.h'
    text = path.read_text(encoding='utf-8')
    start = text.index('static const Label labels[]={')
    end = text.index('\n};', start)
    table = text[start:end].split('\n')
    arrays = dict(re.findall(r'static const unsigned char (px\d+)\[\]=\{([^}]*)\};', text))
    top = max(int(k[2:]) for k in arrays)
    out, dropped, added, written = [], set(), [], set()
    for line in table:
        m = ROW.match(line)
        if not m:
            out.append(line)
            continue
        lang = 'ko' if re.search('[가-힣]', m[4]) else 'en'
        if not DIGIT_ROW.match(m[4]):
            out.append(line)
            continue
        dropped.add(m[3])
        if lang in written:
            continue
        written.add(lang)
        for words in CATEGORIES[lang] + SCOPE[lang]:
            canvas = legend_row(words, SIZES['legend', lang], WHITE[::-1])
            top += 1
            added.append('static const unsigned char px%d[]={%s};\n' % (top, ','.join(map(str, canvas.tobytes()))))
            out.append('{6,-1,-1,99,99,0,0,0,0.0f,0.0f,0.0f,0.0f,%d,%d,px%d}, /* legend %s */' % (canvas.width, canvas.height, top, words))
    text = text[:start] + '\n'.join(out) + text[end:]
    text = re.sub(r'static const unsigned char (px\d+)\[\]=\{[^}]*\};\n', lambda g: '' if g[1] in dropped else g[0], text)
    text = text.replace('static const Label labels[]={', ''.join(added) + 'static const Label labels[]={', 1)
    s = text.index('static const Label labels[]={')
    count = sum(1 for l in text[s:text.index('\n};', s)].split('\n') if l.startswith('{'))
    per = (count - 876 - 2) // 2
    text = re.sub(r'#define LEGEND_PER_LANG \d+', '#define LEGEND_PER_LANG %d' % per, text)
    text = re.sub(r'#define LABEL_COUNT \d+', '#define LABEL_COUNT %d' % count, text)
    path.write_text(text, encoding='utf-8')
    print('LABEL_COUNT', count, 'LEGEND_PER_LANG', per)


if __name__ == '__main__':
    main()
