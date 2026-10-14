#!/usr/bin/env python3
"""Require equivalent ROM output from both native host architectures."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arm64", type=Path)
    parser.add_argument("amd64", type=Path)
    args = parser.parse_args()
    arm, amd = [json.loads(path.read_text()) for path in [args.arm64, args.amd64]]
    assert arm["passed"] and amd["passed"]
    assert arm["platform"] == "linux/arm64" and amd["platform"] == "linux/amd64"
    for field in ["bytes", "sha256"]:
        left = {sample["sample"]: sample[field] for sample in arm["samples"]}
        right = {sample["sample"]: sample[field] for sample in amd["samples"]}
        assert len(left) == 5 and left == right, f"Architecture output differs: {field}"
    print("Both architectures passed and generated identical ROMs for all five examples.")


if __name__ == "__main__":
    main()
