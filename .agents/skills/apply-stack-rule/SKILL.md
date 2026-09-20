---
name: apply-stack-rule
description: Load the matching pinned technology or format frame. Use when changing Python, FastAPI, React, Vite, TypeScript, Flutter, JSON, YAML, TOML, Markdown, SQL, OpenAPI, Docker, auth, documents, or any stack-pin technology.
---

# Apply a stack rule

This repo has no Cursor-style glob rules. Codex 0.155.1 injects only the
cwd `AGENTS.md` chain (32 KiB). Frames live in
`plugins/hack-agent-standards/standards/` and are loaded on demand.

1. Confirm the worktree and that this is still a setup-only repo unless
   the owner opened the product remote.
2. If the change is Codex session, models, context, or spawn: edit
   `build/stack-pin.json` and `.codex/config.toml` together, then
   `just check`. Do not fork those numbers into a frame first.
3. Read `plugins/hack-agent-standards/standards/INDEX.md`. Open CORE for
   motion. Open QUALITY when proving. Open one area file. Prefer
   `$hack-agent-standards:<layer-skill>` when the layer is obvious.
4. Open `build/stack-pin.json` for the exact version.
5. Follow the pin and the opened frame. Owner text this turn wins where
   it specifies; the rest stays on the frame.
6. Do not load the rest of the catalogue. Do not copy
   `docs/research/` into the change.

If INDEX has no file for the topic, stay on CORE + the pin.
Do not invent a new stack to fill the gap. This repo skill is the
unqualified INDEX alias. Plugin skills need
`$hack-agent-standards:<name>` (router
`$hack-agent-standards:apply-agent-standard`).
