"""2x map view arithmetic against the real header."""
from pathlib import Path
import subprocess, tempfile
ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
    c = Path(d) / 't.c'; out = Path(d) / 't'
    c.write_text('''#include <assert.h>
#include "zoom.h"
int main(void) {
    /* centred view: screen centre input maps to itself; sprite doubled; neighbours stay adjacent */
    int a[23] = {0}, b[23] = {0};
    a[4] = 100; a[5] = 200; a[6] = 50; a[7] = 30; a[10] = 3; a[11] = 4;
    b[4] = 150; b[5] = 200; b[6] = 50; b[7] = 30;
    zoom_sprite(a, -658, -360); zoom_sprite(b, -658, -360);
    assert(a[4] == -458 && a[5] == 40 && a[6] == 100 && a[7] == 60 && a[10] == 6 && a[11] == 8);
    assert(a[4] + a[6] == b[4]);
    /* fixed size: centre lands where the scaled sprite's centre lands, size unchanged */
    int f[23] = {0}, g[23] = {0};
    f[4] = g[4] = 100; f[5] = g[5] = 200; f[6] = g[6] = 40; f[7] = g[7] = 20;
    zoom_sprite(g, -658, -360); zoom_sprite_fixed(f, -658, -360);
    assert(f[6] == 40 && f[7] == 20 && f[4] + f[6] / 2 == g[4] + g[6] / 2 && f[5] + f[7] / 2 == g[5] + g[7] / 2);
    /* floor name lands TITLE_GAP above the legend and at its left, after the .9 GUI scale */
    float dy = .9f * zoom_title_dy(572) + 218 - (572 - 16), dx = .9f * zoom_title_dx() + 287 - 14;
    assert(dy > -.01f && dy < .01f && dx > -.01f && dx < .01f);
    /* overlay agrees with native output 48+.9x for the same input */
    float x = 100, nx = 48 + .9f * x, ny = 36 + .9f * 200;
    float e = zoom_out_x(nx, -658) - (48 + .9f * (2 * x - 658));
    assert(e > -.01f && e < .01f);
    e = zoom_out_y(ny, -360) - (36 + .9f * (2 * 200 - 360));
    assert(e > -.01f && e < .01f);
    /* centre output point stays put */
    e = zoom_out_y(360, -360) - 360; assert(e > -.01f && e < .01f);
    float ox = -658, oy = -360;
    zoom_pan(PAD_RIGHT, 20, &ox, &oy); assert(ox == -668 && oy == -360);
    zoom_pan(PAD_LEFT | PAD_UP, 20, &ox, &oy); assert(ox == -658 && oy == -350);
    /* clamps and frame-gap limit */
    ox = 0; oy = 0; zoom_pan(PAD_LEFT | PAD_UP, 1000, &ox, &oy); assert(ox == -232 && oy == -40);
    ox = -1316; oy = -720; zoom_pan(PAD_RIGHT | PAD_DOWN, 1000, &ox, &oy); assert(ox == -728 && oy == -680);
    /* the doubled panel still covers the screen at both ends (output 0..1280, 0..720) */
    assert(48 + .9f * (2 * 0 + ZOOM_X_MAX) + 160 <= .1f && 48 + .9f * (2 * 960 + ZOOM_X_MIN) + 160 >= 1279.9f);
    assert(36 + .9f * (2 * 0 + ZOOM_Y_MAX) <= .1f && 36 + .9f * (2 * 720 + ZOOM_Y_MIN) >= 719.9f);
    ox = -600; oy = -300; zoom_pan(PAD_RIGHT, 100000, &ox, &oy); assert(ox == -650);
    return 0;
}
''')
    subprocess.run(['clang', '-I', str(ROOT / 'src'), str(c), '-o', str(out)], check=True)
    subprocess.run([str(out)], check=True)
print('PASS: zoom sprite, overlay and pan arithmetic')
