# 3. Stack version pin

- Status: accepted
- Date: 2026-09-19
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The team needs one file that states the current stable versions for the
hackathon app stack and what Codex already registers. Versions must be
re-checked on hackathon day.

## Decision Drivers

- Latest compatible stable, not canary/alpha
- One source of truth, not scattered README numbers
- Codex CLI pin stays in `build/codex-pin.json`
- bun is the JS installer; pnpm is out
- Node Active LTS + CPython 3.14 via uv

## Considered Options

- pnpm as the JS installer
- Node 26 Current
- Pin verified stables: Node LTS, Python 3.14, bun, uv

## Decision Outcome

Chosen option: `build/stack-pin.json` is the stack SoT. `control`
names the loop: pin files are law, `.codex/config.toml` is the runtime
projection, `just check` is proof, `docs/rules/` is on-demand detail.

- Node `24.21.0` Active LTS. Reject Node 26 Current until 2026-10-28.
- Python `3.14.7` via `uv python install`. Bootstrap scripts still
  accept system Python 3.11+.
- bun `1.4.2`. `package.json` `packageManager` is `bun@1.4.2`.
- uv `0.12.17`.
- pnpm is rejected.
- Product web/backend/data choices: `docs/adr/0004-product-stack.md`.
  Next.js is rejected; React + Vite is the web app.
- Codex models are `gpt-6-astra` + `gpt-5.6-sol` at `xhigh` (ADR 0007).
- Codex session law is `registered.session` (ADR 0006): no sandbox,
  never ask.

`./setup` module `30-runtimes` downloads the pinned official Node/bun
archives and the official uv installer, then pins CPython through uv.

Hackathon re-verify: `just reverify`.

## Confirmation

- `python3 scripts/check_codex_setup.py`
- `python3 scripts/check_stack.py`
- `./setup --status`
- Hackathon-day only: `just reverify`
