<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 16c5389 docs(serena): record hierarchical bootstrap catalog
Scope: scripts/check_codex_setup.py, scripts/check_stack.py, tests/
Area: TEST
-->

# TEST-01-CHECKS

## Purpose

Prove Codex artifacts, the installer catalog, and required host versions.

## Source Of Truth

- `scripts/check_codex_setup.py`: dependency-free Python 3.11 artifact validator.
- `scripts/check_stack.py`: host doctor + generated `build/stack-standard.md`.
- `tests/test_check_codex_setup.py`: validator plus `./setup --dry-run`.
- `tests/test_check_stack.py`: version extract, standard contents, required doctor.

## Entry Points

- `python3 scripts/check_codex_setup.py`
- `python3 scripts/check_stack.py`
- `pytest -q`
- `ruff check scripts tests`
- `./setup --status`

## Current Behavior

The artifact validator requires catalog ids `prereqs`, `codex-cli`, `runtimes`, `project-verify`, stack-pin schema 2 (React/Vite, no Next.js), verify probes for required host tools, and `build/stack-standard.md`. The doctor fails only when required host tools drift; declared Homebrew/global tools may DRIFT without failing.

## Invariants

- Do not claim the setup is ready unless the validator, doctor, and `codex --version` were actually run.

## Verification

- `./setup --dry-run`
- `python3 scripts/check_codex_setup.py`
- `python3 scripts/check_stack.py`
- `pytest -q`
- `codex --version`
