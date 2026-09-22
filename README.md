# hack-setup

Shared Codex `0.155.1` setup for a three-person team that will later work in
one private repo: `BAITC-Hacks/hack-a58598e0-saint-tibo`.

This public staging repo holds the project surfaces, the installer catalog,
and the frozen product stack. Do not push the hackathon repo until the owner
says go.

## One command after clone

Supported hosts: macOS (arm64/x86_64), Ubuntu/Linux (x86_64/arm64), and
Windows x86_64 **natively** (ADR 0012; WSL2 also works as a POSIX path).

macOS / Linux / WSL:

```bash
git clone git@github.com:NDDev-OpenNetwork/hack-setup.git
cd hack-setup
./setup --member <danil|ivan|artem>
. install/env.sh
```

Windows (PowerShell):

```powershell
git clone https://github.com/NDDev-OpenNetwork/hack-setup.git
cd hack-setup
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 --member <danil|ivan|artem>
. .\install\env.ps1
```

`./setup` (POSIX) and `.\setup.ps1` (Windows) are the only root entries.
`--member <name>` (or bare `--danil`/`--ivan`/`--artem`; `-Member` also
works on PowerShell) applies the shared git defaults and writes your git
identity from `gh api user` — the gh login must match the pinned member
login (`stack-pin.json` `team.members`), so wrong-lane commits cannot
happen silently. Without `--member` the defaults still apply but identity
is skipped. `--os <macos|ubuntu|windows>` asserts the target family, or
previews it under `--dry-run`.
Modules: prereqs → member → official Codex CLI → Node/bun/uv/Python 3.14 →
project verify. JS installer is bun. Web is React + Vite +
TypeScript 7.0.2 only, not Next.js.

Host prerequisites: `git`, `gh` (GitHub CLI, `gh auth login` — the
workflow is github-first). POSIX also needs `tar`, `curl` or `wget`,
`sha256sum` or `shasum`, `python3 >= 3.11` (all in-box or one package on
Ubuntu/macOS). Windows uses in-box `tar.exe`, `Get-FileHash`, and
`ConvertFrom-Json`, so no host python is required to bootstrap; `gh`
installs via `winget install GitHub.cli`. Strict doctor
(`check_stack.py --strict`) also expects the declared tools when you
work in their area: rustc, go, docker + compose, psql, redis-server,
ruff, pytest, just, ty.

```bash
./setup --dry-run   # planned work, no downloads (same flags on setup.ps1)
./setup --status    # check without installing
just check          # artifact validator + host doctor
```

`install/env.sh` / `install\env.ps1` put `$REPO/.local/bin`,
`~/.local/bin`, and `~/.bun/bin` (bun global installs) ahead of system
shims; Windows additionally exposes `%LOCALAPPDATA%\Programs\OpenAI\Codex\bin`.

## Pins

| File | Role |
| --- | --- |
| `build/codex-pin.json` | Codex CLI `0.155.1` + official installer hashes |
| `build/stack-pin.json` | Product stack schema 2. `control` names the loop |
| `.codex/config.toml` | Runtime projection of session + models + features |
| `build/stack-standard.md` | Generated; refresh with `--write` |
| `just check` | Proof that pin == config == AGENTS == generated |
| `docs/adr/0001`–`0016` | Decisions |
| `justfile` | Project commands (`just gate`, `just check`, `just repair`) |
| `plugins/hack-agent-standards/standards/` | On-demand frames. `docs/research/` is archive |

```bash
codex --version     # expected: codex-cli 0.155.1
just check          # artifact validator + host doctor
just live           # real Serena MCP proof (handshake/symbol/memory)
just repair         # diagnose + auto-fix safe drift (plugin cache, user config)
just stack          # print generated standard
just reverify       # hackathon-day network drift
```

Desktop is the ChatGPT app (`brew install --cask chatgpt`). Do not install
the discontinued `codex-app` cask.

## After clone

1. Run `./setup --member <your-name>` (or `just setup` + `--member`).
2. Trust this project in Codex so `.codex/config.toml` loads. Session
   law is YOLO (`approval_policy = "never"`,
   `sandbox_mode = "danger-full-access"`). See ADR 0006.
3. `./setup` also registers the marketplace and installs all five
   plugins (`saint-tibo`, `hack-agent-standards`, `hack-agent-workflow`,
   `hack-agent-lsp`, `hack-agent-mcp`), and pre-warms the MCP stdio
   caches (serena-agent via uvx, shadcn via bunx).
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
6. MCP servers: six wired via `[mcp_servers.*]` in
   `.codex/config.toml` (law: `registered.mcp_servers`) — serena
   (semantic code + memories), shadcn (component registries), context7
   (versioned docs), grep (real code on GitHub), deepwiki (repo Q&A),
   keenable (web search). All keyless; optional `CONTEXT7_API_KEY` /
   `KEENABLE_API_KEY` env vars lift limits. Verify: `codex mcp list`.
   ADR 0013.

See `AGENTS.md` and `install/README.md` for layout.

## Devin setup (twin)

`devin-setup/` is a self-contained second setup for the Devin CLI —
same law model, same `--member`/`--os` flags, same shared
prereqs/member/runtimes code (byte-identical, checker-guarded). It pins
`devin 3000.11.1` + `herdr 0.9.1`, projects `.devin/` config, MCP and
hooks, installs the `hack-devin-workflow` plugin locally, and replaces
codex_app thread orchestration with herdr panes (`herdr agent
start/prompt/read/wait`). Docs and proof: `devin-setup/README.md`,
`devin-setup/AGENTS.md`, `cd devin-setup && just gate`.
