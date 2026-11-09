"""Story-event marks (kind 6) from a decrypted bhd.exe analysis image and the game's scene archives, read only.

    python tools/build_events.py <bhd analysis image> <nativePC/arc/event dir>

Writes data/story-events.json, src/event_marks.h and docs/story-events.md. Needs capstone (analysis only, not a build input).

How a scene is found (bhd.exe, 2026-11-08):
  * 0x6af460(scene no, ...) is the only caller of 0x480b40, which creates uBhdEventScheduler (DTI 0xcf34dc) with the number at
    +0x60; the scheduler (0x507840) loads arc\\event\\e<stage><room>_<no> for the current room. Each call site's room is the
    uEventR<room> class whose factory precedes it in the code (call numbers match the archive files of that room exactly).
  * Done-flag: the flag-set calls (0x4919a0 bank, bit) in the same function between the previous scene call and this one, else
    up to the next scene call; a flag the function also tests (0x4916a0) wins. Bank 0 (256 bits, flag base +4) is the story bank:
    its bits are set in one room and tested in others (e.g. bit 0x25: set in 409/315, tested by the stage 5 rooms).
  * Character: the archive's ep models; ep00 Chris / ep03 Rebecca are his side, ep01 Jill / ep02 Barry hers; both or neither = both.
  * Weight: every placed scene has character models and voice (sound\\event); scenes without characters are skipped.
Position: the room anchor (the scene's trigger area is not tied to the call), spread inside the room shape off the room name."""
from pathlib import Path
import json
import math
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import room_geometry as rg  # noqa: E402

BASE = 0x400000
ROOMS_TABLE = 0xcc8e00  # EXE_ROOMS + module base: 154 records x 96 bytes (map x, y, offset x, y, scale x, z)
SET, CLR, TST, PLAY = 0x4919a0, 0x491870, 0x4916a0, 0x6af460
BOSS = {'40c': 'entering starts the Plant 42 fight (boss room rule)', '210': 'entering the Attic starts the Yawn fight (boss room rule)'}
STORY_BANK = 4  # hide_bank value of bank 0 (banks 1-3 keep their numbers)
SPREAD = 16.0   # canvas px between the marks of one room


class Image:
    def __init__(self, path):
        from capstone import Cs, CS_ARCH_X86, CS_MODE_32
        self.b = Path(path).read_bytes()
        pe = struct.unpack_from('<I', self.b, 60)[0]
        opt = pe + 24
        self.secs = []
        for i in range(struct.unpack_from('<H', self.b, pe + 6)[0]):
            o = opt + struct.unpack_from('<H', self.b, pe + 20)[0] + i * 40
            _n, vs, va, _sz, raw = struct.unpack_from('<8sIIII', self.b, o)
            self.secs.append((va, vs, raw))
        self.md = Cs(CS_ARCH_X86, CS_MODE_32)

    def off(self, a):
        for rva, size, raw in self.secs:
            if rva <= a - BASE < rva + size:
                return a - BASE - rva + raw
        raise ValueError(hex(a))

    def va(self, o):
        for rva, size, raw in self.secs:
            if raw <= o < raw + size:
                return BASE + rva + o - raw
        return None

    def ptr_refs(self, value):
        p, out, i = struct.pack('<I', value), [], 0
        while (i := self.b.find(p, i)) >= 0:
            if (a := self.va(i)) is not None:
                out.append(a)
            i += 1
        return out

    def calls_to(self, target):
        s = self.off(0x401000)
        out, i = [], s
        while (i := self.b.find(b'\xe8', i, s + 0x818000)) >= 0:
            a = self.va(i)
            if (a + 5 + struct.unpack_from('<i', self.b, i + 1)[0]) & 0xffffffff == target:
                out.append(a)
            i += 1
        return out

    def dis(self, a, n):
        return list(self.md.disasm(self.b[self.off(a):self.off(a) + n], a))

    def function(self, a):
        """The int3-padded function around a."""
        o = self.off(a)
        while not (self.b[o - 1] == 0xcc and self.b[o - 2] == 0xcc):
            o -= 1
        e = self.off(a)
        while self.b[e:e + 3] != b'\xcc\xcc\xcc':
            e += 1
        return self.va(o), self.va(e)

    def flag_ops(self, s, e):
        """[(address, op, bank, bit|scene)] of the flag and scene calls between s and e; None where not an immediate."""
        names, out, prev = {SET: 'SET', CLR: 'CLR', TST: 'TST', PLAY: 'PLAY'}, [], []
        for i in self.dis(s, e - s):
            if i.mnemonic == 'call' and i.op_str.startswith('0x') and int(i.op_str, 16) in names:
                ps = [imm(x.op_str) for x in prev if x.mnemonic == 'push']
                op = names[int(i.op_str, 16)]
                out.append((i.address, op, ps[-1] if ps else None, ps[-2] if len(ps) > 1 and op != 'PLAY' else None))
                prev = []
            else:
                prev = [] if i.mnemonic == 'call' else (prev + [i])[-8:]
        return out


def imm(s):
    try:
        return int(s, 0)
    except ValueError:
        return None


def room_classes(img):
    """[(factory address, room id)] of the uEventR<room> classes, in code order."""
    out = []
    for m in re.finditer(rb'uEventR([0-9a-f]{3})\0', img.b):
        name = img.va(m.start())
        refs = [a for a in img.ptr_refs(name) if a < 0xc00000] if name else []
        if not refs:
            continue
        for i in img.dis(refs[0] - 1, 0x30):
            mm = re.match(r'dword ptr \[(0x[0-9a-f]+)\], (0x[0-9a-f]+)$', i.op_str)
            if i.mnemonic == 'mov' and mm:
                factory = struct.unpack_from('<I', img.b, img.off(int(mm.group(2), 16) + 4))[0]
                out.append((factory, m.group(1).decode()))
                break
    return sorted(out)


def archive(path):
    d = path.read_bytes()
    n = struct.unpack_from('<H', d, 6)[0]
    names = [d[8 + i * 80:8 + i * 80 + 64].split(b'\0')[0].decode('latin1') for i in range(n)]
    eps = sorted({m.group(1) for x in names if (m := re.search(r'\\ep(\d\d)$', x))})
    return eps, any(x.startswith('sound\\event') for x in names), len(d)


def character(eps):
    chris, jill = bool({'00', '03'} & set(eps)), bool({'01', '02'} & set(eps))
    return 'chris' if chris and not jill else 'jill' if jill and not chris else 'both'


def scenes(img, event_dir):
    classes = room_classes(img)
    for site in img.calls_to(PLAY):
        room = max((c for c in classes if c[0] <= site), default=(0, None))[1]
        s, e = img.function(site)
        ops = img.flag_ops(s, e)
        k = [o[0] for o in ops].index(site)
        no = ops[k][2]
        last = max((j for j in range(k) if ops[j][1] == 'PLAY'), default=-1)
        nxt = min((j for j in range(k + 1, len(ops)) if ops[j][1] == 'PLAY'), default=len(ops))
        flags = lambda r: [(o[2], o[3]) for o in ops[r] if o[1] == 'SET' and o[2] is not None and o[3] is not None and o[2] < 4]
        tested = {(o[2], o[3]) for o in ops if o[1] == 'TST'}
        f = Path(event_dir) / ('e%s_%02d.arc' % (room, no)) if no is not None else None
        eps, voice, size = archive(f) if f and f.exists() else ([], False, 0)
        yield dict(room=room, site=hex(site), scene=no, before=flags(slice(last + 1, k)), after=flags(slice(k + 1, nxt)),
                   tested=tested, eps=eps, voice=voice, size=size)


def pick(found, rooms):
    placed, skipped = {}, []
    for x in found:
        r = rooms[x['room']]
        base = dict(room=x['room'], ko=r['name_ko'], en=r['external_name'].split(' - ')[-1], site=x['site'], scene=x['scene'])
        before, after = x['before'], x['after']
        pref = [f for f in before + after if f in x['tested']]
        flag = pref[-1] if pref and pref[-1] in before else pref[0] if pref else before[-1] if before else after[0] if after else None
        # r405 scene 1 sets b0[133] at 0x64a000; init tests it at 0x4c0ced.
        if x['site'] == '0x649fa4':
            flag = (0, 133)
        reason = ('scene number computed at run time' if x['scene'] is None else BOSS.get(x['room']) or
                  ('no characters in the scene (camera/object only)' if not x['eps'] else None) or
                  (None if flag else 'the scene sets no flag, so it cannot be hidden once played'))
        if reason:
            skipped.append(dict(base, reason=reason))
            continue
        how = ('set before' if flag in before else 'set after') + ' the scene call' + (', also tested there' if flag in x['tested'] else '')
        # Cast includes the other protagonist; native r106 init selects these only for Chris.
        chr = 'chris' if x['room'] == '106' and flag in ((0, 1), (0, 4)) else character(x['eps'])
        key = (x['room'], flag, chr)
        if key in placed:
            placed[key]['scenes'].append(x['scene'])
            placed[key]['sites'].append(x['site'])
            continue
        placed[key] = dict(room=x['room'], section=r['native_index'], area=r['map_area'], floor=r['map_floor'], ko=r['name_ko'],
                           en=base['en'], bank=flag[0], bit=flag[1], chr=key[2], scenes=[x['scene']], sites=[x['site']],
                           evidence=how, eps=x['eps'], kb=x['size'] // 1024, voice=x['voice'])
    # a scene for both characters already covers a one-character scene with the same flag in that room
    marks = [m for k, m in placed.items() if k[2] == 'both' or (k[0], k[1], 'both') not in placed]
    return marks, skipped


def spots(img, marks):
    """Canvas points inside each room, nearest its middle, SPREAD apart and off its name boxes; world x, z through the room record."""
    shapes = rg.shapes()
    boxes = {}
    for n in json.loads((ROOT / 'data/room_names.json').read_text(encoding='utf-8'))['names']:
        boxes.setdefault(n['room'], []).append(n['box'])
    taken = {}
    for m in marks:
        sh, sec = shapes[m['section']], m['section']
        x0, y0, x1, y1 = sh.bounds()
        pts = [(x0 + (i + .5) * 2, y0 + (j + .5) * 2) for i in range(int((x1 - x0) / 2)) for j in range(int((y1 - y0) / 2))]
        pts = [p for p in pts if sh.contains(*p) and sh.distance_outside(p[0] + 5, p[1]) == 0 and sh.distance_outside(p[0] - 5, p[1]) == 0
               and sh.distance_outside(p[0], p[1] + 5) == 0 and sh.distance_outside(p[0], p[1] - 5) == 0]
        free = [p for p in pts if not any(b[0] - 8 <= p[0] <= b[2] + 8 and b[1] - 8 <= p[1] <= b[3] + 8 for b in boxes.get(sec, []))] or pts
        cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        used = taken.setdefault(sec, [])
        best = min((p for p in free if all(math.dist(p, q) >= SPREAD for q in used)), key=lambda p: math.dist(p, (cx, cy)), default=None)
        best = best or min(free, key=lambda p: math.dist(p, (cx, cy)))
        used.append(best)
        r = struct.unpack_from('<4i2f', img.b, img.off(ROOMS_TABLE + 96 * sec))
        m['canvas'] = [round(best[0], 1), round(best[1], 1)]
        m['world'] = [round(((best[0] - 48) / .9 - r[0] - r[2]) / (r[4] * .015), 1), round(((best[1] - 36) / .9 - r[1] + r[3]) / (r[5] * .015), 1)]
        m['room_record'] = list(r)


def main():
    img = Image(sys.argv[1])
    rooms = {r['room_id']: r for r in json.loads((ROOT / 'data/rooms.json').read_text(encoding='utf-8'))}
    marks, skipped = pick(list(scenes(img, sys.argv[2])), rooms)
    spots(img, marks)
    for n, m in enumerate(marks):
        m['id'] = n  # internal only: event marks are drawn without a name
    (ROOT / 'data/story-events.json').write_text(json.dumps(dict(
        note='tools/build_events.py output (bhd.exe analysis image + nativePC/arc/event, 2026-11-08). bank 0-3 = flag bank; hide_bank in '
             'src/event_marks.h is 4 for bank 0.', events=marks, skipped=skipped), ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    cbits = {'both': 0, 'chris': 0x10, 'jill': 0x20}
    rows = ['/* Generated by tools/build_events.py from data/story-events.json: story scenes (kind 6), hidden once their flag is set.',
            ' * room, area, floor, flag, world x, z, file, kind, key visits, hide bank (4 = bank 0), hide bit, character (0x10 Chris, 0x20 Jill). */',
            '#define EVENT_MARK_COUNT %d' % len(marks), '#define EVENT_MARK_ROWS \\']
    for m in marks:
        rows.append('    {%d, %d, %d, 0, %.1ff, %.1ff, 255, 6, {0}, %d, %d, 0x%02x}, /* %s, scenes %s */ \\' % (
            m['section'], m['area'], m['floor'], m['world'][0], m['world'][1], m['bank'] or STORY_BANK, m['bit'], cbits[m['chr']],
            m['en'], ','.join(map(str, m['scenes']))))
    (ROOT / 'src/event_marks.h').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    md = ['# Story events (spoiler scenes)', '',
          'Generated from `data/story-events.json` (`tools/build_events.py`). Markers are the purple `?` of the [6] Events toggle (off by default). '
          'Position = the room anchor: the scene\'s trigger area is not tied to the scene call in the game code, so each mark sits inside its room, '
          'spread apart and off the room name. Done-flag `bank:bit` is set by the scene\'s own code; the mark is hidden once it is 1. '
          'Character: shown only in that character\'s game (from the scene\'s cast). Event marks have no name on the map (the ? diamond only); `id` is internal.', '',
          '| 방 / Room | 캐릭터 / Character | 장면 / Scenes | 완료 플래그 / Done-flag | 근거 / Evidence | id |', '|---|---|---|---|---|---|']
    for m in marks:
        md.append('| %s / %s | %s | e%s_%s (%s KB) | %d:%d | %s (%s) | %d |' % (
            m['ko'], m['en'], m['chr'], m['room'], ','.join('%02d' % s for s in m['scenes']), m['kb'], m['bank'], m['bit'],
            m['evidence'], ', '.join(m['sites']), m['id']))
    md += ['', '## Found but not placed', '', '| 방 / Room | 장면 / Scene | 호출 / Call | 이유 / Reason |', '|---|---|---|---|']
    for s in skipped:
        md.append('| %s / %s | %s | %s | %s |' % (s['ko'], s['en'], '-' if s['scene'] is None else 'e%s_%02d' % (s['room'], s['scene']), s['site'], s['reason']))
    (ROOT / 'docs/story-events.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(len(marks), 'marks,', len(skipped), 'skipped')


if __name__ == '__main__':
    main()
