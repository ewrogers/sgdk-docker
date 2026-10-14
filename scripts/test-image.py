#!/usr/bin/env python3
"""Exercise the real container tools and fresh upstream examples."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("--platform", required=True, choices=("linux/arm64", "linux/amd64"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    metadata = json.loads(subprocess.check_output(["docker", "image", "inspect", args.image], text=True))[0]
    assert metadata["Architecture"] == args.platform.split("/")[1], "Wrong image architecture"
    assert metadata["Config"]["User"] == "sgdk", "Image must default to an unprivileged user"
    base = ["docker", "run", "--rm", "--platform", args.platform,
            "--user", f"{os.getuid()}:{os.getgid()}", "-v", f"{output}:/workspace", args.image]

    def run(name, command, expected=0):
        with (output / f"{name}.log").open("w") as log:
            result = subprocess.run([*base, *command], stdout=log, stderr=subprocess.STDOUT)
        if result.returncode != expected:
            raise RuntimeError(f"{name}: expected exit {expected}, got {result.returncode}; see its log")
        return (output / f"{name}.log").read_text()

    doctor = run("doctor", ["doctor"])
    assert ("aarch64" if args.platform.endswith("arm64") else "x86_64") in doctor
    assert "16.2.0" in doctor and "2.47" in doctor and "18.1" in doctor
    assert "SGDK: 2.11" in doctor
    run("source-access", ["sh", "-c", 'test -r /usr/local/share/sgdk/sources/gcc.tar.xz && test -r /usr/local/share/sgdk/sources/gdb.tar.xz'])
    # The generic entrypoint must preserve arguments and command failures.
    assert run("arguments", ["sh", "-c", 'printf "%s\\n" "$@"', "label", "two words", "semi;colon"]) == "two words\nsemi;colon\n"
    run("command-failure", ["sh", "-c", "exit 17"], expected=17)
    (output / "smoke.c").write_text("int answer(int x) { return x + 42; }\n")
    (output / "smoke.s").write_text(".text\n.globl entry\nentry:\n moveq #42,%d0\n rts\n")
    run("compile", ["m68k-elf-gcc", "-m68000", "-std=c17", "-g", "-c", "smoke.c", "-o", "smoke.o"])
    run("assemble", ["m68k-elf-as", "-m68000", "smoke.s", "-o", "assembly.o"])
    assert "elf32-m68k" in run("object", ["m68k-elf-objdump", "-f", "smoke.o"])
    debug = run("debugger", ["m68k-elf-gdb", "--batch", "-ex", "file smoke.o", "-ex", "info functions answer"])
    assert "answer" in debug
    # This upstream VGM includes negative PCM samples. ARM64 used to turn them
    # into zero because xgmtool converted negative doubles straight to unsigned.
    run("pcm-conversion", ["xgmtool", "/opt/sgdk/sample/game/platformer/res/sound/sonic2Emerald.vgm", "pcm.bin", "-s"])
    assert hashlib.sha256((output / "pcm.bin").read_bytes()).hexdigest() == "c464966762d769dbe7b1aa78d495a2847c5133896bc3636dfb9053ac2b1cf49f", "PCM conversion differs from the established AMD64 output"
    # A sample near a rounding boundary exposed ARM64's fused operations.
    run("pcm-rounding", ["xgmtool", "/opt/sgdk/sample/snd/xgm-player/res/SMetroid Crateria Surface.vgm", "pcm-rounding.bin", "-s"])
    assert hashlib.sha256((output / "pcm-rounding.bin").read_bytes()).hexdigest() == "cc2d6ad87a98a16481602de4a6ab91e8338addfd35e2636371eae7e5ae3a95db", "PCM resampling rounding differs between hosts"
    samples = ["basics/hello-world", "basics/image", "game/platformer", "snd/sound-test", "snd/xgm-player"]
    results = []
    for sample in samples:
        name = sample.split("/")[-1]
        run(f"copy-{name}", ["sh", "-c", 'test ! -e "$GDK/sample/$1/out/rom.bin" && cp -R "$GDK/sample/$1" "$2"', "copy", sample, name])
        run(f"build-{name}", ["build", "-C", name, "release"])
        data = (output / name / "out/rom.bin").read_bytes()
        assert data[0x100:0x104] == b"SEGA" and len(data) % 131072 == 0
        # SGDK's sizebnd uses its own XOR checksum, not Sega's word-sum format.
        stored = int.from_bytes(data[0x18e:0x190], "big")
        raw = bytearray(data)
        raw[0x18e:0x190] = b"\0\0"
        checksum = 0
        for index in range(0, len(raw), 4):
            checksum ^= int.from_bytes(raw[index:index + 4], "big")
        assert stored == (checksum ^ (checksum >> 16)) & 65535
        results.append({"sample": sample, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        print(f"Passed {sample}: {len(data):,} bytes", flush=True)
    run("clean", ["build", "-C", "hello-world", "clean"])
    run("debug-build", ["build", "-C", "hello-world", "debug"])
    run("debug-symbols", ["m68k-elf-gdb", "--batch", "-ex", "file hello-world/out/rom.out", "-ex", "info functions main"])
    (output / "hello-world/src/main.c").write_text("#error Intentional failure: verify build errors reach the caller\n")
    with (output / "build-failure.log").open("w") as log:
        result = subprocess.run([*base, "build", "-C", "hello-world", "release"], stdout=log, stderr=subprocess.STDOUT)
    assert result.returncode != 0, "Compiler failures must propagate"
    report = {"passed": True, "platform": args.platform, "image_id": metadata["Id"],
              "samples": results, "doctor": doctor, "input_sources": "Unmodified SGDK 2.11 examples bundled in the image"}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Passed {args.platform}; report: {output / 'report.json'}")


if __name__ == "__main__":
    main()
