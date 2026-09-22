---
name: repo-orientation
description: Map the Saint Tibo Codex 0.155.1 setup. Use when starting work, asking where files live, which CLI pin to use, or how skills, plugins, and config are laid out.
---

Read `AGENTS.md` Mechanism, `build/codex-pin.json`, `build/stack-pin.json`
`control`, `build/stack-standard.md`, and `install/catalog.toml` first.
Pin is law. `.codex/config.toml` is the runtime projection. `just check`
is proof.

Report:

1. CLI pin: `0.155.1` / `rust-v0.155.1`. Reject alphas and `Codex.app`.
2. Bootstrap: `./setup` → `install/modules/<nn>-*`. Do not create a root file named `install`.
3. Repo skills: `.agents/skills/`. Team plugin skill is `saint-tibo`.
   Standards plugin skills: `build/stack-pin.json`
   `registered.standards_plugin_skills`. Invoke
   `$hack-agent-standards:<name>`. Names stay unique across
   `.agents/skills` and both plugins.
4. Marketplace: `.agents/plugins/marketplace.json` →
   `./plugins/saint-tibo` then `./plugins/hack-agent-standards`.
5. Project config: `.codex/config.toml`. Session law is `registered.session` / ADR 0006: `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`. Models: `gpt-6-astra` + `gpt-6-sol` / `xhigh`, window `872000` / compact `700000` (ADR 0007). `agents.enabled = false`. Do not add `.codex/agents/*.toml`.
6. Later working repo: `BAITC-Hacks/hack-a58598e0-saint-tibo`. Do not push it unless the owner asked.

App/runtime versions live in `build/stack-pin.json` schema 2. Web is
React + Vite + TypeScript `7.0.2` only, not Next.js. JS installer is bun.
Host doctor:
`python3 scripts/check_stack.py`. Do not invent unpinned libraries.
This repository still has no application code.
