<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 2410c1c feat(install): install codex from the sha256-verified package tarball
Scope: setup, install/, justfile, docs/adr/0002-hierarchical-bootstrap.md
Area: INFRA
-->

# INFRA-01-BOOTSTRAP

## Purpose

One-command install after clone on macOS/Linux (`./setup`) and native
Windows x86_64 (`.\setup.ps1`), with a numbered module catalog.

## Source Of Truth

- `./setup`: POSIX entry; execs `install/bootstrap.sh`.
- `.\setup.ps1`: native Windows entry; calls `install/bootstrap.ps1`.
- `install/catalog.toml`: snapshot (`schema_version=1`, `entry="./setup"`, `entry_windows="./setup.ps1"`). Not consumed at runtime.
- `install/modules/<nn>-<id>/module.sh` + `module.ps1`: discovered by glob `modules/[0-9][0-9]-*`; every module needs both twins.
- `justfile`: wrappers for setup/status/check/gate. No Makefile.
- `docs/adr/0002-hierarchical-bootstrap.md`, `0012-windows-via-wsl2.md` (now native).

## Entry Points

- `./setup` or `just setup`: install numbered modules (skip `disabled`).
- `.\setup.ps1` on Windows (`powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1`).
- `just dry-run` / `./setup --dry-run`
- `just status` / `./setup --status`
- `./setup --print-env`
- `. install/env.sh`: prepend `$REPO/.local/bin` then `$HOME/.local/bin`.
- `. .\install\env.ps1`: same plus `%LOCALAPPDATA%\Programs\OpenAI\Codex\bin`.
- `just check` / `just gate`

## Current Behavior

Bootstrap sources `install/lib/{common,os,download}.{sh,ps1}`, detects the platform, and globs `10-prereqs`, `20-codex-cli`, `30-runtimes`, `40-project-verify`. A `disabled` file skips a module. `catalog.toml` `enabled` is documentary. The artifact gate requires numbered dirs to match the catalog exactly and every module to have both `.sh` and `.ps1` twins. The Windows twin needs no host python — pin reads are `ConvertFrom-Json`, hashes are `Get-FileHash`, zips are `Expand-Archive`; codex lands via the pinned official `install.ps1` (junctions + persistent user PATH under `%LOCALAPPDATA%\Programs\OpenAI\Codex\bin`), uv via pinned `uv-installer.ps1`, python via `uv python install --default`, bun via zip (`bunx.exe` = hardlink of `bun.exe`), node via `win-x64.zip` + `npm.cmd`/`npx.cmd` shims.

Codex module installs `rust-v0.155.1` into `~/.local/bin` and symlinks `$REPO/.local/bin`; primary path downloads the pinned `codex-package-<triple>.tar.gz` and verifies `packages.<platform>.sha256`, with hashed official `install.sh` as fallback for a platform missing from `packages`. It also writes the managed `~/.codex/sol.config.toml` profile overlay and strips a legacy `[profiles.sol]` table from the user config (0.155.1 ignores project-local `profiles`; since 0.134 `--profile` reads `<name>.config.toml` files). Runtimes module installs pinned Node, bun, uv, and CPython from `build/stack-pin.json`, links `python3.<minor>` from `runtimes.python.version`, guarantees `bunx`/`uvx` links on every path (bunx is argv0 dispatch on the bun binary; both were previously skipped on early-return), and pre-warms the MCP stdio caches (`uvx --from serena-agent==<mcp.serena.version>`, `bunx shadcn@<frontend.shadcn>`). Verify module registers the marketplace, installs all five plugins (`saint-tibo`, `hack-agent-standards`, `hack-agent-workflow`, `hack-agent-lsp`, `hack-agent-mcp`), then runs full `repair_setup.py` (converges notify-block + hook-trust that module 20 may skip on fresh hosts without python3), then the two Python checkers — a fresh machine would fail cache-parity otherwise. `bootstrap.sh` exports `$HACK_LOCAL_BIN:~/.local/bin:~/.bun/bin` into PATH before the module loop so freshly installed binaries are visible to later modules.

`. install/env.sh` resolves the sourced file via `BASH_SOURCE[0]` (bash) or zsh `%x`. POSIX `sh`/`dash` fail closed.

## Contracts And Data

- Module actions: `install`, `status`, `dry-run`.
- Catalog ids: `prereqs`, `codex-cli`, `runtimes`, `project-verify`.
- Add a future installer as `install/modules/<nn>-<id>/module.sh` + `module.ps1` and the matching `catalog.toml` row.

## Invariants

- Do not add a root file named `install`.
- Do not add a Makefile.
- Do not vendor the official Codex installer; pin URL + sha256.
- Windows x86_64 is native (ADR 0012); Windows arm64 is fail-closed (WSL2 pointer). WSL2 Ubuntu stays a supported POSIX path.
- Homebrew copies are not uninstalled; repo `.local/bin` must win PATH order.

## Verification

- `just dry-run`
- `just status`
- `just check`

## Known Gaps

- Bootstrap still globs; an extra numbered dir would install if `./setup` is run before the artifact gate.
- Codex `packages.*.sha256` are verified on the tarball install path; `install.sh` sha256 covers only the fallback.
