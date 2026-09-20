#!/usr/bin/env python3
"""Compare selected stack-pin versions to live latest. Network required.

ai.openai is compared to PyPI latest again — the LiteLLM openai<3 cap
is gone with LiteLLM. ai.bifrost is checked against the latest
transports/* release tag on GitHub (the Docker tag tracks it).
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
    ("frontend.forms.tanstack_form", "@tanstack/react-form"),
    ("runtimes.bun", "bun"),
    ("quality.biome", "@biomejs/biome"),
    ("quality.vitest", "vitest"),
    ("quality.playwright", "@playwright/test"),
]
PYPI = [
    ("backend.fastapi", "fastapi"),
    ("ai.openai", "openai"),
    ("quality.ty", "ty"),
    ("quality.ruff", "ruff"),
    ("quality.pytest", "pytest"),
    ("quality.pytest_asyncio", "pytest-asyncio"),
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


def github_latest_tag(repo: str, prefix: str) -> str:
    url = f"https://api.github.com/repos/{repo}/releases?per_page=100"
    with urllib.request.urlopen(url, timeout=20) as response:
        releases = json.load(response)
    tags = [r["tag_name"] for r in releases if r["tag_name"].startswith(prefix)]
    if not tags:
        raise SystemExit(f"no {prefix}* releases in {repo}")
    return tags[0]


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
    bifrost = pin.get("ai", {}).get("bifrost", {})
    pinned_tag = bifrost.get("github_tag", "")
    latest_tag = github_latest_tag("maximhq/bifrost", "transports/")
    mark = "OK" if pinned_tag == latest_tag else "DRIFT"
    if mark == "DRIFT":
        drift += 1
    print(f"{mark:5} {'ai.bifrost':28} pin={pinned_tag:12} latest={latest_tag} (transports tag)")
    if drift:
        print(f"DRIFT {drift} entries; update build/stack-pin.json and verified_on")
        return 1
    print("PASS stack pin matches live latest tags for tracked packages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
