/* Native 2x map view (RE3-style: toggle + held directions pan). Sprite x/y are the 0x5561d0 input: its output is
 * 48+.9x, 36+.9y, and the overlay's label points are in that output space. off = where input 0 lands when doubled. */
/* The 960x720 map panel sits at output x 208..1072 (ox 160), 36..684. */
#define ZOOM_CX 480 /* input point of the 1280x720 screen centre */
#define ZOOM_CY 360
/* off that keep the doubled panel covering the whole 16:9 picture */
#define ZOOM_X_MIN (-728.0f)
#define ZOOM_X_MAX (-232.0f)
#define ZOOM_Y_MIN (-680.0f)
#define ZOOM_Y_MAX (-40.0f)
#define ZOOM_PAN_PX_PER_MS 0.5f /* RE3: 4 of 320 px a frame at 30 fps */
#define PAD_UP    0x10010u
#define PAD_RIGHT 0x20020u
#define PAD_DOWN  0x40040u
#define PAD_LEFT  0x80080u
static float clampf_(float v, float lo, float hi) { return v < lo ? lo : v > hi ? hi : v; }
static float zoom_clamp_x(float off) { return clampf_(off, ZOOM_X_MIN, ZOOM_X_MAX); }
static float zoom_clamp_y(float off) { return clampf_(off, ZOOM_Y_MIN, ZOOM_Y_MAX); }
/* s = sprite as int[]: +0x10 x, +0x14 y, +0x18 w, +0x1c h, +0x28/+0x2c pivot. Whole-pixel off keeps sprites seamless. */
static void zoom_sprite(int *s, float off_x, float off_y) {
    s[4] = 2 * s[4] + (int)off_x; s[5] = 2 * s[5] + (int)off_y;
    s[6] *= 2; s[7] *= 2; s[10] *= 2; s[11] *= 2;
}
/* Same point on the map, native size: for the player marker and native icons. */
static void zoom_sprite_fixed(int *s, float off_x, float off_y) {
    s[4] = 2 * s[4] + (int)off_x + s[6] / 2; s[5] = 2 * s[5] + (int)off_y + s[7] / 2;
}
static float zoom_out_x(float x, float off_x) { return 2 * x - 48 + .9f * (int)off_x; }
static float zoom_out_y(float y, float off_y) { return 2 * y - 36 + .9f * (int)off_y; }
/* Floor name, measured in 1280x720: native left 287, centre y 218. Left aligns with the legend; centre sits TITLE_GAP above it.
 * Its GUI position is in map input units, so a screen move is divided by .9 (v41 screenshot: it moved .9 of what was asked). */
#define TITLE_NATIVE_X 287.0f
#define TITLE_NATIVE_Y 218.0f
#define TITLE_LEFT 14.0f
#define TITLE_GAP 16.0f
static float zoom_title_dx(void) { return (TITLE_LEFT - TITLE_NATIVE_X) / .9f; }
static float zoom_title_dy(float legend_top) { return (legend_top - TITLE_GAP - TITLE_NATIVE_Y) / .9f; }
/* Held directions move the view: content goes the other way. */
static void zoom_pan(unsigned held, unsigned ms, float *off_x, float *off_y) {
    float d = (ms > 100 ? 100 : ms) * ZOOM_PAN_PX_PER_MS;
    if (held & PAD_RIGHT) *off_x -= d;
    if (held & PAD_LEFT) *off_x += d;
    if (held & PAD_DOWN) *off_y -= d;
    if (held & PAD_UP) *off_y += d;
    *off_x = zoom_clamp_x(*off_x); *off_y = zoom_clamp_y(*off_y);
}
