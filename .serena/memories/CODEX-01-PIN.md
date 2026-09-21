<!-- Memory Metadata
Last updated: 2026-09-21
Last commit: 63ddace docs(serena): record deploy-e2e verification and full issue closure
Scope: build/codex-pin.json, docs/adr/0001-codex-cli-155-pin.md, install/modules/20-codex-cli/module.{sh,ps1}
Area: CODEX
-->

# CODEX-01-PIN

## Purpose

Record the Codex CLI pin for this repository.

## Source Of Truth

- `build/codex-pin.json`: `codex_cli=0.155.1`, `release_tag=rust-v0.155.1`, official `install.sh` URL/sha256, per-platform package hashes.
- `docs/adr/0001-codex-cli-155-pin.md`.
- `AGENTS.md` records release commit `be2951ea34f0d295ed0becf97079f92fa5f6950e`.

## Current Behavior

`./setup` installs the official standalone package to `$HOME/.local/bin/codex` and symlinks `$REPO/.local/bin/codex`. The module downloads the pinned `codex-package-<triple>.tar.gz`, verifies `packages.<platform>.sha256`, extracts the binary, and skips when `--version` already matches. Hashed official `install.sh` is the fallback for a platform missing from `packages`. On Windows the twin accepts only `*.exe` candidates when resolving the installed binary — npm `codex.ps1`/`.cmd` shims version-match but break outside their prefix.

## Contracts And Data

- Reject `0.156.0-alpha.*` and discontinued `codex-app` / `Codex.app`.
- Official installer: `https://github.com/openai/codex/releases/download/rust-v0.155.1/install.sh`.
- Installer env: `CODEX_RELEASE`, `CODEX_NON_INTERACTIVE`, `CODEX_INSTALL_DIR`, `CODEX_INSTALLER_USE_RELEASES_OPENAI_COM`.
- Plugin schema: `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`.

## Invariants

- `codex --version` must print `codex-cli 0.155.1` before setup work is treated as verified.
- Do not use the unpinned `chatgpt.com/codex/install.sh` as the catalog installer.

## Verification

- `codex --version`
- `python3 -c "import json; print(json.load(open('build/codex-pin.json'))['codex_cli'])"`

## Known Gaps

- Installer verifies downloaded package bytes against `packages.*.sha256`; `install.sh` sha256 covers only the fallback path.
