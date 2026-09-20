<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: bc3c4c3 fix(docs+check): document plugin install steps; scope legacy-profile ban to sol
Scope: scripts/check_codex_setup.py, scripts/check_stack.py, tests/, justfile, AGENTS.md, build/stack-pin.json registered.standards_plugin_skills
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

The artifact validator requires catalog ids `prereqs`, `codex-cli`, `runtimes`, `project-verify`, that `install/modules/<nn>-*` matches those rows, and that each module dir has both `module.sh` and `module.ps1` twins (`setup.ps1`/`bootstrap.ps1`/`env.ps1` + catalog `entry_windows` required since ADR 0012 native Windows). `codex-pin.json` and `runtimes.{node,bun}.packages` must cover all 5 PINNED_PLATFORMS incl. `windows-x86_64`; `installer_ps1` required on codex-pin and `runtimes.uv`. Repo skills must be `repo-orientation`, `quality-gate`, `one-repo-workflow`, `apply-stack-rule`. Plugin iteration is marketplace-driven (`.agents/plugins/marketplace.json` is the SoT): names map to `registered.<suffix>_plugin{,_skills}` (saint-tibo uses bare `plugin`/`plugin_skills`), each plugin's disk skills must equal its pin list, and every plugin skill must be AGENTS-named `$<plugin>:<skill>`. Nested templates must be `plugins/hack-agent-standards/nested/{README,web,api,mobile,desktop,telegram,infra}.md`. `justfile` must exist and define `gate`/`check`/`setup`/`test`. `Makefile` / `makefile` / `GNUmakefile` must not exist. `AGENTS.md` must route to `plugins/hack-agent-standards/standards`, include `## Motion`, and must not mention `docs/rules`. INDEX markdown links must exist. `docs/rules/` and `docs/agent-standards/` must not exist. `.codex/config.toml` must match `registered.session` (never + danger-full-access + live web search) and `models` (`gpt-6-astra` / `gpt-5.6-sol` / `xhigh` / requested `872000`/`700000`). `agents.enabled` and `features.multi_agent*` must be false. Do not add `.codex/agents/*.toml`. No project `.rules`. Project config must not define `profiles`; when the codex binary exists the user config must have no legacy `[profiles.sol]` and `~/.codex/sol.config.toml` must match `models.*`. Installed plugin caches under `~/.codex/plugins/cache/saint-tibo/<name>/<version>` must be byte-identical to `plugins/<name>/` (re-run `codex plugin add` on drift). Every `standards/*.md` file must be linked from INDEX.

Stack-pin schema 2: `control.rules` = `plugins/hack-agent-standards/standards/INDEX.md`. `registered.standards_plugin.id` = `hack-agent-standards@saint-tibo`. typescript `7.0.2` with no `compat_package`, `api_client.workspace` = `not-web`, `quality.just` = `1.58.0`. `do_not_use` includes Next.js, pnpm, asyncpg, TS6-in-web, `@hey-api/openapi-ts@next`, `bun add shadcn`, unconstrained RapidOCR/opencv-python, httpx 1.x, GNU make. Required conflicts include `hey-api-ts7-runtime` and `docling-opencv-cv2`.

Required probes must be OK. Declared tools (rustc, go, docker, compose, psql, redis-server, ruff, pytest, just, ty) may DRIFT or be MISSING without failing the default doctor.

## Invariants

- Do not claim the setup is ready unless `just gate` was actually run.
- `just reverify` is hackathon-day / network, not an everyday gate.

## Verification

- `just gate`
- `just test`

## Known Gaps

- Live `test_check_stack_doctor_passes` is host-state, not hermetic.
