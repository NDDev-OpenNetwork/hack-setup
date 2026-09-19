<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 53d8d31 docs: accept ADR 0008 and retarget routers to the plugin
Scope: scripts/check_codex_setup.py, scripts/check_stack.py, tests/, justfile, AGENTS.md
Area: TEST
-->

# TEST-01-CHECKS

## Purpose

Prove Codex artifacts, the installer catalog, and required host versions.

## Source Of Truth

- `justfile` recipes `gate`, `check`, `test`.
- `scripts/check_codex_setup.py`: dependency-free Python 3.11 artifact validator.
- `scripts/check_stack.py`: host doctor + generated `build/stack-standard.md`.
- `tests/test_check_codex_setup.py`: validator plus `./setup --dry-run`.
- `tests/test_check_stack.py`: version extract, standard contents, `doctor_decision`, live required doctor.
- `tests/test_env_sh.py`: bash/zsh `. install/env.sh` PATH heads.

## Entry Points

- `just gate`: `./setup --status`, `check_codex_setup.py`, `check_stack.py`, `codex --version`.
- `just check`: the two Python scripts. This is `stack-pin.control.proof`. It requires pin `control` paths, config == pin session/models/features, and AGENTS Mechanism.
- `just test`: `pytest -q` (use `pytest` / `~/.local/bin/pytest`, not `python3 -m pytest` on uv CPython).
- `ruff check scripts tests`

## Current Behavior

The artifact validator requires catalog ids `prereqs`, `codex-cli`, `runtimes`, `project-verify` and that `install/modules/<nn>-*` matches those rows. Repo skills must be `repo-orientation`, `quality-gate`, `one-repo-workflow`, `apply-stack-rule`. Team plugin skills must be `{saint-tibo}`. Standards plugin skills must be `{apply-agent-standard}`. Marketplace plugins must be `saint-tibo` then `hack-agent-standards`. Config must enable both `saint-tibo@saint-tibo` and `hack-agent-standards@saint-tibo`. `justfile` must exist and define `gate`/`check`/`setup`/`test`. `Makefile` / `makefile` / `GNUmakefile` must not exist. `AGENTS.md` must route to `plugins/hack-agent-standards/standards` and must not mention `docs/rules`. INDEX markdown links must exist. `docs/rules/` and `docs/agent-standards/` must not exist. `.codex/config.toml` must match `registered.session` (never + danger-full-access + live web search) and `models` (`gpt-6-astra` / `gpt-5.6-sol` / `xhigh` / requested `872000`/`700000`). `agents.enabled` and `features.multi_agent*` must be false. Do not add `.codex/agents/*.toml`. No project `.rules`.

Stack-pin schema 2: `control.rules` = `plugins/hack-agent-standards/standards/INDEX.md`. `registered.standards_plugin.id` = `hack-agent-standards@saint-tibo`. typescript `7.0.2` with no `compat_package`, `api_client.workspace` = `not-web`, `quality.just` = `1.58.0`. `do_not_use` includes Next.js, pnpm, asyncpg, TS6-in-web, `@hey-api/openapi-ts@next`, `bun add shadcn`, unconstrained RapidOCR/opencv-python, httpx 1.x, GNU make. Required conflicts include `hey-api-ts7-runtime` and `docling-opencv-cv2`.

Required probes must be OK. Declared tools (rustc, go, docker, compose, psql, redis-server, ruff, pytest, just) may DRIFT or be MISSING without failing the default doctor.

## Invariants

- Do not claim the setup is ready unless `just gate` was actually run.
- `just reverify` is hackathon-day / network, not an everyday gate.

## Verification

- `just gate`
- `just test`

## Known Gaps

- Live `test_check_stack_doctor_passes` is host-state, not hermetic.
