# Install catalog

One command after clone:

```sh
git clone git@github.com:NDDev-OpenNetwork/hack-setup.git
cd hack-setup
./setup
. install/env.sh
```

`./setup` is the only root entry. macOS cannot keep both a file named `install` and directory `install/`.

## Hierarchy

```text
setup                         # execs install/bootstrap.sh
install/
  catalog.toml                # snapshot of numbered dirs; not read at runtime
  bootstrap.sh                # globs modules/<nn>-*/module.sh
  env.sh                      # prepends .local/bin then ~/.local/bin
  lib/                        # POSIX helpers
  modules/
    10-prereqs/               # python3 3.11+, tar, curl|wget, sha256
    20-codex-cli/             # pinned rust-v0.155.1 package tarball + sha256
    30-runtimes/              # Node LTS, bun, uv, CPython 3.14
    40-project-verify/        # artifact gate + pinned versions
```

Add a future installer as `install/modules/<nn>-<id>/module.sh` (`install` / `status` / `dry-run`) and the matching `catalog.toml` row. Disable with a `disabled` file in that directory. Bootstrap does not read `enabled`.

## Pins

`build/codex-pin.json` is the Codex CLI pin. `build/stack-pin.json` is the
product stack pin; module `30-runtimes` installs Node/bun/uv/Python from it.
The Codex module downloads the pinned `codex-package-<triple>.tar.gz`,
verifies `packages.<platform>.sha256`, and extracts the binary. When the
pin has no package for the platform, it falls back to the hashed official
`install.sh` with:

```sh
CODEX_RELEASE=0.155.1
CODEX_NON_INTERACTIVE=1
CODEX_INSTALLER_USE_RELEASES_OPENAI_COM=false
CODEX_INSTALL_DIR=$HOME/.local/bin
```

The binary is installed to `~/.local/bin/codex` (not a clone-absolute PATH) and symlinked to `$REPO/.local/bin/codex`. Windows is fail-closed.

## Commands

| Command | Effect |
| --- | --- |
| `./setup` | install numbered modules (skip `disabled`) |
| `./setup --dry-run` | print planned work |
| `./setup --status` | check without downloads |
| `./setup --print-env` | print PATH export |
| `just test` | pytest |
| `just check` | artifact validator + host doctor |
| `just gate` | AGENTS four-command ready gate |
| `just stack` | print generated stack standard |
