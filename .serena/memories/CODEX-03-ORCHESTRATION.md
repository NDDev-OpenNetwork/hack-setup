<!-- Memory Metadata
Last updated: 2026-09-21
Last commit: audit-wave fixes (issues #1-#19 vs a77e2fb)
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
  then the prompt points at it. The BRIEF LIVES IN THE ORCHESTRATOR
  CHECKOUT (`.agent/briefs/<user>-<round>.md`, gitignored) — a fresh
  worktree does NOT contain it, so the prompt carries ABSOLUTE paths to
  brief + worktree. File/patch tools bind to the thread's inherited
  cwd, not a `cd` in exec — workers must use absolute paths or verify
  cwd first. Workers never create `.agent/orchestrator` in a worktree.
- Lanes: feat/<issue>-<slug> → <user> → dev → main. Worker merges only
  to own lane + `done: <sha>` issue comment + refreshes
  `.serena/memories/<DOMAIN>-*.md`. Orchestrator merge gate: no active
  workers, no claim conflicts, then spawn the read-only verify agent
  thread (live dev surface + logs + OpenObserve alerts → LIVE-OK/FAIL).
  Worktree retirement AFTER merge needs an inventory first — list
  uncommitted changes, untracked files, and ignored `.agent/` evidence
  before `worktree remove`; `--force` deletes them silently.
  Owner merge beacons: «слить/лить/залить/закинуть/отправить в дев».
- Integration owner: Danil by default; Ivan/Artem integrate ONLY when
  they explicitly take the role. Issue lifecycle: implemented →
  lane-ready → integrated → live-verified → closed. An issue is not
  closed because code was written; `dev`→`main` is the owner's call.
- Issue threshold (agents do all dev): open an issue for anything that
  will be implemented and for discovered problems not fixed inline;
  dedup by root cause. Skip only trivia inside already-claimed files
  (typo, local rename, one-line config). Anything touching a contract,
  another lane's files, data, or deploy behavior is never trivia.
- Sync agent: after a lane push the worker spawns `sync/<user>/<round>`
  — updates CURRENT-state memories + NEXT-SESSION, deletes stale/noisy
  notes, never touches product code, commits `docs(serena): …`.
- Cannot-fake boundary (user call): auth/permissions, the primary
  presented user journey, secrets/personal-data handling, and the
  deployment itself are never faked. `hack:` markers only on secondary
  surfaces, with ceiling + upgrade path. ru/kk/en are all core.
- Deploy: server-side pull watcher `install/deploy/deploy-watch.sh`
  (systemd 30 s timer). Fetches the configured branch, REFUSES dirty /
  local-ahead / diverged checkouts (ff-only when local is an ancestor),
  deploys via configured command, bounded health poll, then writes
  `.deployed-sha` = the actual checked-out HEAD after success — never
  the merely-desired remote SHA. dev←dev, prod←main.
  `provision-server.sh` is repeatable + non-destructive: verifies
  git/docker/compose/curl/systemd, clones only when absent, NEVER
  `reset --hard` an existing checkout, refuses dirty/ahead/diverged,
  preserves `/etc/default/hack-deploy` (writes only when absent, via
  temp+chmod+mv over a separate SSH call), installs watcher+timer,
  starts the timer only when the app `.env` exists or `START_TIMER=1`,
  quotes remote values. No GitHub admin needed (BAITC org: push/triage
  only, Actions 404).
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
  SETUP:CHECK + STATUS, not the no-tests ruleset. Session log
  `.agent/session-log.ndjson` is bounded (rotated at 512 KiB).
- Servers: two doctl droplets day-before; `provision-server.sh <host>
  <branch> <repo>`; vibestrap compose healthchecks exist
  (`/health/ready`, frontend fetch). BAITC repo untouched until day.
- ADR 0015: `developer_instructions` (compaction-proof law block) +
  `compact_prompt` (preserves issue/branch/worktree/lane/hack: state) +
  `check_for_update_on_startup=false`. Lane guard: PreToolUse matcher
  `Bash|exec_command|write_stdin|shell`; payload keys cmd/chars/command/
  input; shlex-TOKENIZED argv (quoted paths/refspecs parse right)
  resolving `git -C <path>` to the TARGET repo — protected-branch
  authority comes from that repo's tracked `.codex/lanes.json`, not the
  caller's cwd. Covers protected push, +force, :delete, --all/--mirror,
  wildcard, bare/HEAD on protected upstream, `gh pr merge`,
  `gh api .../merge(s)` — unless untracked `.agent/orchestrator` marker.
  Tested by `tests/test_lane_guard.py` (incl. `-C`, quoted, `-u`,
  push-options). Hook commands resolve root via
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
  `install/notify.sh|ps1`. notify.sh parses JSON safely, bounds text to
  120 chars, strips `"\`+newlines, escapes `'`→`''` for PowerShell —
  notification failures are non-fatal, no command injection via
  last-assistant-message.
