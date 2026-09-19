<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 2d182e1 docs(plugin): list apply-stack-rule among repo skill names
Scope: build/stack-pin.json, build/stack-standard.md, docs/adr/0003-stack-pin.md, docs/adr/0004-product-stack.md, justfile, scripts/check_stack.py
Area: STACK
-->

# STACK-01-PIN

## Purpose

Frozen product + toolchain standard and host doctor.

## Source Of Truth

- `build/stack-pin.json` schema 2, `verified_on` 2026-09-20. `control` names the pin → config → `just check` loop.
- `build/stack-standard.md`: generated; refresh with `python3 scripts/check_stack.py --write`.
- `docs/adr/0003-stack-pin.md`, `docs/adr/0004-product-stack.md`, `docs/adr/0006-codex-yolo-session.md`, and `docs/adr/0007-codex-models-context.md`.
- Codex session: `registered.session` (`never` + `danger-full-access` + `web_search=live`).
- Codex models: `models.primary=gpt-6-astra`, `models.secondary=gpt-5.6-sol`, `reasoning_effort=xhigh`. Window/compact `872000`/`700000`; usable `828400`; 90% compact cap `784800`.
- `justfile` / `quality.just` `1.58.0`.
- Codex CLI remains `build/codex-pin.json`.

## Entry Points

- `just check` / `python3 scripts/check_stack.py`: required host doctor + stale standard.
- `just stack`: print the generated standard.
- `python3 scripts/check_stack.py --strict`: also fail declared host drift/missing.
- `just reverify`: hackathon-day network check. openai is range-checked for LiteLLM (`>=2.20,<3`), not compared to latest 3.x.

## Current Behavior

Web is React 19.3 + Vite 8.3 + TypeScript 7.0.2 only. No `typescript@6` / `@typescript/typescript6` / typescript-eslint in web. `@hey-api/openapi-ts` `0.99.0` is not a web workspace dep; do not take `@next`. shadcn via `bunx shadcn@4.21.0` only. `@types/node` is `24.13.6`. JS installer is bun.

API: FastAPI, `httpx` `0.28.1` (`<1`). Isolated Python envs: API/workers redis-py 8.1.0, Telegram redis-py 7.4.1. openai `2.54.0` (LiteLLM `1.101.0` `openai>=2.20,<3`). cliproxyapi `7.3.9` is a GitHub release. Docling default extra `standard` is not API-safe; only `cv2` is opencv-python-headless `5.0.0.93`.

Flutter 3.47.5 + bundled Dart 3.13.4. Tauri 2 npm `2.11.4`/`2.11.1`, crate `2.11.5`.

`./setup` installs Codex plus Node/bun/uv/Python. Required probes: `codex`, `node`, `bun`, `python`, `uv`. Declared probes (including `just`) report OK/MISSING/DRIFT and do not fail the default doctor.

## Contracts And Data

- `package.json` `packageManager` is `bun@1.4.2`.
- `.node-version` and `.python-version` must match the pin.
- Node 24.21.0 Active LTS; reject Node 26 Current until 2026-10-28.

## Invariants

- No Makefile. Project commands are `just`.
- Web/desktop typescript is only `7.0.2`. Generated clients are typechecked by that `tsc`.
- User code never runs in the API process.
- Do not put openai 3.x in the API env.
- Version bumps are explicit pin edits.

## Change Rules

- Edit `build/stack-pin.json`, then `python3 scripts/check_stack.py --write`.

## Verification

- `just gate`
- `just reverify` (network; hackathon-day)

## Known Gaps

- `reverify_stack_pin.py` checks a subset of pins; openai is range-checked (`>=2.20,<3`).
- `@hey-api/openapi-ts` `0.99.0` still crashes next to typescript 7; wait for a stable release without the Compiler API.
