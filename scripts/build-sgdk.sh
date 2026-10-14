#!/bin/sh
set -eu
python3 /build/fetch-sources.py sgdk sjasm maccer
mkdir -p /opt/sgdk /build/sjasm /build/maccer
tar -xf /opt/sources/sgdk.tar.gz --strip-components=1 -C /opt/sgdk
python3 /build/patch-sgdk.py
tar -xf /opt/sources/sjasm.tar.gz --strip-components=1 -C /build/sjasm
unzip -q /opt/sources/maccer.zip -d /build/maccer
# Replace Windows binaries and rebuild libraries with this exact GCC version.
find /opt/sgdk/bin -type f \( -name '*.exe' -o -name '*.dll' \) -delete
rm -f /opt/sgdk/lib/*.a
gcc -O2 /opt/sgdk/tools/bintos/src/bintos.c -o /opt/sgdk/bin/bintos
# ARM64 can fuse PCM resampling arithmetic; use identical rounding on both hosts.
gcc -O2 -ffp-contract=off -I/opt/sgdk/tools/xgmtool/inc /opt/sgdk/tools/xgmtool/src/*.c -lm -o /opt/sgdk/bin/xgmtool
g++ -std=c++20 -O2 -I/opt/sgdk/tools/convsym/include /opt/sgdk/tools/convsym/src/main.cpp -o /opt/sgdk/bin/convsym
cd /build/sjasm/Sjasm
# Upstream's makefile expects lower case on a case-sensitive Linux filesystem.
mv Sjasm.cpp sjasm.cpp
make -f ../Makefile
install sjasm /opt/sgdk/bin/sjasm
cd /build/maccer
gcc main.c -O2 '-DVERSION_STRING="2.6"' '-DKMOD_VERSION="0.2"' -lm -o /opt/sgdk/bin/mac68k
cd /opt/sgdk
make -f makelib.gen clean
make -f makelib.gen -j1 release EXTRA_FLAGS=-std=gnu17
make -f makelib.gen cleanobj cleandep
make -f makelib.gen -j1 debug EXTRA_FLAGS=-std=gnu17
make -f makelib.gen cleanobj cleandep cleanlst
# Samples remain available as source templates, never as prebuilt proof ROMs.
find sample -type d -name out -prune -exec rm -rf '{}' +
rm -rf /build/sjasm /build/maccer
