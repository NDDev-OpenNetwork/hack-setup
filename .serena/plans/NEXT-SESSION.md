# Next session — 2026-09-20

Resume here. Chat is Russian. Repo files stay English. Do not add the
BAITC remote. No application source. Do not commit unless the owner asks.

## Mechanism

One loop. `build/stack-pin.json` `control` names it.

1. Law: `build/codex-pin.json` + `build/stack-pin.json`
2. Runtime: `.codex/config.toml` (projection of session + models + features)
3. Proof: `just check`. Ready: `just gate`
4. Detail: `plugins/hack-agent-standards/standards/INDEX.md` → CORE,
   QUALITY when proving, one area file. Prefer
   `$hack-agent-standards:<layer-skill>`. Router
   `$hack-agent-standards:apply-agent-standard`. Repo alias
   `$apply-stack-rule`. Pin numbers win. Owner turn beats a frame.
5. Why: ADRs 0001–0016

Do not fork numbers into frames, skills, or memories first. Edit pin +
config together, then `just check`.

## Current law (from the pin)

- CLI `0.155.1` / `rust-v0.155.1` / `be2951ea…`
- Session: `never` + `danger-full-access` + `web_search=live` (ADR 0006)
- Models: `gpt-6-astra` + `gpt-5.6-sol`, both `xhigh`. In-repo sol =
  `/review` or `codex -m gpt-5.6-sol` (project `model` outranks profile
  overlays). Module 20 writes `~/.codex/sol.config.toml` for unpinned
  dirs and strips legacy `[profiles.sol]` from the user config
- Context `872000` / compact `700000` / usable `828400` (ADR 0007)
- Subagents off. No `.codex/agents/*.toml`. No `model_catalog_json`
- Commands: `justfile` only
- Web TS `7.0.2` only. bun installer. No Next.js / pnpm
- Forms: `@tanstack/react-form` `1.33.5` + Standard Schema (zod direct,
  no adapter). No react-hook-form / @hookform/resolvers / zod-form-adapter
- LLM gateway: Bifrost `maximhq/bifrost:v2.2.1` (ADR 0010). API calls it
  via openai `3.16.2` `base_url`. No litellm in any env
- Frames plugin: `hack-agent-standards@saint-tibo` (ADR 0008)
- Workflow plugin: `hack-agent-workflow@saint-tibo` (ADR 0009) —
  serena-first `session-boot`, github-first `github-flow`,
  agent-first `agent-handoff`; invoke `$hack-agent-workflow:<name>`
- LSP plugin: `hack-agent-lsp@saint-tibo` (ADR 0011) — `lsp-map`
  + `lsp-setup`; the `lsp.*` matrix pins one server per language
- Plugin skill sets: `registered.{standards,workflow,lsp}_plugin_skills`

Tibo 1M/900k is documented, not runtime. Catalog max is 872000.

## Repo

This tree is `NDDev-OpenNetwork/hack-setup` on `main`.
`.codex/` is only `config.toml`.
Later remote (no git remote): `BAITC-Hacks/hack-a58598e0-saint-tibo`.
Setup owner stream: Danil.

## Done (committed and pushed on `main`)

- `9732012` catalogue: INDEX + CORE + QUALITY + 12 area files, all `ready`;
  15 layer skills; nested AGENTS templates; Motion kernel in `AGENTS.md`
- `2410c1c` module 20 installs the pinned `codex-package-<triple>.tar.gz`
  (verifies `packages.<platform>.sha256`); `install.sh` is fallback.
  ADRs 0001+0002 updated
- `06ace13` serena memories synced
- `c8ceb4b` forms switched to `@tanstack/react-form` + Standard Schema;
  `reverify` watches the new package; stale RHF refs removed
- Checker fails on `standards/*.md` orphans not linked in INDEX
- Host: all declared tools match the pin (`--strict` 15/15); Devin stale
  locks, research zip, merged branch cleaned
- Host codex: project trusted, `marketplace add .` done — config and all
  five plugins are live on this host
- `bc3c4c3` plugin install steps documented; legacy-profile ban scoped
  to `sol`
- `af3f9dd` checker enforces plugin cache parity with the repo
- `a0dba2e` `ty` `0.0.82` declared as a host tool
- `bdd614a` `hack-agent-workflow` plugin (ADR 0009): session-boot /
  github-flow / agent-handoff
- `1222e53`..`a5fa77d` LiteLLM → Bifrost gateway (ADR 0010); CI
  `check.yml` with artifacts + setup-e2e on ubuntu+macos; `dev` branch
  live; module 40 installs all plugins
- `cde1512` `hack-agent-lsp` plugin (ADR 0011): `lsp.*` matrix in the
  pin, `version_from` rendering, checker + reverify coverage
- `dfa98fc` serena sync for the lsp plugin
- `692874d` TS LSP is bundled `tsserver` (tsgo only exists as
  native-preview dev builds); `typescript-language-server` 6.0.0 is the
  optional stdio wrapper
- `5dcdbed` env.sh puts the JS-global bin dir on PATH; lsp-setup splits
  strict-declared / bundled / toolchain-required rows honestly
- `057e173` + `5947536` JS LSP installs use `bun i -g` into `~/.bun/bin`
  (npm banned by `do_not_use`); pin formatting restored
- Deep audit wave: `lsp.dart` now resolves `clients.flutter.dart`
  (3.13.4, the actual server version); `lsp.markdown` package filled;
  CI artifacts job bootstraps the pinned uv instead of pip; checker
  rejects npm/pip/pnpm in `lsp.*.install`; REVIEW covers all 5 plugins
- Windows x86_64 support = WSL2 Ubuntu (ADR 0012): os.sh detects WSL,
  `.gitattributes` pins eol=lf, CI gains a `setup-e2e-windows-wsl` job;
  checker + module 40 now iterate `marketplace.json` as the plugin SoT
- `ac7b1a2`+`2621efe` ADR 0012 superseded: Windows x86_64 is NATIVE —
  parallel PowerShell hierarchy (`setup.ps1`, `bootstrap.ps1`, `env.ps1`,
  `lib/*.ps1`, `module.ps1` per module), `windows-x86_64` packages pinned
  in codex-pin (`f45c273b…`) + node/bun zips, `installer_ps1` pins for
  codex (`ab832ca3…`) and uv (`e08cfe98…`); checker requires the ps1
  twins + `entry_windows`; CI `setup-e2e-windows` (windows-latest) is
  GREEN — codex-cli 0.155.1, all 5 plugins installed/enabled, both
  checkers PASS, all 5 required probes OK on a real Windows host. WSL2
  remains an optional POSIX path; Windows arm64 fail-closed.
  Strict-mode `.Count` scalar bug fixed via `@(...)` wrap.
- ADR 0013: six MCP servers are law in `registered.mcp_servers` and
  projected into `.codex/config.toml` — serena (stdio
  `uvx serena-agent==1.7.0`, codex context, `activate_project` per
  session; 1.7.0 predates `--project-from-cwd`), shadcn (stdio
  `bunx shadcn@4.21.0 mcp`), context7/grep/deepwiki/keenable remote
  keyless (`CONTEXT7_API_KEY`/`KEENABLE_API_KEY` env-var refs only).
  Plugin `mcp.json` was rejected: pinned codex forces stdio cwd into
  the plugin root and strips client-owned headers. Plugin
  `hack-agent-mcp` ships four skills (mcp-usage, serena-workflow,
  research-workflow, component-workflow). Module 30 now guarantees
  `bunx`/`uvx` links on all paths and pre-warms both stdio caches.
  reverify tracks `mcp.serena` (PyPI serena-agent).
- Skills wave: `hack-agent-workflow` gained `hack-mode` (ponytail
  ladder adapted: no review round, no test suite, `hack:` markers,
  done = verified live), `ship-verify` (build on server + check the
  live surface) and `debt-ledger` (harvest hack:/ponytail: markers).
  Upstream snapshot archived at `docs/research/ponytail/` (MIT,
  e3ba2aa6). Hooks live at project layer `.codex/hooks.json` +
  `.codex/hooks/hack_mode.py` (plugin manifests cannot carry hooks —
  plugin_hooks removed, openai/codex#39895): SessionStart injects the
  ruleset, UserPromptSubmit emits a one-line reminder and tracks
  standalone whole-message commands (`normal mode`, `hack ultra`,
  `hack mode`) in `~/.codex/hack-setup-mode.json`. Law:
  `registered.hooks`; checker `check_hooks` enforces file/events/
  scripts and bans Subagent* hooks.
- Orchestration wave (ADR 0014): `delegate-worker` skill — main Codex
  App chat spawns visible worker threads via `codex_app.*` tools
  (create_thread/send_message_to_thread/list_threads/read_thread);
  NOT subagents, `agents.enabled=false` stands. `github-flow` rewritten
  to the full lane model `feat/<issue>` → `<user>` → `dev` → `main`
  with orchestrator merge gate + live-verify. Deploy kit
  `install/deploy/`: server-side pull watcher (deploy-watch.sh +
  systemd units + provision-server.sh) — no GitHub admin needed.
  UserPromptSubmit hook now emits a STATUS line per prompt (repo,
  branch, dirty count, last commit, @me issues via 60 s cache at
  `~/.codex/hack-issues-<repo>.json` refreshed by a detached
  `_refresh-issues` subprocess — daemon threads die with the process).
  Law: `registered.deploy` + `registered.hooks`.
- Product skeleton: `NDDev-OpenNetwork/vibestrap` — private mirror of
  `R3flector/vibestrap` (public, no upstream license file), admin
  access, `main` + `dev` branches. Agent surface projected
  (`9f8eae7` on dev=main): `.codex/config.toml` + hooks + AGENTS
  hackathon section + `.agent/briefs/` gitignored. Local clone at
  `~/Developer/NDDev-OpenNetwork/vibestrap`. BAITC repo untouched
  until hackathon day.
- codex_app schema verified against pinned `be2951ea` source
  (`tui/src/dynamic_tools.rs`): 9 tools — list_threads,
  list_archived_threads, read_thread, wait_threads (≤8 targets, ≤120 s,
  0=snapshot), send_message_to_thread, create_thread, fork_thread,
  set_thread_title, set_thread_archived. NO handoff_thread /
  set_thread_pinned. create_thread = {prompt≤1000B, title?, model?}
  only — child inherits cwd (worktree isolation goes in the prompt);
  full briefs live in `.agent/briefs/*.md`. hook hack_mode.py is now
  repo-portable: STATE/GH_CACHE named per ROOT.name, SKILL falls back
  to `~/.codex/plugins/cache/*/hack-agent-workflow/*/` when the repo
  has no plugins/ tree.
- ADR 0015 surface wave: `developer_instructions` (additive developer
  block, compaction-proof — NOT `model_instructions_file` which
  replaces base instructions) + custom `compact_prompt` (preserves
  issues/branch/worktree/lane/`hack:` markers) +
  `check_for_update_on_startup=false` in project config. Hook surface
  now 6 events: +PreToolUse lane guard (exec_command|write_stdin|Bash|shell matcher) — denies protected-branch
  pushes + `gh pr merge` unless `.agent/orchestrator` marker exists
  (activates only where tracked `.codex/lanes.json` declares protected
  branches — vibestrap has it, hack-setup does not push-guard itself);
  +PostToolUse ship-verify nudge after `git push`; +SessionEnd
  appends `.agent/session-log.ndjson`. additionalContext only lands on
  PreToolUse/PostToolUse/SessionStart/UserPromptSubmit/SubagentStart —
  PostCompact cannot inject, so compact survival lives in
  `compact_prompt` + SessionStart `compact` matcher. `notify` is
  host-owned: module 20 writes a managed `# hack-setup:` block into
  `~/.codex/config.toml` → `install/notify.sh`/`notify.ps1` toast on
  agent-turn-complete (scrubber now also strips `# hack-setup` inline
  lines). No custom slash commands in 0.155.1 — `/worktree` `/fork`
  `/app` are the manual paths.
- `Interrupt` is the 6th hook event — same ndjson log as SessionEnd.
  SessionEnd/Interrupt timeout caps at 3 s (clamped otherwise).
- ADR 0016: hooks are trust-by-hash — non-managed hooks run only when
  `hooks.state.<key>.trusted_hash` in the USER config layer matches
  sha256 of the canonical normalized identity. `repair_setup.py
  --only hook-trust` ports `hook_hash`/`version_for_toml` to Python and
  writes the managed block (module 20 calls it at install). Verified in
  a real `codex exec` — hooks Completed. Upstream: compact_prompt is
  ignored under remote compaction (#34428) — SessionStart compact
  matcher is the real re-injection; App threads shadow
  developer_instructions (#33238/#11004) — AGENTS.md is the reliable
  channel.
- `just repair` = `scripts/repair_setup.py` (law `registered.repair`):
  auto-fixes plugin-cache drift, managed notify/sol user-config blocks,
  `.agent` dirs, stale hook bytecode, corrupt `~/.codex/hack-*` state;
  reports codex/python3/hook-smoke/env/git/serena; ends with the real
  checkers. Never clobbers a foreign `notify` key (duplicate key would
  break the user TOML). module.ps1 emits the notify path as a TOML
  literal string (backslashes broke basic-string escapes).
- Commit messages carry no attribution trailers — sole author is the
  repo owner (Team rules in AGENTS.md). History was rewritten clean
  (filter-repo, all SHAs changed; teammates must re-sync clones).

## Next

- Servers: two doctl droplets day-before; only SSH keys needed from
  the user; `install/deploy/provision-server.sh <host> <branch>` each
  (dev→dev, prod→main). vibestrap compose already healthchecks
  postgres/backend/frontend — set HACK_DEPLOY_HEALTH to
  `http://localhost:8000/health/ready` or `:3000`.
- Hackathon day: import the adapted vibestrap into the BAITC repo
  (owner word only).
- Product trees (`web/`, `api/`, …) and nested `AGENTS.md` copies only
  when that code is authored. Copy from `nested/` in the same change.

Not requested: BAITC remote, Serena/hooks install.

## Open threads
### State 2026-09-21 — external audit pack closed (issues #1–#19 vs a77e2fb)

All 19 implementation findings verified against source and fixed;
`just check`/`gate`/`test` (17 tests) green; `just live` proves the real
Serena MCP chain. Landed as `4b3b243` (impl) + `a923dd9` (tests) +
`6c692c0` (workflow docs) + `002d843` (serena sync) + `122ebfd`
(resolver/package-recovery/plugin-summary). Mid-wave PR #22 added
`product/vibestrap` submodule + `.gds/` — audit commits were rebased on
it; dev carries a merge commit for the pre-rebase SHAs. main==dev at
`a52bd96`. Issue disposition: 14 closed `live-verified` (#1,2,5,6,8,10,
12,13,14,15,16,17,18,19); 5 open `integrated` awaiting a real host —
#3/#4 need a live worker spawn, #7 a real droplet re-run, #9/#11 a real
Windows pass; #20 tracker stays open. Lifecycle labels exist on the repo.

Landed this pass (audit wave):
- repair_setup.py: `pinned_version()` reads `codex_cli` key (no
  fallback); `fix_config_cleanup` is the single writer for legacy
  user-config cleanup — preserves owned headers + ALL `[hooks.state.*]`
  (local and foreign checkouts) + `[[array-of-tables]]`, converges on
  re-run; plugin cache prunes non-selected version dirs.
- module 20/40: `status` is observational only (install repairs then
  checks); module.ps1 cleanup scoped per-checkout like the POSIX twin.
- hack_mode.py lane guard: shlex tokenization, `git -C <path>` resolves
  protected authority from the TARGET repo's lanes.json, quoted paths
  handled; tested by tests/test_lane_guard.py. Session log rotated at
  512 KiB. Hook smoke runs with forced `mode=full` env so persisted
  `off` state can't fail it.
- Serena: `ls_specific_settings.python_ty.ty_version` pins ty 0.0.82;
  `powershell` dropped from language_servers (missing pwsh aborted the
  whole LS manager on POSIX — find_symbol died). NEW
  `scripts/verify_serena.py` = `[live]` proof: stdio MCP handshake →
  activate → tools/list (23) → find_symbol via python_ty → memory
  write/read/delete (arg is `memory_name`; tool errors are isError
  results). Wired as `just live`.
- Runtimes: `just` 1.58.0 installed by module 30 from per-platform
  sha256-pinned GitHub assets (all 5 platforms) — moved to required
  probes. `./setup` exercised end-to-end on darwin-arm64.
- deploy-watch.sh: refuses dirty/local-ahead/diverged server checkouts,
  ff-only from ancestor, `.deployed-sha` = actual HEAD after a
  SUCCESSFUL deploy+healthcheck. provision-server.sh: non-destructive
  (no reset --hard, env written only if absent via separate SSH
  temp+mv), prereq checks incl. compose-plugin/curl, remote values
  quoted, `user@host` accepted. Timer now ALWAYS runs: deploy-watch.sh
  self-gates on `$dir/.env` until the first deploy — no manual
  `systemctl start` step.
- notify.sh: JSON-safe parse, 120-char bound, `'`→`''` PS escaping,
  injection-neutral (verified with hostile payload).
- Workflow skills: brief stays in ORCHESTRATOR checkout (worktree lacks
  it) with absolute paths; file tools bind to thread cwd; retirement
  needs inventory before `worktree remove`; sync agent
  `sync/<user>/<round>` owns memory updates; issue lifecycle
  implemented→lane-ready→integrated→live-verified→closed; Danil
  default integrator (Ivan/Artem opt-in); issue threshold = anything
  implemented or any non-trivia discovery (contracts/other lanes/data/
  deploy are never trivia); cannot-fake = auth, primary journey,
  secrets/personal data, deployment; ru/kk/en all core.
- CI: pinned pytest from the pin, `sh -n` loops every shell file,
  reverify filters draft/prerelease releases.
- Proof labels: checkers print `[artifact]`/`[installed]`; live proofs
  print `[live]`.

Landed this pass (deep re-audit + CI-green wave):
- CI was RED on every push — two real failures found and fixed:
  unit tests needed inline `git -c user.email/user.name` (clean
  runners carry no gitconfig), and `setup-e2e-windows` proved the
  official install.ps1 exits 0 with NO binary. module.ps1 is now
  package-first like module.sh (sha256-verified archive, version
  post-condition); install.ps1 is only the no-package fallback.
- hack_mode.py: transparent-prefix scan — sudo/doas plus
  wrapper flag+arg combos (`sudo -u root`, `nice -n 5`) denied;
  `echo git push` / commit-message mentions stay allowed.
- module.sh/ps1 sol-profile + standalone dirs honor CODEX_HOME
  (same resolver as checkers/repair); mise.toml gains just 1.58.0
  and check_stack_pin enforces it; Install-Uv prefers pwsh.
- Issues: #9 + #11 closed `live-verified` (CI windows job is the
  real Windows proof — Install-Just, package path, .cmd shims,
  both checkers all ran green on windows-latest).
- CI now green on main AND dev (all 4 jobs incl. windows).
- Remaining open: #3/#4 (live orchestrator→worker run on the
  product repo), #7 (real droplet re-provision), #20 tracker.

Landed this pass (per-member installs + OS targeting, #23):
- `team` block in stack-pin: members danil/ivan/artem -> github logins
  (rldyourmnd/r3flector/letya999), shared `git_defaults` (ff-only,
  prune+pruneTags, rerere, autoStash, zdiff3, lf, no autocrlf) and
  `windows_git_defaults` (core.longpaths).
- modules/15-member (sh+ps1): `gh api user` login must equal the
  member's pinned login; git identity = profile name + email or
  `id+login@users.noreply.github.com` (no personal mail in repo);
  `gh auth setup-git`, `ssh -T` probe, `.agent/member` marker.
  No `--member` -> git defaults still applied, identity skipped with
  WARN (install) / note (status) — never fatal without a selection.
- bootstrap.sh/ps1: `--member <name>` + `--danil/--ivan/--artem`
  shorthands; `--os <macos|ubuntu|windows>` — real installs must match
  host family (POSIX rejects windows target -> `.\setup.ps1` hint and
  vice versa); `--dry-run` previews another OS. HACK_MEMBER /
  HACK_TARGET_OS env equivalents.
- hack_mode.py STATUS line shows `member=<name>` from the marker.
- Checker: catalog expects 5 modules incl. member; team block, git
  defaults and flag surface (`--member`, `--os`, shorthands in both
  bootstraps) enforced.
- PS5.1 gotcha (CI run 35645725406): BOM-less ps1 decodes as ANSI —
  em-dashes become smart quotes that toggle string state. module.ps1
  is pure ASCII in executable lines; `gh api` multi-line JSON joined
  before ConvertFrom-Json.
- 27 tests pass incl. 7 member/flag cases; `--member danil` ran live
  on this host (identity from gh profile, ssh ok, marker written).
- Remaining: Ivan/Artem run `./setup --member ivan|artem` on their
  hosts (module dies on a wrong gh login — intended guard).

Audit wave on top (all pushed, CI green):
- `check_ps1_ascii` in check_codex_setup: non-ASCII allowed only in
  comments of *.ps1 — static guard for the PS5.1 ANSI-decode bug class.
- noreply fallback without `id`: `login@users.noreply.github.com`
  (old GitHub format) instead of `None+login@`/`+login@`.
- `--member=`/`--os=` empty values die in bootstrap.sh (ps1 parity).
- bootstrap.ps1 accepts single-dash PowerShell forms (-Member, -Status,
  -Dry-Run, -Os; case-insensitive) alongside --flags; setup.ps1 header
  + usage updated.
- justfile `setup *args` forwards flags (`just setup --member ivan`);
  checker accepts parameterized recipe.
- README quickstart is member-first; AGENTS.md documents both flag
  styles.

Landed previous pass (hardening sweep, no live-host items):
- hack_mode.py: `_split_tokens` — posix=False on Windows so
  `C:\repo` keeps backslashes, outer quotes stripped manually; `git -C`
  relative dirs resolve against payload cwd (was hook process cwd —
  silent bypass); STATE/GH_CACHE/plugin cache honor `CODEX_HOME`.
- check_codex_setup.py: `check_serena_project` — ty_version must equal
  quality.ty pin, python_ty required, `powershell` LS banned (missing
  pwsh aborts whole LS manager), ls_workspace_folders must carry `.`;
  hook checker now validates `commandWindows` script refs too.
- reverify_stack_pin.py: per-row ERR — a registry failure prints ERR
  and exits 2 (never silent pass, never aborts remaining rows).
  Verified live 2026-09-21: all 28 tracked pins match latest;
  verified_on bumped.
- deploy kit: watcher self-gates on missing .env until first deploy;
  service `EnvironmentFile=-` + static Description (was invalid
  `%E{}`); provision accepts `user@host`, timer always enabled.
- .gitmodules: vibestrap URL → SSH (private repo, team uses keys).
- tests: +2 lane-guard regressions (relative -C, Windows tokenize) —
  19 passed.

Open:
- ~/.codex/config.toml has foreign root `notify` (Codex Computer Use
  app) — repair warns by design; merge manually only if toast wanted.
- vibestrap push policy: dev pushes need owner beacon / orchestrator
  marker (guard is working — it denied test pushes).
- Remaining internet-verify items: remote compaction SessionStart
  behavior, Codex App thread instruction shadowing (#33238 noted in
  pin). Windows items are now covered by CI `setup-e2e-windows`.
- GitHub issues #1–#19 carry per-issue evidence comments; #20 is the
  integration tracker owned by Danil.


