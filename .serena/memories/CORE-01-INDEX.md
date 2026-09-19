<!-- Memory Metadata
Last updated: 2026-09-19
Last commit: 67b0862 chore: add license, ignore rules, and Serena languages
Scope: AGENTS.md, build/codex-pin.json, .agents/, .codex/, plugins/saint-tibo/, scripts/check_codex_setup.py
Area: CORE
-->

# CORE-01-INDEX

## Purpose

Index durable project knowledge for the Codex 0.155.1 team setup repository.

## Source Of Truth

- `AGENTS.md`: Codex project instructions.
- `build/codex-pin.json`: CLI pin.
- `docs/adr/0001-codex-cli-155-pin.md`: pin decision.
- Codex surfaces: `mem:CODEX-01-PIN`, `mem:CODEX-02-SURFACES`.
- Checks: `mem:TEST-01-CHECKS`.

## Entry Points

- `python3 scripts/check_codex_setup.py`: static artifact gate.
- `codex --version`: runtime CLI pin proof.

## Current Behavior

The repository contains only Codex project surfaces. There is no application stack. Later working remote is `BAITC-Hacks/hack-a58598e0-saint-tibo` and is not pushed unless the owner asks.

## Invariants

- Codex CLI pin is `0.155.1` / `rust-v0.155.1`.
- Repo skill names do not collide with plugin skill names.
- No secrets in the public tree.

## Verification

- `python3 scripts/check_codex_setup.py`
- `pytest -q tests/test_check_codex_setup.py`
- `codex --version`
