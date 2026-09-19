---
name: repo-orientation
description: Map the Saint Tibo Codex 0.155.1 setup. Use when starting work, asking where files live, which CLI pin to use, or how skills, plugins, and agents are laid out.
---

Read `AGENTS.md` and `build/codex-pin.json` first.

Report:

1. CLI pin: `0.155.1` / `rust-v0.155.1`. Reject alphas and `Codex.app`.
2. Repo skills: `.agents/skills/`. Plugin skill name `saint-tibo` is the only plugin skill and must stay unique.
3. Marketplace: `.agents/plugins/marketplace.json` → `./plugins/saint-tibo`.
4. Project config and custom agents: `.codex/config.toml`, `.codex/agents/{mapper,reviewer,implementer}.toml`.
5. Later working repo: `BAITC-Hacks/hack-a58598e0-saint-tibo`. Do not push it unless the owner asked.

Do not invent a product stack. This repository is Codex setup only.
