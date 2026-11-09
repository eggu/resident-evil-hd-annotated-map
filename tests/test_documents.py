"""Documents (the game's file list, Korean names as the game shows them, captured 2026-11-07 from its text table in order) against
the markers: every file has a floor-pickup row in src/labels.h, the Room 003 examine file is a synthetic mark, or it is listed here
as having no marker with the reason. A new row or a dropped one changes this list, so it fails until the list is reviewed."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
h = (ROOT / 'src/labels.h').read_text(encoding='utf-8')
keyrows = {re.sub(r'[ /의]', '', m[1]) for m in re.finditer(r'^\{4,.*?/\* ◇([^*]*)\*/$', h, re.M)}
rows = {re.sub(r'[ /의]', '', m[8]) for m in re.finditer(r'^\{5,(-?\d+),(-?\d+),(\d+),(\d+),(\d+),(\d+),(\d+),.*?/\* □([^*]*)\*/$', h, re.M) if m[7] == '1'}
FILES = ['저택에서 입수한 문서 1', '저택에서 입수한 문서 2', '정원과 기숙사에서 입수한 문서', '연구소에서 입수한 문서', 'S.T.A.R.S. 설명서', '케네스의 필름',
         '저주의 책', '트레버의 수기', '버려진 메모', '식물도감', '시체 처리에 관한 주의 사항', '사육사의 일지', '어느 연구원의 유서', '보안 부장의 메일',
         '자살자의 유서', '식물 42 보고서', '유기화학 실험 문서', '어느 가족의 사진', '배리의 사진', '어느 연구원의 편지', 'V-ACT에 관해', '팩스',
         '연구소 경비 시스템 자료', '관찰 기록서']
norm = lambda t: re.sub(r'[ /의]', '', t)
src = (ROOT / 'src/synth_marks.h').read_text(encoding='utf-8')
synthetic = {'유기화학 실험 문서', '케네스의 필름', '버려진 메모', '자살자의 유서'} if 'SYN_DOC_SUICIDE' in src else set()  # the Room 003 object (mNo 90): the key item 빨간 책 / Red Book, its description is this file's title
unmarked = [f for f in FILES if norm(f) not in rows and norm(f) not in keyrows and f not in synthetic]
# Reviewed 2026-11-08. Each file without a marker, with the reason:
REASONS = {  # user, 2026-11-08: the four are given by an EVENT after picking up / examining an item, not by a pickup of their own
    '저택에서 입수한 문서 1': 'folder title of the Files screen (documents by area), not an object the game places',
    '저택에서 입수한 문서 2': 'folder title of the Files screen',
    '정원과 기숙사에서 입수한 문서': 'folder title of the Files screen',
    '연구소에서 입수한 문서': 'folder title of the Files screen',
    'S.T.A.R.S. 설명서': 'two parts, given automatically with the first key item (Golden Arrow or Emblem) and the first defensive weapon: no single object (evilresource S.T.A.R.S. Manual)',
}
EXPECTED = list(REASONS)
assert unmarked == EXPECTED, unmarked
assert '유기화학 실험 문서' in synthetic
print(f'PASS: {len(FILES) - len(unmarked)} of {len(FILES)} files have a marker (key item rows, document rows or the synthetic one); {len(unmarked)} listed without, each with a reason')
