#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "reward_state.h"
#include "reward_rules.h"
static void set(unsigned *bank, unsigned bit) { bank[bit/32] |= 1u << (bit%32); }
int main(void) {
    unsigned tests=0;
    for (unsigned id=1;id<sizeof reward_rules/sizeof *reward_rules;id++) {
        const RewardRule *r=&reward_rules[id];
        for (unsigned mask=0;mask<(1u<<r->count);mask++)
            for (unsigned ready=0;ready<2;ready++) for (unsigned taken=0;taken<2;taken++) {
                unsigned b1[16]={0},b2[16]={0},b3[16]={0},count=0;
                for (unsigned i=0;i<r->count;i++) if (mask>>i&1) {set(b1,r->bits[i]);count++;}
                if (ready && r->ready < 512) set(r->bank==2?b2:b1,r->ready);
                if (taken) set(b3,r->pickup);
                count=0;
                for(unsigned i=0;i<r->count;i++) count+=reward_bit(b1,r->bits[i]);
                int active=reward_bit(r->bank==2?b2:b1,r->ready);
                int expected=taken?-1:active&&count==r->count?5:(int)count;
                assert(reward_state(r,b1,b2,b3)==expected);
                unsigned puzzles=0;
                for(unsigned step=0;step<=r->count;step++) {
                    int shown=reward_visible(r,2,step,b1,b2,b3);
                    assert(shown==(expected>=0&&expected<5&&(unsigned)expected==step));
                    puzzles+=shown;
                }
                int item=reward_visible(r,4,0,b1,b2,b3);
                assert(item==(expected==5));
                assert(puzzles+item==(taken?0:1));
                assert(!reward_visible(r,7,0,b1,b2,b3));
                assert(!reward_bit(b1,512));
                tests++;
            }
    }
    /* Multi-reward grave: taking one crest cannot hide the remaining two. */
    {
        unsigned a[16]={0},b[16]={0},c[16]={0}; set(a,56);
        assert(reward_state(&reward_rules[14],a,b,c)==5);
        set(c,110);
        assert(reward_state(&reward_rules[14],a,b,c)==-1);
        assert(reward_state(&reward_rules[15],a,b,c)==5);
        assert(reward_state(&reward_rules[16],a,b,c)==5);
    }
    /* Small dining room: candle and cupboard are both required, in either order. */
    for(unsigned mask=0;mask<4;mask++) {
        unsigned a[16]={0},b[16]={0},c[16]={0};
        if(mask&1)set(a,32); if(mask&2)set(a,33);
        assert(reward_state(&reward_rules[12],a,b,c)==(mask==3?5:(mask!=0)));
    }
    assert(tests==164);
    printf("PASS: %u reward states; exactly one puzzle/pickup or none after collection\n",tests);
}
