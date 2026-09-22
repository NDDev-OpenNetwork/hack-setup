---
name: github-flow
description: Run the Saint Tibo GitHub-first lane model. Use when taking, doing, merging, or releasing a task — issues are the source of truth; lanes are feat/<issue> → <user> → dev → main; each member merges their own lane into dev and proves it on their own dev server, the integrator alone ships dev → main to prod.
---

GitHub issues are the single source of truth for tasks. Branches form
lanes: `feat/<issue>-<slug>` → `<user>` → `dev` → `main`. `dev` is a
shared branch — each member merges their own lane into it; `main` is
protected and only the integrator ships `dev` → `main`.

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
`<user>`, `done: <sha>` commented) → `integrated` (member merged
`<user>` → `dev`, comment `integrated: <sha>`) → `live-verified`
(verify agent reports `LIVE-OK <sha>`) → `closed`. An issue is closed
only on the live-verified signal — never on "code written".

## Integrator

Danil (`rldyourmnd`) is the integrator — he alone moves `dev` → `main`
(prod autodeploys `main`). Merging `<user>` → `dev` is NOT gated on
him: every member lands their own lane on `dev` and verifies it on
their own dev server. Everyone codes; release is a role, not a
privilege.

## Worker loop (implementation session)

1. Take a named issue (`gh issue list --assignee @me`, or
   `gh issue create` + self-assign). Comment which files you claim.
2. Cut `feat/<issue>-<slug>` off `dev` — in your own worktree, never in
   a checkout another session is using.
3. Commit with Conventional Commits; split implementation, docs, and
   knowledge sync. No test suite — `hack:` markers on deferred corners.
4. Feature verified live (`/hack-devin-workflow:ship-verify`) → merge
   into **your personal named branch** (`danil`/`ivan`/`artem`) and
   push it. Comment `done: <sha>` on the issue. Next feature.
5. Lane green → run **Merge to dev** below yourself and verify on your
   own dev server — `dev` is not gated on anyone.

The repo enforces lanes mechanically: `lanes.json` (`.devin/` or
`.codex/` — both are honored) declares `main` protected, and the
PreToolUse hook denies pushes to it and `gh pr merge` from any
checkout without the untracked `.agent/orchestrator` marker. The
integrator creates it once: `mkdir -p .agent && touch
.agent/orchestrator` in his checkout — worker worktrees never have it.
`dev` is shared: every member pushes their own merges into it, no
marker needed.

## Merge to dev (the member does it, not the orchestrator)

1. `git fetch origin`; check no teammate's open issue claims files your
   `dev..<user>` diff touches — if it does, sync first.
2. `git checkout dev && git pull` — always merge onto the latest `dev`.
3. `git merge --no-ff <user>` into `dev`, resolve conflicts, make the
   merge green, push. Your dev server pulls `dev` itself (deploy
   watcher).
4. Verify live on YOUR dev server. Report one line + comment
   `integrated: <sha>` on the issue.

## Release (integrator only)

`dev` → `main` is the integrator's (Danil's) call — the prod server
pulls `main` itself; then verify prod live and report.

## Rules

- Status lives in issues and PRs, not in chat.
- Commit atomically and early — each logical slice lands as its own
  Conventional Commit so GitHub history tracks progress.
- Merges keep full history: `git merge --no-ff` only — never squash or
  rebase merge methods, never rewrite shared history. The hook denies
  `gh pr merge --squash/--rebase/--method`, `gh api` squash/rebase
  `merge_method`, and `git merge --squash`; repo merge settings disable
  the buttons too.
- Never push `BAITC-Hacks/hack-a58598e0-saint-tibo` until the owner
  says go. The staging repo is public — no secrets, tokens, or private
  hackathon strategy.
- Direct pushes to `main` are not the flow; `dev` integrates, `main`
  ships.
