# Claude Code notes for hack-setup

This repository is Codex harness setup, not an application. The product is
the tracked Codex project surfaces.

## Pin

Codex CLI must be `0.155.1`. See `build/codex-pin.json` and
`docs/adr/0001-codex-cli-155-pin.md`. Do not retarget alphas or the retired
`Codex.app` desktop bundle.

## Do not treat this as a Claude skill tree

Repo workflows live in `.agents/skills/`. Do not copy them into
`.claude/skills/` unless a Claude-only workflow is required. Do not add a
root `CLAUDE.md`.

## Commands

```bash
python3 scripts/check_codex_setup.py
codex --version
```

## Diagnostics

Use `/memory`, `/context`, `/hooks`, `/mcp`, `/permissions`, `/doctor`, and
`/status` for Claude-side state. Codex plugin/marketplace state is inspected
with `codex plugin marketplace list` after the project is trusted.

## Delivery constraint

Do not push to `BAITC-Hacks/hack-a58598e0-saint-tibo` until the owner
explicitly asks.
