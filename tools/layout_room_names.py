"""Place every room name at build time on its room's real shape (data/room_shapes.json) and redraw its raster in src/labels.h.

Rules (RE0 HD wiki 03, the shared default since 2026-11-07), in canvas units (game pixels at 1280x720; 1 unit = 2 raster px):
1. Fixed at generation. The runtime draws a name at its anchor (labels x, y) with raster offset (ax, ay); a resized name grows
   away from the anchor, so a leader's room end stays put.
2. The room's filled silhouette, not its rectangle (holes are filled by the extractor).
3. Pole of inaccessibility: the cell farthest from the shape's edge (ties nearest the centroid). The box goes to the free
   point nearest the pole among those within 0.05 of the best coverage (or covering fully).
4. Smallest rooms first.
5. Corridors: narrower than two name heights and the box at the pole covers under half -> outside with a leader. Also when no
   free point is left inside.
6. Leaders: axis-aligned from an edge cell of the room into empty map space (not on or beside another room, not across a
   name), at most LEADER_MAX long, shortest first; the box beyond its end sits on no room. A narrow room no leader can
   leave (enclosed by other rooms) keeps its name inside over its neighbours; nothing free at all stops the build.
7. 150%: a one-line name wider than 150% of its room's width wraps at the space nearest its middle.
8. Room names avoid each other (same floor, same language, unless one replaces the other: section_rules.h or the same map
   position); they avoid no marks (marks.h weighs them at run time).
9. Korean and English are placed separately.
10. check(): restated apart from the search; any violation stops generation.
The legend and readout are not avoided here: the map offset that places a floor on screen is known only at run time, and
the panels are drawn over the map there.

Usage: python tools/layout_room_names.py [--check-only]. Writes src/labels.h (room-name rows and rasters only) and
data/room_names.json (the layout, readable)."""
from pathlib import Path
import argparse
import json
import math
import re
from PIL import Image, ImageDraw
import room_geometry
from render_labels import FONT, STROKE, LINE_GAP, OUTLINE, font

ROOT = Path(__file__).resolve().parents[1]
CANVAS = (1280, 720)
RASTER = 2               # raster px per canvas unit (1440p, name size 100%)
LEADER_MAX = 60          # canvas units (RE0 HD: 60 on the same 1280x720 canvas)
LEADER_MIN = 4
WRAP = 1.5
COLOUR = (255, 255, 255)  # white: the run time multiplies it by the Rooms colour (INI [Colors])
SIZE = {1: 23, 2: 21}     # font px by language (render_labels.SIZES[0, ...])
LEADER_FILL, LEADER_EDGE, LEADER_RADIUS = (190, 190, 185, 255), (20, 18, 16, 120), 2
ROW = re.compile(r'^\{0,(?P<room>\d+),(?P<room2>-?\d+),(?P<area>\d+),(?P<floor>\d+),(?P<flag>\d+),(?P<chr>\d+),(?P<lang>\d+),'
                 r'(?P<x>[-\d.]+)f,(?P<y>[-\d.]+)f,(?P<x2>[^,]+),(?P<y2>[^,]+),(?P<w>\d+),(?P<h>\d+),(?P<px>px\d+),'
                 r'(?P<reward>\d+),(?P<step>\d+),(?P<ax>[-\d.]+)f,(?P<ay>[-\d.]+)f,(?P<tail>.*)\}, /\* (?P<text>.*) \*/$')


# ---- room masks on the canvas grid -------------------------------------------------------------------------------------
class Mask:
    """Cells (x, y) of one room: cell centre inside the shape. Bounding box, distance to the edge, integral image."""

    def __init__(self, shape):
        x0, y0, x1, y1 = shape.bounds()
        self.x0, self.y0 = max(0, int(x0) - 1), max(0, int(y0) - 1)
        self.x1, self.y1 = min(CANVAS[0], int(math.ceil(x1)) + 1), min(CANVAS[1], int(math.ceil(y1)) + 1)
        self.cells = set()
        for y in range(self.y0, self.y1):
            for x in range(self.x0, self.x1):
                if shape.contains(x + .5, y + .5):
                    self.cells.add((x, y))
        self.width = (max(x for x, _ in self.cells) - min(x for x, _ in self.cells) + 1) if self.cells else 0
        self._integral()
        self._distance()

    def _integral(self):
        w, h = self.x1 - self.x0 + 1, self.y1 - self.y0 + 1
        s = [[0] * (w + 1) for _ in range(h + 1)]
        for j in range(h):
            row = 0
            for i in range(w):
                row += (self.x0 + i, self.y0 + j) in self.cells
                s[j + 1][i + 1] = s[j][i + 1] + row
        self.sum = s

    def covered(self, l, t, r, b):
        """Cells of the box [l, r) x [t, b) inside the room (integer bounds, clipped)."""
        l, t = max(l, self.x0), max(t, self.y0)
        r, b = min(r, self.x1), min(b, self.y1)
        if r <= l or b <= t:
            return 0
        i0, j0, i1, j1 = l - self.x0, t - self.y0, r - self.x0, b - self.y0
        return self.sum[j1][i1] - self.sum[j0][i1] - self.sum[j1][i0] + self.sum[j0][i0]

    def _distance(self):
        """Chamfer (3-4) distance to the nearest cell outside, in cells."""
        inf = 1 << 30
        d = {c: inf for c in self.cells}
        for c in self.cells:
            x, y = c
            if any((x + dx, y + dy) not in self.cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                d[c] = 3
        order = sorted(self.cells, key=lambda c: (c[1], c[0]))
        for passes in (order, order[::-1]):
            sign = 1 if passes is order else -1
            for x, y in passes:
                for dx, dy, cost in ((-1, 0, 3), (0, -1, 3), (-1, -1, 4), (1, -1, 4)):
                    n = (x + sign * dx, y + sign * dy)
                    if n in d and d[n] + cost < d[(x, y)]:
                        d[(x, y)] = d[n] + cost
        self.dist = {c: v / 3 for c, v in d.items()}
        if self.cells:
            cx = sum(x for x, _ in self.cells) / len(self.cells)
            cy = sum(y for _, y in self.cells) / len(self.cells)
            best = max(self.dist.values())
            self.pole = min((c for c, v in self.dist.items() if v == best), key=lambda c: ((c[0] + .5 - cx) ** 2 + (c[1] + .5 - cy) ** 2, c))
            self.depth = best

    def edges(self):
        return sorted(c for c in self.cells if any((c[0] + dx, c[1] + dy) not in self.cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))))


# ---- text ------------------------------------------------------------------------------------------------------------
def text_size(lines, px):
    f = font(px)
    boxes = [f.getbbox(line, stroke_width=STROKE) for line in lines]
    return max(b[2] - b[0] for b in boxes), sum(b[3] - b[1] for b in boxes) + LINE_GAP * (len(lines) - 1)


def wrap(text, room_width, px):
    """One line unless wider than 150% of the room and there is a space: then at the space nearest the middle."""
    w, _ = text_size([text], px)
    if w / RASTER <= WRAP * room_width or ' ' not in text:
        return [text]
    middle = len(text) / 2
    at = min((i for i, c in enumerate(text) if c == ' '), key=lambda i: (abs(i - middle), i))
    return [text[:at], text[at + 1:]]


def box_size(lines, px):
    w, h = text_size(lines, px)
    return math.ceil((w + 2) / RASTER), math.ceil((h + 2) / RASTER)


# ---- layout ----------------------------------------------------------------------------------------------------------
def hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def exclusive_pairs(data):
    pairs = {(int(a), int(b)) for a, b in re.findall(r'\{(\d+),(\d+)\}', (ROOT / 'src/section_rules.h').read_text())}
    pairs |= {(b, a) for a, b in pairs}
    by_pos = {}
    for r in data['rooms']:
        by_pos.setdefault((r['area'], r['floor'], tuple(r['map'])), []).append(r['room'])
    for rooms in by_pos.values():
        pairs |= {(a, b) for a in rooms for b in rooms if a != b}
    return pairs


def place_floor(names, masks, union, exclusive):
    """names: dicts with room, lines, box size; placed in order. Fills box, anchor, leader."""
    placed = []

    def free(box, room):
        return all(not hit(box, p['box']) or (room, p['room']) in exclusive for p in placed)

    for n in sorted(names, key=lambda n: (len(masks[n['room']].cells), n['room'])):
        m, (bw, bh) = masks[n['room']], n['size']
        px, py = m.pole

        def box_at(cx, cy):
            l, t = int(round(cx - bw / 2)), int(round(cy - bh / 2))
            return (l, t, l + bw, t + bh)

        def coverage(box):
            return m.covered(*box) / (bw * bh)

        ideal = box_at(px + .5, py + .5)
        narrow = 2 * m.depth < 2 * bh and coverage(ideal) < .5
        def inside():
            found = []
            for x, y in m.cells:
                b = box_at(x + .5, y + .5)
                if b[0] >= 0 and b[1] >= 0 and b[2] <= CANVAS[0] and b[3] <= CANVAS[1] and free(b, n['room']):
                    found.append((coverage(b), (x, y), b))
            if not found:
                return None
            best = max(c for c, _, _ in found)
            ok = [(c, cell, b) for c, cell, b in found if c >= best - .05 or c == 1]
            c, cell, b = min(ok, key=lambda t: ((t[1][0] - px) ** 2 + (t[1][1] - py) ** 2, t[1]))
            return {'box': b, 'anchor': (cell[0] + .5, cell[1] + .5), 'leader': None, 'coverage': c}

        # a corridor takes a leader; a room with no free place inside tries one too. A narrow room that no leader can leave
        # (enclosed by other rooms) keeps its name inside, over its neighbours, as long as it covers no other name.
        place = (None if narrow else inside()) or leader(n, m, union, masks, placed, exclusive) or (inside() if narrow else None)
        if place:
            n.update(place)
        else:  # check() stops the build
            b = box_at(px + .5, py + .5)
            n.update(box=b, anchor=(px + .5, py + .5), leader=None, coverage=coverage(b), failed=True)
        placed.append(n)


def leader(n, m, union, masks, placed, exclusive):
    bw, bh = n['size']
    near_other = set()
    for r, other in masks.items():
        if r != n['room']:
            for x, y in other.cells:
                near_other.update((x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    best = None
    for ex, ey in m.edges():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (ex + dx, ey + dy) in m.cells:
                continue
            path = []
            for step in range(1, LEADER_MAX + 1):
                c = (ex + dx * step, ey + dy * step)
                if c in union or c in near_other or not (0 <= c[0] < CANVAS[0] and 0 <= c[1] < CANVAS[1]):
                    break
                path.append(c)
                if step < LEADER_MIN or (best and step >= best[0]):
                    continue
                qx, qy = c[0] + .5 + dx * .5, c[1] + .5 + dy * .5  # the far edge of the last cell
                if dx:
                    l = int(round(qx)) if dx > 0 else int(round(qx)) - bw
                    t = int(round(qy - bh / 2))
                else:
                    l = int(round(qx - bw / 2))
                    t = int(round(qy)) if dy > 0 else int(round(qy)) - bh
                box = (l, t, l + bw, t + bh)
                if box[0] < 0 or box[1] < 0 or box[2] > CANVAS[0] or box[3] > CANVAS[1]:
                    continue
                if any((x, y) in union for x in range(box[0], box[2]) for y in range(box[1], box[3])):
                    continue
                line = (min(ex, c[0]), min(ey, c[1]), max(ex, c[0]) + 1, max(ey, c[1]) + 1)
                if any((hit(box, p['box']) or hit(line, p['box'])) and (n['room'], p['room']) not in exclusive for p in placed):
                    continue
                pole = (ex - m.pole[0]) ** 2 + (ey - m.pole[1]) ** 2
                key = (step, pole, ex, ey, dx, dy)
                if not best or key < best:
                    best = key + (box, (ex + .5, ey + .5), (qx, qy))
    if not best:
        return None
    return {'box': best[6], 'anchor': best[7], 'leader': [best[7], best[8]], 'coverage': 0.0}


# ---- check (independent of the search) --------------------------------------------------------------------------------
def check(layout, shapes, exclusive):
    errors = []
    for n in layout:
        tag = '%s room %d (%s)' % (n['lang'], n['room'], ' / '.join(n['lines']))
        b, (ax, ay), s = n['box'], n['anchor'], shapes[n['room']]
        if n.get('failed'):
            errors.append(tag + ': no free place')
        if b[0] < 0 or b[1] < 0 or b[2] > CANVAS[0] or b[3] > CANVAS[1]:
            errors.append(tag + ': off the canvas')
        if not s.contains(ax, ay):
            errors.append(tag + ': anchor outside its room')
        if n['leader']:
            (x0, y0), (x1, y1) = n['leader']
            length = abs(x1 - x0) + abs(y1 - y0)
            if (x0 != x1 and y0 != y1) or length > LEADER_MAX + 1:
                errors.append(tag + ': leader not axis-aligned or too long (%.1f)' % length)
            for r, other in shapes.items():
                if (other.area, other.floor) == (s.area, s.floor):
                    if any(other.contains(x + .5, y + .5) for x in range(b[0], b[2]) for y in range(b[1], b[3])):
                        errors.append(tag + ': outside name on room %d' % r)
                        break
        for o in layout:
            if o is n or (o['area'], o['floor'], o['lang']) != (n['area'], n['floor'], n['lang']) or (n['room'], o['room']) in exclusive:
                continue
            if o['room'] > n['room'] and hit(b, o['box']):
                errors.append(tag + ': overlaps room %d' % o['room'])
            if n['leader']:
                (x0, y0), (x1, y1) = n['leader']
                line = (min(x0, x1), min(y0, y1), max(x0, x1) + .01, max(y0, y1) + .01)
                if hit(line, o['box']):
                    errors.append(tag + ': leader crosses room %d' % o['room'])
    return errors


# ---- rasters ---------------------------------------------------------------------------------------------------------
def raster(n):
    """Text box plus leader on one canvas (raster px); returns the image and the anchor inside it."""
    px = SIZE[n['lang_id']]
    b = n['box']
    pts = [b[0], b[1], b[2], b[3]]
    if n['leader']:
        (x0, y0), (x1, y1) = n['leader']
        pts = [min(pts[0], x0, x1), min(pts[1], y0, y1), max(pts[2], x0, x1), max(pts[3], y0, y1)]
    m = LEADER_RADIUS + 1
    ox, oy = pts[0] * RASTER - m, pts[1] * RASTER - m
    w, h = int(math.ceil(pts[2] * RASTER - ox + m)), int(math.ceil(pts[3] * RASTER - oy + m))
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    if n['leader']:
        (x0, y0), (x1, y1) = [(x * RASTER - ox, y * RASTER - oy) for x, y in n['leader']]
        steps = int(max(abs(x1 - x0), abs(y1 - y0)))
        line = [(round(x0 + (x1 - x0) * i / steps), round(y0 + (y1 - y0) * i / steps)) for i in range(steps + 1)]
        for radius, fill in ((LEADER_RADIUS, LEADER_EDGE), (LEADER_RADIUS - 1, LEADER_FILL)):
            for x, y in line:
                d.rectangle((x - radius, y - radius, x + radius, y + radius), fill=fill)
    f = font(px)
    tw, th = text_size(n['lines'], px)
    cx, cy = (b[0] + b[2]) / 2 * RASTER - ox, (b[1] + b[3]) / 2 * RASTER - oy
    y = cy - th / 2
    for line in n['lines']:
        l, t, r, bb = f.getbbox(line, stroke_width=STROKE)
        d.text((round(cx - (r - l) / 2 - l), round(y - t)), line, font=f, fill=COLOUR + (255,), stroke_width=STROKE,
               stroke_fill=OUTLINE + (255,))
        y += bb - t + LINE_GAP
    ax, ay = n['anchor'][0] * RASTER - ox, n['anchor'][1] * RASTER - oy
    return im, ax, ay


# ---- driver ----------------------------------------------------------------------------------------------------------
def read_rows(text):
    rows = []
    for i, line in enumerate(text.split('\n')):
        m = ROW.match(line)
        if m and int(m['flag']) < 900:  # 900+: refill tanks drawn as icons
            rows.append((i, m))
    return rows


def layout(rows, data):
    shapes = room_geometry.shapes(data)
    masks, exclusive = {}, exclusive_pairs(data)
    rows = [(i, m) for i, m in rows if int(m['room']) in shapes]  # area-5 lifts (37, 142, 150): no map shape, never drawn on a map
    for _, m in rows:
        r = int(m['room'])
        if r not in masks:
            masks[r] = Mask(shapes[r])
    names = []
    for i, m in rows:
        r, lang = int(m['room']), int(m['lang'])
        text = ' '.join(m['text'].split(' / '))
        lines = wrap(text, masks[r].width, SIZE[lang])
        names.append({'row': i, 'room': r, 'area': int(m['area']), 'floor': int(m['floor']), 'lang_id': lang,
                      'lang': 'ko' if lang == 1 else 'en', 'text': text, 'lines': lines, 'size': box_size(lines, SIZE[lang])})
    floors = {}
    for n in names:
        floors.setdefault((n['area'], n['floor'], n['lang']), []).append(n)
    for key in sorted(floors):
        rooms = {n['room'] for n in floors[key]}
        floor_masks = {r: masks[r] for r in masks if (shapes[r].area, shapes[r].floor) == key[:2]}
        union = set().union(*(fm.cells for fm in floor_masks.values()))
        place_floor(floors[key], {r: masks[r] for r in rooms} | floor_masks, union, exclusive)
    return names, shapes, exclusive


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check-only', action='store_true')
    a = ap.parse_args()
    path = ROOT / 'src/labels.h'
    text = path.read_text(encoding='utf-8')
    data = room_geometry.load()
    rows = read_rows(text)
    names, shapes, exclusive = layout(rows, data)
    errors = check(names, shapes, exclusive)
    if errors:
        raise SystemExit('room-name layout check failed:\n' + '\n'.join(errors))
    if a.check_only:
        print('check passed: %d names' % len(names))
        return
    lines = text.split('\n')
    arrays = {}
    for n in names:
        m = ROW.match(lines[n['row']])
        im, ax, ay = raster(n)
        arrays[m['px']] = ','.join(map(str, im.tobytes()))
        lines[n['row']] = ('{0,%s,%s,%s,%s,%s,%s,%s,%.2ff,%.2ff,%s,%s,%d,%d,%s,%s,%s,%.2ff,%.2ff,%s}, /* %s */' % (
            m['room'], m['room2'], m['area'], m['floor'], m['flag'], m['chr'], m['lang'], n['anchor'][0], n['anchor'][1], m['x2'], m['y2'],
            im.width, im.height, m['px'], m['reward'], m['step'], ax, ay, m['tail'], ' / '.join(n['lines'])))
    text = '\n'.join(lines)
    text = re.sub(r'(static const unsigned char (px\d+)\[\]=\{)[^}]*(\};)', lambda g: g[1] + arrays[g[2]] + g[3] if g[2] in arrays else g[0], text)
    path.write_text(text, encoding='utf-8')
    out = [{'room': n['room'], 'lang': n['lang'], 'lines': n['lines'], 'anchor': [round(v, 2) for v in n['anchor']],
            'box': list(n['box']), 'leader': n['leader'], 'coverage': round(n['coverage'], 3)} for n in sorted(names, key=lambda n: n['row'])]
    (ROOT / 'data/room_names.json').write_text(json.dumps({'_note': 'tools/layout_room_names.py output; canvas units (1280x720).',
                                                           'leader_max': LEADER_MAX, 'names': out}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('%d names placed, %d with leaders' % (len(names), sum(1 for n in names if n['leader'])))


if __name__ == '__main__':
    main()
