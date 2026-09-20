---
name: lsp-setup
description: Install or repair the pinned language servers on a Saint Tibo host. Use when an editor or Serena cannot find an LSP, or on a fresh machine.
---

`./setup` pins node, bun, python, uv, codex and the plugins; LSP
servers ride on that toolchain but are not installed by it — install
only what your language and editor need. Every command below is
idempotent and version-pinned in `build/stack-pin.json` `lsp.*`.

Already present on a compliant host (no action):

- `ty server`, `ruff server` — declared host tools, proven by
  `check_stack.py --strict`
- `biome lsp-proxy` — per-project `bunx @biomejs/biome`
- `tsserver` — ships inside the pinned `typescript` dependency; VS
  Code/Cursor attach it built-in. Editors needing stdio:
  `bun i -g typescript-language-server@6.0.0`

Needs a matching toolchain on the host first:

- `rust-analyzer` — `rustup component add rust-analyzer` (requires a
  rustup-installed toolchain; a distro `rustc` has no component add)
- `dart language-server` — inside the Flutter SDK; `./setup` does not
  install Flutter, install it per the `clients.flutter` pin
- `gopls` — needs the pinned Go (`verify.declared` go 1.27.1)

Per-language extras:

```bash
go install golang.org/x/tools/gopls@v0.23.0          # Go
cargo install taplo-cli --locked --version 0.10.0    # TOML
brew install marksman                                # Markdown, macOS
bun i -g vscode-langservers-extracted@4.10.0         # JSON/HTML/CSS
bun i -g yaml-language-server@1.24.0                 # YAML
bun i -g bash-language-server@5.8.1                  # Shell
bun i -g dockerfile-language-server-nodejs@0.15.0    # Dockerfile
```

Notes:

- `bun i -g` is the JS installer (npm/pnpm banned by
  `do_not_use`); its global bins land in `~/.bun/bin`, on PATH after
  `. install/env.sh`. Verify with `which <server>`.
- `marksman` on Linux: no brew — fetch the `marksman-linux-x64` asset
  from GitHub release `2026-02-08`, chmod +x, drop into
  `~/.local/bin`.
- If an editor reports a missing server, check the binary is on PATH
  inside the editor's shell — launch the editor from a shell that
  sourced `install/env.sh`, or point the editor at the absolute path.
- Do not install servers globally that duplicate the matrix (no second
  Python or TS language server).
