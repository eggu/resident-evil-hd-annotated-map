/* Reward state shared by puzzle and pickup labels: -1 collected, 0..4 puzzle, 5 collectible. */
/* ready=512: scripted reward enters inventory directly, so keep its puzzle until pickup. */
typedef struct { unsigned pickup, bank, ready, count, bits[4]; } RewardRule;
static unsigned reward_bit(const unsigned *bank, unsigned bit) {
    return bit < 512 && ((bank[bit >> 5] >> (bit & 31)) & 1);
}
static int reward_state(const RewardRule *rule, const unsigned *b1, const unsigned *b2, const unsigned *b3) {
    if (reward_bit(b3, rule->pickup)) return -1;
    unsigned count = 0;
    for (unsigned i = 0; i < rule->count; i++) count += reward_bit(b1, rule->bits[i]);
    if (count == rule->count && reward_bit(rule->bank == 2 ? b2 : b1, rule->ready)) return 5;
    return (int)count;
}
static int reward_visible(const RewardRule *rule, int kind, unsigned step,
                          const unsigned *b1, const unsigned *b2, const unsigned *b3) {
    int state = reward_state(rule, b1, b2, b3);
    return kind == 4 ? state == 5 : kind == 2 && state >= 0 && state < 5 && (unsigned)state == step;
}
