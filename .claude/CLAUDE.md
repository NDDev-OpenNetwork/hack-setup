# Claude Code notes for hack-setup

This repository is Codex harness setup, not an application. The product is
the tracked Codex project surfaces.

Law is `build/codex-pin.json` + `build/stack-pin.json`. Runtime is
`.codex/config.toml`. Proof is `just check`. Rules are on-demand.

## Pin

Codex CLI must be `0.155.1`. See `build/codex-pin.json` and
`docs/adr/0001-codex-cli-155-pin.md`. The product stack is
`build/stack-pin.json` schema 2 and `docs/adr/0004-product-stack.md`.
Do not add Next.js, pnpm, `typescript@6` in web, `@hey-api/openapi-ts`
next to TypeScript `7.0.2`, or a Makefile. Codex session is YOLO
(`registered.session`, ADR 0006): never ask, no OS sandbox. Models
are `gpt-6-astra` / `gpt-5.6-sol` at `xhigh`, window `872000` /
compact `700000`, no Codex subagents (ADR 0007). Commands:
`just gate` / `just check`. Host doctor: `python3 scripts/check_stack.py`.
Hackathon-day: `just reverify`. `docs/research/` is archive, not law.

## Do not treat this as a Claude skill tree

Repo workflows live in `.agents/skills/`. Do not copy them into
`.claude/skills/` unless a Claude-only workflow is required. Do not add a
root `CLAUDE.md`.

## Commands

```bash
./setup
. install/env.sh
just gate
just test
```

Do not add a root file named `install`. The entry is `./setup`.

## Diagnostics

Use `/memory`, `/context`, `/hooks`, `/mcp`, `/permissions`, `/doctor`, and
`/status` for Claude-side state. Codex plugin/marketplace state is inspected
with `codex plugin marketplace list` after the project is trusted.

## Delivery constraint

Do not push to `BAITC-Hacks/hack-a58598e0-saint-tibo` until the owner
explicitly asks.
