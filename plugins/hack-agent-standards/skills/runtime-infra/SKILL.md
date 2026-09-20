---
name: runtime-infra
description: Load INFRA.md. Use when changing Docker Compose, Caddy, Vector, OpenObserve, OTel, collab/live/gpu profiles, or what to publish.
---

# runtime-infra

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Open CORE.md, INFRA.md, pin deploy.*. FORMATS for YAML/Caddyfile.
   QUALITY for hop-split telemetry. DATA for two Redis / RustFS.
   EDUCATION when touching collab/live.
4. Only Caddy publishes 80/443. `collab` / `live` / `gpu` stay off
   the spine. Browser LiveKit edge is Cloud unless the owner names
   self-host. Two Redis Compose services, one image.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:runtime-infra` (plugin). Repo alias
`$apply-stack-rule` still opens INDEX when the layer is unclear.

