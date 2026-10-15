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
    for report in [arm, amd]:
        regression = report.get("m68k_copy_regression", {})
        assert regression.get("sdk_upload_download") == "passed", "Missing executed SDK copy regression"
        assert regression.get("compiler_default") == "passed", "Missing compiler default regression"
        assert regression.get("negative_control") == "reproduced", "Missing failing negative control"
        assert regression.get("far_branch") == "passed", "Missing M68000 far-branch regression"
        assert regression.get("cpu_policy") == "passed", "Missing M68000 CPU policy regression"
    for field in ["bytes", "sha256"]:
        left = {sample["sample"]: sample[field] for sample in arm["samples"]}
        right = {sample["sample"]: sample[field] for sample in amd["samples"]}
        assert len(left) == 5 and left == right, f"Architecture output differs: {field}"
    print("Both architectures passed and generated identical ROMs for all five examples.")


if __name__ == "__main__":
    main()
