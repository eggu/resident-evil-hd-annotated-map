/* Native state evidence: diagnostics/mapoverlay-rebecca-review-20261017. */
static int rebecca_active(int chris, const unsigned *bank0, float timer) {
    unsigned started = (bank0[76/32] >> (76%32)) & 1;
    unsigned arrived = (bank0[32/32] >> (32%32)) & 1;
    unsigned rescued = (bank0[33/32] >> (33%32)) & 1;
    unsigned dead = (bank0[34/32] >> (34%32)) & 1;
    return chris && started && !rescued && !dead && (arrived || timer >= 3600.0f);
}
