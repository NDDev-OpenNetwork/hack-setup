<!-- Memory Metadata
Last updated: 2026-09-19
Last commit: 67b0862 chore: add license, ignore rules, and Serena languages
Scope: build/codex-pin.json, docs/adr/0001-codex-cli-155-pin.md
Area: CODEX
-->

# CODEX-01-PIN

## Purpose

Record the verified Codex CLI pin for this repository.

## Source Of Truth

- `build/codex-pin.json`: `codex_cli=0.155.1`, `release_tag=rust-v0.155.1`.
- `docs/adr/0001-codex-cli-155-pin.md`: accepted 2026-09-19.

## Current Behavior

Local PATH uses bun global `@openai/codex`. It was upgraded from `0.153.2` to `0.155.1` on 2026-09-19. Homebrew cask `codex` also publishes `0.155.1` but is not first on PATH.

## Contracts And Data

- Reject `0.156.0-alpha.*` and discontinued `codex-app` / `Codex.app`.
- Official docs: `https://developers.openai.com/codex` and `https://developers.openai.com/plugins/build/plugins`.
- Plugin schema: `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`.

## Invariants

- `codex --version` must print `codex-cli 0.155.1` before setup work is treated as verified.
- Do not treat NDDev `nddev-codex-app` `0.146.0` checkers as the contract for new artifacts.

## Verification

- `codex --version`
- `python3 -c "import json; print(json.load(open('build/codex-pin.json'))['codex_cli'])"`
