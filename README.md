# hack-setup

Shared Codex `0.155.1` setup for a three-person team that will later work in
one private repo: `BAITC-Hacks/hack-a58598e0-saint-tibo`.

This public staging repo holds the project surfaces, the installer catalog,
and the frozen product stack. Do not push the hackathon repo until the owner
says go.

## One command after clone

macOS and Linux:

```bash
git clone git@github.com:NDDev-OpenNetwork/hack-setup.git
cd hack-setup
./setup
. install/env.sh
```

`./setup` is the only root entry. Modules: prereqs → official Codex CLI →
Node/bun/uv/Python 3.14 → project verify. JS installer is bun. Web is
React + Vite, not Next.js. Windows is fail-closed.

```bash
./setup --dry-run   # planned work, no downloads
./setup --status    # check without installing
make check          # artifact validator + host doctor
```

`install/env.sh` puts `$REPO/.local/bin` and `~/.local/bin` ahead of
brew/npm shims.

## Pins

| File | Role |
| --- | --- |
| `build/codex-pin.json` | Codex CLI `0.155.1` + official installer hashes |
| `build/stack-pin.json` | Product stack schema 2 |
| `build/stack-standard.md` | Generated version table; refresh with `--write` |
| `docs/adr/0001`–`0004` | Decisions |

```bash
codex --version                      # expected: codex-cli 0.155.1
python3 scripts/check_stack.py       # required host tools must match
python3 scripts/check_stack.py --list
python3 scripts/reverify_stack_pin.py
```

Desktop is the ChatGPT app (`brew install --cask chatgpt`). Do not install
the discontinued `codex-app` cask.

## After clone

1. Run `./setup` (or `make setup`).
2. Trust this project in Codex so `.codex/config.toml` loads.
3. Use repo skills from `.agents/skills/`.
4. Custom agents: `mapper`, `reviewer`, `implementer`.

See `AGENTS.md` and `install/README.md` for layout.
