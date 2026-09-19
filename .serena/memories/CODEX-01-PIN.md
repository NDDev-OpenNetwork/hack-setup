<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 28de672 docs(serena): sync stack pin and bootstrap memories
Scope: build/codex-pin.json, docs/adr/0001-codex-cli-155-pin.md, install/modules/20-codex-cli/module.sh
Area: CODEX
-->

# CODEX-01-PIN

## Purpose

Record the verified Codex CLI pin for this repository.

## Source Of Truth

- `build/codex-pin.json`: `codex_cli=0.155.1`, `release_tag=rust-v0.155.1`, official `install.sh` URL/sha256, per-platform package hashes.
- `docs/adr/0001-codex-cli-155-pin.md`: accepted 2026-09-19.

## Current Behavior

`./setup` installs the official standalone package to `$HOME/.local/bin/codex` and symlinks `$REPO/.local/bin/codex`. `. install/env.sh` puts those directories ahead of bun/npm/brew shims. bun global `@openai/codex@0.155.1` may still exist; PATH order decides which binary runs.

## Contracts And Data

- Reject `0.156.0-alpha.*` and discontinued `codex-app` / `Codex.app`.
- Official installer: `https://github.com/openai/codex/releases/download/rust-v0.155.1/install.sh`.
- Installer env: `CODEX_RELEASE`, `CODEX_NON_INTERACTIVE`, `CODEX_INSTALL_DIR`, `CODEX_INSTALLER_USE_RELEASES_OPENAI_COM`.
- Official docs: `https://developers.openai.com/codex` and `https://developers.openai.com/plugins/build/plugins`.
- Plugin schema: `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`.

## Invariants

- `codex --version` must print `codex-cli 0.155.1` before setup work is treated as verified.
- Do not use the unpinned `chatgpt.com/codex/install.sh` as the catalog installer.

## Verification

- `codex --version`
- `python3 -c "import json; print(json.load(open('build/codex-pin.json'))['codex_cli'])"`
