# 14. Orchestrator/worker via Codex App threads, lanes feat→user→dev→main, pull-watcher deploys

- Status: accepted
- Date: 2026-09-21
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The hackathon operating model: a user talks to one main Codex App chat
(the orchestrator) which registers issues, spawns implementation
sessions, merges lanes, and ships. Three people run this in parallel.
We needed: a session-spawn mechanism, a branch topology that survives
parallel workers, and a deploy path that works without GitHub admin
rights on the product org.

## Decision

**Spawn:** the Codex App injects a dynamic task namespace into sessions
running inside the app (`codex_app.*`; the same tools are `codex_tui.*`
in TUI). Verified against pinned `be2951ea` source
(`tui/src/dynamic_tools.rs`): `list_threads`, `list_archived_threads`,
`read_thread`, `wait_threads` (≤8 targets, ≤120 s), `send_message_to_thread`,
`create_thread`, `fork_thread`, `set_thread_title`, `set_thread_archived`.
No `handoff_thread`/`set_thread_pinned` in this pin. Two schema
constraints drive the design: `create_thread` takes only
`{prompt, title?, model?}` — the child **inherits the caller's cwd** —
and `prompt` is capped at **1,000 bytes**, so the full brief is written
to `.agent/briefs/<name>.md` and the prompt carries a pointer plus a
worktree instruction. These are top-level user-visible threads, not
subagents, so `agents.enabled = false` and `features.multi_agent =
false` stay law. `codex queue --thread <id>` is the CLI fallback for
messaging a thread.

**Isolation:** every worker thread cuts its own `git worktree` from
`dev` as its first action (the brief mandates it). Two agents never
share a working tree.

**Lanes:** `feat/<issue>-<slug>` → `<user>` (personal branch) → `dev` →
`main`. Workers merge only into their own `<user>` lane. Amended
2026-09-22: each member merges `<user>` → `dev` themselves (pull `dev`,
make the merge green, `--no-ff`, push, verify on their own dev server —
one dev server per member); there is no orchestrator merge gate on
`dev`. `dev` → `main` is the integrator's (Danil's) call — the single
prod server autodeploys `main`.

**Deploy:** server-side pull watcher (`install/deploy/`), a 30-second
systemd timer running `deploy-watch.sh` — fetch, ff-only pull, deploy
command, health curl. No GitHub Actions secrets or self-hosted runners
required; both are unavailable on the hackathon org (push/triage only,
admin 404 on actions APIs).

**Prompt enrichment:** the UserPromptSubmit hook injects a one-line
`STATUS` (repo, branch, dirty count, last commit, assigned issues via a
60-second gh cache refreshed by a detached process) so the orchestrator
always sees live state without asking.

## Consequences

- The orchestrator chat must run in Codex App (or an app-server
  client); plain `codex` CLI sessions lack `codex_app.*` tools.
- Worker briefs are generated per spawn — template lives in
  `$hack-agent-workflow:delegate-worker`.
- The product repo (vibestrap base, adapted) must carry the same agent
  surface — AGENTS + `.codex/` are projected there when it is created.
- Branch tips of `dev`/`main` are always deployable by definition —
  the member-merge-green protocol plus the `main`-only lane guard are
  what protect prod.
- Known upstream caveats honoured: whole-message-only mode commands
  (#161), no Subagent* hooks (#502), threaded+timed stdin read (#443),
  scope preservation over line-count laziness (#602).
