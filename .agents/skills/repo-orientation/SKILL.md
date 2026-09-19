---
name: repo-orientation
description: Map the Saint Tibo Codex 0.155.1 setup. Use when starting work, asking where files live, which CLI pin to use, or how skills, plugins, and agents are laid out.
---

Read `AGENTS.md`, `build/codex-pin.json`, `build/stack-pin.json`,
`build/stack-standard.md`, and `install/catalog.toml` first.

Report:

1. CLI pin: `0.155.1` / `rust-v0.155.1`. Reject alphas and `Codex.app`.
2. Bootstrap: `./setup` → `install/modules/<nn>-*`. Do not create a root file named `install`.
3. Repo skills: `.agents/skills/`. Plugin skill name `saint-tibo` is the only plugin skill and must stay unique.
4. Marketplace: `.agents/plugins/marketplace.json` → `./plugins/saint-tibo`.
5. Project config and custom agents: `.codex/config.toml`, `.codex/agents/{mapper,reviewer,implementer}.toml`.
6. Later working repo: `BAITC-Hacks/hack-a58598e0-saint-tibo`. Do not push it unless the owner asked.

App/runtime versions live in `build/stack-pin.json` schema 2. Web is
React + Vite, not Next.js. JS installer is bun. Host doctor:
`python3 scripts/check_stack.py`. Do not invent unpinned libraries.
This repository still has no application code.
