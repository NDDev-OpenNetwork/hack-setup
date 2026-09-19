<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 2d182e1 docs(plugin): list apply-stack-rule among repo skill names
Scope: setup, install/, justfile, docs/adr/0002-hierarchical-bootstrap.md
Area: INFRA
-->

# INFRA-01-BOOTSTRAP

## Purpose

One-command macOS/Linux install after clone, with a numbered module catalog.

## Source Of Truth

- `./setup`: root entry; execs `install/bootstrap.sh`.
- `install/catalog.toml`: snapshot (`schema_version=1`, `entry="./setup"`). Not consumed at runtime.
- `install/modules/<nn>-<id>/module.sh`: discovered by glob `modules/[0-9][0-9]-*`.
- `justfile`: wrappers for setup/status/check/gate. No Makefile.
- `docs/adr/0002-hierarchical-bootstrap.md`.

## Entry Points

- `./setup` or `just setup`: install numbered modules (skip `disabled`).
- `just dry-run` / `./setup --dry-run`
- `just status` / `./setup --status`
- `./setup --print-env`
- `. install/env.sh`: prepend `$REPO/.local/bin` then `$HOME/.local/bin`.
- `just check` / `just gate`

## Current Behavior

Bootstrap sources `install/lib/{common,os,download}.sh`, rejects non-Darwin/Linux hosts, and globs `10-prereqs`, `20-codex-cli`, `30-runtimes`, `40-project-verify`. A `disabled` file skips a module. `catalog.toml` `enabled` is documentary. The artifact gate requires numbered dirs to match the catalog exactly.

Codex module installs official `rust-v0.155.1` into `~/.local/bin` and symlinks `$REPO/.local/bin`; it verifies `install.sh` sha256 and does not use `packages.*.sha256`. Runtimes module installs pinned Node, bun, uv, and CPython from `build/stack-pin.json` and links `python3.<minor>` from `runtimes.python.version`. Verify module runs the two Python checkers.

`. install/env.sh` resolves the sourced file via `BASH_SOURCE[0]` (bash) or zsh `%x`. POSIX `sh`/`dash` fail closed.

## Contracts And Data

- Module actions: `install`, `status`, `dry-run`.
- Catalog ids: `prereqs`, `codex-cli`, `runtimes`, `project-verify`.
- Add a future installer as `install/modules/<nn>-<id>/module.sh` and the matching `catalog.toml` row.

## Invariants

- Do not add a root file named `install`.
- Do not add a Makefile.
- Do not vendor the official Codex installer; pin URL + sha256.
- Windows is fail-closed.
- Homebrew copies are not uninstalled; repo `.local/bin` must win PATH order.

## Verification

- `just dry-run`
- `just status`
- `just check`

## Known Gaps

- Bootstrap still globs; an extra numbered dir would install if `./setup` is run before the artifact gate.
- Codex `packages.*.sha256` are stored and unused by the installer.
