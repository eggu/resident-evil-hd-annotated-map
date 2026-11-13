"""Build and package the release ZIP without accessing an installed game."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, tempfile, zipfile
ROOT = Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--test', action='store_true', help='Run portable state/atlas checks (requires clang and Pillow)')
    args = p.parse_args()
    if args.test:
        subprocess.run([sys.executable, str(ROOT/'tests/run.py')], check=True)
    version = (ROOT/'VERSION').read_text().strip()
    dist = ROOT/'dist'
    dist.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='re1hd-annotated-map-') as d:
        binary = Path(d)/'RE1HD.AnnotatedMap.asi'
        # version resource + stripped symbols: an unstripped DLL without them drew antivirus false positives
        (ROOT/'src/rc_version.h').write_text(f'#define VER_STR "{version}"\n#define VER_NUM {",".join(version.split("."))},0\n')
        subprocess.run([sys.executable,'-m','ziglang','cc','-target','x86-windows-gnu',
            '-shared','-O2','-s',str(ROOT/'src/re1_mapnames.c'),str(ROOT/'src/version.rc'),'-o',str(binary),
            '-lkernel32','-luser32'],cwd=d,check=True)
        blob = binary.read_bytes()
        assert blob[:2] == b'MZ'
        package = dist/f'RE1-HD-Annotated-Map-{version}.zip'
        loader = ROOT/'packaging/ultimate-asi-loader'
        members = {'scripts/RE1HD.AnnotatedMap.asi': blob,
            'scripts/RE1HD.AnnotatedMap.ini': (ROOT/'packaging/RE1HD.AnnotatedMap.ini').read_bytes(),
            'scripts/UltimateASILoader-LICENSE.txt': (loader/'UltimateASILoader-LICENSE.txt').read_bytes(),
            'dinput8.dll': (loader/'dsound.dll').read_bytes(), # the loader picks its role from its file name
            'RE1-HD-Annotated-Map-README.txt': (ROOT/'packaging/README.txt').read_bytes(),
            'LICENSE.txt': (ROOT/'LICENSE').read_bytes(),
            'NOTICE.md': (ROOT/'NOTICE.md').read_bytes()}
        temporary = dist/(package.name+'.tmp')
        try:
            with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as z:
                for name, data in members.items():
                    info = zipfile.ZipInfo(name, date_time=(2026,10,28,0,0,0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    z.writestr(info,data)
            with zipfile.ZipFile(temporary) as z:
                assert z.testzip() is None and set(z.namelist()) == set(members)
                assert all(z.read(n)==data for n,data in members.items())
            temporary.replace(package)
        finally:
            temporary.unlink(missing_ok=True)
    report = dict(version=version, asi_sha256=hashlib.sha256(blob).hexdigest(),
        package_sha256=sha(package), tests_run=args.test,
        zig_version=subprocess.check_output([sys.executable,'-m','ziglang','version'],text=True).strip(),
        source_sha256={str(f.relative_to(ROOT)):sha(f) for f in sorted((ROOT/'src').iterdir())})
    (dist/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2)); print(package)

if __name__ == '__main__': main()
