/* Spawn guards verified against native room/event code; pickup flags remain bank3. */
static int state_bit(const unsigned *bank,unsigned n) { return (bank[n/32]>>(n%32))&1; }
static int companion_dead(int jill,const unsigned *b0) { return state_bit(b0,jill?37:34); }
/* Generated from the native per-room "all items taken" predicates (0x4830b0.. range; tools/item_gates.py).
 * A listed pickup can only exist when one term holds; literal = 0x8000 | bank<<10 | index<<1 | wanted value. */
#define GATE_TERMS 3
#define GATE_LITS 6
typedef struct { unsigned short room, flag, jill, term[GATE_TERMS][GATE_LITS]; } ItemGate;
static const ItemGate item_gates[] = {
    {0,128,0,{{0x80c3,0x80c4,0x80c6}}},
    {0,128,1,{{0x8044,0x80c5,0x80c6,0x80c8,0x8452},{0x8045,0x808b,0x80c5,0x80c6,0x80c8,0x8452}}},
    {0,129,0,{{0x80c2,0x8453,0x8454},{0x80c3,0x80c4,0x80c7,0x8453,0x8454},{0x80c3,0x80c5,0x8453,0x8454}}},
    {0,129,1,{{0x8044,0x8453},{0x8045,0x808b,0x8453}}},
    {0,509,0,{{0x84b7}}},
    {0,509,1,{{0x84b7}}},
    {3,16,0,{{0x8fc7}}},
    {3,16,1,{{0x8fc7}}},
    {3,31,0,{{0x8fc7}}},
    {3,32,1,{{0x8fc7}}},
    {5,130,0,{{0x848b}}},
    {5,130,1,{{0x848b}}},
    {12,194,0,{{0x84cc}}},
    {12,194,1,{{0x84cc}}},
    {12,195,0,{{0x84cc}}},
    {12,195,1,{{0x84cc}}},
    {12,196,0,{{0x84cc}}},
    {12,196,1,{{0x84cc}}},
    {12,197,0,{{0x84cc}}},
    {12,197,1,{{0x84cc}}},
    {12,198,0,{{0x84cc}}},
    {12,198,1,{{0x84cc}}},
    {13,347,0,{{0x842f}}},
    {13,347,1,{{0x842f}}},
    {22,207,1,{{0x80c0}}},
    {22,209,1,{{0x80c0}}},
    {22,211,1,{{0x80c0}}},
    {24,88,0,{{0x8547}}},
    {24,88,1,{{0x8547}}},
    {24,89,0,{{0x8547}}},
    {24,89,1,{{0x8547}}},
    {24,90,0,{{0x8547}}},
    {24,90,1,{{0x8547}}},
    {24,92,0,{{0x8547}}},
    {24,92,1,{{0x8547}}},
    {24,93,0,{{0x8547}}},
    {24,93,1,{{0x8547}}},
    {24,509,0,{{0x861b}}},
    {24,509,1,{{0x861b}}},
    {27,119,0,{{0x8c8b}}},
    {27,119,1,{{0x8c8b}}},
    {27,120,0,{{0x8c8b}}},
    {27,120,1,{{0x8c8b}}},
    {27,121,0,{{0x8c8b}}},
    {27,121,1,{{0x8c8b}}},
    {27,122,0,{{0x8c8b}}},
    {27,122,1,{{0x8c8b}}},
    {48,466,0,{{0x8521}}},
    {48,466,1,{{0x8521}}},
    {49,34,0,{{0x8fe9}}},
    {49,34,1,{{0x8fe9}}},
    {58,190,0,{{0x8d1d,0x8d1f}}},
    {58,190,1,{{0x8d1d,0x8d1f}}},
    {58,191,0,{{0x8d1d,0x8d1f}}},
    {58,191,1,{{0x8d1d,0x8d1f}}},
    {58,486,0,{{0x8d1d,0x8d1f}}},
    {58,486,1,{{0x8d1d,0x8d1f}}},
    {93,123,1,{{0x8049}}},
    {93,506,1,{{0x8049}}},
    {94,338,0,{{0x8537}}},
    {94,338,1,{{0x8537}}},
    {114,170,0,{{0x8fcb}}},
    {114,170,1,{{0x8fcb}}},
};
static int gate_open(int source,unsigned flag,int jill,const unsigned *b0,const unsigned *b1,const unsigned *b3) {
    const unsigned *const banks[4]={b0,b1,0,b3};
    for (unsigned i=0;i<sizeof item_gates/sizeof *item_gates;i++) {
        const ItemGate *g=&item_gates[i];
        if (g->room!=(unsigned)source || g->flag!=flag || g->jill!=(unsigned)!!jill) continue;
        for (int t=0;t<GATE_TERMS && g->term[t][0];t++) {
            int all=1;
            for (int l=0;l<GATE_LITS && g->term[t][l];l++) {
                unsigned v=g->term[t][l];
                if (state_bit(banks[v>>10&7],v>>1&511)!=(int)(v&1)) all=0;
            }
            if (all) return 1;
        }
        return 0;
    }
    return 1;
}
static int placed_item_available(int kind,unsigned flag,int source,int jill,const unsigned *b0,const unsigned *b1,const unsigned *b3) {
    /* Synthetic fuel labels have no bank3 pickup bit: charge339, inserted270, power271. */
    if (kind==2 && flag==512) return !state_bit(b1,339) && !state_bit(b1,270) && !state_bit(b1,271);
    if (kind==2 && flag==513) return state_bit(b1,339) && !state_bit(b1,270) && !state_bit(b1,271);
    if (kind==4 && flag==514) return state_bit(b1,270) && !state_bit(b1,271);
    if (kind==2 && flag==515) return !state_bit(b1,110) && !state_bit(b3,207);
    if (kind==4 && flag==208 && source==22) return 0; /* Spent rack item intentionally hidden. */
    if (kind==1 && (flag==45 || flag==47)) return companion_dead(jill,b0);
    if (kind==4 && flag==405) return companion_dead(jill,b0) && state_bit(b1,216);
    if (kind==5 && flag==509) return state_bit(b1,source==0?91:269);
    if (kind==5 && flag==506) return jill && state_bit(b0,36);
    if (kind==5 && (flag==482 || flag==490)) {
        if (state_bit(b3,482) || state_bit(b3,490)) return 0;
        if (!jill) return flag==482;
        int alternate=state_bit(b0,98) && (!state_bit(b0,99) || state_bit(b0,139) || state_bit(b1,9));
        return flag==490 ? alternate : !alternate && state_bit(b0,139);
    }
    /* X-Ray Room A board (handlers 0x6614e0 slot 1 -> bank1 205/206, 0x661660 slot 2 -> 207/208): a photo on the board has
     * been used there; its retake row is no target (user decision 2026-11-09), so the two board rows never show. */
    if (kind==4 && source==138 && (flag==392 || flag==393)) return 0;
    if (kind==4 && flag==320) return state_bit(b1,139);
    /* Old Key (Chris) in the 1F bathtub: room init 0x4a60c4 spawns it only once the tub is drained, bank1[37]. */
    if (kind==4 && flag==77) return state_bit(b1,37);
    if (kind==4 && flag==69 && source==116) return state_bit(b1,62);
    /* Crypt ammo: native 0x4a7bc6..0x4a7c69 requires all four masks inserted. */
    if (kind==7 && flag==463 && source==11) return state_bit(b1,50) && state_bit(b1,51) && state_bit(b1,52) && state_bit(b1,53);
    /* weapons below are key items (kind 4) since 2026-11-07, as in RE0 HD */
    if (kind==4 && flag==23 && source==53) return jill && state_bit(b0,7);
    if (kind==4 && flag==401 && source==122) return !jill && state_bit(b0,98);
    if (kind==4 && flag==123 && source==93) return jill && state_bit(b0,37);
    return kind<4 || gate_open(source,flag,jill,b0,b1,b3);
}
