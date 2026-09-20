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
React + Vite + TypeScript 7.0.2 only, not Next.js. Windows is fail-closed.

```bash
./setup --dry-run   # planned work, no downloads
./setup --status    # check without installing
just check          # artifact validator + host doctor
```

`install/env.sh` puts `$REPO/.local/bin` and `~/.local/bin` ahead of
brew/npm shims.

## Pins

| File | Role |
| --- | --- |
| `build/codex-pin.json` | Codex CLI `0.155.1` + official installer hashes |
| `build/stack-pin.json` | Product stack schema 2. `control` names the loop |
| `.codex/config.toml` | Runtime projection of session + models + features |
| `build/stack-standard.md` | Generated; refresh with `--write` |
| `just check` | Proof that pin == config == AGENTS == generated |
| `docs/adr/0001`–`0009` | Decisions |
| `justfile` | Project commands (`just gate`, `just check`) |
| `plugins/hack-agent-standards/standards/` | On-demand frames. `docs/research/` is archive |

```bash
codex --version     # expected: codex-cli 0.155.1
just check          # artifact validator + host doctor
just stack          # print generated standard
just reverify       # hackathon-day network drift
```

Desktop is the ChatGPT app (`brew install --cask chatgpt`). Do not install
the discontinued `codex-app` cask.

## After clone

1. Run `./setup` (or `just setup`).
2. Trust this project in Codex so `.codex/config.toml` loads. Session
   law is YOLO (`approval_policy = "never"`,
   `sandbox_mode = "danger-full-access"`). See ADR 0006.
3. From the repo root, register and install the plugins:

   ```bash
   codex plugin marketplace add .
   codex plugin add saint-tibo@saint-tibo
   codex plugin add hack-agent-standards@saint-tibo
   codex plugin add hack-agent-workflow@saint-tibo
   ```

   Installed plugins are a copy under `~/.codex/plugins/cache/`. After
   editing `plugins/*/` re-run `codex plugin add <name>@saint-tibo`;
   `just check` fails on drift.
4. Use repo skills from `.agents/skills/`.
5. Models: `gpt-6-astra` primary, `gpt-5.6-sol` secondary — `/review`
   uses it; an explicit sol session here is `codex -m gpt-5.6-sol`
   (project `model` outranks profile overlays). `./setup` also installs
   `~/.codex/sol.config.toml` so `--profile sol` works in unpinned dirs.
   Both `xhigh`. Context `872000` / compact `700000`. No Codex
   subagents. ADR 0007. Frames: `hack-agent-standards@saint-tibo`,
   ADR 0008.

See `AGENTS.md` and `install/README.md` for layout.
