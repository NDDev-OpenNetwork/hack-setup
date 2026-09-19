#!/usr/bin/env python3
"""Compare selected stack-pin versions to live latest. Network required.

Packages marked reverify=pinned-compatible (openai 2.9.0) are not compared
to npm/PyPI latest.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN_PATH = ROOT / "build" / "stack-pin.json"
NPM = [
    ("frontend.react", "react"),
    ("frontend.vite", "vite"),
    ("frontend.tailwindcss", "tailwindcss"),
    ("frontend.shadcn", "shadcn"),
    ("frontend.zod", "zod"),
    ("runtimes.bun", "bun"),
    ("quality.biome", "@biomejs/biome"),
    ("quality.vitest", "vitest"),
    ("quality.playwright", "@playwright/test"),
]
PYPI = [
    ("backend.fastapi", "fastapi"),
    ("quality.ruff", "ruff"),
    ("quality.pytest", "pytest"),
    ("runtimes.uv", "uv"),
]


def lookup(data: dict[str, object], dotted: str) -> str:
    cur: object = data
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            raise SystemExit(f"missing {dotted}")
        cur = cur[part]
    if not isinstance(cur, dict):
        raise SystemExit(f"{dotted} is not an object")
    version = cur.get("version")
    if not isinstance(version, str):
        raise SystemExit(f"{dotted}.version missing")
    return version


def npm_latest(name: str) -> str:
    with urllib.request.urlopen(f"https://registry.npmjs.org/{name}", timeout=20) as response:
        payload = json.load(response)
    return str(payload["dist-tags"]["latest"])


def pypi_latest(name: str) -> str:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=20) as response:
        payload = json.load(response)
    return str(payload["info"]["version"])


def node_lts() -> str:
    with urllib.request.urlopen("https://nodejs.org/dist/index.json", timeout=20) as response:
        rows = json.load(response)
    for row in rows:
        if row.get("lts"):
            return str(row["version"]).lstrip("v")
    raise SystemExit("no Node LTS in index.json")


def main() -> int:
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    print(f"pin verified_on={pin.get('verified_on')} schema={pin.get('schema_version')}")
    drift = 0
    for label, package in NPM:
        pinned = lookup(pin, label)
        latest = npm_latest(package)
        mark = "OK" if pinned == latest else "DRIFT"
        if mark == "DRIFT":
            drift += 1
        print(f"{mark:5} {label:28} pin={pinned:12} latest={latest}")
    for label, package in PYPI:
        pinned = lookup(pin, label)
        latest = pypi_latest(package)
        mark = "OK" if pinned == latest else "DRIFT"
        if mark == "DRIFT":
            drift += 1
        print(f"{mark:5} {label:28} pin={pinned:12} latest={latest}")
    pinned_node = lookup(pin, "runtimes.node")
    latest_node = node_lts()
    mark = "OK" if pinned_node == latest_node else "DRIFT"
    if mark == "DRIFT":
        drift += 1
    print(f"{mark:5} {'runtimes.node':28} pin={pinned_node:12} latest={latest_node} (newest LTS row)")
    if drift:
        print(f"DRIFT {drift} entries; update build/stack-pin.json and verified_on")
        return 1
    print("PASS stack pin matches live latest tags for tracked packages")
    print("NOTE openai 2.9.0 is pinned-compatible for LiteLLM, not latest 3.x")
    return 0


if __name__ == "__main__":
    sys.exit(main())
