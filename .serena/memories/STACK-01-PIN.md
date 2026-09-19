<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 28de672 docs(serena): sync stack pin and bootstrap memories
Scope: build/stack-pin.json, build/stack-standard.md, docs/adr/0003-stack-pin.md, docs/adr/0004-product-stack.md, scripts/check_stack.py
Area: STACK
-->

# STACK-01-PIN

## Purpose

Frozen product + toolchain standard and host doctor.

## Source Of Truth

- `build/stack-pin.json` schema 2.
- `build/stack-standard.md`: generated table; refresh with `python3 scripts/check_stack.py --write`.
- `docs/adr/0003-stack-pin.md` and `docs/adr/0004-product-stack.md`.
- Codex CLI remains `build/codex-pin.json`.

## Entry Points

- `python3 scripts/check_stack.py`: required host doctor + stale standard.
- `python3 scripts/check_stack.py --list`: print the generated standard.
- `python3 scripts/check_stack.py --strict`: also fail declared host drift/missing.
- `python3 scripts/reverify_stack_pin.py`: live npm/PyPI tags; skip openai 2.9.0 vs 3.x.

## Current Behavior

Web is React 19.3 + Vite 8.3, not Next.js. JS installer is bun. Backend is FastAPI. PostgreSQL is SoT. Isolated Python envs: API/workers redis-py 8.1.0, Telegram redis-py 7.4.1. OpenAI SDK in API is 2.9.0 for LiteLLM `<3`. Flutter 3.47.5 + bundled Dart 3.13.4. `./setup` installs only Codex plus Node/bun/uv/Python; Rust/Go/Docker/Postgres remain declared.

## Contracts And Data

- Required probes: `codex`, `node`, `bun`, `python`, `uv`.
- Declared probes report MATCH/MISSING/DRIFT and do not fail the default doctor.
- `package.json` `packageManager` is `bun@1.4.2`. `.node-version` and `.python-version` must match the pin.

## Invariants

- Do not add pnpm, Next.js, R3F, or a second JS lockfile.
- Generated OpenAPI clients; do not hand-write a parallel DTO layer.
- User code never runs in the API process.

## Change Rules

- Edit `build/stack-pin.json`, then `python3 scripts/check_stack.py --write`.
- Hackathon version bumps are explicit pin edits, not floating latest.

## Verification

- `python3 scripts/check_codex_setup.py`
- `python3 scripts/check_stack.py`
- `python3 scripts/reverify_stack_pin.py`
