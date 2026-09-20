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
setup.ps1                     # calls install/bootstrap.ps1 (native Windows)
install/
  catalog.toml                # snapshot of numbered dirs; not read at runtime
  bootstrap.sh                # globs modules/<nn>-*/module.sh
  bootstrap.ps1               # globs modules/<nn>-*/module.ps1
  env.sh / env.ps1            # session PATH for the user shell
  lib/                        # POSIX helpers (.sh) + Windows twins (.ps1)
  modules/
    10-prereqs/               # tar, git, gh; python3 3.11+ on POSIX
    20-codex-cli/             # pinned rust-v0.155.1 package/installer + sha256
    30-runtimes/              # Node LTS, bun, uv, CPython 3.14
    40-project-verify/        # artifact gate + pinned versions
```

Every module dir carries a `module.sh` (POSIX) and a `module.ps1`
(native Windows) twin — same ids, actions, and pin reads; the checker
requires both. Add a future installer as `install/modules/<nn>-<id>/`
with both files (`install` / `status` / `dry-run`) and the matching
`catalog.toml` row. Disable with a `disabled` file in that directory.
Bootstrap does not read `enabled`.

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

The binary is installed to `~/.local/bin/codex` (not a clone-absolute PATH) and symlinked to `$REPO/.local/bin/codex`. The module also writes the managed `~/.codex/sol.config.toml` profile overlay and strips a legacy `[profiles.sol]` table from the user config (Codex 0.155.1 ignores project-local `profiles`; since 0.134 `--profile` reads `<name>.config.toml`). Supported hosts: macOS, Ubuntu/Linux, and Windows x86_64 natively — `.\setup.ps1` runs the pinned official `install.ps1`, which manages `%LOCALAPPDATA%\Programs\OpenAI\Codex\bin` and the persistent user PATH (ADR 0012). WSL2 works as a POSIX path; Windows arm64 is fail-closed.

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
