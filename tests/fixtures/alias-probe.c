/* SGDK's CPU-transfer access pattern: u16 producers, u32 bulk reads. */
typedef unsigned short u16;
typedef unsigned long u32;

__attribute__((noipa)) static u32 update(u16 *word, u32 *pair)
{
    *pair = 0xAABBCCDD;
    *word = 0x1234;
    return *pair;
}

int probe(void)
{
    u32 pair;
    u32 result = update((u16 *)&pair, &pair);
    return result != 0x1234CCDD;
}
