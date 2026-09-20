# 11. Language-server matrix as a pinned standard

- Status: accepted
- Date: 2026-09-20
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

Editor and agent tooling drifts per machine: different teammates pick
different Python/TS language servers, and Serena-style symbol
navigation depends on whichever LSP happens to be installed. The setup
already pins every other tool; LSP was the gap.

## Decision Outcome

Ship `plugins/hack-agent-lsp` (portable Agent Plugins 1.0.0) plus an
`lsp` section in `build/stack-pin.json`:

- One server per language, no alternates: `tsserver` bundled with
  `typescript` 7.0.2 (tsgo exists only as `@typescript/native-preview`
  dev builds — not pinned; `typescript-language-server` 6.0.0 is the
  optional stdio wrapper), `biome lsp-proxy`, `ty server`, `ruff server`,
  `rust-analyzer` (rustup component), `dart language-server` (Flutter
  SDK), `gopls` v0.23.0, `taplo` 0.10.0, `marksman` 2026-02-08,
  `vscode-langservers-extracted` 4.10.0, `yaml-language-server` 1.24.0,
  `bash-language-server` 5.8.1, `dockerfile-language-server-nodejs`
  0.15.0.
- `version_from` rows inherit existing pins (no number forks);
  `version` rows are pinned in `lsp.*` only.
- Two skills: `lsp-map` (the matrix and its rules) and `lsp-setup`
  (idempotent install commands per server).
- Agents prove code via the pinned CLIs, not editor diagnostics.
- `just reverify` tracks the npm-packaged servers and the GitHub-tag
  releases (`gopls/v*`, taplo, marksman, bifrost transports).

## Consequences

- Registered as `registered.lsp_plugin` + `lsp_plugin_skills`;
  marketplace row fourth; enabled in `.codex/config.toml`; module 40
  installs it with the rest.
- A missing language means "no server", not "pick one"; editor choice
  stays personal, the server does not.

## Confirmation

- `just check`, `pytest -q`, `just reverify` pass
- `codex plugin list` shows `hack-agent-lsp@saint-tibo` installed
