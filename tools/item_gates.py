"""Print the item_gates C table for src/item_state.h from the game's per-room "all items taken" predicates.

Usage: python tools/item_gates.py IMAGE [--labels src/labels.h] > table.txt

IMAGE is an analysis memory image of a legally owned bhd.exe: a 16 MiB flat dump where file offset = VA - 0x400000.
It is never included in this repository. The labels table says which pickup flags belong to which room.

Needs capstone at runtime (pip install capstone). It is deliberately not in requirements.txt, because neither the
build nor the tests use this tool.

The C table goes to stdout and statistics go to stderr. Term simplification iterates over sets, so set
PYTHONHASHSEED=0 when comparing two runs: a different hash seed can give a different but equivalent set of terms.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import itertools
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x400000
FLAG_TEST = 0x4916a0  # call target of the flag test: push index; push bank; call
PREDICATE_LO, PREDICATE_HI = 0x481000, 0x486800  # int3-delimited predicate range
PICKUP_KINDS = (4, 5, 7)
ROW = re.compile(r'^\{(-?\d+),(-?\d+),(-?\d+),\d+,\d+,(\d+),')


def read_rows(path):
    """Label rows of src/labels.h as dicts with kind, room, room2 and flag."""
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = ROW.match(line)
            if m:
                kind, room, room2, flag = map(int, m.groups())
                rows.append(dict(kind=kind, room=room, room2=room2, flag=flag))
    if not rows:
        raise SystemExit(f'no label rows found in {path}')
    return rows


def source_room(row):
    return row['room2'] if row['room2'] >= 0 else row['room']


def predicate_starts(img):
    starts = []
    a = PREDICATE_LO - BASE
    while a < PREDICATE_HI - BASE:
        if img[a] == 0xCC and img[a + 1] != 0xCC:
            starts.append(a + 1 + BASE)
        a += 1
    return starts


def walk(img, md, flagrooms, start):
    """Follow every path of one predicate. Returns (room, item flags, paths per flag, unknowns, flag counts) or None."""
    out = defaultdict(set)
    flags = Counter()
    unk = set()
    budget = [30000]
    memo = set()

    # first pass: collect b3 flags reachable, ignoring gates
    def run(addr, path, pushes, cond, dreg, itemset, depth, seen):
        budget[0] -= 1
        if budget[0] < 0:
            unk.add('budget')
            return
        key = (addr, tuple(pushes), cond, dreg, frozenset(path))
        if key in memo:
            return
        memo.add(key)
        while True:
            if addr in seen and len(seen) > 2000:
                return
            ins = next(md.disasm(img[addr - BASE:addr - BASE + 16], addr), None)
            if ins is None:
                unk.add('bad')
                return
            m, o = ins.mnemonic, ins.op_str
            nxt = addr + ins.size
            if m == 'push':
                try:
                    pushes = pushes + [int(o, 0)]
                except ValueError:
                    pushes = pushes + [None]
            elif m == 'call':
                t = None
                try:
                    t = int(o, 0)
                except ValueError:
                    pass
                if t == FLAG_TEST and len(pushes) >= 2 and pushes[-1] is not None and pushes[-2] is not None:
                    cond = ('F', pushes[-1], pushes[-2])
                    pushes = []
                    if cond[1] == 3:
                        flags[cond[2]] += 1
                        if itemset is not None and cond[2] in itemset:
                            out[cond[2]].add(tuple(path))
                else:
                    cond = ('X', o)
                    pushes = []
                    unk.add('call ' + o)
            elif m == 'cmp' and '0x5110' in o:
                imm = int(o.split(',')[1], 0)
                cond = ('C', imm)
            elif m == 'mov' and o.endswith('+ 0x24]'):
                dreg = o.split(',')[0]
            elif m == 'test' and dreg and o == f'{dreg}, {dreg}':
                cond = ('D', 0)
            elif m == 'cmp' and dreg and o.startswith(dreg + ','):
                cond = ('D', int(o.split(',')[1], 0))
            elif m in ('ret', 'int3'):
                return
            elif m == 'jmp':
                try:
                    addr = int(o, 0)
                    continue
                except ValueError:
                    unk.add('jmpind')
                    return
            elif m in ('je', 'jne'):
                t = int(o, 0)
                eq_target = t if m == 'je' else nxt
                ne_target = nxt if m == 'je' else t
                if cond is None:
                    unk.add('jcc?' + hex(addr))
                if cond and cond[0] == 'F':
                    if itemset is not None and cond[1] == 3 and cond[2] in itemset:
                        addr = ne_target  # taken assumed
                        cond = None
                        continue
                    run(ne_target, path + [('F', cond[1], cond[2], 1)], pushes, None, dreg, itemset, depth + 1, seen)
                    addr = eq_target
                    path = path + [('F', cond[1], cond[2], 0)]
                    cond = None
                    continue
                if cond and cond[0] in 'CD':
                    run(eq_target, path + [(cond[0], cond[1], 1)], pushes, None, dreg, itemset, depth + 1, seen)
                    addr = ne_target
                    path = path + [(cond[0], cond[1], 0)]
                    cond = None
                    continue
                if cond and cond[0] == 'X':
                    run(ne_target, path + [('X', cond[1], 1)], pushes, None, dreg, itemset, depth + 1, seen)
                    addr = eq_target
                    path = path + [('X', cond[1], 0)]
                    cond = None
                    continue
                run(t, path, pushes, None, dreg, itemset, depth + 1, seen)
                addr = nxt
                continue
            elif m.startswith('j'):
                unk.add(m + '@' + hex(addr))
                try:
                    run(int(o, 0), path, pushes, None, dreg, itemset, depth + 1, seen)
                except Exception:  # also drops a path that hit the recursion limit
                    pass
            addr = nxt

    end = start
    while img[end - BASE] != 0xCC or img[end - BASE + 1] != 0xCC:
        end += 1
        if end - start > 0x1800:
            break
    stack = []
    for ins in md.disasm(img[start - BASE:end - BASE], start):
        if ins.mnemonic == 'push':
            try:
                stack.append(int(ins.op_str, 0))
            except ValueError:
                stack.append(None)
        elif ins.mnemonic == 'call':
            try:
                if int(ins.op_str, 0) == FLAG_TEST and len(stack) >= 2 and stack[-1] == 3 and stack[-2] is not None:
                    flags[stack[-2]] += 1
            except ValueError:
                pass
            stack = []
    if not flags:
        return None
    room = Counter()
    for f in flags:
        for s in flagrooms.get(f, ()):
            room[s] += 1
    if not room:
        return None
    best = room.most_common(1)[0][0]
    iset = {f for f in flags if best in flagrooms.get(f, ())}
    run(start, [], [], None, None, iset, 0, set())
    return best, iset, out, unk, flags


def char_of(lit):
    if lit[0] != 'C':
        return None
    k, v = lit[1], lit[2]
    return 'chris' if (k == 0) == (v == 1) else 'jill'


def reduce_terms(terms):
    terms = {frozenset(t) for t in terms}
    changed = True
    while changed:
        changed = False
        for a, b in itertools.combinations(list(terms), 2):
            d = a ^ b
            if len(d) == 2:
                x, y = list(d)
                if x[:-1] == y[:-1] and x[-1] != y[-1]:
                    terms.discard(a)
                    terms.discard(b)
                    terms.add(a & b)
                    changed = True
                    break
        if changed:
            continue
        for a, b in itertools.permutations(list(terms), 2):
            if a < b:
                terms.discard(b)
                changed = True
                break
    return terms


def conditions(paths):
    """Paths of one flag -> reduced terms per character; None means no path reaches it."""
    result = {}
    for who in ('chris', 'jill'):
        ts = []
        for p in paths:
            bad = False
            lits = set()
            for lit in p:
                if lit[0] == 'C':
                    if char_of(lit) != who:
                        bad = True
                        break
                elif lit[0] == 'D':
                    continue
                else:
                    lits.add(lit)
            if bad:
                continue
            if any((lit[:-1] + (1 - lit[-1],)) in lits for lit in lits if isinstance(lit[-1], int)):
                continue  # contradiction
            ts.append(lits)
        result[who] = reduce_terms(ts) if ts else None
    return result


def analyse(img, md, rows):
    """Run all predicates; returns {(room, flag): per-character terms}."""
    flagrooms = defaultdict(set)
    for r in rows:
        if r['kind'] in PICKUP_KINDS:
            flagrooms[r['flag']].add(source_room(r))
    results = {}
    starts = predicate_starts(img)
    for s in starts:
        try:
            x = walk(img, md, flagrooms, s)
        except Exception as e:
            print('ERR', hex(s), e, file=sys.stderr)
            continue
        if x:
            results[s] = x
    rooms = {v[0] for v in results.values()}
    print(f'{len(starts)} functions, {len(results)} with item flags; rooms {len(rooms)}', file=sys.stderr)
    table = {}
    for room, iset, out, _unk, _flags in results.values():
        for f, paths in out.items():
            table[(room, f)] = conditions(paths)
        for f in iset - set(out):
            table[(room, f)] = {'chris': None, 'jill': None}
    return table


def gate_rows(table, rows):
    """Table -> [(room, flag, jill, sorted literal terms)], only for flags that have a pickup row in that room."""
    keys = {(source_room(r), r['flag']) for r in rows if r['kind'] in PICKUP_KINDS}
    out = []
    for (room, flag), c in sorted(table.items()):
        if (room, flag) not in keys:
            continue
        for jill, who in ((0, 'chris'), (1, 'jill')):
            t = c[who]
            if t is None:
                continue
            ts = reduce_terms([frozenset(lit for lit in x if lit[0] == 'F') for x in t])
            if not ts or frozenset() in ts:
                continue
            lits = [sorted((lit[1] << 10 | lit[2] << 1 | lit[3]) | 0x8000 for lit in x) for x in ts]
            lits.sort()
            out.append((room, flag, jill, lits))
    return out


def format_table(gates):
    max_terms = max((len(g[3]) for g in gates), default=0)
    max_lits = max((len(term) for g in gates for term in g[3]), default=0)
    print(f'{len(gates)} gates, max terms {max_terms} max lits {max_lits}', file=sys.stderr)
    lines = ['/* Generated from the native per-room "all items taken" predicates (0x4830b0.. range; tools/item_gates.py).',
             ' * A listed pickup can only exist when one term holds; literal = 0x8000 | bank<<10 | index<<1 | wanted value. */',
             f'#define GATE_TERMS {max_terms}', f'#define GATE_LITS {max_lits}',
             'typedef struct { unsigned short room, flag, jill, term[GATE_TERMS][GATE_LITS]; } ItemGate;',
             'static const ItemGate item_gates[] = {']
    for room, flag, jill, lits in gates:
        terms = ','.join('{' + ','.join(hex(x) for x in t) + '}' for t in lits)
        lines.append('    {%d,%d,%d,{%s}},' % (room, flag, jill, terms))
    lines.append('};')
    return '\n'.join(lines) + '\n'


def main():
    p = argparse.ArgumentParser(description='Print the item_gates C table from an analysis memory image.')
    p.add_argument('image', type=Path, help='16 MiB flat memory image; file offset = VA - 0x400000')
    p.add_argument('--labels', type=Path, default=ROOT / 'src/labels.h', help='labels table (default: src/labels.h)')
    args = p.parse_args()
    try:
        from capstone import Cs, CS_ARCH_X86, CS_MODE_32
    except ImportError:
        raise SystemExit('capstone is required: pip install capstone')
    img = args.image.read_bytes()
    if len(img) < PREDICATE_HI - BASE + 1:
        raise SystemExit(f'{args.image}: {len(img)} bytes does not cover the predicate range; expected a 16 MiB image')
    rows = read_rows(args.labels)
    sys.stdout.write(format_table(gate_rows(analyse(img, Cs(CS_ARCH_X86, CS_MODE_32), rows), rows)))


if __name__ == '__main__':
    main()
