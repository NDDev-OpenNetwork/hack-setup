<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 2d182e1 docs(plugin): list apply-stack-rule among repo skill names
Scope: AGENTS.md, build/, .agents/, .codex/, plugins/saint-tibo/, install/, justfile, docs/rules/, docs/adr/
Area: CORE
-->

# CORE-01-INDEX

## Purpose

Index durable knowledge for the Codex 0.155.1 team setup repository. No application code.

## Source Of Truth

- Control loop: pin (`build/codex-pin.json` + `build/stack-pin.json`) → runtime (`.codex/config.toml`) → proof (`just check` / `just gate`) → on-demand rules (`docs/rules/INDEX.md`). `AGENTS.md` is the router.
- `AGENTS.md`: Codex project instructions. Router to `docs/rules/INDEX.md`.
- `docs/rules/INDEX.md`: on-demand technology/format rules. Pin numbers win.
- `docs/adr/0001`–`0007`: accepted decisions. Session law is ADR 0006. Models/context/no-subagents is ADR 0007.
- `build/codex-pin.json`: CLI pin plus official installer/package sha256.
- `build/stack-pin.json`: product stack schema 2.
- `build/stack-standard.md`: generated from the pin via `python3 scripts/check_stack.py --write`.
- `justfile`: project command runner (`just` `1.58.0`). No Makefile.
- Codex surfaces: `mem:CODEX-01-PIN`, `mem:CODEX-02-SURFACES`.
- Stack: `mem:STACK-01-PIN`.
- Bootstrap: `mem:INFRA-01-BOOTSTRAP`.
- Checks: `mem:TEST-01-CHECKS`.

`docs/research/` is an archive. It is not runtime law.

## Entry Points

- `./setup`: macOS/Linux catalog install after clone.
- `just gate`: AGENTS four-command ready gate.
- `just check`: artifact validator + host doctor.
- `codex --version`: runtime CLI pin proof.

## Current Behavior

Author remote is `NDDev-OpenNetwork/hack-setup`. Later working remote is `BAITC-Hacks/hack-a58598e0-saint-tibo` and is not pushed unless the owner asks. `./setup` installs only Codex plus Node/bun/uv/Python. Isolated Serena and `hooks.json` are not installed by `./setup`. Web typescript is only `7.0.2`. Codex session models are `gpt-6-astra` / `gpt-5.6-sol` at `xhigh`, window `872000` / compact `700000`. Codex subagents are off.

## Invariants

- Codex CLI pin is `0.155.1` / `rust-v0.155.1`.
- Root entry is `./setup`, not a file named `install`.
- Project commands are `just`. Do not add a Makefile.
- Repo skill names do not collide with plugin skill names.
- No secrets in the public tree.
- Do not add pnpm, Next.js, R3F, a second JS lockfile, typescript@6 in web, `@hey-api/openapi-ts@next`, `bun add shadcn`, or unconstrained `docling` / `opencv-python`.

## Verification

- `just gate`
- `just test`
