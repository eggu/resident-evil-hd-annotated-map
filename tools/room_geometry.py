"""Room shapes of data/room_shapes.json in canvas units (game pixels at 1280x720, the space of src/labels.h)."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def load(path=ROOT / 'data/room_shapes.json'):
    return json.loads(Path(path).read_text(encoding='utf-8'))


class Shape:
    """One room: texel runs placed on the canvas by the transform. Canvas = origin + gui_scale * (map + texel * texel_scale)."""

    def __init__(self, room, transform, perturb=(0, 0, 1, 1)):
        self.room, self.area, self.floor = room['room'], room['area'], room['floor']
        self.runs = room.get('runs', [])
        ox, oy = transform['origin']
        g = transform['gui_scale']
        tx, ty = transform['texel']
        dx, dy, fx, fy = perturb  # tests only: a wrong offset or scale must fail
        self.x0, self.y0 = ox + g * room['map'][0] + dx, oy + g * room['map'][1] + dy
        self.sx, self.sy = g * tx * fx, g * ty * fy
        self.w, self.h = room['rect'][2], room['rect'][3]

    def texel(self, x, y):
        return int((x - self.x0) // self.sx), int((y - self.y0) // self.sy)

    def contains(self, x, y):
        u, v = self.texel(x, y)
        if not (0 <= v < len(self.runs)):
            return False
        r = self.runs[v]
        return any(r[i] <= u < r[i + 1] for i in range(0, len(r), 2))

    def bounds(self):
        return self.x0, self.y0, self.x0 + self.w * self.sx, self.y0 + self.h * self.sy

    def distance_outside(self, x, y, limit=40.0, step=0.5):
        """0 inside, else the distance to the nearest inside point (searched on rings, up to limit)."""
        if self.contains(x, y):
            return 0.0
        r = step
        while r <= limit:
            n = max(8, int(r * 6))
            for i in range(n):
                import math
                a = 2 * math.pi * i / n
                if self.contains(x + r * math.cos(a), y + r * math.sin(a)):
                    return r
            r += step
        return float('inf')


def shapes(data=None, perturb=(0, 0, 1, 1)):
    data = data or load()
    return {r['room']: Shape(r, data['transform'], perturb) for r in data['rooms'] if r.get('runs')}
