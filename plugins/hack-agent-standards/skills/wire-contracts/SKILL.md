---
name: wire-contracts
description: Load CONTRACTS.md. Use when changing OpenAPI, operationId, generated TS/Dart clients, hey-api, dart-dio, SSE events, WebSocket envelope, or pagination.
---

# wire-contracts

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Open CORE.md, CONTRACTS.md, PYTHON.md if the dump changes. AUTH
   for securitySchemes / CSRF / collab+livekit ops. WEB/CLIENTS as
   consumers. Pin frontend.api_client and
   clients.flutter.openapi_generator.
4. Dump `app.openapi()` then regen both clients when api/ exists.
   SSE is `fastapi.sse`. No just generate-clients in this setup repo.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:wire-contracts` (plugin). Repo alias
`$apply-stack-rule` still opens INDEX when the layer is unclear.

