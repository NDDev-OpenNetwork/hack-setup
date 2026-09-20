---
name: lsp-setup
description: Install or repair the pinned language servers on a Saint Tibo host. Use when an editor or Serena cannot find an LSP, or on a fresh machine.
---

`./setup` pins the toolchain; LSP servers ride on it. Install only what
you need — every command below is idempotent and version-pinned in
`build/stack-pin.json` `lsp.*`.

Already installed by `./setup` (no action):

- `ty server`, `ruff server` — uv tools (`quality.ty`, `quality.ruff`)
- `biome lsp-proxy` — per-project `bunx @biomejs/biome`
- `tsserver` — ships with the pinned `typescript` package; VS
  Code/Cursor use it built-in. Editors needing stdio:
  `npm i -g typescript-language-server@6.0.0` next to the pinned TS
- `dart language-server` — inside the Flutter SDK
- `rust-analyzer` — `rustup component add rust-analyzer`

Per-language extras:

```bash
go install golang.org/x/tools/gopls@v0.23.0          # Go
cargo install taplo-cli --locked --version 0.10.0    # TOML
brew install marksman                                # Markdown
npm i -g vscode-langservers-extracted@4.10.0         # JSON/HTML/CSS
npm i -g yaml-language-server@1.24.0                 # YAML
npm i -g bash-language-server@5.8.1                  # Shell
npm i -g dockerfile-language-server-nodejs@0.15.0    # Dockerfile
```

Notes:

- npm `-g` goes to the pinned node from `./setup` (`.local/bin`), not a
  system package manager.
- `taplo` on Linux: `cargo install` works; `brew` also carries it.
- `gopls` needs the pinned Go (`verify.declared` go 1.27.1).
- If an editor reports a missing server, check the binary is on PATH
  inside the editor's shell — launch the editor from a shell that
  sourced `install/env.sh`, or point the editor at the absolute path.
- Do not install servers globally that duplicate the matrix (no second
  Python or TS language server).
