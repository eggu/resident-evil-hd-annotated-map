"""Write fonts/SourceHanSansSC-{Medium,Bold}-zh.otf: Source Han Sans SC (Adobe, SIL Open Font License 1.1) cut down to the
characters the Simplified Chinese rasters use (data/zh_cn.json plus printable ASCII and the legend punctuation), so the
repository carries ~150 KB per weight instead of two 16 MB fonts. The full fonts are read from local/fonts/ (ignored; release
2.004 or later from https://github.com/adobe-fonts/source-han-sans, SubsetOTF/SC). Needs fontTools. Run after changing
data/zh_cn.json, then tools/render_zh.py and the other generators (docs/DEVELOPMENT.md)."""
from pathlib import Path
import json
import sys
from fontTools import subset

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ('Medium', 'Bold')


def characters():
    data = json.loads((ROOT / 'data/zh_cn.json').read_text(encoding='utf-8'))
    text = ''.join(v for k, group in data.items() if not k.startswith('_') for v in group.values())
    text += ''.join(chr(c) for c in range(0x20, 0x7f)) + '·：（）%'
    return ''.join(sorted(set(text) - set('|')))


def main(src=ROOT / 'local/fonts'):
    chars = characters()
    for w in WEIGHTS:
        options = subset.Options()
        options.name_IDs = ['*']
        options.name_legacy = True
        options.name_languages = ['*']
        options.notdef_outline = True
        options.layout_features = ['*']
        font = subset.load_font(str(Path(src) / ('SourceHanSansSC-%s.otf' % w)), options)
        s = subset.Subsetter(options)
        s.populate(text=chars)
        s.subset(font)
        out = ROOT / 'fonts' / ('SourceHanSansSC-%s-zh.otf' % w)
        subset.save_font(font, str(out), options)
        print(out.relative_to(ROOT), out.stat().st_size, 'bytes,', len(chars), 'characters')


if __name__ == '__main__':
    main(*sys.argv[1:])
