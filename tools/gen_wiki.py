"""Generate the bilingual table pages of docs/wiki from committed data; no game files or network. Needs Pillow.

python tools/gen_wiki.py          write the table pages
python tools/gen_wiki.py --check  fail if a page is stale or a wiki rule is broken

01-native-map, 02-data-pipeline, 10-sources and README are written by hand and only checked here.
"""
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import re
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / 'docs/wiki'
ICONS = '../../assets/icons'
ROOM_COUNT = 154
FUEL_FLAGS = range(900, 905)
MARKS = '★◆◇□'
HAND_PAGES = ('README', '01-native-map', '02-data-pipeline', '10-sources')
# Page, Korean title, English title, marker groups it shows. Legend rows are UI text, not markers.
GROUPS = (
    ('03-rooms', '방 목록', 'Rooms', {'room'}),
    ('04-locks-keys', '잠긴 문과 열쇠', 'Locks and keys', {'lock'}),
    ('05-key-items', '핵심 아이템', 'Key items', {'key'}),
    ('06-puzzles-events', '퍼즐과 이벤트', 'Puzzles and events', {'puzzle', 'event', 'fuel'}),
    ('07-documents-maps', '문서와 지도', 'Documents and maps', {'document'}),
    ('08-common-items', '일반 아이템', 'Common items', {'common'}),
    ('09-save-points', '타자기와 아이템 상자', 'Typewriters and item boxes', set()),
    ('11-enemies', '적', 'Enemies', set()),
)
KIND_GROUP = {0: 'room', 1: 'lock', 2: 'puzzle', 3: 'event', 4: 'key', 5: 'document', 6: 'legend', 7: 'common'}
LOCAL_PATH = re.compile(r'/Users/|/home/|/tmp/|[A-Z]:\\')
ENEMY_NAMES = {
    'enemy-adder': ('독사', 'Adder'), 'enemy-cerberus': ('케르베로스', 'Cerberus'), 'enemy-chimera': ('키메라', 'Chimera'),
    'enemy-crimson-head': ('크림슨 헤드', 'Crimson Head'), 'enemy-crow': ('까마귀', 'Crow'), 'enemy-hunter': ('헌터', 'Hunter'),
    'enemy-lisa-trevor': ('리사 트레버', 'Lisa Trevor'), 'enemy-neptune': ('넵튠', 'Neptune'),
    'enemy-plant-42': ('플랜트 42', 'Plant 42'), 'enemy-tyrant': ('타이런트', 'Tyrant'), 'enemy-wasp': ('말벌', 'Wasp'),
    'enemy-web-spinner': ('웹 스피너', 'Web Spinner'), 'enemy-yawn': ('요운', 'Yawn'), 'enemy-zombie': ('좀비', 'Zombie'),
}
# Words for the hand-written rules of placed_item_available in src/item_state.h; key = (kind, flag, source room or None).
# {n} is filled per source room. main() fails if a rule is added to or removed from the header without updating this.
ALTERNATE_KO = '뱅크 0 플래그 98 켜짐 그리고 (뱅크 0 플래그 99 꺼짐 또는 뱅크 0 플래그 139 켜짐 또는 뱅크 1 플래그 9 켜짐)'
ALTERNATE_EN = 'bank 0 flag 98 set and (bank 0 flag 99 clear or bank 0 flag 139 set or bank 1 flag 9 set)'
HAND_RULES = {
    (1, 45, None): ('동료 사망 후 (크리스: 뱅크 0 플래그 34, 질: 뱅크 0 플래그 37)', "After the companion's death (Chris: bank 0 flag 34, Jill: bank 0 flag 37)"),
    (1, 47, None): ('동료 사망 후 (크리스: 뱅크 0 플래그 34, 질: 뱅크 0 플래그 37)', "After the companion's death (Chris: bank 0 flag 34, Jill: bank 0 flag 37)"),
    (2, 512, None): ('캡슐 충전 전, 삽입 전, 전원 공급 전', 'Capsule not charged or inserted, power not on'),
    (2, 513, None): ('캡슐 충전 후, 삽입 전, 전원 공급 전', 'Capsule charged, not inserted, power not on'),
    (2, 515, None): ('뱅크 1 플래그 110 꺼짐, 뱅크 3 플래그 207 꺼짐', 'Bank 1 flag 110 clear, bank 3 flag 207 clear'),
    (4, 69, 116): ('뱅크 1 플래그 62 켜짐', 'Bank 1 flag 62 set'),
    (4, 77, None): ('욕조 물을 뺀 뒤 (뱅크 1 플래그 37)', 'After the bathtub is drained (bank 1 flag 37)'),
    (4, 208, 22): ('표시 안 함 (사용된 거치대 아이템)', 'Never shown (spent rack item)'),
    (4, 320, None): ('뱅크 1 플래그 139 켜짐', 'Bank 1 flag 139 set'),
    (4, 392, 138): ('뱅크 1 플래그 205 또는 206 켜짐', 'Bank 1 flag 205 or 206 set'),
    (4, 393, 138): ('뱅크 1 플래그 207 또는 208 켜짐', 'Bank 1 flag 207 or 208 set'),
    (4, 405, None): ('동료 사망 후 (크리스: 뱅크 0 플래그 34, 질: 뱅크 0 플래그 37), 그리고 뱅크 1 플래그 216 켜짐', "After the companion's death (Chris: bank 0 flag 34, Jill: bank 0 flag 37) and bank 1 flag 216 set"),
    (4, 514, None): ('캡슐 삽입 후, 전원 공급 전', 'Capsule inserted, power not on'),
    (5, 482, None): ('크리스: 항상. 질: 뱅크 0 플래그 139 켜짐이고 대체 조건 거짓. 둘 중 하나를 얻으면 둘 다 사라짐', 'Chris: always. Jill: bank 0 flag 139 set and the alternate condition false. Both disappear once either is taken'),
    (5, 490, None): ('크리스: 표시 안 함. 질: 대체 조건 참. 둘 중 하나를 얻으면 둘 다 사라짐', 'Chris: never. Jill: the alternate condition true. Both disappear once either is taken'),
    (5, 506, None): ('질 전용, 뱅크 0 플래그 36 켜짐', 'Jill only, bank 0 flag 36 set'),
    (5, 509, None): ('뱅크 1 플래그 {n} 켜짐', 'Bank 1 flag {n} set'),
    (4, 23, 53): ('질 전용, 뱅크 0 플래그 7 켜짐', 'Jill only, bank 0 flag 7 set'),
    (4, 123, 93): ('질 전용, 뱅크 0 플래그 37 켜짐', 'Jill only, bank 0 flag 37 set'),
    (4, 401, 122): ('크리스 전용, 뱅크 0 플래그 98 켜짐', 'Chris only, bank 0 flag 98 set'),
    (7, 463, 11): ('가면 네 개를 모두 끼운 뒤 (뱅크 1 플래그 50–53)', 'After all four masks are inserted (bank 1 flags 50–53)'),
}
RESCUE_RULE = ('크리스 전용, 구출 이벤트가 진행 중일 때', 'Chris only, while the rescue event is active')
# Pickups with extra native checks in re1_mapnames.c that have no hand-written wording.
EXTRA_GATED = ((4, 357), (4, 344))


@dataclass(frozen=True)
class Marker:
    kind: int
    room: int
    room2: int
    area: int
    floor: int
    flag: int
    chr: int
    reward: int
    step: int
    icon: int
    x2: float
    y2: float
    ko: tuple
    en: tuple

    @property
    def group(self):
        assert self.kind in KIND_GROUP, f'unknown marker kind {self.kind}'
        return 'fuel' if self.kind == 0 and self.flag in FUEL_FLAGS else KIND_GROUP[self.kind]

    @property
    def source(self):
        return self.room2 if self.room2 >= 0 else self.room

    def label(self, ko):
        return self.ko if ko else self.en


def clean_text(comment):
    """Row comment -> display text: no category mark, ' / ' line breaks joined."""
    text = comment.lstrip(MARKS).strip()
    return re.sub(r' / (·?)', lambda m: m[1] or ' ', text)


def read_labels(path):
    """Labels table -> (markers with paired Korean/English text, legend row count, raw marker row count)."""
    raw = []
    legend = 0
    for line in path.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^\{(.*)\}, /\* (.*) \*/$', line)
        if not m:
            continue
        s = m[1].split(',')
        if s[0] == '6':
            legend += 1
            continue
        raw.append((s, m[2]))
    markers = []
    i = 0
    while i < len(raw):
        s, comment = raw[i]
        span = 1
        text = (clean_text(comment), float(s[8][:-1]), float(s[9][:-1]))
        other = text
        if s[7] != '0':
            assert s[7] == '1', f'row {i}: Korean row must come first'
            t, comment2 = raw[i + 1]
            assert t[7] == '2' and t[:7] == s[:7] and t[15:17] == s[15:17], f'unpaired label: {comment} / {comment2}'
            other = (clean_text(comment2), float(t[8][:-1]), float(t[9][:-1]))
            span = 2
        last = s[-1]
        markers.append(Marker(int(s[0]), int(s[1]), int(s[2]), int(s[3]), int(s[4]), int(s[5]), int(s[6]), int(s[15]),
                              int(s[16]), 0 if last.endswith('}') else int(last), float(s[10][:-1]), float(s[11][:-1]),
                              text, other))
        i += span
    return markers, legend, len(raw)


def check_groups(groups, markers):
    """Every marker group appears on exactly one page, so no row can be left out silently."""
    shown = [g for page in groups for g in page[3]]
    assert len(shown) == len(set(shown)), 'marker group on two pages'
    kinds = {m.group for m in markers} - {'legend'}
    assert set(shown) == kinds, f'marker groups not on a page: {sorted(kinds ^ set(shown))}'


def hand_rule_keys(item_state):
    """(kind, flag, source or None) of each rule in placed_item_available."""
    body = item_state[item_state.index('static int placed_item_available'):]
    keys = set()
    for line in body.splitlines():
        m = re.search(r'if \(kind==(\d+) && (.*?)\) (?:return|\{)', line)
        if m:
            sources = re.findall(r'source==(\d+)', m[2])
            for flag in re.findall(r'flag==(\d+)', m[2]):
                keys.add((int(m[1]), int(flag), int(sources[0]) if sources else None))
    return keys


def icon_stems(header):
    """Embedded icons[] index -> PNG stem, by exact pixels, because the header has no names."""
    pngs = {}
    for f in sorted((ROOT / 'assets/icons').glob('*.png')):
        if f.name != 'kerosene.png':
            pngs[Image.open(f).convert('RGBA').tobytes('raw', 'BGRA')] = f.stem
    stems = {}
    for i, values in re.findall(r'^static const unsigned char icpx(\d+)\[\]=\{([^}]+)\};', header, re.M):
        stems[int(i)] = pngs[bytes(map(int, values.split(',')))]
    return stems


def ranges(values):
    """Sorted ints -> '1–4, 7'."""
    parts = []
    for v in sorted(values):
        if parts and parts[-1][1] == v - 1:
            parts[-1][1] = v
        else:
            parts.append([v, v])
    return ', '.join(str(a) if a == b else f'{a}–{b}' for a, b in parts)


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def table(headers, rows):
    return '\n'.join('| ' + ' | '.join(map(cell, row)) + ' |' for row in [headers, ['---'] * len(headers), *rows])


class Wiki:
    def __init__(self):
        header = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
        self.markers, self.legend, self.raw_rows = read_labels(ROOT / 'src/labels.h')
        self.rooms = json.loads((ROOT / 'data/rooms.json').read_text(encoding='utf-8'))
        assert [r['native_index'] for r in self.rooms] == list(range(ROOM_COUNT)), 'rooms.json must list rooms 0..153'
        self.count = int(re.search(r'#define LABEL_COUNT (\d+)', header)[1])
        assert self.count == self.raw_rows + self.legend, 'labels.h rows were not all parsed'
        self.stems = icon_stems(header)
        self.enemy_em = [int(v) for v in re.search(r'enemy_icon_of_em\[64\]=\{([^}]+)\}', header)[1].split(',')]
        self.crimson_icon = int(re.search(r'#define CRIMSON_ICON (\d+)', header)[1])
        item_state = (ROOT / 'src/item_state.h').read_text(encoding='utf-8')
        self.gates = {tuple(map(int, g)) for g in re.findall(r'^\s*\{(\d+),(\d+),([01]),\{', item_state, re.M)}
        assert self.gates, 'no item gates found'
        assert hand_rule_keys(item_state) == set(HAND_RULES), 'item_state.h rules and HAND_RULES differ'
        native = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
        assert all(f'l->kind == {k} && l->flag == {f}' in native for k, f in EXTRA_GATED), 'EXTRA_GATED is out of date'
        sections = (ROOT / 'src/section_rules.h').read_text(encoding='utf-8')
        self.replaced_by = defaultdict(list)
        for a, b in re.findall(r'\{(\d+),(\d+)\}', sections):
            self.replaced_by[int(a)].append(int(b))
        crimson = (ROOT / 'src/crimson_data.h').read_text(encoding='utf-8')
        block = crimson[crimson.index('crimson_enemies[] = {'):]
        self.crimson = [tuple(map(int, c)) for c in re.findall(r'^\{(\d+),(-?\d+),(-?\d+),', block[:block.index('};')], re.M)]
        assert self.crimson, 'no crimson records found'
        self.names = {}
        for m in self.markers:
            if m.group == 'room':
                assert m.room not in self.names, f'two names for room {m.room}'
                self.names[m.room] = m
        check_groups(GROUPS, self.markers)
        used = {k for m in self.markers for k, r in HAND_RULES.items() if self.rule_key_matches(k, m)}
        assert used == set(HAND_RULES), f'hand rules with no row: {set(HAND_RULES) - used}'
        rows = sum(1 if m.kind == 7 else 2 for m in self.markers)
        assert rows == self.raw_rows, 'marker rows were lost in pairing'

    @staticmethod
    def rule_key_matches(key, m):
        return key[0] == m.kind and key[1] == m.flag and key[2] in (None, m.source)

    def room_name(self, i, ko):
        if i in self.names:
            return self.names[i].label(ko)[0]
        return (self.rooms[i]['name_ko'] if ko else self.rooms[i]['external_name']) or '—'

    def room_ref(self, i, ko):
        return f"{self.rooms[i]['room_id']} {self.room_name(i, ko)}"

    @staticmethod
    def who(m, ko):
        mask = m.chr & 0xff  # 0x100 = vertical door: label placement only, never a restriction
        assert not m.chr & ~0x1ff and (not mask or mask & 0x30), f'unknown chr mask {m.chr:#x}'
        names = [n for bit, n in ((0x10, '크리스' if ko else 'Chris'), (0x20, '질' if ko else 'Jill')) if mask & bit]
        return names[0] if len(names) == 1 else '—'

    @staticmethod
    def difficulty(m, ko):
        low = m.chr & 7
        if not low or low == 7:
            return '—'
        names = (('매우 쉬움·쉬움', 'Very Easy/Easy'), ('보통', 'Normal'), ('어려움', 'Hard'))
        return ', '.join(names[i][0 if ko else 1] for i in range(3) if low >> i & 1)

    def condition(self, m, ko):
        lang = 0 if ko else 1
        word = '조건부' if ko else 'conditional'
        parts = []
        if m.kind == 3:
            parts.append(RESCUE_RULE[lang])
        rule = next((text for key, text in HAND_RULES.items() if self.rule_key_matches(key, m)), None)
        if rule:
            parts.append(rule[lang].replace('{n}', '91' if m.source == 0 else '269'))
        elif m.kind >= 4:
            mask = m.chr & 0x30
            jills = [j for j in (0, 1) if not mask or mask & (0x20 if j else 0x10)]
            gated = [j for j in jills if (m.source, m.flag, j) in self.gates]
            if gated:
                names = (('크리스', 'Chris'), ('질', 'Jill'))
                parts.append(word if gated == jills else f'{word} ({names[gated[0]][lang]})')
        if m.reward or (m.kind, m.flag) in EXTRA_GATED:
            parts.append(word)
        return '; '.join(dict.fromkeys(parts)) or '—'

    def base_columns(self, m, ko):
        return [f'{m.area}:{m.floor}', self.rooms[m.room]['room_id'], self.room_name(m.room, ko)]

    def state_columns(self, m, ko):
        return [self.who(m, ko), self.difficulty(m, ko), self.condition(m, ko), '—' if m.kind == 3 else m.flag]

    def source_column(self, m, ko):
        return self.room_ref(m.source, ko) if m.source != m.room else '—'

    def xy(self, m, ko):
        return f'{m.label(ko)[1]:g},{m.label(ko)[2]:g}'

    def select(self, *groups):
        return [m for m in self.markers if m.group in groups]

    def rooms_page(self, ko):
        rows = []
        for r in self.rooms:
            i = r['native_index']
            rows.append([f"{r['map_area']}:{r['map_floor']}", i, r['room_id'], self.room_name(i, True),
                         self.room_name(i, False), self.xy(self.names[i], ko) if i in self.names else '—',
                         ', '.join(map(str, self.replaced_by[i])) or '—'])
        notes = ('`Cell`은 게임의 방 번호, `대체`는 같은 층의 확장·통합 구역입니다. 그 구역이 보이면 이 방의 이름 대신 그 구역의 이름을 표시합니다. 이름이 없는 방은 주석이 없습니다.' if ko else
                 '`Cell` is the game\'s room index. `Replaced by` lists expanded or combined sections on the same floor: when one is visible, its name is shown instead. Rooms without a name have no annotation.')
        return notes, table(['Map', 'Cell', 'Room ID', '한국어', 'English', 'x,y', '대체' if ko else 'Replaced by'], rows)

    def locks_page(self, ko):
        rows = [[*self.base_columns(m, ko), self.room_ref(m.room2, ko), m.label(ko)[0], self.xy(m, ko), f'{m.x2:g},{m.y2:g}',
                 *self.state_columns(m, ko)] for m in self.select('lock')]
        notes = ('열쇠 이름은 그 문을 여는 열쇠입니다. 표식은 아직 들어가지 않은 쪽 방에 표시되며(`x,y`는 첫 번째 방, `x2,y2`는 연결 방) 문이 열리면 사라집니다. `flag`는 문 잠금 해제 비트입니다.' if ko else
                 'The name is the key that opens the door. The marker sits on the side not yet entered (`x,y` in the room, `x2,y2` in the connected room) and disappears once the door is unlocked. `flag` is the door-unlock bit.')
        headers = (['Map', 'Room ID', '방', '연결 방', '열쇠', 'x,y', 'x2,y2', '캐릭터', '난이도', '출현 조건', 'flag'] if ko else
                   ['Map', 'Room ID', 'Room', 'Connected room', 'Key', 'x,y', 'x2,y2', 'Character', 'Difficulty', 'Condition', 'flag'])
        return notes, table(headers, rows)

    def pickup_headers(self, ko, *extra):
        if ko:
            return ['Map', 'Room ID', '방', '실제 위치', *extra, 'x,y', '캐릭터', '난이도', '출현 조건', 'flag']
        return ['Map', 'Room ID', 'Room', 'Physical room', *extra, 'x,y', 'Character', 'Difficulty', 'Condition', 'flag']

    def key_items_page(self, ko):
        rows = [[*self.base_columns(m, ko), self.source_column(m, ko), m.label(ko)[0], self.xy(m, ko), *self.state_columns(m, ko)]
                for m in self.select('key')]
        notes = ('`방`은 표식이 속한 지도 구역, `실제 위치`는 아이템이 있는 방이 다를 때의 방입니다. `flag`는 획득 비트(뱅크 3)이며, 514는 실제 비트가 없는 모드 내부 번호입니다.' if ko else
                 '`Room` is the map section that owns the marker; `Physical room` is the room holding the item when it differs. `flag` is the pickup bit (bank 3); 514 is an internal number with no real bit.')
        return notes, table(self.pickup_headers(ko, '표식' if ko else 'Marker'), rows)

    def puzzles_page(self, ko):
        types = {'puzzle': ('퍼즐', 'Puzzle'), 'event': ('이벤트', 'Event'), 'fuel': ('연료통', 'Fuel tank')}
        rows = [[*self.base_columns(m, ko), types[m.group][0 if ko else 1], m.label(ko)[0], self.xy(m, ko),
                 *self.state_columns(m, ko), m.step if m.reward else '—']
                for m in self.select('puzzle', 'event', 'fuel')]
        notes = ('주황색 ! 표식은 퍼즐, 보라색 ? 표식은 이벤트입니다. 방 안의 대략적인 위치입니다. 연속 퍼즐의 `step`은 지금까지 끝낸 입력 수이고, `(0)` 같은 숫자는 표식 이름의 일부입니다. 연료통은 남은 충전 횟수를 표시하고 비면 회색이 되며 방 이름 키 `1`을 따릅니다. `flag`는 퍼즐 보상의 획득 비트(뱅크 3)이며, 900–904, 512, 513, 515는 실제 비트가 없는 모드 내부 번호입니다.' if ko else
                 "An orange ! is a puzzle and a purple ? is an event. Positions are approximate. `step` is the number of inputs done so far in a multi-step puzzle, and numbers such as `(0)` are part of the marker name. Fuel tanks show the refills left, turn grey when empty and follow the room name key `1`. `flag` is the pickup bit (bank 3) of the puzzle's reward; 900–904, 512, 513 and 515 are internal numbers with no real bit.")
        extra = (['유형', '표식'] if ko else ['Type', 'Marker'])
        headers = (['Map', 'Room ID', '방', *extra, 'x,y', '캐릭터', '난이도', '출현 조건', 'flag', 'step'] if ko else
                   ['Map', 'Room ID', 'Room', *extra, 'x,y', 'Character', 'Difficulty', 'Condition', 'flag', 'step'])
        return notes, table(headers, rows)

    def documents_page(self, ko):
        kinds = {'badge-document': ('문서', 'Document'), 'badge-map': ('지도', 'Map')}
        rows = [[*self.base_columns(m, ko), self.source_column(m, ko), kinds[self.stems[m.icon - 1]][0 if ko else 1],
                 m.label(ko)[0], self.xy(m, ko), *self.state_columns(m, ko)] for m in self.select('document')]
        notes = (f'`방`과 `실제 위치`, `flag`는 [핵심 아이템](05-key-items.md)과 같습니다. 대체 조건 = {ALTERNATE_KO}.' if ko else
                 f'`Room`, `Physical room` and `flag` work as in [Key items](05-key-items.en.md). Alternate condition = {ALTERNATE_EN}.')
        return notes, table(self.pickup_headers(ko, '유형' if ko else 'Type', '표식' if ko else 'Marker'), rows)

    def common_page(self, ko):
        names = json.loads((ROOT / 'data/item_names.json').read_text(encoding='utf-8'))
        rows = []
        for m in self.select('common'):
            item = int(m.en[0].split()[-1])
            assert (ROOT / f'assets/icons/{item}.png').exists(), f'no icon for item {item}'
            rows.append([*self.base_columns(m, ko), self.source_column(m, ko), names[str(item)][1 if ko else 0],
                         f'![{item}]({ICONS}/{item}.png)', self.xy(m, ko), *self.state_columns(m, ko)])
        notes = ('아이템 이름은 영어는 Evil Resource, 한국어는 이 모드의 번역을 따릅니다. 조건이 다른 같은 위치는 행이 나뉩니다.' if ko else
                 'Item names follow Evil Resource. One location can have several rows with different conditions.')
        return notes, table(self.pickup_headers(ko, '아이템' if ko else 'Item', '아이콘' if ko else 'Icon'), rows)

    def save_page(self, ko):
        icons = f'![typewriter]({ICONS}/badge-typewriter.png) ![item box]({ICONS}/badge-itembox.png)'
        points = json.loads((ROOT / 'data/save_points.json').read_text())
        mark = lambda on: '○' if on else '—'
        rows = [[self.room_ref(p['room'], ko), self.room_name(p['room'], ko), mark(p['typewriter']), mark(p['item_box'])] for p in points]
        headers = ['Room ID', '방', '타자기', '아이템 상자'] if ko else ['Room ID', 'Room', 'Typewriter', 'Item box']
        note = (f'{icons}\n\n기본 배율에서는 게임 자체의 안내 표시를 그대로 사용합니다. 2배 확대 중에는 그 안내가 숨겨지므로 방문한 방의 가운데에 아이콘을 대신 그립니다. 기계의 실제 위치가 아니라 방의 가운데입니다. 키 `0`으로 함께 꺼집니다.' if ko else
                f"{icons}\n\nAt normal scale the game's own callouts are used. While the map is zoomed 2x they are hidden, so icons are drawn in the middle of each visited room. That is the room's middle, not the machine's exact spot. Key `0` hides them too.")
        return note, table(headers, rows)

    def enemies_page(self, ko):
        by_stem = defaultdict(list)
        for em, icon in enumerate(self.enemy_em):
            if icon != 255:
                by_stem[self.stems[icon]].append(em)
        crimson = self.stems[self.crimson_icon]
        assert set(by_stem) | {crimson} <= set(ENEMY_NAMES), 'enemy icon without a name'
        lang = 0 if ko else 1
        kinds = [[ENEMY_NAMES[s][lang], f'![{s}]({ICONS}/{s}.png)', ranges(by_stem[s])] for s in sorted(by_stem, key=lambda s: ENEMY_NAMES[s][1])]
        kinds.append([ENEMY_NAMES[crimson][lang], f'![{crimson}]({ICONS}/{crimson}.png)', '—'])
        grouped = defaultdict(list)
        for enemy, room, room2 in self.crimson:
            grouped[room, room2].append(enemy)
        places = [[f"{self.rooms[a]['map_area']}:{self.rooms[a]['map_floor']}", self.room_ref(a, ko), self.room_ref(b, ko) if b >= 0 else '—',
                   len(ids), ranges(ids)] for (a, b), ids in sorted(grouped.items())]
        if ko:
            notes = ('적 위치는 저장소에 표로 들어 있지 않습니다. 모드는 플레이 중 게임이 실제로 만든 적을 방마다 기록하고, 키 `7`을 켜면 그 기록을 표시합니다.\n\n'
                     '- 불러온 세이브에서 방문한 방의 적만, 같은 캐릭터·같은 난이도 분류일 때 표시합니다. 들어가지 않은 방에는 표시되지 않습니다.\n'
                     '- 쓰러뜨린 적은 사라집니다. 방을 다시 불러오면 그 방의 기록을 새로 씁니다.\n'
                     '- 더 오래된 세이브를 불러와 게임 시계가 되돌아가면 그 시점 이후의 기록을 지웁니다.\n'
                     '- 기록은 `RE1HD.AnnotatedMap.enemies.dat`에 저장합니다. 게임 메모리나 세이브에는 쓰지 않습니다.\n\n'
                     '크림슨 헤드는 쓰러진 자리에 아이콘을 표시하며, 부활 이벤트 전이나 타이머가 남아 있으면 회색입니다. 적 표시 중 `7`을 길게 누르면 남은 분을 켜고 끕니다.\n\n'
                     '## 적 종류\n\n`유형`은 게임의 적 유형 번호이며 각 번호의 아이콘은 `enemy_icon_of_em`에서 나옵니다. 표에 없는 번호는 그리지 않습니다.')
            tail = ('## 크림슨 헤드 대체 표\n\n기록이 시작되기 전에 쓰러진 적은 이 표로 방을 정합니다. 적의 좌표나 출현 조건이 아니라 적 번호와 방의 대응입니다.', ['Map', '방', '두 번째 방', '수', '적 번호'])
            first = ['적', '아이콘', '유형']
        else:
            notes = ('The repository has no table of enemy positions. While you play, the mod records the enemies the game actually spawns in each room, and key `7` shows those records.\n\n'
                     '- Enemies appear only in rooms visited in the loaded save, and only for the same character and difficulty class. Rooms you never entered show none.\n'
                     '- Defeated enemies disappear. Loading a room again rewrites its records.\n'
                     '- If an older save moves the game clock back, records made after that point are removed.\n'
                     '- Records are stored in `RE1HD.AnnotatedMap.enemies.dat`. Nothing is written to game memory or saves.\n\n'
                     'Crimson Heads show an icon where the enemy fell. It is grey before the revival event and while the timer is running. Hold `7` while enemies are on to switch the minutes left on or off.\n\n'
                     '## Enemy types\n\n`Type` is the game\'s enemy type number, and `enemy_icon_of_em` gives its icon. Numbers not listed are not drawn.')
            tail = ('## Crimson Head fallback table\n\nFor an enemy defeated before recording began, this table decides the room. It maps enemy numbers to rooms; it holds neither enemy coordinates nor appearance conditions.', ['Map', 'Room', 'Second room', 'Count', 'Enemy numbers'])
            first = ['Enemy', 'Icon', 'Type']
        return notes, table(first, kinds) + f'\n\n{tail[0]}\n\n' + table(tail[1], places)

    def caveat(self, ko, rows):
        if not rows:
            return '스포일러 포함.' if ko else 'Spoilers.'
        return ('스포일러 포함. 현재 src/labels.h의 조건별 표식 행이며 고유 아이템 수나 동시 출현 수가 아닙니다. 런타임 추가 판정은 아래 설명과 [데이터와 표 읽기](02-data-pipeline.md)를 참고하세요.' if ko else
                'Spoilers. Rows are conditional variants from current src/labels.h, not unique item counts or simultaneous spawns. Additional runtime gates apply; see the notes and [Data and table notation](02-data-pipeline.en.md).')

    def pages(self):
        builders = {'03-rooms': self.rooms_page, '04-locks-keys': self.locks_page, '05-key-items': self.key_items_page,
                    '06-puzzles-events': self.puzzles_page, '07-documents-maps': self.documents_page,
                    '08-common-items': self.common_page, '09-save-points': self.save_page, '11-enemies': self.enemies_page}
        assert set(builders) == {g[0] for g in GROUPS}
        out = {}
        for stem, title_ko, title_en, groups in GROUPS:
            for ko, suffix, title in ((True, '.md', title_ko), (False, '.en.md', title_en)):
                nav = f'[한국어]({stem}.md) | [English]({stem}.en.md) · [Index](README{suffix})'
                notes, body = builders[stem](ko)
                blocks = [f'# {title}', nav, self.caveat(ko, groups), notes] + ([body] if body else [])
                out[stem + suffix] = '\n\n'.join(blocks) + '\n'
        return out


def verify(pages):
    """Rules for all pages, generated or hand-written. Returns the page count."""
    stems = [g[0] for g in GROUPS] + list(HAND_PAGES)
    missing = [p for s in stems for p in (f'{s}.md', f'{s}.en.md') if p not in pages and not (WIKI / p).exists()]
    assert not missing, f'missing wiki pages: {missing}'
    everything = dict(pages)
    for s in HAND_PAGES:
        for suffix in ('.md', '.en.md'):
            everything[s + suffix] = (WIKI / (s + suffix)).read_text(encoding='utf-8')
    for name, text in everything.items():
        hit = LOCAL_PATH.search(text)
        assert not hit, f'{name}: local path {hit[0]!r}'
    for suffix in ('.md', '.en.md'):
        index = everything['README' + suffix]
        unlinked = [s for s in stems if s != 'README' and f'({s}{suffix})' not in index]
        assert not unlinked, f'README{suffix} does not link {unlinked}'
    return len(everything)


def main():
    p = argparse.ArgumentParser(description='Generate docs/wiki table pages from committed data.')
    p.add_argument('--check', action='store_true', help='fail if pages are stale instead of writing them')
    args = p.parse_args()
    wiki = Wiki()
    pages = wiki.pages()
    if args.check:
        stale = [n for n, text in pages.items() if not (WIKI / n).exists() or (WIKI / n).read_text(encoding='utf-8') != text]
        if stale:
            raise SystemExit(f'stale wiki pages, run tools/gen_wiki.py: {stale}')
    else:
        WIKI.mkdir(parents=True, exist_ok=True)
        for name, text in pages.items():
            (WIKI / name).write_text(text, encoding='utf-8')
    total = verify(pages)
    print(f'{"Checked" if args.check else "Generated"} {len(pages)} table pages ({total} wiki pages); '
          f'{len(wiki.rooms)} rooms; {len(wiki.markers)} markers.', file=sys.stdout)


if __name__ == '__main__':
    main()
