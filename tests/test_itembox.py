"""Exercise the actual draw guard for native map/list/box states."""
from pathlib import Path
import re
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / 'src/re1_mapnames.c').read_text()
guard = re.search(r'if \(u32\(map \+ 0x629c\) != 0\) return;', source).group()
assert source.index('readable(map, 0x62a0)') < source.index(guard) < source.index('U32 area =')
assert source.index(guard) < source.index('set_states(dev);')  # no state changes or legend before guard
with tempfile.TemporaryDirectory() as d:
    c = Path(d) / 'guard.c'
    c.write_text('''#include <assert.h>
#include <string.h>
typedef unsigned int U32;
static U32 u32(const void *p) { U32 v; memcpy(&v,p,4); return v; }
static int drawn;
static void draw(unsigned char *map) { ''' + guard + ''' drawn++; }
int main(void) {
 unsigned char map[0x62a0] = {0};
 U32 states[] = {0,1,2,1,0};
 int expected[] = {1,1,1,1,2};
 for (int i=0;i<5;i++) {
  memcpy(map+0x629c,&states[i],4); draw(map); assert(drawn==expected[i]);
 }
}
''')
    subprocess.run(['clang', str(c), '-o', str(Path(d)/'guard')], check=True)
    subprocess.run([str(Path(d)/'guard')], check=True)
print('PASS: map -> box list -> contents -> list -> map; all overlay draws gated')
