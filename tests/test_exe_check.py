"""The EXE guard accepts the supported PE header values and rejects anything else."""
from pathlib import Path
import subprocess, tempfile
ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
    c = Path(d) / 't.c'; out = Path(d) / 't'
    c.write_text('''#include <assert.h>
#include <string.h>
#include "exe_check.h"
int main(void) {
    unsigned char m[0x200] = {'M', 'Z'};
    *(int *)(m + 0x3c) = 0x100;
    *(unsigned *)(m + 0x108) = EXE_TIMESTAMP; *(unsigned *)(m + 0x150) = EXE_IMAGE_SIZE;
    assert(exe_supported(m));
    *(unsigned *)(m + 0x108) = EXE_TIMESTAMP + 1; assert(!exe_supported(m));
    *(unsigned *)(m + 0x108) = EXE_TIMESTAMP; *(unsigned *)(m + 0x150) = 0; assert(!exe_supported(m));
    *(unsigned *)(m + 0x150) = EXE_IMAGE_SIZE; m[0] = 0; assert(!exe_supported(m));
    return 0;
}
''')
    subprocess.run(['clang', '-I', str(ROOT / 'src'), str(c), '-o', str(out)], check=True)
    subprocess.run([str(out)], check=True)
print('PASS: EXE guard')
