---
name: lsp-map
description: Load the Saint Tibo language-server matrix. Use when choosing, configuring, or questioning an LSP server for any language in the stack.
---

One language server per language. The matrix is law:
`build/stack-pin.json` `lsp.*`. Do not add a second server for a
language; do not pick versions outside the pin.

| Language | Server | Version source |
| --- | --- | --- |
| TypeScript / TSX | `tsserver` (bundled) | `runtimes.typescript` 7.0.2; optional stdio wrapper `typescript-language-server` 6.0.0 |
| JS/TS lint+format | `biome lsp-proxy` | `quality.biome` |
| Python types | `ty server` | `quality.ty` |
| Python lint/format | `ruff server` | `quality.ruff` |
| Rust | `rust-analyzer` | `runtimes.rust` (rustup component) |
| Go | `gopls` | `lsp.go` pin (`go install` it) |
| Dart / Flutter | `dart language-server` | `clients.flutter` (bundled) |
| TOML | `taplo lsp` | `lsp.toml` pin |
| Markdown | `marksman` | `lsp.markdown` pin |
| JSON / HTML / CSS | `vscode-langservers-extracted` | `lsp.json_html_css` pin |
| YAML | `yaml-language-server` | `lsp.yaml` pin |
| Shell | `bash-language-server` | `lsp.shell` pin |
| Dockerfile | `dockerfile-language-server-nodejs` | `lsp.dockerfile` pin |

Rules:

1. `version_from` rows inherit the toolchain pin — never restate the
   number elsewhere. `lsp.*` rows with `version` are pinned there only.
2. Agents prove code with the pinned CLIs (`ty check`, `ruff check`,
   `biome check`, `tsc`), not with editor diagnostics. LSP is for
   editors and for Serena-style symbol navigation.
3. No pyright/pylsp, no eslint LSP, no `@typescript/native-preview`
   (tsgo ships only as dated dev builds — wait for a stable bin). The
   matrix rows above are the whole list. A missing language means
   "no server", not "pick one".
4. Editor choice is personal (VS Code / Cursor / Zed); the server and
   its version are not.
5. Change = edit `lsp.*` in the pin, `--write` the standard, `just check`.
