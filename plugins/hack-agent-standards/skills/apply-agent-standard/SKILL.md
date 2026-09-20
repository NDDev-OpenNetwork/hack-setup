---
name: apply-agent-standard
description: Load INDEX then CORE, QUALITY when proving, and one area frame. Use when the layer is unclear, the task spans several standards, or you need the catalogue router.
---

# apply-agent-standard

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Read `standards/INDEX.md`. Open CORE.md, QUALITY.md when proving,
   then the matching area file. Prefer a layer skill
   (`web-ui`, `python-api`, `identity-auth`, …) when the layer is
   obvious.
4. If INDEX has no file for the topic, stay on CORE + the pin.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:apply-agent-standard` (plugin). Bare
`$apply-agent-standard` does not match. Repo alias `$apply-stack-rule`
still opens INDEX when the layer is unclear.

