"""The real is_device, compiled on the host with a fake memory map. The D3D9 device is recognised when its vtable lives in a
non-game image (the original rule), when overlays or hook libraries own a few of its slots, and when the object points at a
heap copy of the whole table (every slot still in d3d9.dll). It is still refused for the game's own
objects, a first COM slot owned by another module, more than DEVICE_FOREIGN_MAX foreign slots, or a slot outside any image."""
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / 'src/re1_mapnames.c').read_text(encoding='utf-8')
cut = lambda a, b: s[s.index(a):s.index(b)]

PROG = r'''
#include <assert.h>
#include <stdint.h>
typedef unsigned char BYTE;
/* fake modules: function "addresses" are plain numbers in these ranges; the image vtable is a real array registered as d3d9 */
#define D3D9  ((void *)0x10000000)
#define OTHER ((void *)0x20000000)
static BYTE *exe = (BYTE *)0x00400000;
static void *vt_image[119], *vt_heap[119];
static int readable(const void *p, unsigned n) { (void)n; return p != 0; }
static int in_image(const void *p, void **base) {
    uintptr_t a = (uintptr_t)p;
    if (p == (void *)vt_image) { *base = D3D9; return 1; }
    if (a >= 0x10000000 && a < 0x10100000) { *base = D3D9; return 1; }
    if (a >= 0x20000000 && a < 0x20100000) { *base = OTHER; return 1; }
    if (a >= 0x00400000 && a < 0x00c19000) { *base = exe; return 1; }
    return 0; /* heap */
}
''' + cut('#define DEVICE_FOREIGN_MAX', '/* the device the game itself presents with') + r'''
static void fill(void **vt, uintptr_t base) { for (int i = 0; i < 119; i++) vt[i] = (void *)(base + 0x1000 + 16 * i); }
int main(void) {
    void *obj[1];
    obj[0] = vt_image; fill(vt_image, 0x10000000);
    assert(is_device(obj) == 1);                               /* the original case: table and slots in d3d9 */
    vt_image[17] = (void *)0x20000100; vt_image[42] = (void *)0x20000200; vt_image[16] = (void *)0x20000300;
    assert(is_device(obj) == 4);                               /* three slots hooked by an overlay */
    vt_image[0] = (void *)0x20000400; assert(is_device(obj) == 0);   /* QueryInterface owned elsewhere: not a device */
    fill(vt_image, 0x10000000);
    for (int i = 3; i < 3 + 16; i++) vt_image[i] = (void *)0x20000000;
    assert(is_device(obj) == 17);                              /* DEVICE_FOREIGN_MAX foreign slots: still accepted */
    vt_image[3 + 16] = (void *)0x20000000; assert(is_device(obj) == 0); /* one more: refused */
    fill(vt_image, 0x10000000); vt_image[50] = (void *)0x50000000;
    assert(is_device(obj) == 0);                               /* a slot outside every image */
    obj[0] = vt_heap; fill(vt_heap, 0x10000000);
    assert(is_device(obj) == 1);                               /* heap copy of the table, every slot in d3d9 */
    vt_heap[42] = (void *)0x20000000; assert(is_device(obj) == 2);   /* heap copy with EndScene hooked */
    fill(vt_heap, 0x00401000); assert(is_device(obj) == 0);    /* heap table of a game object: refused */
    fill(vt_heap, 0x10000000); vt_heap[0] = (void *)0x50000000; assert(is_device(obj) == 0); /* slot 0 outside images */
    assert(is_device(0) == 0);
    return 0;
}
'''
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 'device.c', Path(d) / 'device'
    c.write_text(PROG, encoding='utf-8')
    subprocess.run(['clang', '-w', str(c), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
print('PASS: D3D9 device recognised with its table in d3d9, with up to 16 slots hooked, and as a heap copy; game objects, foreign '
      'QueryInterface, too many foreign slots and slots outside images refused')
