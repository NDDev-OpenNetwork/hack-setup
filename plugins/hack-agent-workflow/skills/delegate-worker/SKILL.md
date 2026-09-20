---
name: delegate-worker
description: Spawn and steer a worker Codex App thread from the main orchestrator chat. Use when the user asks to delegate issues to an agent, start an implementation session, spawn a worker, or hand a feature round to a separate thread. Covers brief format, worktree isolation, monitoring and messaging.
---

# Delegate a worker thread

The main chat orchestrates; worker threads implement. This uses Codex
App's `codex_app.*` thread tools — not subagents, so `agents.enabled`
stays false. Requires the main chat to run inside Codex App (or an
app-server-connected client) where `codex_app.*` tools exist.

## Spawn

If `codex_app.*` tools are not in this session's tool list, the main
chat is not running inside Codex App — stop and tell the user to open
the orchestrator chat in the app instead of improvising a subagent.

`codex_app.create_thread` with:

- **workspace**: the product repo checkout. For isolation give the
  worker its own git worktree (`git worktree add ../<repo>-w<N>
  feat/<issue>-<slug>` from `dev`) — two agents never share one working
  tree.
- **title**: `worker/<user>/<round or issue>` so the sidebar shows who
  it belongs to.
- **prompt**: the brief below, generated fresh each time.

## Brief template

```
You are the implementation worker for <user>'s lane.

Issues (github-first, SoT): #12 <title>, #15 <title> — read them with
`gh issue view` before starting.

Rules you live under (already injected by hooks; recap):
- $hack-agent-workflow:hack-mode — laziest working solution, no review
  round, no test suite, `hack:` markers on cut corners.
- $hack-agent-workflow:github-flow — feat/<n>-<slug> off dev → merge
  into `<user>` when the feature verifies live. Never push to dev or
  main yourself.
- $hack-agent-workflow:ship-verify — done means live on the dev server.
- Claim your files on each issue (comment) before editing.

Loop per issue: implement → build+run → verify live → commit → merge to
`<user>` branch → comment "done: <sha>" on the issue → next issue.

When the round is complete reply with: DONE <user> — merged to <user>
@ <sha>; verified live at <url>; hack: markers left: <n>.
Blockers: report immediately, do not improvise scope.
```

## Monitor and steer

- `codex_app.list_threads` / `read_thread` — check status and progress.
- `codex_app.send_message_to_thread` (or `codex queue --thread <id>
  --message "..."`) — follow-up instructions, extra issues, corrections.
- Worker finished → user reviews → archive the thread.

## Merge gate (main chat, before `<user>` → `dev`)

1. No active worker threads on that lane (`list_threads`).
2. `git fetch` + check `dev..<user>` diff touches no files another user
   has claimed on open issues.
3. Merge `--no-ff`, push `dev`, let the dev server pull it.
4. Verify live on the dev deployment (`ship-verify`), then report.

`dev` → `main` happens only on the owner's word after dev verifies.
