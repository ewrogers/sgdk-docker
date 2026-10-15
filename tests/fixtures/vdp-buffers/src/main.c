#include <genesis.h>

/* Exercise the actual SDK CPU-transfer routine under release LTO. The runner
 * records VDP writes; it does not pretend to emulate graphics hardware. */
__attribute__((noipa)) int main(bool hard_reset)
{
    (void)hard_reset;
    u16 colors[64];
    u16 text[33];
    for (u16 i = 0; i < 64; i++) colors[i] = 0x0200 + i * 2;
    DMA_doCPUCopyDirect(0xC0000000, colors, 64, -1);
    for (u16 i = 0; i < 33; i++) text[i] = 0xA000 + i;
    DMA_doCPUCopyDirect(0x40000000, text, 33, -1);
    /* Word-aligned, not necessarily long-aligned, including the tail loop. */
    DMA_doCPUCopyDirect(0x40000000, text + 1, 17, -1);
    return 0;
}
