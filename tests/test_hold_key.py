"""Key 7: a short press is a tap, a long press fires once, and releasing after it does nothing. Toggles fire once per press
and rest KEY_REST_MS (a bounce 200 ms later is ignored)."""
from pathlib import Path
import subprocess, tempfile
ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
    c = Path(d) / 't.c'; out = Path(d) / 't'
    c.write_text('''#include <assert.h>
#include "hold_key.h"
int main(void) {
    HoldKey k = {0};
    assert(hold_key_step(&k, 0, 0) == HOLD_NONE);
    assert(hold_key_step(&k, 1, 100) == HOLD_NONE);
    assert(hold_key_step(&k, 1, 300) == HOLD_NONE);
    assert(hold_key_step(&k, 0, 350) == HOLD_TAP);
    assert(hold_key_step(&k, 0, 400) == HOLD_NONE);
    assert(hold_key_step(&k, 1, 1000) == HOLD_NONE);
    assert(hold_key_step(&k, 1, 1500) == HOLD_LONG);
    assert(hold_key_step(&k, 1, 2500) == HOLD_NONE);
    assert(hold_key_step(&k, 0, 2600) == HOLD_NONE);
    KeyRest r = {0};
    assert(key_rest_step(&r, 1, 0) == 1);       /* first press, even at tick 0 */
    assert(key_rest_step(&r, 1, 50) == 0);      /* held */
    assert(key_rest_step(&r, 0, 100) == 0);
    assert(key_rest_step(&r, 1, 200) == 0);     /* bounce inside the rest */
    assert(key_rest_step(&r, 0, 250) == 0);
    assert(key_rest_step(&r, 1, 400) == 1);     /* a new press after the rest */
    assert(key_rest_step(&r, 0, 450) == 0 && key_rest_step(&r, 1, 749) == 0 && key_rest_step(&r, 0, 760) == 0);
    assert(key_rest_step(&r, 1, 760) == 1);
    return 0;
}
''')
    subprocess.run(['clang', '-I', str(ROOT / 'src'), str(c), '-o', str(out)], check=True)
    subprocess.run([str(out)], check=True)
print('PASS: key 7 tap and hold; toggle rest')
