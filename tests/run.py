"""Portable tests; no game EXE, game directory, font, network, or installation."""
from pathlib import Path
import os, subprocess, sys, tempfile
ROOT = Path(__file__).resolve().parents[1]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
for test in sorted((ROOT/'tests').glob('test_*.py')):
    subprocess.run([sys.executable,str(test)],cwd=ROOT,env=env,check=True)
with tempfile.TemporaryDirectory() as d:
    out=Path(d)/'rewards'
    subprocess.run(['clang','-I',str(ROOT/'src'),str(ROOT/'tests/test_reward_state.c'),'-o',str(out)],check=True)
    subprocess.run([str(out)],check=True)
    out=Path(d)/'enemy'
    subprocess.run(['clang','-I',str(ROOT/'src'),str(ROOT/'tests/test_enemy_rec.c'),'-o',str(out)],check=True)
    subprocess.run([str(out)],check=True)
print('PASS: portable runtime/state/atlas/snapshot suite')
