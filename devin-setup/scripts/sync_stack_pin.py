#!/usr/bin/env python3
"""Sync devin-setup/build/stack-pin.json from the root stack pin.

The shared install modules (member, runtimes) read
$HACK_REPO_ROOT/build/stack-pin.json. devin-setup keeps that contract
by projecting the root pin byte-for-byte into its own build/ — a
generated copy, not a second law. check_devin_setup.py fails on drift.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "build" / "stack-pin.json"
TARGET = ROOT / "build" / "stack-pin.json"


def main() -> int:
    if not SOURCE.is_file():
        print(f"missing source pin {SOURCE}", file=sys.stderr)
        return 1
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)
    print(f"synced {TARGET.relative_to(ROOT.parent)} <- {SOURCE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
