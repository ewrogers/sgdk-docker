#!/usr/bin/env python3
"""Apply the narrowly scoped host portability fix to pinned SGDK sources."""
from pathlib import Path

source = Path("/opt/sgdk/tools/xgmtool/src/util.c")
data = source.read_bytes()
old = b"byte = round(sample);"
new = b"byte = (unsigned char) (int) round(sample);"
if data.count(old) != 2:
    raise RuntimeError("SGDK PCM conversion changed; review the portability patch")
# Negative floating-point values cannot be converted directly to unsigned char
# in portable C. Convert to a representable signed integer first, then let the
# defined unsigned conversion encode the signed 8-bit PCM sample.
source.write_bytes(data.replace(old, new))
