---
name: github-flow
description: Run the Saint Tibo GitHub-first task loop. Use when taking, doing, or closing a task — issues are the source of truth, PRs carry status.
---

GitHub issues are the single source of truth for tasks. Tasks are named
and assigned; all work traces to an issue.

Loop:

1. Take a named issue (`gh issue list --assignee @me`, or
   `gh issue create` + self-assign). Comment which files you claim.
2. Cut a work branch for that issue. Commit with Conventional Commits;
   split implementation, tests, docs, and knowledge sync.
3. Done → merge the work branch into **your personal named branch**
   (e.g. `danil`) and close the issue. Your branch is yours — push it
   freely.
4. Owner says "сливаем" / merge → pull `dev`, rebase or merge yours
   onto it, adapt and re-verify under `dev`, then
   `gh pr create` yours → `dev` with Summary + test plan.
5. Owner says "релиз" / release → `dev` → `main` PR, then the deploy
   step. Release and deploy are owner calls only.

Rules:

- Status lives in issues and PRs, not in chat.
- Never push `BAITC-Hacks/hack-a58598e0-saint-tibo` until the owner
  says go. The staging repo is public — no secrets, tokens, or private
  hackathon strategy.
- Direct pushes to `main` are not the flow; `dev` integrates, `main`
  ships.
