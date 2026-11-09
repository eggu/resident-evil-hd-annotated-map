/* The one bhd.exe build this mod's native addresses belong to: PE header values, which the Steam stub leaves alone. */
#define EXE_TIMESTAMP   0x6a27c7dfu
#define EXE_IMAGE_SIZE  0x9a6000u
static int exe_supported(const unsigned char *image) {
    if (image[0] != 'M' || image[1] != 'Z') return 0;
    const unsigned char *pe = image + *(const int *)(image + 0x3c);
    return *(const unsigned *)(pe + 8) == EXE_TIMESTAMP && *(const unsigned *)(pe + 0x50) == EXE_IMAGE_SIZE;
}
