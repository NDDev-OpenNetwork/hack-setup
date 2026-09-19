<!-- Memory Metadata
Last updated: 2026-09-19
Last commit: b0d6d67 docs: document one-command clone-and-setup flow
Scope: setup, install/, Makefile, docs/adr/0002-hierarchical-bootstrap.md
Area: INFRA
-->

# INFRA-01-BOOTSTRAP

## Purpose

One-command macOS/Linux install after clone, with a numbered module catalog for future installers.

## Source Of Truth

- `./setup`: root entry; execs `install/bootstrap.sh`.
- `install/catalog.toml`: documented module contract (`schema_version=1`, `entry="./setup"`).
- `install/modules/<nn>-<id>/module.sh`: discovered in numeric order.
- `docs/adr/0002-hierarchical-bootstrap.md`: accepted 2026-09-19.

## Entry Points

- `./setup`: install enabled modules.
- `./setup --dry-run`: print planned work, no downloads.
- `./setup --status`: check without installing.
- `./setup --print-env`: print PATH export.
- `. install/env.sh`: prepend `$REPO/.local/bin` then `$HOME/.local/bin`.
- `make setup` / `make dry-run` / `make status`.

## Current Behavior

Bootstrap sources `install/lib/{common,os,download}.sh`, rejects non-Darwin/Linux hosts, and runs `10-prereqs`, `20-codex-cli`, `30-project-verify`. Codex module downloads official `rust-v0.155.1/install.sh`, verifies `build/codex-pin.json` `installer.sha256`, runs it with `CODEX_RELEASE=0.155.1`, `CODEX_NON_INTERACTIVE=1`, `CODEX_INSTALLER_USE_RELEASES_OPENAI_COM=false`, `CODEX_INSTALL_DIR=$HOME/.local/bin`, then symlinks into `$REPO/.local/bin`. A `disabled` file in a module directory skips that module.

## Contracts And Data

- Module actions: `install`, `status`, `dry-run`.
- Pin installer URL must contain `rust-v0.155.1/install.sh`.
- Packages keyed `darwin-arm64`, `darwin-x86_64`, `linux-arm64`, `linux-x86_64`.
- Add a future installer as `install/modules/<nn>-<id>/module.sh` and a `catalog.toml` row.

## Invariants

- Do not add a root file named `install`; it cannot coexist with `install/` on macOS.
- Do not vendor the official 800-line installer; pin URL + sha256.
- Do not write a clone-absolute PATH into shell profiles; official binary lives in `~/.local/bin`.
- Windows is fail-closed.
- bun/npm/brew copies are not uninstalled; `install/env.sh` wins PATH order.

## Change Rules

- Keep `catalog.toml` in sync with `install/modules/`; `scripts/check_codex_setup.py` enforces that.
- Disable a module with a `disabled` file rather than deleting the directory unless the catalog row is removed too.

## Verification

- `./setup --dry-run`
- `./setup --status`
- `python3 scripts/check_codex_setup.py`
- `codex --version`
