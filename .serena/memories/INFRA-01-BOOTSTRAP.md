<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 16c5389 docs(serena): record hierarchical bootstrap catalog
Scope: setup, install/, Makefile, docs/adr/0002-hierarchical-bootstrap.md
Area: INFRA
-->

# INFRA-01-BOOTSTRAP

## Purpose

One-command macOS/Linux install after clone, with a numbered module catalog.

## Source Of Truth

- `./setup`: root entry; execs `install/bootstrap.sh`.
- `install/catalog.toml`: documented module contract (`schema_version=1`, `entry="./setup"`).
- `install/modules/<nn>-<id>/module.sh`: discovered in numeric order.
- `docs/adr/0002-hierarchical-bootstrap.md`.

## Entry Points

- `./setup`: install enabled modules.
- `./setup --dry-run`: print planned work, no downloads.
- `./setup --status`: check without installing.
- `./setup --print-env`: print PATH export.
- `. install/env.sh`: prepend `$REPO/.local/bin` then `$HOME/.local/bin`.
- `make setup` / `make dry-run` / `make status` / `make check`.

## Current Behavior

Bootstrap sources `install/lib/{common,os,download}.sh`, rejects non-Darwin/Linux hosts, and runs `10-prereqs`, `20-codex-cli`, `30-runtimes`, `40-project-verify`. Codex module installs official `rust-v0.155.1` into `~/.local/bin` and symlinks `$REPO/.local/bin`. Runtimes module installs pinned Node, bun, uv, and CPython 3.14 from `build/stack-pin.json`. Verify module runs `scripts/check_codex_setup.py` and `scripts/check_stack.py`.

## Contracts And Data

- Module actions: `install`, `status`, `dry-run`.
- Catalog ids: `prereqs`, `codex-cli`, `runtimes`, `project-verify`.
- Add a future installer as `install/modules/<nn>-<id>/module.sh` and a `catalog.toml` row.

## Invariants

- Do not add a root file named `install`.
- Do not vendor the official Codex installer; pin URL + sha256.
- Windows is fail-closed.
- Homebrew copies are not uninstalled; `install/env.sh` wins PATH order.

## Verification

- `./setup --dry-run`
- `./setup --status`
- `python3 scripts/check_codex_setup.py`
- `python3 scripts/check_stack.py`
