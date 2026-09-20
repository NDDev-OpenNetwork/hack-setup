---
name: identity-auth
description: Load AUTH.md. Use when changing OIDC/OAuth, sessions, CSRF, Telegram initData, native PKCE, membership, RLS later, collab/LiveKit mint, Calendar, or Stripe test.
---

# identity-auth

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Open CORE.md, AUTH.md, pin auth.*. DATA for redis-durable /
   course_id. WEB/CLIENTS for cookie vs Bearer. INFRA for collab
   internal DNS. CONTRACTS for BearerAuth and `v1-auth-*` /
   `v1-payments-*`.
4. Module `api/modules/identity`, HTTP `api/http/v1/identity.py`,
   wire `/v1/auth/*`, tag `auth`. CSRF `GET /v1/auth/csrf`. Payments
   `POST /v1/payments/webhook`. Ed25519 only. `BOT_SERVICE_TOKEN` ≠
   CurrentUser. Collab authenticate is Compose DNS, not public
   Caddy `/v1`.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:identity-auth` (plugin). Repo alias
`$apply-stack-rule` still opens INDEX when the layer is unclear.

