/* self-check of the record/visibility predicate: zig cc test_enemy_rec.c -o t && ./t */
#include <assert.h>
#include <stdio.h>
#include "enemy_rec.h"
int main(void) {
    EnemyRec z = {10, 2, 20, 77, 1, 2, 100.f, -50.f, 1000.f};
    assert(enemy_shown(&z, 1, 2, 1500.f, 1, 0));            /* alive, visited, same mode */
    assert(!enemy_shown(&z, 1, 2, 1500.f, 1, 1));           /* killed (also: revived crimson is drawn by the crimson code) */
    assert(!enemy_shown(&z, 1, 2, 1500.f, 0, 0));           /* room not visited in this save */
    assert(!enemy_shown(&z, 0, 2, 1500.f, 1, 0));           /* other character */
    assert(!enemy_shown(&z, 1, 4, 1500.f, 1, 0));           /* other difficulty */
    assert(!enemy_shown(&z, 1, 2, 900.f, 1, 0));            /* older save: record is from the future */
    assert(enemy_diff_class(0) == 1 && enemy_diff_class(3) == 1 && enemy_diff_class(1) == 2 && enemy_diff_class(2) == 4);
    enemy_enter_reset();
    assert(!enemy_stale(&z));                                 /* entry not seen: unchanged behaviour */
    enemy_enter(10, 900.f); assert(!enemy_stale(&z));         /* entered before the spawn: still there */
    enemy_enter(10, 1001.f); assert(!enemy_stale(&z));        /* a spawn within the slack of the entry is that load's */
    enemy_enter(10, 1004.f); assert(enemy_stale(&z));         /* entered later, nothing respawned: gone (wasps after insecticide) */
    assert(!enemy_stale(&(EnemyRec){11, 1, 12, 0, 1, 2, 0, 0, 1000.f}));   /* another room is untouched */
    enemy_enter_reset(); assert(!enemy_stale(&z));
    EnemyRec a = z, b = z; b.room = 11; b.stamp = 2000.f;
    assert(enemy_add(&a) && enemy_add(&b) && enemy_n == 2);
    a.x = 1.f; assert(enemy_add(&a) && enemy_n == 2);        /* same key replaces */
    assert(enemy_purge_after(1500.f) == 1 && enemy_n == 1 && enemy_recs[0].room == 10);
    assert(enemy_clear_room(10) == 1 && enemy_n == 0);
    enemy_add(&a); enemy_add(&b);
    static char buf[ENEMY_MAX * 90 + 16];
    int n = enemy_serialize(buf, sizeof buf);
    assert(n == 7 + 2 * 81);
    enemy_n = 0; enemy_load_text(buf, n);
    assert(enemy_n == 2 && enemy_recs[0].x == 1.f && enemy_recs[1].stamp == 2000.f);
    buf[10] = 'z'; enemy_load_text(buf, n); assert(enemy_n == 1);   /* corrupt line skipped */
    buf[0] = 'X'; enemy_load_text(buf, n); assert(enemy_n == 0);    /* corrupt header: empty */
    /* the Insecticide (bank1 188) removes the wasps (em 12) of the Central Corridor (room 109) and the Gallery (room 112), nothing else */
    EnemyRec w1 = {109, 0, WASP_EM, 0, 1, 2, 0, 0, 100.f}, w2 = {112, 1, WASP_EM, 0, 1, 2, 0, 0, 100.f}, w3 = {40, 0, WASP_EM, 0, 1, 2, 0, 0, 100.f}, z1 = {109, 0, 20, 5, 1, 2, 0, 0, 100.f};
    assert(WASP_NEST_FLAG == 188 && WASP_EM == 12);
    assert(!enemy_wasp_gone(&w1, 0) && !enemy_wasp_gone(&w2, 0));            /* flag clear: shown */
    assert(enemy_wasp_gone(&w1, 1) && enemy_wasp_gone(&w2, 1));             /* flag set: all wasp records of the two rooms, old or new */
    assert(!enemy_wasp_gone(&w3, 1) && !enemy_wasp_gone(&z1, 1));           /* another room, another enemy: untouched */
    /* wasps do not depend on the session clock: a newer save's record, an entry or a purge from another save keep them */
    assert(enemy_shown(&w1, w1.chr, w1.diff, w1.stamp - 500.f, 1, 0) && !enemy_shown(&z1, z1.chr, z1.diff, z1.stamp - 500.f, 1, 0));
    enemy_enter(w1.room, w1.stamp + 100.f); assert(!enemy_stale(&w1));
    enemy_n = 0; enemy_recs[enemy_n++] = w1; enemy_recs[enemy_n++] = z1;
    assert(enemy_purge_after(-1.f) == 1 && enemy_n == 1 && enemy_recs[0].em == WASP_EM);
    EnemyRec ty = {148, 0, TYRANT_EM, 657, 1, 2, 0, 0, 100.f}, ty2 = ty; ty2.room = 75;
    assert(!enemy_tyrant_gone(&ty, 0) && enemy_tyrant_gone(&ty, 1) && !enemy_tyrant_gone(&ty2, 1) && !enemy_tyrant_gone(&z1, 1));
    assert(LAB_CLEARED_FLAG == 215 && enemy_room_cleared(134, 1) && !enemy_room_cleared(134, 0) && !enemy_room_cleared(133, 1));
    puts("enemy_rec ok");
    return 0;
}
