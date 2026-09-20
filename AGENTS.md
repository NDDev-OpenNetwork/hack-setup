# Saint Tibo Codex setup

Shared Codex project surfaces for a three-person team. Author here. The later
working repo is `BAITC-Hacks/hack-a58598e0-saint-tibo`. Do not push there
until the owner says go. This repository is toolchain and instructions only.
Do not add application source, screens, or business logic here.

## Mechanism

One loop. Do not fork numbers outside the pin.

1. Law: `build/codex-pin.json` + `build/stack-pin.json`.
2. Runtime: `.codex/config.toml` after trust. It is a projection of
   `registered.session`, `models`, and `registered.features`.
3. Proof: `just check` (pin == config == this file == generated standard).
   Ready: `just gate`.
4. Tech detail: `plugins/hack-agent-standards/standards/INDEX.md`
   → CORE, QUALITY when proving, one area file. Plugin skills are
   `$hack-agent-standards:<skill>` (see Motion). Bare `$name` does
   not match a plugin skill. Pin numbers win.
5. Why: ADRs 0001–0012.

## Pin

- Codex CLI `0.155.1` (`rust-v0.155.1`, commit `be2951ea34f0d295ed0becf97079f92fa5f6950e`). Reject alphas.
- Proof: `codex --version` must print `codex-cli 0.155.1`.
- Pin file: `build/codex-pin.json`.
- Stack versions: `build/stack-pin.json` schema 2. Re-verify on
  hackathon day with `just reverify`. `docs/research/` is archive, not law.
- Web is React 19.3 + Vite 8.3 + TypeScript `7.0.2` only. Do not add Next.js,
  `typescript@6`, `@typescript/typescript6`, or typescript-eslint in web.
  JS installer is bun.
- API contract is FastAPI OpenAPI; clients are generated, not rewritten.
  `@hey-api/openapi-ts` `0.99.0` is not a web workspace dependency. No `@next`.
- Isolated Python envs: API/workers (`redis` 8.1.0), Telegram (`redis` 7.4.1),
  GPU/ML, plus the Bifrost LLM gateway container
  (`maximhq/bifrost:v2.2.1`). Do not merge those lockfiles.
  One `cv2`: `opencv-python-headless` only. Do not `uv add docling` unconstrained.
  Install shadcn with `bunx shadcn@4.21.0`, never `bun add shadcn`.
- Session law: no OS sandbox, never ask. Pin:
  `build/stack-pin.json` `registered.session`. Config:
  `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`,
  `allow_login_shell = true`, `web_search = "live"`. `--full-auto` is
  not this. Do not add project `.codex/rules`. ADR 0006.
- Models: primary `gpt-6-astra`, secondary `gpt-5.6-sol`.
  `/review` is `gpt-5.6-sol` (project `review_model`). For a sol session
  in this tree use `codex -m gpt-5.6-sol` — the project `model` key
  outranks profile overlays. `./setup` also writes
  `~/.codex/sol.config.toml` so `--profile sol` works in unpinned dirs.
  Both `model_reasoning_effort = "xhigh"`. No luna/terra, no bare
  `gpt-5.6`.
  Context `872_000`, compact `700_000`. Catalog max for both slugs
  is `872000` (usable `/status` `828400`). Do not write 1M / 900k;
  0.155.1 clamps those.
  Do not spawn Codex subagents. ADR 0007.
- PostgreSQL is SoT. Qdrant is a derived index. RustFS holds objects.
  DuckDB is analytics only. User code never runs in the API process.

## Motion

Full playbook: `plugins/hack-agent-standards/standards/CORE.md`. Do not
dump the catalogue into this file.

- Layers first (`web/`, `api/`, workers, clients, `infra/`). DDD modules
  inside a layer. Implement through the layers the request needs.
- i18n dictionaries `ru` / `kk` / `en` on the first user-facing string.
- Logs → Vector → OpenObserve; traces/metrics OTLP → OpenObserve
  (`deploy.pipeline`).
- PostgreSQL is SoT. User code never runs in the API process.
- Owner text this turn wins. Unspecified slices follow the opened frame
  and the pin.

Layer skills (plugin `hack-agent-standards`): `apply-agent-standard`
(INDEX), `core-motion`, `quality-proof`, `pin-dependencies`, `web-ui`,
`python-api`, `wire-contracts`, `data-stores`, `native-clients`,
`ai-models`, `identity-auth`, `text-formats`, `file-documents`,
`education-lessons`, `runtime-infra`.

Workflow skills (plugin `hack-agent-workflow`, invoke
`$hack-agent-workflow:<name>`): `session-boot` (serena-first open:
memories + NEXT-SESSION + issues), `github-flow` (github-first loop:
named issue → work branch → personal named branch → dev → main),
`agent-handoff` (agent-first close: memories + plan + quoted proof),
`delegate-worker` (orchestrator → visible Codex App worker thread via
`codex_app.*` tools: brief with issues, lane, worktree; not subagents),
`hack-mode` (persistent hackathon delivery mode: laziest working
solution, no review round, no test suite, `hack:` markers on deferred
corners), `ship-verify` (build on the server, check the live result —
done means live), `debt-ledger` (harvest `hack:`/`ponytail:` markers
for post-hackathon cleanup). hack-mode + ship-verify adapted from
ponytail (MIT), archive at `docs/research/ponytail/`.

Tooling skills (plugin `hack-agent-lsp`, invoke
`$hack-agent-lsp:<name>`): `lsp-map` (one pinned language server per
language, `lsp.*` in the stack pin), `lsp-setup` (install the pinned
servers on a host).

MCP skills (plugin `hack-agent-mcp`, invoke `$hack-agent-mcp:<name>`):
`mcp-usage` (route between the six servers, verify, debug),
`serena-workflow` (activate_project, memories, symbol edits),
`research-workflow` (context7 docs, grep code, deepwiki repos,
keenable web), `component-workflow` (shadcn registry flow). Server
wiring is law: `registered.mcp_servers` → `.codex/config.toml`
`[mcp_servers.*]`. Keyless by default; keys via env-var names only.

Hooks live at the project layer: `.codex/hooks.json` runs
`.codex/hooks/hack_mode.py` — injects the `hack-mode` ruleset on
SessionStart (startup/resume/clear/compact) and a one-line reminder +
`STATUS` line (repo, branch, dirty count, last commit, assigned issues
via 60 s gh cache) on every prompt. Plugin manifests cannot carry
hooks in 0.155.1 (`plugin_hooks` removed, openai/codex#39895); no
subagent hooks (agents are disabled and lazy-mode injection biases
reviewers). Standalone commands toggle per-project state
(`~/.codex/hack-setup-mode.json`): `hack ultra`, `normal mode`,
`hack mode`. Law: `registered.hooks`.

Orchestration (ADR 0014): the main chat in Codex App spawns visible
worker threads with `codex_app.create_thread` +
`send_message_to_thread` — user-owned threads, not subagents, so
`agents.enabled = false` stands. Lanes: `feat/<issue>` → `<user>` →
`dev` → `main` (see `$hack-agent-workflow:github-flow`). Deploys are
server-side pull watchers (`install/deploy/`): dev follows `dev`, prod
follows `main`. Law: `registered.deploy`.

## Technology rules

Codex 0.155.1 has no glob / `.mdc` / `alwaysApply` loader. Do not dump the
catalogue into this file. Do not add `plugins/hack-agent-standards/standards/*`
to `project_doc_fallback_filenames`.

1. Read `plugins/hack-agent-standards/standards/INDEX.md`.
2. Open CORE for motion. Open QUALITY when proving. Open one matching
   area file. Prefer `$hack-agent-standards:<layer-skill>` when the
   layer is obvious. Do not load the rest of the catalogue.
3. Prefer `$hack-agent-standards:apply-agent-standard` when the layer
   is unclear. Repo alias `$apply-stack-rule` still opens INDEX.

If a later product directory has its own `AGENTS.md`, read that file before
editing that tree. Nested `AGENTS.override.md` wins in that directory.
Templates: `plugins/hack-agent-standards/nested/`. Copy in the same
change that creates the tree. Do not create empty product trees.

## Layout

| Surface | Path | Rule |
| --- | --- | --- |
| Instructions | `AGENTS.md` | This file. Nested `AGENTS.override.md` wins in that directory. |
| Tech rules | `plugins/hack-agent-standards/standards/` | On-demand frames. Router is `INDEX.md`. |
| Layer skills | `plugins/hack-agent-standards/skills/` | Thin loaders. Names in Motion. |
| Nested AGENTS templates | `plugins/hack-agent-standards/nested/` | Copy when the product tree is created. |
| Standards plugin | `plugins/hack-agent-standards/plugin.json` | First setup component. Portable Agent Plugins 1.0.0. |
| Repo skills | `.agents/skills/<name>/SKILL.md` | Source of truth. Do not copy these names into the plugin. |
| Marketplace | `.agents/plugins/marketplace.json` | Paths are relative to the repo root. |
| Plugin | `plugins/saint-tibo/plugin.json` | Portable Agent Plugins 1.0.0. |
| Workflow plugin | `plugins/hack-agent-workflow/plugin.json` | serena-first / github-first / agent-first. ADR 0009. |
| MCP plugin | `plugins/hack-agent-mcp/plugin.json` | MCP workflow skills. Wiring: `registered.mcp_servers`. ADR 0013. |
| Hooks | `.codex/hooks.json` + `.codex/hooks/` | hack-mode injection + prompt STATUS. Law: `registered.hooks`. Never plugin manifests. |
| Deploy kit | `install/deploy/` | Server-side pull watcher + provision script. dev→`dev`, prod→`main`. ADR 0014. |
| Project config | `.codex/config.toml` | YOLO after trust. Matches `registered.session` + `models` + `registered.mcp_servers`. Loads only after the project is trusted. |
| Bootstrap | `./setup` / `.\setup.ps1` → `install/` | macOS/Linux + native Windows modules. Discovery: `install/modules/<nn>-*`. |
| Codex pin | `build/codex-pin.json` | CLI `0.155.1` + official installer hashes. |
| Stack pin | `build/stack-pin.json` | Schema 2. Generated table: `build/stack-standard.md`. |
| Commands | `justfile` | `just gate` / `just check`. No Makefile. |

Do not add team skills under `$CODEX_HOME/skills` (deprecated). Do not add
root `plugin.json` fields other than the portable schema. Do not mix
`default_permissions` with `sandbox_mode`. Do not add a root file named
`install` (it cannot coexist with `install/` on macOS).

Installed plugins are a copy under `~/.codex/plugins/cache/`, not a live
view of the repo. After editing `plugins/*/`, refresh with
`codex plugin add <name>@saint-tibo` — `just check` fails on drift.

## Team rules

- One claimed file owner at a time. Do not edit a file another teammate has open.
- Conventional Commits. Split implementation, tests, docs, and knowledge sync.
- No secrets, tokens, cookies, or private hackathon strategy in this public repo.
- Do not claim a check passed unless you ran it.
- Check commands must not silently format, rewrite lockfiles, generate
  clients, or apply migrations.

## Code Review Rules

- Versions come from `build/stack-pin.json`. Do not invent unpinned libraries.
- Do not add application source in this staging repo.
- Reject pnpm, Next.js, a second JS lockfile, and items in
  `build/stack-pin.json` `do_not_use`.
- Reject `gpt-5.6-luna`, `gpt-5.6-terra`, and Codex `spawn_agent` / multi-agent.

## Bootstrap

```bash
git clone git@github.com:NDDev-OpenNetwork/hack-setup.git
cd hack-setup
./setup
. install/env.sh
```

`./setup` downloads the pinned Codex package tarball, verifies its sha256
from `build/codex-pin.json` `packages.*` (hashed official `install.sh` is
the fallback), and runs the numbered modules under `install/modules/`.
Supported hosts: macOS, Ubuntu/Linux, and Windows x86_64 natively via
`.\setup.ps1` → `install/bootstrap.ps1` — a PowerShell twin of the same
catalog (pinned `install.ps1`, `uv-installer.ps1`, bun/node zips; ADR
0012). WSL2 Ubuntu also works as a POSIX path; Windows arm64 is
fail-closed.

## Quality gate

```bash
./setup --status
python3 scripts/check_codex_setup.py
python3 scripts/check_stack.py
codex --version
```

All four must succeed before the setup is treated as ready. `just gate`
runs the same four. `just check` is only the two Python scripts. Host
doctor fails if Codex/Node/bun/Python/uv drift.
`python3 scripts/check_stack.py --list` prints the frozen standard.
`--strict` also requires declared host tools (Rust/Go/Docker/...).
Hackathon-day live drift only: `just reverify`.
