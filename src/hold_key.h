/* One key with two actions, polled: released early = tap, kept down past HOLD_KEY_MS = hold (once per press). */
#define HOLD_KEY_MS 500u
typedef struct { unsigned long down_ms; int down, fired; } HoldKey;
enum { HOLD_NONE, HOLD_TAP, HOLD_LONG };
static int hold_key_step(HoldKey *k, int is_down, unsigned long now) {
    if (is_down) {
        if (!k->down) { k->down = 1; k->fired = 0; k->down_ms = now; return HOLD_NONE; }
        if (!k->fired && now - k->down_ms >= HOLD_KEY_MS) { k->fired = 1; return HOLD_LONG; }
        return HOLD_NONE;
    }
    int tap = k->down && !k->fired;
    k->down = 0;
    return tap ? HOLD_TAP : HOLD_NONE;
}
/* A toggle fires on a new press and not again within KEY_REST_MS: live, one press fired three times 200 ms apart (RE0 HD). */
#define KEY_REST_MS 350u
typedef struct { unsigned long last; unsigned char down, used; } KeyRest;
static int key_rest_step(KeyRest *k, int is_down, unsigned long now) {
    int hit = is_down && !k->down;
    k->down = (unsigned char)(is_down != 0);
    if (!hit || (k->used && now - k->last < KEY_REST_MS)) return 0;
    k->last = now; k->used = 1;
    return 1;
}
