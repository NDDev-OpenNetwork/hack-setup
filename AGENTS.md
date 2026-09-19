# Saint Tibo Codex setup

Shared Codex project surfaces for a three-person team. Author here. The later
working repo is `BAITC-Hacks/hack-a58598e0-saint-tibo`. Do not push there
until the owner says go.

## Pin

- Codex CLI `0.155.1` (`rust-v0.155.1`). Reject alphas.
- Proof: `codex --version` must print `codex-cli 0.155.1`.
- Pin file: `build/codex-pin.json`.
- Decision: `docs/adr/0001-codex-cli-155-pin.md`.
- Stack versions: `build/stack-pin.json` schema 2. Re-verify on
  hackathon day with `python3 scripts/reverify_stack_pin.py`.
- Web is React 19.3 + Vite 8.3. Do not add Next.js. JS installer is bun.
- API contract is FastAPI OpenAPI; clients are generated, not rewritten.
- Isolated Python envs: API/workers (`redis` 8.1.0), Telegram (`redis` 7.4.1),
  GPU/ML, optional LiteLLM proxy-runtime. Do not merge those lockfiles.
- PostgreSQL is SoT. Qdrant is a derived index. RustFS holds objects.
  DuckDB is analytics only. User code never runs in the API process.

## Layout

| Surface | Path | Rule |
| --- | --- | --- |
| Instructions | `AGENTS.md` | This file. Nested `AGENTS.override.md` wins in that directory. |
| Repo skills | `.agents/skills/<name>/SKILL.md` | Source of truth. Do not copy these names into the plugin. |
| Marketplace | `.agents/plugins/marketplace.json` | Paths are relative to the repo root. |
| Plugin | `plugins/saint-tibo/plugin.json` | Portable Agent Plugins 1.0.0. |
| Project config | `.codex/config.toml` | Loads only after the project is trusted. |
| Custom agents | `.codex/agents/*.toml` | `mapper`, `reviewer`, `implementer`. |
| Bootstrap | `./setup` → `install/` | macOS/Linux catalog. JS installer is bun. Add future installers as `install/modules/<nn>-<id>/`. |
| Codex pin | `build/codex-pin.json` | CLI `0.155.1` + official installer hashes. |
| Stack pin | `build/stack-pin.json` | Schema 2. Generated table: `build/stack-standard.md`. |

Do not add team skills under `$CODEX_HOME/skills` (deprecated). Do not add
root `plugin.json` fields other than the portable schema. Do not mix
`default_permissions` with `sandbox_mode`. Do not add a root file named
`install` (it cannot coexist with `install/` on macOS).

## Team rules

- One claimed file owner at a time. Do not edit a file another teammate has open.
- Conventional Commits. Split implementation, tests, docs, and knowledge sync.
- No secrets, tokens, cookies, or private hackathon strategy in this public repo.
- Do not claim a check passed unless you ran it.

## Bootstrap

```bash
git clone git@github.com:NDDev-OpenNetwork/hack-setup.git
cd hack-setup
./setup
. install/env.sh
```

`./setup` downloads the pinned official Codex `install.sh`, verifies its
sha256 from `build/codex-pin.json`, and runs the numbered modules under
`install/modules/`. Windows is fail-closed.

## Quality gate

```bash
./setup --status
python3 scripts/check_codex_setup.py
python3 scripts/check_stack.py
codex --version
```

All four must succeed before the setup is treated as ready. Host doctor
fails if Codex/Node/bun/Python/uv drift. `python3 scripts/check_stack.py
--list` prints the frozen standard. `--strict` also requires declared
host tools (Rust/Go/Docker/...).
