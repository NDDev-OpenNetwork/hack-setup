---
name: github-flow
description: Run the Saint Tibo GitHub-first lane model. Use when taking, doing, merging, or releasing a task — issues are the source of truth; lanes are feat/<issue> → <user> → dev → main, with the dev server proving dev and the prod server following main.
---

GitHub issues are the single source of truth for tasks. Branches form
lanes: `feat/<issue>-<slug>` → `<user>` → `dev` → `main`.

## Issue capture (agents file, threshold calibrated)

All work is done by agents — issues are cheap coordination, not
bureaucracy. File an issue (`gh issue create` + self-assign) for:

- anything you will implement (no issue, no work),
- every problem you DISCOVER but don't fix inline — a bug in another
  domain, a broken contract, stale doc, data inconsistency. Dedup by
  root cause: `gh issue list` + one search before creating.

Skip the issue only for trivia fixed in the same commit you are already
making: a typo, a local rename, a one-line config fix inside files you
already claimed. If it touches a contract, another lane's files, data,
or deploy behavior — it is never trivia.

## Issue lifecycle (states live in issue comments)

`implemented` (feature branch pushed) → `lane-ready` (merged to
`<user>`, `done: <sha>` commented) → `integrated` (orchestrator merged
`<user>` → `dev`, comment `integrated: <sha>`) → `live-verified`
(verify agent reports `LIVE-OK <sha>`) → `closed`. An issue is closed
only on the live-verified signal — never on "code written".

## Integrator

Danil (`rldyourmnd`) is the default integration owner — the merge gate
below is his. Ivan or Artem may integrate only when they explicitly
take it (issue comment or chat word); the orchestrator confirms who
holds integration before merging. Everyone codes; integration is a
role, not a privilege.

## Worker loop (implementation thread)

1. Take a named issue (`gh issue list --assignee @me`, or
   `gh issue create` + self-assign). Comment which files you claim.
2. Cut `feat/<issue>-<slug>` off `dev` — in your own worktree, never in
   a checkout another thread is using.
3. Commit with Conventional Commits; split implementation, docs, and
   knowledge sync. No test suite — `hack:` markers on deferred corners.
4. Feature verified live (`ship-verify`) → merge into **your personal
   named branch** (`danil`/`ivan`/`artem`) and push it. Comment
   `done: <sha>` on the issue. Next feature.

The repo enforces lanes mechanically: `.codex/lanes.json` declares
`dev`/`main` protected, and the PreToolUse hook denies pushes to them
and `gh pr merge` from any checkout without the untracked
`.agent/orchestrator` marker. The orchestrator creates it once:
`mkdir -p .agent && touch .agent/orchestrator` in the main checkout —
worker worktrees never have it. Workers pushing their own lane are
unaffected.

## Merge gate (orchestrator, before `<user>` → `dev`)

1. No active worker threads on that lane
   (`codex_app.list_threads` / `read_thread`).
2. `git fetch origin`; the `dev..<user>` diff must not touch files
   another lane claimed on open issues.
3. `git merge --no-ff <user>` into `dev`, push. The dev server pulls
   `dev` itself (deploy watcher).
4. Verify live on the dev deployment. Report one line.

## Release (owner call only)

`dev` → `main` only when the owner says deploy. The prod server pulls
`main` itself; then verify prod live and report.

## Merge beacons

Owner words that mean "integrate `<user>` into `dev` now": **«слить»,
«лить», «залить», «закинуть», «отправить», «влить», "merge to dev"**.
Hearing one → run the merge gate above. They do NOT mean `dev` →
`main`; that still waits for an explicit deploy call.

## Rules

- Status lives in issues and PRs, not in chat.
- Never push `BAITC-Hacks/hack-a58598e0-saint-tibo` until the owner
  says go. The staging repo is public — no secrets, tokens, or private
  hackathon strategy.
- Direct pushes to `main` are not the flow; `dev` integrates, `main`
  ships.
