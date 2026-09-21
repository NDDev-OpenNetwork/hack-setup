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
    ("lsp.typescript_stdio", "typescript-language-server"),
    ("lsp.json_html_css", "vscode-langservers-extracted"),
    ("lsp.yaml", "yaml-language-server"),
    ("lsp.shell", "bash-language-server"),
    ("lsp.dockerfile", "dockerfile-language-server-nodejs"),
]
PYPI = [
    ("backend.fastapi", "fastapi"),
    ("ai.openai", "openai"),
    ("quality.ty", "ty"),
    ("quality.ruff", "ruff"),
    ("quality.pytest", "pytest"),
    ("quality.pytest_asyncio", "pytest-asyncio"),
    ("runtimes.uv", "uv"),
    ("mcp.serena", "serena-agent"),
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
    # Stable releases only — a prerelease/draft tag must never read as
    # "latest" and trigger a false DRIFT (#19).
    tags = [
        r["tag_name"]
        for r in releases
        if r["tag_name"].startswith(prefix)
        and not r.get("prerelease")
        and not r.get("draft")
    ]
    if not tags:
        raise SystemExit(f"no stable {prefix}* releases in {repo}")
    return tags[0]


def node_lts() -> str:
    with urllib.request.urlopen("https://nodejs.org/dist/index.json", timeout=20) as response:
        rows = json.load(response)
    for row in rows:
        if row.get("lts"):
            return str(row["version"]).lstrip("v")
    raise SystemExit("no Node LTS in index.json")


def row(latest_fn) -> tuple[str | None, str | None]:
    """One lookup — a failure is an ERR row, never a silent skip or an
    abort that hides the remaining rows (#19). Returns (latest, err)."""
    try:
        return latest_fn(), None
    except SystemExit as exc:  # "no stable releases" style lookups
        return None, str(exc)
    except Exception as exc:
        return None, str(exc)


def mark(pinned: str, latest: str | None, err: str | None) -> str:
    if err is not None or latest is None:
        return "ERR"
    return "OK" if latest == pinned else "DRIFT"


def main() -> int:
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    print(f"pin verified_on={pin.get('verified_on')} schema={pin.get('schema_version')}")
    drift = 0
    errors = 0
    registry_rows = [(label, pkg, npm_latest) for label, pkg in NPM] + [
        (label, pkg, pypi_latest) for label, pkg in PYPI
    ]
    for label, package, fn in registry_rows:
        pinned = lookup(pin, label)
        latest, err = row(lambda f=fn, p=package: f(p))
        m = mark(pinned, latest, err)
        drift += m == "DRIFT"
        errors += m == "ERR"
        print(f"{m:5} {label:28} pin={pinned:12} latest={latest or err}")
    pinned_node = lookup(pin, "runtimes.node")
    latest_node, err = row(node_lts)
    m = mark(pinned_node, latest_node, err)
    drift += m == "DRIFT"
    errors += m == "ERR"
    print(f"{m:5} {'runtimes.node':28} pin={pinned_node:12} latest={latest_node or err} (newest LTS row)")
    github_rows = [("ai.bifrost", pin.get("ai", {}).get("bifrost", {}))]
    for name, entry in pin.get("lsp", {}).items():
        if isinstance(entry, dict) and entry.get("github_tag"):
            github_rows.append((f"lsp.{name}", entry))
    for label, entry in github_rows:
        pinned_tag = entry.get("github_tag", "")
        latest_tag, err = row(
            lambda e=entry: github_latest_tag(
                e.get("github_repo", ""), e.get("github_prefix", "")
            )
        )
        m = mark(pinned_tag, latest_tag, err)
        drift += m == "DRIFT"
        errors += m == "ERR"
        print(f"{m:5} {label:28} pin={pinned_tag:22} latest={latest_tag or err}")
    if errors:
        print(f"ERR {errors} lookups failed — pin state unknown, not verified")
        return 2
    if drift:
        print(f"DRIFT {drift} entries; update build/stack-pin.json and verified_on")
        return 1
    print("PASS stack pin matches live latest tags for tracked packages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
