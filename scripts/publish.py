#!/usr/bin/env python3
"""Publish only the exact local image IDs that passed both platform tests."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="ewrogers/sgdk")
    parser.add_argument("--version", default="2.11-gcc16.2.0-binutils2.47")
    parser.add_argument("--arm64", type=Path, required=True, help="Passed ARM64 report.json")
    parser.add_argument("--amd64", type=Path, required=True, help="Passed AMD64 report.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    subprocess.run([sys.executable, str(root / "compare-reports.py"), str(args.arm64), str(args.amd64)], check=True)
    reports = [json.loads(path.read_text()) for path in [args.arm64, args.amd64]]
    # Resolve every report before any registry mutation.
    for report in reports:
        metadata = json.loads(subprocess.check_output(["docker", "image", "inspect", report["image_id"]], text=True))[0]
        assert metadata["Architecture"] == report["platform"].split("/")[1]
    digests = []
    for report in reports:
        arch = report["platform"].split("/")[1]
        tag = f"{args.image}:{args.version}-{arch}"
        subprocess.run(["docker", "tag", report["image_id"], tag], check=True)
        subprocess.run(["docker", "push", tag], check=True)
        metadata = json.loads(subprocess.check_output(["docker", "image", "inspect", tag], text=True))[0]
        digests.append(next(value for value in metadata["RepoDigests"] if value.startswith(args.image + "@")))
    subprocess.run(["docker", "buildx", "imagetools", "create", "--tag", f"{args.image}:{args.version}",
                    "--tag", f"{args.image}:2.11", "--tag", f"{args.image}:latest", *digests], check=True)
    manifest = json.loads(subprocess.check_output(["docker", "buildx", "imagetools", "inspect", f"{args.image}:{args.version}", "--raw"], text=True))
    platforms = {entry["platform"]["architecture"] for entry in manifest["manifests"]}
    assert platforms == {"arm64", "amd64"}, "Published index must contain both tested architectures"
    print(f"Published {args.image}:{args.version} with native ARM64 and AMD64 images.")


if __name__ == "__main__":
    main()
