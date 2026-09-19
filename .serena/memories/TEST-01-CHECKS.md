<!-- Memory Metadata
Last updated: 2026-09-19
Last commit: 67b0862 chore: add license, ignore rules, and Serena languages
Scope: scripts/check_codex_setup.py, tests/test_check_codex_setup.py
Area: TEST
-->

# TEST-01-CHECKS

## Purpose

Record the checks that prove Codex setup artifacts are valid.

## Source Of Truth

- `scripts/check_codex_setup.py`: dependency-free Python 3.11 validator.
- `tests/test_check_codex_setup.py`: subprocess wrapper expecting PASS.

## Entry Points

- `python3 scripts/check_codex_setup.py`: pin, AGENTS.md size, config bans, custom agents, portable plugin, marketplace path, skill names.
- `pytest -q tests/test_check_codex_setup.py`: same script via pytest.
- `ruff check scripts/check_codex_setup.py`: lint for the validator.
- `codex --version`: runtime pin.

## Current Behavior

On 2026-09-19 these passed: validator PASS, pytest 1 passed, ruff clean, `codex-cli 0.155.1`, official `plugin.schema.json` validation of `plugins/saint-tibo/plugin.json`.

## Invariants

- Do not claim the setup is ready unless the validator and `codex --version` were actually run.

## Verification

- `python3 scripts/check_codex_setup.py`
- `pytest -q tests/test_check_codex_setup.py`
- `codex --version`
