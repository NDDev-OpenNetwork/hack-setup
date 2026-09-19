<!-- Memory Metadata
Last updated: 2026-09-19
Last commit: b0d6d67 docs: document one-command clone-and-setup flow
Scope: scripts/check_codex_setup.py, tests/test_check_codex_setup.py
Area: TEST
-->

# TEST-01-CHECKS

## Purpose

Record the checks that prove Codex setup artifacts and the bootstrap catalog are valid.

## Source Of Truth

- `scripts/check_codex_setup.py`: dependency-free Python 3.11 validator.
- `tests/test_check_codex_setup.py`: subprocess wrappers for the validator and `./setup --dry-run`.

## Entry Points

- `python3 scripts/check_codex_setup.py`: pin, installer sha256, catalog modules, AGENTS.md size, config bans, custom agents, portable plugin, marketplace path, skill names.
- `pytest -q tests/test_check_codex_setup.py`: validator plus dry-run.
- `ruff check scripts/check_codex_setup.py tests/test_check_codex_setup.py`: lint for the validator.
- `./setup --status`: module status including `codex --version`.

## Current Behavior

The validator requires `install/catalog.toml` to list `prereqs`, `codex-cli`, and `project-verify`, rejects a root file named `install`, and requires 64-char lowercase sha256 for the official installer and four platform packages.

## Invariants

- Do not claim the setup is ready unless the validator and `codex --version` were actually run.

## Verification

- `./setup --dry-run`
- `python3 scripts/check_codex_setup.py`
- `pytest -q tests/test_check_codex_setup.py`
- `codex --version`
