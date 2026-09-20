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
- create_thread = {prompt≤1000B, title?, model?}; child inherits cwd.
  Full brief → `.agent/briefs/<user>-<round>.md` (gitignored); prompt =
  mission + pointer + `git worktree add` instruction.
- Lanes: feat/<issue>-<slug> → <user> → dev → main. Worker merges only
  to own lane + `done: <sha>` issue comment. Orchestrator merge gate:
  no active workers, no claim conflicts, live-verify on dev.
- Deploy: server-side pull watcher `install/deploy/` (systemd 30 s
  timer, ff-only pull, compose build, health curl). dev←dev, prod←main.
  No GitHub admin needed (BAITC org: push/triage only, Actions 404).
- Product skeleton: `NDDev-OpenNetwork/vibestrap` (private mirror of
  R3flector/vibestrap, no upstream license). Agent surface projected:
  `.codex/{config.toml,hooks.json,hooks/hack_mode.py}` + AGENTS
  hackathon section. Local clone `~/Developer/NDDev-OpenNetwork/vibestrap`.
- hack_mode.py is repo-portable: state/cache files per ROOT.name;
  SKILL.md falls back to `~/.codex/plugins/cache/*/hack-agent-workflow/`.
- Servers: two doctl droplets day-before; `provision-server.sh <host>
  <branch> <repo>`; vibestrap compose healthchecks exist
  (`/health/ready`, frontend fetch). BAITC repo untouched until day.
