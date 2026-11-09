/* Recorded enemy spawns: pure data + predicates (no Windows/game access), shared by re1_mapnames.c and
 * test_enemy_rec.c. A record = one enemy the game actually spawned (hook on 0x47f500, mode 0) in a room.
 * Per-save rule (coordinator decision A, nothing is written into game memory or saves):
 *   shown  <=>  room visited (bank5) in the loaded state  &&  killed flag bank2[gid] clear
 *               &&  same character + difficulty class  &&  stamp <= current game clock (wasps: bank1 188 only).
 * plus: a clock regression (older save loaded) purges records stamped after the new clock; a room load replaces
 * that room's records. Residual error: see ../enemies-runtime/NOTES.md. */
#ifndef ENEMY_REC_H
#define ENEMY_REC_H
#include <string.h>

#define ENEMY_MAX 1024
#define ENEMY_REGRESS 15.0f /* clock ticks (1/30 s): smaller backward jumps are not a load */
typedef struct { int room; unsigned slot, em, gid, chr, diff; float x, z, stamp; } EnemyRec;
static EnemyRec enemy_recs[ENEMY_MAX];
static int enemy_n;

/* difficulty class as the game's spawn masks: Very Easy/Easy 1, Normal 2, Hard 4 */
static unsigned enemy_diff_class(unsigned d) { return d == 1 ? 2 : d == 2 ? 4 : 1; }

static int enemy_is_wasp(const EnemyRec *r);
static int enemy_shown(const EnemyRec *r, unsigned chr, unsigned diff_class, float now, int visited, int killed) {
    /* wasps exist in every save until bank1 188 (enemy_wasp_gone): the session clock says nothing about them */
    return visited && !killed && r->chr == chr && r->diff == diff_class && (r->stamp <= now || enemy_is_wasp(r));
}

/* Entering a room (the load destination INV+0xe472c/0xe4730) respawns what the game still wants there; a room that spawns
 * nothing (wasps after the Insecticide, any scripted mass kill) leaves its old records behind. A record stamped before the
 * room's last entry (minus the poll slack) therefore no longer exists. 0 = entry not seen yet. */
#define ENEMY_ENTER_SLACK 3.0f /* clock ticks: the entry is polled every 50 ms, spawns stamp at or after the destination is set */
static float enemy_room_enter[154];
static void enemy_enter(int room, float now) { if (room >= 0 && room < 154) enemy_room_enter[room] = now; }
static void enemy_enter_reset(void) { memset(enemy_room_enter, 0, sizeof enemy_room_enter); }
static int enemy_stale(const EnemyRec *r) {
    if (enemy_is_wasp(r)) return 0; /* an entry seen in another save (insecticide used there) must not hide them here */
    float e = r->room >= 0 && r->room < 154 ? enemy_room_enter[r->room] : 0;
    return e > 0 && r->stamp + ENEMY_ENTER_SLACK < e;
}

/* Wasps (em 12) of the Residence Central Corridor (room 109, r405) and Gallery (room 112, r408) are gone for good once the Insecticide was
 * used: bank1 188, set by the wasp nest event (object state machine at 0x646dd0, state 6) and read by the room 0x405 wasp code (0x47aa81) and
 * the room code (0x4c0a63). Their spawn records carry no kill flag, so the record is hidden by that flag. */
#define WASP_EM 12
#define WASP_NEST_FLAG 188
static int enemy_is_wasp(const EnemyRec *r) { return r->em == WASP_EM && (r->room == 109 || r->room == 112); }
static int enemy_wasp_gone(const EnemyRec *r, int nest_flag_set) { return nest_flag_set && enemy_is_wasp(r); }

/* Main Laboratory (room 148) Tyrant (em 49, kill flag bank2 657): waking Barry (bank1 22) clears that kill flag again
 * (read-only capture 2026-11-09, ~3 s after the wake), so after the wake the Tyrant is gone by bank1 22. */
#define TYRANT_EM 49
#define BARRY_WOKEN_FLAG 22
static int enemy_tyrant_gone(const EnemyRec *r, int woken) { return woken && r->em == TYRANT_EM && r->room == 148; }

/* 'O' Room (room 134, r505): its init 0x4c84d0 spawns its enemies (0x4e9fa0) only while bank1 215 is clear; the Main Laboratory
 * init 0x4cc8f0 sets 215 in the Tyrant sequence, after which the room is empty (its zombies and their corpses are gone). */
#define LAB_CLEARED_FLAG 215
static int enemy_room_cleared(int room, int cleared) { return cleared && room == 134; }

static void enemy_remove(int i) { enemy_recs[i] = enemy_recs[--enemy_n]; }

static int enemy_clear_room(int room) {
    int n = 0;
    for (int i = enemy_n - 1; i >= 0; i--) if (enemy_recs[i].room == room) { enemy_remove(i); n++; }
    return n;
}

/* clock went backwards (older save loaded): nothing stamped later can belong to this timeline */
static int enemy_purge_after(float now) {
    int n = 0;
    for (int i = enemy_n - 1; i >= 0; i--) if (enemy_recs[i].stamp > now && !enemy_is_wasp(&enemy_recs[i])) { enemy_remove(i); n++; }
    return n;
}

/* same (room, slot, gid, em) replaces: one enemy is one record even if the spawn code runs twice */
static int enemy_add(const EnemyRec *r) {
    for (int i = 0; i < enemy_n; i++) {
        const EnemyRec *o = &enemy_recs[i];
        if (o->room == r->room && o->slot == r->slot && o->gid == r->gid && o->em == r->em) { enemy_recs[i] = *r; return 1; }
    }
    if (enemy_n >= ENEMY_MAX) return 0;
    enemy_recs[enemy_n++] = *r;
    return 1;
}

/* text file: "RE1EN1" then "room slot em gid chr diff xbits zbits stampbits" (floats as hex bit patterns) */
static unsigned enemy_f2u(float f) { unsigned u; memcpy(&u, &f, 4); return u; }
static float enemy_u2f(unsigned u) { float f; memcpy(&f, &u, 4); return f; }

static int enemy_fmt_line(char *out, int cap, const EnemyRec *r) {
    static const char hex[] = "0123456789abcdef";
    const unsigned v[9] = {(unsigned)r->room, r->slot, r->em, r->gid, r->chr, r->diff, enemy_f2u(r->x), enemy_f2u(r->z), enemy_f2u(r->stamp)};
    int n = 0;
    for (int i = 0; i < 9; i++) {
        if (n + 10 > cap) return -1;
        for (int s = 28; s >= 0; s -= 4) out[n++] = hex[v[i] >> s & 15];
        out[n++] = i < 8 ? ' ' : '\n';
    }
    return n;
}

static int enemy_parse_line(const char *p, EnemyRec *r) {
    unsigned v[9];
    for (int i = 0; i < 9; i++) {
        unsigned x = 0; int d = 0;
        for (; (*p >= '0' && *p <= '9') || (*p >= 'a' && *p <= 'f'); p++, d++) x = x << 4 | (unsigned)(*p <= '9' ? *p - '0' : *p - 'a' + 10);
        if (d != 8 || *p != (i < 8 ? ' ' : '\n')) return 0;
        p++; v[i] = x;
    }
    r->room = (int)v[0]; r->slot = v[1]; r->em = v[2]; r->gid = v[3]; r->chr = v[4]; r->diff = v[5];
    r->x = enemy_u2f(v[6]); r->z = enemy_u2f(v[7]); r->stamp = enemy_u2f(v[8]);
    return r->room >= 0 && r->room < 154 && r->gid < 1024 && r->em < 64 && r->x == r->x && r->z == r->z && r->stamp == r->stamp;
}

/* whole table -> text; returns length or -1 */
static int enemy_serialize(char *out, int cap) {
    int n = 0;
    if (cap < 8) return -1;
    memcpy(out, "RE1EN1\n", 7); n = 7;
    for (int i = 0; i < enemy_n; i++) {
        int k = enemy_fmt_line(out + n, cap - n, &enemy_recs[i]);
        if (k < 0) return -1;
        n += k;
    }
    return n;
}

/* text -> table; a wrong header or a bad line is ignored (bad lines skipped, bad header = empty table) */
static void enemy_load_text(const char *text, int len) {
    enemy_n = 0;
    if (len < 7 || memcmp(text, "RE1EN1\n", 7)) return;
    for (int p = 7; p + 81 <= len && enemy_n < ENEMY_MAX; p += 81) { /* fixed width: 9 x 8 hex + 8 spaces + \n */
        EnemyRec r;
        if (enemy_parse_line(text + p, &r)) enemy_recs[enemy_n++] = r;
    }
}
#endif
