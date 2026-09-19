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
  catalog.toml                # documented module contract
  bootstrap.sh                # discovers modules/<nn>-*/module.sh
  env.sh                      # prepends .local/bin then ~/.local/bin
  lib/                        # POSIX helpers
  modules/
    10-prereqs/               # python3 3.11+, tar, curl|wget, sha256
    20-codex-cli/             # official rust-v0.155.1 install.sh + digest
    30-project-verify/        # scripts/check_codex_setup.py + codex --version
```

Add a future installer as `install/modules/<nn>-<id>/module.sh` (`install` / `status` / `dry-run`). Disable with a `disabled` file in that directory. Keep `catalog.toml` in sync.

## Pins

`build/codex-pin.json` is the source of truth for Codex CLI `0.155.1`, the official `install.sh` URL/sha256, and per-platform package hashes. The Codex module downloads that script, verifies the digest, then runs:

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
| `./setup` | install enabled modules |
| `./setup --dry-run` | print planned work |
| `./setup --status` | check without downloads |
| `./setup --print-env` | print PATH export |
| `make test` | pytest |
