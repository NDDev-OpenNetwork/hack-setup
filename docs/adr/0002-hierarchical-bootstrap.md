# 2. Hierarchical macOS/Linux bootstrap

- Status: accepted
- Date: 2026-09-19
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The team needs one clone-then-install command that works on macOS and
Linux, and a place to drop future system installers without rewriting
the entrypoint.

## Decision Drivers

- One command after `git clone`
- macOS cannot keep both a file named `install` and directory `install/`
- Pin the official Codex `install.sh` and its sha256, not an unpinned URL
- Install the CLI to `~/.local/bin` so shell profiles do not store a
  clone-absolute PATH
- Leave room for later modules (runtimes, CLIs, datasets)

## Considered Options

- Root file `./install` plus ad-hoc scripts
- Vendor the 800-line official installer
- Hierarchical `install/modules/<nn>-<id>/` with `./setup` as the entry

## Decision Outcome

Chosen option: `./setup` execs `install/bootstrap.sh`. Modules are
discovered in numeric order. `install/catalog.toml` is the documented
contract and is enforced by `scripts/check_codex_setup.py`.

The Codex module downloads
`https://github.com/openai/codex/releases/download/rust-v0.155.1/install.sh`,
verifies `build/codex-pin.json` `installer.sha256`, then runs:

```
CODEX_RELEASE=0.155.1
CODEX_NON_INTERACTIVE=1
CODEX_INSTALLER_USE_RELEASES_OPENAI_COM=false
CODEX_INSTALL_DIR=$HOME/.local/bin
```

Windows is fail-closed. bun/npm/brew copies are not uninstalled; PATH
order after `. install/env.sh` prefers the pinned binary.

## Consequences

Future installers add a numbered directory and a catalog row. The
validator must stay in sync with the catalog. A Darwin root file named
`install` must never be added.

## Confirmation

- `./setup --dry-run` exits 0
- `./setup` installs or links Codex CLI `0.155.1`
- `python3 scripts/check_codex_setup.py` exits 0
