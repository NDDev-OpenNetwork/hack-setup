# hack-setup

Shared Codex `0.155.1` setup for a three-person team that will later work in
one private repo: `BAITC-Hacks/hack-a58598e0-saint-tibo`.

This public staging repo holds the project surfaces and the installer
catalog. Do not push the hackathon repo until the owner says go.

## One command after clone

macOS and Linux:

```bash
git clone git@github.com:NDDev-OpenNetwork/hack-setup.git
cd hack-setup
./setup
. install/env.sh
```

`./setup` is the only root entry. It runs numbered modules under
`install/modules/` (prereqs → official Codex CLI pin → project verify).
Add future installers as `install/modules/<nn>-<id>/module.sh` and list
them in `install/catalog.toml`. Windows is fail-closed.

```bash
./setup --dry-run   # planned work, no downloads
./setup --status    # check without installing
```

`install/env.sh` puts `$REPO/.local/bin` and `~/.local/bin` ahead of
bun/npm/brew shims. The official installer writes `~/.local/bin/codex`
and the bootstrap symlinks it into the repo `.local/` tree.

## Pin proof

```bash
codex --version
# expected: codex-cli 0.155.1
```

Desktop is the ChatGPT app (`brew install --cask chatgpt`). Do not install
the discontinued `codex-app` cask.

## After clone

1. Run `./setup` (or `make setup`).
2. Trust this project in Codex so `.codex/config.toml` loads.
3. Use repo skills from `.agents/skills/` (`/skills` or `$name`).
4. Custom agents: `mapper`, `reviewer`, `implementer`.

## Layout

See `AGENTS.md` and `install/README.md`. Pin and rationale:
`build/codex-pin.json`, `docs/adr/0001-codex-cli-155-pin.md`,
`docs/adr/0002-hierarchical-bootstrap.md`.
