---
name: text-formats
description: Load FORMATS.md. Use when changing JSON, YAML, TOML, Markdown, SQL, env, Caddyfile, Vector YAML, justfile, or pin/OpenAPI dump formatting.
---

# text-formats

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Open CORE.md, FORMATS.md. INFRA if the file is Compose/Caddy/Vector. CONTRACTS if it is OpenAPI.
4. Check does not rewrite. No second formatter fleet (Prettier/Taplo/SQLFluff) as required.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:text-formats` (plugin). Repo alias
`$apply-stack-rule` still opens INDEX when the layer is unclear.

