---
name: apply-stack-rule
description: Load the matching pinned technology or format rule. Use when changing Python, FastAPI, React, Vite, TypeScript, Flutter, JSON, YAML, TOML, Markdown, SQL, OpenAPI, Docker, auth, documents, or any stack-pin technology.
---

# Apply a stack rule

This repo has no Cursor-style glob rules. Codex 0.155.1 injects only the
cwd `AGENTS.md` chain (32 KiB). Technology law lives in `docs/rules/` and
is loaded on demand.

1. Confirm the worktree and that this is still a setup-only repo unless
   the owner opened the product remote.
2. If the change is Codex session, models, context, or spawn: edit
   `build/stack-pin.json` and `.codex/config.toml` together, then
   `just check`. Do not fork those numbers into a rule file first.
3. Read `docs/rules/INDEX.md`. Pick the one or two files that match the
   files and behavior you will change.
4. Read those files. Open `build/stack-pin.json` for the exact version.
5. Follow the pin. Do not invent an unpinned library to silence an error.
6. Do not load the rest of the catalogue. Do not copy
   `docs/research/hackalemai-codex-serena/` into the change.

If INDEX has no row for the change, stop and say the topic is unpinned.
Do not create application source here.
