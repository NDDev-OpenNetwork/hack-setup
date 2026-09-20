# Saint Tibo Codex setup — operating contract

You are running inside the pinned Saint Tibo setup: shared Codex
surfaces for a three-person team, authored here. This file is the
system prompt every session loads — it names the toolchain, the
workflow, and the standards. Everything below is either law (from
`build/`) or a pointer to where the law lives.

This repository carries toolchain and instructions. Product code lives
in the product repo (`NDDev-OpenNetwork/vibestrap` skeleton, later the
hackathon repo `BAITC-Hacks/hack-a58598e0-saint-tibo` — its first push
happens on hackathon day, on the owner's word).

## Mechanism

One loop: pin → projection → proof.

1. Law: `build/codex-pin.json` + `build/stack-pin.json`.
2. Runtime: `.codex/config.toml` after trust — a projection of
   `registered.session`, `models`, `registered.features`,
   `registered.mcp_servers`.
3. Proof: `just check` (pin == config == this file == generated
   standard). Ready: `just gate`.
4. Tech detail: `plugins/hack-agent-standards/standards/INDEX.md`
   → CORE, QUALITY when proving, one area file. Plugin skills are
   `$hack-agent-standards:<skill>` — bare `$name` does not match a
   plugin skill. Pin numbers win.
5. Why: ADRs 0001–0016 under `docs/adr/`.

## The operating model

The user talks to one main Codex App chat — the orchestrator. It
discusses, plans, registers GitHub issues (the source of truth), spawns
visible worker threads, merges lanes, verifies live, ships.

- **Spawn**: `codex_app.create_thread` / `send_message_to_thread` /
  `wait_threads` / `read_thread` — user-owned threads, not subagents.
  Full briefs live in `.agent/briefs/*.md`; prompts carry a pointer.
- **Worktree isolation**: each worker cuts `git worktree add
  ../<repo>-w<N> -b feat/<issue>-<slug> origin/dev` and works inside.
- **Lanes**: `feat/<issue>-<slug>` → `<user>` (`danil`/`ivan`/`artem`)
  → `dev` → `main`. Workers push only their own lane; the orchestrator
  merges `<user>`→`dev` behind the merge gate and `dev`→`main` on the
  owner's word.
- **Lane enforcement is mechanical**: tracked `.codex/lanes.json`
  declares protected branches; the PreToolUse hook denies protected
  pushes and `gh pr merge` unless the checkout carries the untracked
  `.agent/orchestrator` marker (orchestrator checkout only).
- **Deploy**: server-side pull watchers (`install/deploy/`) — dev
  follows `dev`, prod follows `main`, `docker compose` rebuild +
  healthcheck on every branch move. Done means verified live.
- **Hack mode**: laziest working solution, no review round, no test
  suite during the event; every deliberately cut corner gets a
  `hack:` comment for the debt ledger.

Playbooks: `$hack-agent-workflow:delegate-worker`,
`github-flow`, `ship-verify`, `hack-mode`, `session-boot`,
`agent-handoff`, `debt-ledger`.

## Pin

- Codex CLI `0.155.1` (`rust-v0.155.1`, commit
  `be2951ea34f0d295ed0becf97079f92fa5f6950e`). `codex --version` prints
  `codex-cli 0.155.1`. Installer hashes live in `build/codex-pin.json`.
- Stack versions: `build/stack-pin.json` schema 2. Re-verify on
  hackathon day with `just reverify`. `docs/research/` is archive, not
  law.
- Web standard: React 19.3 + Vite 8.3 + TypeScript `7.0.2`, installed
  and run exclusively through bun (`bun install`/`bun add`/`bunx`).
  shadcn arrives via `bunx shadcn@4.21.0`.
- API contract: FastAPI OpenAPI; clients are generated, never rewritten
  (`@hey-api/openapi-ts` `0.99.0` is the generator, not a web
  dependency).
- Python envs stay isolated: API/workers (`redis` 8.1.0), Telegram
  (`redis` 7.4.1), GPU/ML, Bifrost LLM gateway container
  (`maximhq/bifrost:v2.2.1`). Each keeps its own lockfile.
  `opencv-python-headless` is the one `cv2`.
- Session law: `approval_policy = "never"`,
  `sandbox_mode = "danger-full-access"`, `allow_login_shell = true`,
  `web_search = "live"` — the pinned full-access posture (ADR 0006;
  `--full-auto` is a different, weaker flag).
- Models: `gpt-6-astra` primary, `gpt-5.6-sol` secondary
  (`/review`, `codex -m gpt-5.6-sol`, or `--profile sol` outside this
  tree via `~/.codex/sol.config.toml`). Both run
  `model_reasoning_effort = "xhigh"`, context `872_000`, auto-compact
  `700_000` (usable `/status` `828400` — the catalog max is `872000`).
- Parallel work runs through the `codex_app.*` thread tools. Do not
  spawn Codex subagents (ADR 0007).
- Data standard: PostgreSQL is SoT, Qdrant is a derived index, RustFS
  holds objects, DuckDB is analytics only. User code never runs in the
  API process.

## Motion

Full playbook: `plugins/hack-agent-standards/standards/CORE.md`.

- Layers first (`web/`, `api/`, workers, clients, `infra/`); DDD
  modules inside a layer. Implement through the layers the request
  needs.
- i18n dictionaries `ru` / `kk` / `en` land with the first user-facing
  string.
- Observability: logs → Vector → OpenObserve; traces/metrics OTLP →
  OpenObserve (`deploy.pipeline`).
- Owner text this turn wins. Unspecified slices follow the opened frame
  and the pin.

## Plugin map

Every installed plugin and what each skill does. Invoke as
`$<plugin>:<skill>`.

| Plugin | Skills |
| --- | --- |
| `saint-tibo` | `saint-tibo` (project identity/summary) |
| `hack-agent-standards` | `apply-agent-standard` (INDEX router), `core-motion`, `quality-proof`, `pin-dependencies`, `web-ui`, `python-api`, `wire-contracts`, `data-stores`, `native-clients`, `ai-models`, `identity-auth`, `text-formats`, `file-documents`, `education-lessons`, `runtime-infra` |
| `hack-agent-workflow` | `session-boot` (serena-first open), `github-flow` (lanes + merge gate), `agent-handoff` (memories + plan + proof), `delegate-worker` (codex_app threads), `hack-mode` (delivery mode), `ship-verify` (live verification), `debt-ledger` (marker harvest) |
| `hack-agent-lsp` | `lsp-map` (one pinned server per language), `lsp-setup` (install them) |
| `hack-agent-mcp` | `mcp-usage` (route/verify/debug), `serena-workflow` (activate_project, memories, symbol edits), `research-workflow` (context7/grep/deepwiki/keenable), `component-workflow` (shadcn registry) |

Repo skills (`.agents/skills/`): `repo-orientation`,
`one-repo-workflow`, `apply-stack-rule` (INDEX alias), `quality-gate`.

MCP wiring is law: `registered.mcp_servers` → `.codex/config.toml`
`[mcp_servers.*]` — serena + shadcn (stdio), context7, grep, deepwiki,
keenable (HTTP, keyless by default; keys travel as env-var names only).

## Hooks and persistent instructions

`.codex/hooks.json` runs `.codex/hooks/hack_mode.py` on six events
(law: `registered.hooks`, ADR 0015):

- `SessionStart` (startup/resume/clear/compact) injects the hack-mode
  ruleset — including re-injection after every auto-compact.
- `UserPromptSubmit` adds the reminder + `STATUS` line (repo, branch,
  dirty count, last commit, `@me` issues via a 60 s gh cache).
- `PreToolUse` `Bash` is the lane guard described above.
- `PostToolUse` `Bash` reminds ship-verify after `git push`.
- `SessionEnd` and `Interrupt` append `.agent/session-log.ndjson` —
  how sessions end and where they were interrupted (timeout is capped
  at 3 s by Codex for these two events).

Codex runs a non-managed hook only while its `trusted_hash` matches the
hook definition — editing `hooks.json` silently skips hooks until
re-trusted. `just repair` (and module 20 at install) writes the managed
`[hooks.state.*]` entries into `~/.codex/config.toml` itself, so after
pulling hook changes run `just repair` once — no manual `/hooks` review
(ADR 0016).

Upstream caveats that shape this design (ADR 0016): `compact_prompt` is
ignored on the remote-compaction path (openai/codex#34428) — the
`SessionStart` `compact` matcher is the real re-injection channel; Codex
App threads can shadow project `developer_instructions` (#33238/#11004),
so this `AGENTS.md` remains the authoritative instruction channel.

Standalone messages toggle per-project mode
(`~/.codex/hack-mode-<repo>.json`): `hack ultra`, `normal mode`,
`hack mode`.

`developer_instructions` carries the operating law in the base
instruction chain (compaction-proof); `compact_prompt` preserves
issues/branch/worktree/lane/`hack:` markers across compaction;
`check_for_update_on_startup = false` (the CLI is pinned). `notify` is
host-owned: module 20 writes a managed block into
`~/.codex/config.toml` → `install/notify.sh` / `notify.ps1` toast on
turn complete. Custom slash commands do not exist in 0.155.1;
`/worktree`, `/fork`, `/app` cover the manual paths.

## Technology rules

Codex 0.155.1 has no glob / `.mdc` / `alwaysApply` loader. The
catalogue stays out of this file by design.

1. Read `plugins/hack-agent-standards/standards/INDEX.md`.
2. Open CORE for motion. Open QUALITY when proving. Open one matching
   area file. Prefer `$hack-agent-standards:<layer-skill>` when the
   layer is obvious. The rest of the catalogue stays closed.
3. Prefer `$hack-agent-standards:apply-agent-standard` when the layer
   is unclear. Repo alias `$apply-stack-rule` also opens INDEX.

A later product directory may carry its own `AGENTS.md` — read it
before editing that tree; nested `AGENTS.override.md` wins there.
Templates: `plugins/hack-agent-standards/nested/`, copied in the same
change that creates the tree.

## Layout

| Surface | Path | Rule |
| --- | --- | --- |
| Instructions | `AGENTS.md` | This file. Nested `AGENTS.override.md` wins in that directory. |
| Tech rules | `plugins/hack-agent-standards/standards/` | On-demand frames. Router is `INDEX.md`. |
| Layer skills | `plugins/hack-agent-standards/skills/` | Thin loaders. Names in the plugin map. |
| Nested AGENTS templates | `plugins/hack-agent-standards/nested/` | Copy when the product tree is created. |
| Standards plugin | `plugins/hack-agent-standards/plugin.json` | Portable Agent Plugins 1.0.0. |
| Repo skills | `.agents/skills/<name>/SKILL.md` | Source of truth. |
| Marketplace | `.agents/plugins/marketplace.json` | Paths are relative to the repo root. |
| Plugin | `plugins/saint-tibo/plugin.json` | Portable Agent Plugins 1.0.0. |
| Workflow plugin | `plugins/hack-agent-workflow/plugin.json` | serena-first / github-first / agent-first. ADR 0009. |
| MCP plugin | `plugins/hack-agent-mcp/plugin.json` | MCP workflow skills. Wiring: `registered.mcp_servers`. ADR 0013. |
| Hooks | `.codex/hooks.json` + `.codex/hooks/` | Five-event lifecycle. Law: `registered.hooks`. |
| Deploy kit | `install/deploy/` | Server-side pull watcher + provision script. ADR 0014. |
| Notify | `install/notify.sh` / `notify.ps1` | Turn-complete toast, wired into user config by module 20. |
| Project config | `.codex/config.toml` | Projection of the pin; loads after trust. |
| Bootstrap | `./setup` / `.\setup.ps1` → `install/` | macOS/Linux + native Windows modules. Discovery: `install/modules/<nn>-*`. |
| Codex pin | `build/codex-pin.json` | CLI `0.155.1` + official installer hashes. |
| Stack pin | `build/stack-pin.json` | Schema 2. Generated table: `build/stack-standard.md`. |
| Commands | `justfile` | `just gate` / `just check` / `just repair`. |

Installed plugins are a copy under `~/.codex/plugins/cache/`, not a
live view of the repo — after editing `plugins/*/`, refresh with
`codex plugin add <name>@saint-tibo` (`just check` fails on drift).

## Boundaries (hard law)

The standards above define how we work; these few lines define what
the toolchain refuses outright:

- `spawn_agent` / multi-agent features stay off — orchestration uses
  `codex_app.*` threads. Do not spawn Codex subagents.
- This public tree stays clean: secrets, tokens and hackathon-private
  strategy live in env vars and server-side files.
- This tree carries no application source — product work happens in
  the product repo.
- The JS toolchain is bun and the Python toolchain is uv — pnpm, npm
  installs, `pip` and `typescript@6`/`typescript-eslint`/`@next` in web
  are off-standard (`build/stack-pin.json` `do_not_use` lists the rest).
- Models are the pinned pair — `gpt-5.6-luna`, `gpt-5.6-terra` and bare
  `gpt-5.6` are off-standard.

## Team rules

- One claimed file owner at a time — claim files in an issue comment
  before editing.
- Conventional Commits; split implementation, docs, and knowledge sync.
- Commit messages carry only the message itself — the repo owner is the
  sole author. No `Co-Authored-By` lines, no "Generated with" trailers,
  no AI attribution of any kind.
- A check counts as passing only when you ran it.
- Check commands read state — they leave formatting, lockfiles,
  generated clients and migrations untouched.

## Bootstrap

```bash
git clone git@github.com:NDDev-OpenNetwork/hack-setup.git
cd hack-setup
./setup
. install/env.sh
```

`./setup` downloads the pinned Codex package tarball, verifies its
sha256 from `build/codex-pin.json` `packages.*` (hashed official
`install.sh` is the fallback), and runs the numbered modules under
`install/modules/`. Supported hosts: macOS, Ubuntu/Linux, and Windows
x86_64 natively via `.\setup.ps1` → `install/bootstrap.ps1` (ADR 0012).
WSL2 Ubuntu also works as a POSIX path; Windows arm64 is fail-closed.

## Quality gate

```bash
./setup --status
python3 scripts/check_codex_setup.py
python3 scripts/check_stack.py
codex --version
```

All four must succeed before the setup is treated as ready. `just gate`
runs the same four. `just check` is only the two Python scripts.
`just repair` (`scripts/repair_setup.py`, law `registered.repair`)
diagnoses the setup, auto-fixes safe drift — plugin cache parity,
managed notify/sol user-config blocks, `.agent` dirs, stale hook
bytecode, corrupt hook state files — and ends with the real checkers;
it reports rather than touches what needs a human or `./setup`. Host
doctor fails if Codex/Node/bun/Python/uv drift.
`python3 scripts/check_stack.py --list` prints the frozen standard.
`--strict` also requires declared host tools (Rust/Go/Docker/...).
Hackathon-day live drift only: `just reverify`.
