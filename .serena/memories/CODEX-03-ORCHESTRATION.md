<!-- Memory Metadata
Last updated: 2026-09-21
Last commit: c65cd4e fix(orchestration): verify codex_app schema, portable hook
Scope: plugins/hack-agent-workflow/skills/{delegate-worker,github-flow}, install/deploy/, .codex/hooks/, docs/adr/0014-*, build/stack-pin.json registered.{deploy,hooks}, NDDev-OpenNetwork/vibestrap
Area: CODEX
-->

# CODEX-03-ORCHESTRATION

Orchestrator/worker flow and deployment model (ADR 0014).

- Threads: `codex_app.*` (app) / `codex_tui.*` (TUI) dynamic namespace.
  Verified pin surface `be2951ea`: list_threads, list_archived_threads,
  read_thread, wait_threads (≤8, ≤120 s, 0=snapshot),
  send_message_to_thread, create_thread, fork_thread, set_thread_title,
  set_thread_archived. NO handoff_thread / set_thread_pinned.
- create_thread = {prompt≤1000B, title?, model?}; child inherits cwd —
  so the ORCHESTRATOR creates the worktree first
  (`git worktree add ../<repo>-w<N> -b feat/<issue>-<slug> origin/dev`),
  then the prompt tells the worker to `cd` into it. Brief file:
  `.agent/briefs/<user>-<round>.md` (gitignored).
- Lanes: feat/<issue>-<slug> → <user> → dev → main. Worker merges only
  to own lane + `done: <sha>` issue comment + refreshes
  `.serena/memories/<DOMAIN>-*.md`. Orchestrator merge gate: no active
  workers, no claim conflicts, then spawn the read-only verify agent
  thread (live dev surface + logs + OpenObserve alerts → LIVE-OK/FAIL).
  Worktree retirement after merge: `worktree remove` + `branch -d` +
  `prune` + archive thread — clean git is part of done. Owner merge
  beacons: «слить/лить/залить/закинуть/отправить в дев».
- Deploy: server-side pull watcher `install/deploy/` (systemd 30 s
  timer, ff-only pull, compose build, bounded health curl). State is
  `.deployed-sha` — the SHA whose deploy SUCCEEDED, not checkout HEAD:
  failed builds retry next tick, fresh clones deploy once. Dirty tree
  pauses the tick. dev←dev, prod←main.
  No GitHub admin needed (BAITC org: push/triage only, Actions 404).
- Product skeleton: `NDDev-OpenNetwork/vibestrap` (private mirror of
  R3flector/vibestrap, no upstream license). Agent surface projected:
  `.codex/{config.toml,hooks.json,hooks/hack_mode.py,lanes.json}` +
  `build/stack-pin.json` (thin pin + fork exceptions: RHF over TanStack
  Form, TanStack Start, better-auth/drizzle=auth only) +
  `.serena/project.yml`. Local clone `~/Developer/NDDev-OpenNetwork/vibestrap`.
- hack_mode.py is repo-portable: state/cache files per ROOT.name + path
  hash; SKILL.md falls back to
  `~/.codex/plugins/cache/*/hack-agent-workflow/`. Hack-mode ruleset
  injects ONLY where `.codex/lanes.json` exists — the harness repo gets
  SETUP:CHECK + STATUS, not the no-tests ruleset.
- Servers: two doctl droplets day-before; `provision-server.sh <host>
  <branch> <repo>`; vibestrap compose healthchecks exist
  (`/health/ready`, frontend fetch). BAITC repo untouched until day.
- ADR 0015: `developer_instructions` (compaction-proof law block) +
  `compact_prompt` (preserves issue/branch/worktree/lane/hack: state) +
  `check_for_update_on_startup=false`. Lane guard: PreToolUse matcher
  `Bash|exec_command|write_stdin|shell`; payload keys cmd/chars/command/
  input; refspec-TOKENIZED compare (feat/12-main-fix ≠ main) covering
  protected push, +force, :delete, --all/--mirror, wildcard, bare/HEAD
  on protected upstream, `gh pr merge`, `gh api .../merge(s)` —
  unless untracked `.agent/orchestrator` marker; activates via tracked
  `.codex/lanes.json`. Hook commands resolve root via
  `git rev-parse --show-toplevel` (session cwd may be a subdir);
  commandWindows cmd variants mirror all six handlers.
  PostToolUse → ship-verify nudge; SessionEnd/Interrupt (timeout≤3s) →
  `.agent/session-log.ndjson`. SessionStart sources are only
  startup|resume|clear|compact — a forked/edited thread re-fires
  `startup` and DUPLICATES context (upstream #39951); compact sources
  queue until next user turn (#28736). PostCompact CANNOT inject
  context (only PreToolUse/PostToolUse/SessionStart/UserPromptSubmit/
  SubagentStart can). `notify` host-owned → module 20/repair write a
  root-aware TOML block (foreign root notify → WARN) →
  `install/notify.sh|ps1`.
