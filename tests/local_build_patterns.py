"""Local only (needs game binaries, so not in tests/run.py): every builds[] entry in src/re1_mapnames.c against the
bytes of its bhd.exe build. Each byte pattern the mod checks before patching must hold at the table address.

Inputs (environment): RE1HD_TEXT_2026 / RE1HD_TEXT_2018 = decrypted .text (RVA 0x1000), RE1HD_EXE_2026 /
RE1HD_EXE_2018 = the bhd.exe files (header, .rdata/.data checks). A build without its .text is skipped."""
from pathlib import Path
import os, re, struct, sys
ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('stamp image name map_vtable rooms banks renderer inventory roomstate crimson pad_config gui msg_manager '
          'item_ctor spawn_core spawn_frame flag_test bank7 spawn_head flag_head bank7_ctx '
          'sprite pad_held pad_repeat pad_edge gui_hover gui_set_pos site_marker site_pad site_paper zoom hidden').split()
BASE, TEXT = 0x400000, 0x401000
CTOR = bytes([0x56, 0x68, 0xe8, 0x03, 0, 0, 0x6a, 0xff])

def table():
    s = (ROOT/'src/re1_mapnames.c').read_text(encoding='utf-8')
    body = s[s.index('static const Addr builds[2] = {') + 29:]
    body = body[:body.index('\n};') + 3].rstrip(';')
    body = re.sub(r'/\*.*?\*/', '', body, flags=re.S).replace('{', '[').replace('}', ']')
    return [dict(zip(FIELDS, row, strict=True)) for row in eval(body)]

def sections(exe):
    pe = struct.unpack_from('<I', exe, 0x3c)[0]
    n, opt = struct.unpack_from('<H', exe, pe + 6)[0], struct.unpack_from('<H', exe, pe + 20)[0]
    out = {}
    for i in range(n):
        o = pe + 24 + opt + 40 * i
        name = exe[o:o + 8].rstrip(b'\0').decode()
        vsize, va, rsize, raw = struct.unpack_from('<IIII', exe, o + 8)
        out[name] = (va, vsize, raw, rsize)
    return struct.unpack_from('<I', exe, pe + 8)[0], struct.unpack_from('<I', exe, pe + 24 + 56)[0], out

def check(b, t, exe):
    at = lambda va, n: t[va - TEXT:va - TEXT + n]
    call_to = lambda va: at(va, 1) == b'\xe8' and va + 5 + struct.unpack('<i', at(va + 1, 4))[0]
    assert at(BASE + b['item_ctor'], 8) == CTOR, 'item ctor'
    assert at(BASE + b['spawn_core'], 14) == bytes(b['spawn_head']) and b['spawn_frame'] == b['spawn_head'][8], 'spawn core'
    flag = BASE + b['flag_test']
    assert at(flag, 16) == bytes(b['flag_head']), 'flag test head'
    for r in b['bank7']:
        assert at(BASE + r - 8, 8) == bytes(b['bank7_ctx']) and call_to(BASE + r) == flag, hex(r)
    assert call_to(b['site_pad']) == b['pad_repeat'], 'pad site'
    sites = [b['site_marker'], b['site_paper'], *b['zoom'], *b['hidden']]
    assert len(set(sites)) == 39 and all(call_to(v) == b['sprite'] for v in sites), 'sprite sites'
    every = [i for i in range(len(t) - 5) if t[i] == 0xe8 and TEXT + i + 5 + struct.unpack_from('<i', t, i + 1)[0] == b['sprite']]
    assert sorted(TEXT + i for i in every) == sorted(sites), 'every sprite call is sorted'
    for f in ('sprite', 'pad_held', 'pad_repeat', 'pad_edge', 'gui_hover', 'gui_set_pos', 'flag_test'):
        v = b[f] if f != 'flag_test' else flag
        assert t[v - TEXT - 1] == 0xcc, f + ' is not a function start'
    if exe:
        stamp, image, sec = sections(exe)
        assert (stamp, image) == (b['stamp'], b['image']), 'PE header'
        va, vsize = sec['.text'][:2]
        def data(rva, n):
            for sva, svs, raw, rs in sec.values():
                if sva <= rva < sva + rs: return exe[raw + rva - sva:raw + rva - sva + n]
        r = struct.unpack('<24I', data(b['rooms'], 96))
        assert (r[0], r[1], r[7], r[22]) == (136, 353, 2, 54), 'room table'
        vt = struct.unpack('<10I', data(b['map_vtable'], 40))
        assert all(BASE + va <= v < BASE + va + vsize for v in vt), 'map vtable'

ran = 0
for b in table():
    text = os.environ.get('RE1HD_TEXT_' + b['name'])
    if not text or not Path(text).exists():
        print('skip', b['name'], '(no RE1HD_TEXT_%s)' % b['name']); continue
    exe = os.environ.get('RE1HD_EXE_' + b['name'])
    check(b, Path(text).read_bytes(), Path(exe).read_bytes() if exe and Path(exe).exists() else None)
    print('PASS', b['name'], '(with exe)' if exe else '(text only)'); ran += 1
sys.exit(0)
