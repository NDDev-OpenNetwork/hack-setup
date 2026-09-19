<!-- Memory Metadata
Last updated: 2026-09-19
Last commit: b0d6d67 docs: document one-command clone-and-setup flow
Scope: AGENTS.md, build/codex-pin.json, .agents/, .codex/, plugins/saint-tibo/, install/, scripts/check_codex_setup.py
Area: CORE
-->

# CORE-01-INDEX

## Purpose

Index durable project knowledge for the Codex 0.155.1 team setup repository.

## Source Of Truth

- `AGENTS.md`: Codex project instructions.
- `build/codex-pin.json`: CLI pin plus official installer/package sha256.
- `docs/adr/0001-codex-cli-155-pin.md`: pin decision.
- `docs/adr/0002-hierarchical-bootstrap.md`: clone-and-setup decision.
- Codex surfaces: `mem:CODEX-01-PIN`, `mem:CODEX-02-SURFACES`.
- Bootstrap: `mem:INFRA-01-BOOTSTRAP`.
- Checks: `mem:TEST-01-CHECKS`.

## Entry Points

- `./setup`: macOS/Linux catalog install after clone.
- `python3 scripts/check_codex_setup.py`: static artifact gate.
- `codex --version`: runtime CLI pin proof.

## Current Behavior

The repository contains Codex project surfaces and a hierarchical installer catalog. There is no application stack. Later working remote is `BAITC-Hacks/hack-a58598e0-saint-tibo` and is not pushed unless the owner asks.

## Invariants

- Codex CLI pin is `0.155.1` / `rust-v0.155.1`.
- Root entry is `./setup`, not a file named `install`.
- Repo skill names do not collide with plugin skill names.
- No secrets in the public tree.

## Verification

- `./setup --status`
- `python3 scripts/check_codex_setup.py`
- `pytest -q tests/test_check_codex_setup.py`
- `codex --version`
