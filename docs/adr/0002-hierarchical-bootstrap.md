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
discovered by glob `install/modules/[0-9][0-9]-*` in numeric order.
A `disabled` file skips a module. `install/catalog.toml` is a snapshot
of those directories; bootstrap does not read it. `enabled` is
documentary. `scripts/check_codex_setup.py` requires the snapshot to
match the numbered dirs exactly.

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

Current modules: `10-prereqs`, `20-codex-cli`, `30-runtimes`,
`40-project-verify`. Future installers add `install/modules/<nn>-<id>/`
and the matching `catalog.toml` row so the artifact gate still passes.
A Darwin root file named `install` must never be added.

## Confirmation

- `just dry-run` / `./setup --dry-run` exits 0
- `./setup` installs or links Codex CLI `0.155.1` and pinned runtimes
- `just check` exits 0
- Project commands are `justfile`. Do not add a Makefile.
