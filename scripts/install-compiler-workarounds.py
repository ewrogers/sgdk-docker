#!/usr/bin/env python3
"""Disable GCC 16.2's incorrect M68000 shared-pointer auto-increment fold."""
from pathlib import Path
import subprocess


def install():
    compiler = "/opt/m68k/bin/m68k-elf-gcc"
    # A driver default covers ordinary compilation and LTO, including projects
    # that replace EXTRA_FLAGS. Explicit -fauto-inc-dec remains available for
    # reproducing the compiler defect in the regression test.
    library = Path(subprocess.check_output([compiler, "-print-libgcc-file-name"], text=True).strip())
    target = library.parent / "specs"
    if target.exists():
        raise RuntimeError("Compiler already has custom specs; review before replacing them")
    target.write_text("*self_spec:\n%{!fauto-inc-dec:-fno-auto-inc-dec}\n")


if __name__ == "__main__":
    install()
