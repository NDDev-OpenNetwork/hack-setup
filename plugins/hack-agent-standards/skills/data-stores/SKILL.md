---
name: data-stores
description: Load DATA.md. Use when changing PostgreSQL, Qdrant, Redis durable/cache, RustFS, DuckDB, Polars, Arrow, presign, or tenant course_id.
---

# data-stores

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Open CORE.md, DATA.md, pin data.*. AUTH for membership/RLS.
   INFRA for Compose services. PYTHON for Alembic/Taskiq.
4. Two Redis Compose services, one image. Tenant is `course_id`.
   Object keys: server UUID, prefix `c/{course}/…`, never `{tenant}`.
   Private student artifacts stay out of chunks.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:data-stores` (plugin). Repo alias
`$apply-stack-rule` still opens INDEX when the layer is unclear.

