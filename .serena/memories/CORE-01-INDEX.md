<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 16c5389 docs(serena): record hierarchical bootstrap catalog
Scope: AGENTS.md, build/, .agents/, .codex/, plugins/saint-tibo/, install/, scripts/
Area: CORE
-->

# CORE-01-INDEX

## Purpose

Index durable project knowledge for the Codex 0.155.1 team setup repository.

## Source Of Truth

- `AGENTS.md`: Codex project instructions.
- `build/codex-pin.json`: CLI pin plus official installer/package sha256.
- `build/stack-pin.json`: product stack schema 2.
- `build/stack-standard.md`: generated stack table.
- `docs/adr/0001-codex-cli-155-pin.md` through `docs/adr/0004-product-stack.md`.
- Codex surfaces: `mem:CODEX-01-PIN`, `mem:CODEX-02-SURFACES`.
- Stack: `mem:STACK-01-PIN`.
- Bootstrap: `mem:INFRA-01-BOOTSTRAP`.
- Checks: `mem:TEST-01-CHECKS`.

## Entry Points

- `./setup`: macOS/Linux catalog install after clone.
- `python3 scripts/check_codex_setup.py`: static artifact gate.
- `python3 scripts/check_stack.py`: required host doctor + generated standard freshness.
- `python3 scripts/reverify_stack_pin.py`: live version drift check.
- `codex --version`: runtime CLI pin proof.

## Current Behavior

The repository contains Codex project surfaces, a hierarchical installer catalog, and a frozen product stack. There is no application code. Later working remote is `BAITC-Hacks/hack-a58598e0-saint-tibo` and is not pushed unless the owner asks.

## Invariants

- Codex CLI pin is `0.155.1` / `rust-v0.155.1`.
- Root entry is `./setup`, not a file named `install`.
- Repo skill names do not collide with plugin skill names.
- No secrets in the public tree.

## Verification

- `./setup --status`
- `python3 scripts/check_codex_setup.py`
- `python3 scripts/check_stack.py`
- `pytest -q`
- `codex --version`
