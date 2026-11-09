/* Category colours (INI [Colors], user decision 2026-11-08): one #RRGGBB per category, shared by the legend row, the names and
 * the badges. The rasters are white with a dark outline; the draw state multiplies them by the vertex colour. Pure functions so
 * tests compile them on the host. */
#ifndef COLORS_H
#define COLORS_H
enum { COL_ROOM, COL_LOCK, COL_KEY, COL_FILE, COL_PUZZLE, COL_EVENT, COL_COMMON, COL_ENEMY, COL_COUNT };
static const char *const color_keys[COL_COUNT] = {"Rooms", "Locks", "KeyItems", "Files", "Puzzles", "Events", "CommonItems", "Enemies"};
/* the colours the legend rows had before the INI could change them, except common items: cool grey (user decision 2026-11-08) */
static const unsigned color_default[COL_COUNT] = {0xf0e2be, 0xffcd46, 0x5adcff, 0xff8cd2, 0xff9628, 0xb070ff, 0xb8bcc4, 0xeb3c3c};
#define COLOR_OFF     0x6a6a6a /* a disabled legend row: darker than the readout grey, so the two stay apart */
#define COLOR_READOUT 0x8c8c8c /* the size and opacity readouts, [~] */
#define COLOR_HINT    0xaaaaaa /* the zoom hint */
#define COLOR_WHITE   0xffffff /* [0], scope, [H], [\], the title */
static unsigned cat_color[COL_COUNT] = {0xf0e2be, 0xffcd46, 0x5adcff, 0xff8cd2, 0xff9628, 0xb070ff, 0xb8bcc4, 0xeb3c3c};

/* '#RRGGBB' (the '#' is optional, surrounding spaces ignored); 1 and *rgb set on success, else 0 and *rgb untouched. */
static int color_parse(const char *text, unsigned *rgb) {
    unsigned v = 0; int digits = 0;
    while (*text == ' ' || *text == '\t') text++;
    if (*text == '#') text++;
    for (; digits < 6; digits++, text++) {
        char c = *text;
        unsigned d = c >= '0' && c <= '9' ? (unsigned)(c - '0') : c >= 'a' && c <= 'f' ? (unsigned)(c - 'a' + 10) : c >= 'A' && c <= 'F' ? (unsigned)(c - 'A' + 10) : 16u;
        if (d > 15) return 0;
        v = v << 4 | d;
    }
    while (*text == ' ' || *text == '\t' || *text == '\r') text++;
    if (*text) return 0;
    *rgb = v;
    return 1;
}
#endif
