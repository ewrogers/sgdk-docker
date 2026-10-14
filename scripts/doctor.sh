#!/bin/sh
set -eu
printf 'Host: '; uname -m
printf 'SGDK: '; sed -n 's/^#define SGDK_VERSION *//p' "$GDK/inc/genesis.h"
printf 'Target: '; m68k-elf-gcc -dumpmachine
printf 'GCC: '; m68k-elf-gcc -dumpfullversion
m68k-elf-ld --version | head -1
java -version
m68k-elf-gdb --version | head -1
printf 'C flags: %s\n' "$EXTRA_FLAGS"
for tool in make git python3 m68k-elf-as m68k-elf-ar m68k-elf-objcopy m68k-elf-gdb bintos sjasm xgmtool convsym mac68k; do
    command -v "$tool"
done
