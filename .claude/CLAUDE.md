# Claude Code notes for hack-setup

This repository is Codex harness setup, not an application. The product is
the tracked Codex project surfaces.

## Pin

Codex CLI must be `0.155.1`. See `build/codex-pin.json` and
`docs/adr/0001-codex-cli-155-pin.md`. The product stack is
`build/stack-pin.json` schema 2 and `docs/adr/0004-product-stack.md`.
Do not add Next.js or pnpm. Host doctor: `python3 scripts/check_stack.py`.
On hackathon day run `python3 scripts/reverify_stack_pin.py`.

## Do not treat this as a Claude skill tree

Repo workflows live in `.agents/skills/`. Do not copy them into
`.claude/skills/` unless a Claude-only workflow is required. Do not add a
root `CLAUDE.md`.

## Commands

```bash
./setup
. install/env.sh
./setup --status
python3 scripts/check_codex_setup.py
python3 scripts/check_stack.py
codex --version
```

Do not add a root file named `install`. The entry is `./setup`.

## Diagnostics

Use `/memory`, `/context`, `/hooks`, `/mcp`, `/permissions`, `/doctor`, and
`/status` for Claude-side state. Codex plugin/marketplace state is inspected
with `codex plugin marketplace list` after the project is trusted.

## Delivery constraint

Do not push to `BAITC-Hacks/hack-a58598e0-saint-tibo` until the owner
explicitly asks.
