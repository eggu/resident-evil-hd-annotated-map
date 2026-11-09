"""Draw the three eye symbols the Rec Room lamps reveal (src/synth_marks.h) as 32 px sprites: assets/icons/symbol-eye-{1,2,3}.png,
embedded in src/labels.h as icons 97-99. Drawn here, not copied from the game's keypad texture (which holds the same three
glyphs, id\\j_rom\\common\\tex\\common\\pass\\pass_room\\r408_00_ID_HQ): 1 orange lamp = eye with rays, 2 green = eye with a
filled pupil and lashes, 3 red = pointed eye with a split iris. Hard alpha like every icon. Needs Pillow; idempotent."""
from pathlib import Path
import re
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
S = 8  # supersample
INK, RIM = (244, 236, 208, 255), (14, 14, 18, 255)


def lens(d, cx, cy, w, h, width):
    """Outline of a lens-shaped eye: two parabolic arcs meeting at the corners."""
    n = 40
    for sign in (-1, 1):
        pts = [(cx + w * (2.0 * i / n - 1), cy + sign * h * (1 - (2.0 * i / n - 1) ** 2)) for i in range(n + 1)]
        d.line(pts, fill=INK, width=width, joint='curve')


def draw(kind):
    im = Image.new('RGBA', (32 * S, 32 * S))
    d = ImageDraw.Draw(im)
    cx, cy, w, h, t = 16 * S, 17 * S, 14 * S, 7 * S, 2 * S
    if kind == 2:  # filled pupil, lashes above
        lens(d, cx, cy, w, h, t)
        d.ellipse((cx - 5 * S, cy - 5 * S, cx + 5 * S, cy + 5 * S), outline=INK, width=int(1.5 * S))
        d.ellipse((cx - 2 * S, cy - 2 * S, cx + 2 * S, cy + 2 * S), fill=INK)
        d.line((6 * S, 5 * S, 9 * S, 8 * S), fill=INK, width=t)
        d.line((26 * S, 5 * S, 23 * S, 8 * S), fill=INK, width=t)
    elif kind == 1:  # iris ring with rays up and down
        lens(d, cx, cy, w, h, t)
        d.ellipse((cx - 5 * S, cy - 5 * S, cx + 5 * S, cy + 5 * S), outline=INK, width=int(1.5 * S))
        for x0, y0, x1, y1 in ((16, 2, 16, 7), (8, 5, 10, 8), (24, 5, 22, 8), (16, 27, 16, 30)):
            d.line((x0 * S, y0 * S, x1 * S, y1 * S), fill=INK, width=t)
    else:  # pointed eye, split iris
        lens(d, cx, cy, w, h, t)
        d.line((1 * S, cy, 5 * S, cy), fill=INK, width=t)
        d.line((27 * S, cy, 31 * S, cy), fill=INK, width=t)
        d.ellipse((cx - 5 * S, cy - 5 * S, cx + 5 * S, cy + 5 * S), outline=INK, width=int(1.5 * S))
        d.line((cx, cy - 5 * S, cx, cy + 5 * S), fill=INK, width=int(1.5 * S))
    mask = im.getchannel('A').resize((32, 32), Image.Resampling.LANCZOS).point(lambda a: 255 if a > 90 else 0)
    ink = im.resize((32, 32), Image.Resampling.LANCZOS)
    out = Image.new('RGBA', (32, 32))
    from PIL import ImageFilter
    rim = mask.filter(ImageFilter.MaxFilter(3))
    out.paste(RIM, mask=rim)
    out.paste(INK, mask=mask)
    return out


def main():
    pngs = []
    for k in (1, 2, 3):
        im = draw(k)
        im.save(ROOT / ('assets/icons/symbol-eye-%d.png' % k))
        pngs.append(im.tobytes('raw', 'BGRA'))
    p = ROOT / 'src/labels.h'
    h = p.read_text(encoding='utf-8')
    h = re.sub(r'static const unsigned char icpx(9[6-9])\[\]=\{[^}]*\};\n', '', h)
    h = re.sub(r',\{32,32,icpx9[6-9]\}', '', h)
    arrays = ''.join('static const unsigned char icpx%d[]={%s};\n' % (96 + i, ','.join(map(str, b))) for i, b in enumerate(pngs))
    at = h.index('static const struct { U32 w, h; const BYTE *px; } icons[]')
    h = h[:at] + arrays + h[at:]
    h = h.replace('{32,32,icpx95}}', '{32,32,icpx95},{32,32,icpx96},{32,32,icpx97},{32,32,icpx98}}')
    h = re.sub(r'#define ICON_COUNT \d+', '#define ICON_COUNT 99', h)
    p.write_text(h, encoding='utf-8')


if __name__ == '__main__':
    main()
