#include <genesis.h>

/* The real SGDK upload/download functions and normal release LTO are used.
 * The test runner supplies memory for the hardware addresses and holds the
 * Z80 bus. No emulated Z80 or audio device is needed to verify byte copies. */
static const u8 driver[8192] = {
    0xf3, 0xc3, 0xb7, 0x02, [8190] = 0xa5, [8191] = 0x5a
};
static u8 downloaded[8194];

__attribute__((noipa)) int main(bool hard_reset)
{
    (void)hard_reset;
    Z80_upload(0, driver, sizeof(driver));
    for (u16 i = 0; i < sizeof(driver); i++)
        if (((vu8 *)Z80_RAM)[i] != driver[i]) return 1;

    downloaded[0] = 0x69;
    downloaded[8193] = 0x96;
    Z80_download(0, downloaded + 1, sizeof(driver));
    for (u16 i = 0; i < sizeof(driver); i++)
        if (downloaded[i + 1] != driver[i]) return 2;
    if (downloaded[0] != 0x69 || downloaded[8193] != 0x96) return 3;

    /* Zero length, odd lengths, unaligned sources and guarded destinations. */
    static const u16 lengths[] = {0, 1, 2, 3, 31, 255, 256, 511};
    for (u16 test = 0; test < sizeof(lengths) / sizeof(lengths[0]); test++)
    {
        u16 size = lengths[test];
        vu8 *memory = (vu8 *)(Z80_RAM + 0x100);
        memory[-1] = 0x69;
        memory[size] = 0x96;
        Z80_upload(0x100, driver + 1, size);
        for (u16 i = 0; i < size; i++)
            if (memory[i] != driver[i + 1]) return 4;
        if (memory[-1] != 0x69 || memory[size] != 0x96) return 5;
        downloaded[0] = 0x69;
        downloaded[size + 1] = 0x96;
        Z80_download(0x100, downloaded + 1, size);
        for (u16 i = 0; i < size; i++)
            if (downloaded[i + 1] != driver[i + 1]) return 6;
        if (downloaded[0] != 0x69 || downloaded[size + 1] != 0x96) return 7;
    }
    return 0;
}
