# Claude Code notes for hack-setup

The contract is `AGENTS.md` — read it first; it carries the pin, the
operating model, the plugin map, hooks, and the boundaries. This file
only holds Claude-specific deltas. When the two disagree, `AGENTS.md`
wins — update this file in the same change that changes the contract.

This repository is Codex harness setup, not an application. The product
is the tracked Codex project surfaces. Law is `build/codex-pin.json` +
`build/stack-pin.json`; proof is `just check`.

## Do not treat this as a Claude skill tree

Repo workflows live in `.agents/skills/` and plugin skills in
`plugins/*/skills/`. Do not copy them into `.claude/skills/` unless a
Claude-only workflow is required. Do not add a root `CLAUDE.md`.

## Commands

```bash
./setup
. install/env.sh
just gate
just test
just repair
```

`just repair` diagnoses and auto-fixes safe drift (plugin cache,
managed user-config blocks, `.agent` dirs, stale hook bytecode). Do not
add a root file named `install`. The entry is `./setup` /
`.\setup.ps1`.

## Diagnostics

Use `/memory`, `/context`, `/hooks`, `/mcp`, `/permissions`, `/doctor`, and
`/status` for Claude-side state. Codex plugin/marketplace state is inspected
with `codex plugin marketplace list` after the project is trusted.

## Delivery constraint

Do not push to `BAITC-Hacks/hack-a58598e0-saint-tibo` until the owner
explicitly asks.
