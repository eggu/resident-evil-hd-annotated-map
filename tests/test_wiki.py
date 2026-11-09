"""The wiki table pages match the committed data, and a marker group left off the page list fails."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import gen_wiki

subprocess.run([sys.executable, str(ROOT / 'tools/gen_wiki.py'), '--check'], check=True, stdout=subprocess.DEVNULL)
markers, _legend, _rows = gen_wiki.read_labels(ROOT / 'src/labels.h')
gen_wiki.check_groups(gen_wiki.GROUPS, markers)
for page in gen_wiki.GROUPS:
    if page[3]:
        fewer = [g for g in gen_wiki.GROUPS if g is not page]
        try:
            gen_wiki.check_groups(fewer, markers)
        except AssertionError:
            continue
        raise SystemExit(f'leaving out {page[0]} was not detected')
print('PASS: wiki pages are current and every marker group has a page')
