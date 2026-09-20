# Auth

Universe: `build/stack-pin.json` `auth.*` (including
`auth.session`, `auth.google_calendar`, `auth.payments_test`,
`auth.telegram_initdata`),
`backend.fastapi`,
`backend.httpx`, `data.redis_server`, `data.postgresql`,
`clients.telegram`, `clients.flutter`, `clients.tauri`.
Wire: CONTRACTS. Session store: DATA `redis-durable`.
Bot process: CLIENTS. This file mints identity.

Unless the owner said otherwise this turn.

No password signup. Internal PG user + linked identities.
Email is not a join key. OpenAPI `securitySchemes`:
`BearerAuth` only. Telegram `initData` is verified here, not
in the bot graph. Do not create `api/` only to hold this
file.

## Default move

1. One identity module (`api/modules/identity` +
   `api/http/v1/identity.py`). Wire stays `/v1/auth/*`,
   tag `auth`, `operationId` `v1-auth-*`. Payments:
   `api/modules/payments` + `api/http/v1/payments.py` +
   `POST /v1/payments/webhook`. Calendar tokens in
   identity. Do not add Auth0 / Clerk / fastapi-users /
   Authlib **server**.
2. Web: Redis session + opaque `sid` + CSRF header. Native:
   system browser → our callback → one-time code →
   `POST /v1/auth/native/exchange` → opaque Bearer. Mini
   App: `POST /v1/auth/telegram` → same web session.
3. Authlib Starlette client is the only IdP talker. Backend
   is the confidential client. Secrets never leave this
   process. Do not install `httpx2` / `Authlib[clients]`.
4. `CurrentUser` is a **human**: Bearer (native) if present, else
   cookie. Invalid Bearer → 401, do not fall through. The bot
   is a separate principal: compare `BOT_SERVICE_TOKEN` (API
   settings) with a constant-time helper, never the user
   `bearer:{sha256}` map. Bot routes are an allowlist. Resolve
   Telegram `user.id` via `identities`, never as `users.id`.
   Authorize humans from `course_memberships`, not a
   client-supplied tenant id.
5. Proof: callback through the real origin; denied/revoked
   path; webhook on raw bytes; no tokens in logs.

## Pattern

### Identity

Tables (DATA: UUID v7): `users` (email nullable, no unique,
no password) + `identities` unique `(provider, subject)` +
`google_oauth_tokens` for Calendar only.

Login: resolve `(provider, subject)`. Hit + no session → that
user. Miss + no session → insert both. Miss + session → do
not auto-link on the callback; authenticated
`POST /v1/auth/identities` (CSRF) after a fresh provider
proof. Hit + session + different `user_id` → 409. Never
merge two `users` because emails match.

| Provider | Subject | Email verified |
| --- | --- | --- |
| Google | `id_token.sub` | `email_verified` |
| GitHub | `/user` `id` | primary `/user/emails` `verified` |
| Yandex | `/info` `id` | **false** (no claim) |
| Telegram | `user.id` | n/a (signature is the proof) |

First **verified** email may fill `users.email`. Later
verified emails stay on `identities`.

### Authlib

`OAuth` + Redis cache for `nonce` / `code_verifier`.
Session holds only the state marker (CVE-2026-41425).
`client_kwargs={"code_challenge_method": "S256"}` on every
provider. Pass `Request` into `authorize_*`.

Google: metadata URL + `openid email profile`. GitHub:
`read:user user:email`, then `/user` + `/user/emails`.
Yandex: `login:info login:email`, `Authorization: OAuth`
(not Bearer). Redirect URIs are `PUBLIC_ORIGIN` + path,
registered exactly. Do not put IdP tokens in the session.

Do not use Starlette `SessionMiddleware` (payload-in-cookie).
`auth.session` (`starsessions`) `RedisStore` on durable +
`SessionAutoloadMiddleware` (Authlib needs
`request.session`). Prefix → `session:{id}`. HttpOnly.
`SameSite=Lax`. Host-only. `Path=/`. `__Host-sid` when
HTTPS (`Secure`, no Domain). Local HTTP may omit `__Host-`
but still HttpOnly + Lax. Rolling 7d, absolute 30d; Redis
TTL equals the absolute. After login: `regenerate_session_id`.
Payload: `user_id`, `csrf_token`. Mini App is same-origin
behind Caddy — Lax is enough. Split API host: mint a short
opaque Bearer after Ed25519; **do not** set `SameSite=None`.
If CORS is ever needed: exact `WEB_PUBLIC_ORIGIN`,
`allow_credentials=True`, never `*`. Membership allow-list
is loaded per request from Postgres, not stuffed into Redis.
Logout deletes the session row, clears the cookie, and
deletes the Bearer mapping. Bearer TTL 24h. Native one-time
code TTL 60s. Session `SET` failure → 503, never a
memory/cookie fallback.

### CSRF

`GET /v1/auth/csrf` → `{csrf_token}`.
`Cache-Control: no-store`. Clients send `X-CSRF-Token` on
cookie-auth unsafe methods. Not a security scheme. Exempt:
OAuth callbacks, native exchange, telegram exchange,
Stripe webhook, health/ready. Bearer: no CSRF. Rotate on
login. Rate-limit mint routes (csrf, login, native,
telegram, livekit token, collab authenticate). Missing
quota → 429.

### Native (RFC 8252)

App is a public client of **our** API. We stay the
confidential client of the IdPs. Two PKCE layers.

1. System browser to `/v1/auth/native/{provider}/login`.
2. We run Authlib to the IdP.
3. One-time code in Redis GETDEL, TTL 60s, bound to
   challenge + redirect_uri. 302 to the allowlisted native
   URI.
4. `POST /v1/auth/native/exchange` → `{access_token}`
   opaque. `security: []`.
5. Flutter secure storage / Tauri keyring + `setBearerAuth`.

Redirect allowlist: exact URI match (scheme/host/port/path).
Loopback is `http://127.0.0.1:<port>` with a fixed port
allowlist. Reject prefix matches. Bearer: `bearer:{sha256}` →
`user_id`, TTL. Not JWT. Logout deletes it.

### Telegram initData

Ed25519 third-party verify on FastAPI. `BOT_TOKEN` stays in
the telegram env. API holds `TELEGRAM_BOT_ID` + prod/test
flag. Pubkeys are `auth.telegram_initdata` (Telegram’s
published hex). Prod flag selects the prod key only. No
runtime fetch. Missing or invalid `signature` → 401. HMAC
is forbidden in this process (not a fallback).

`auth_date` window 3600s (300s if money). Reject future
skew. Then `SET initdata:{hash} NX EX` and mint the web
session. Later calls use the session, not raw initData.
Subject = `user.id`. Require `user`. Never
`initDataUnsafe`. Never `?user_id=`. Login Widget SHA256
and Telegram OIDC are different products — do not reuse
those secrets.

Copy the algorithm into `api/shared/auth.py`. Do not import
aiogram. Do not log raw initData.

### Calendar

Login scopes stay `openid email profile`. Calendar is a
**second** consent: `calendar.events`, `access_type=offline`.
Tokens in `google_oauth_tokens`. Sync Google client via
`anyio.to_thread` or Taskiq. Persist our event id ↔ Google
id. Login success ≠ calendar grant. Packages are
`auth.google_calendar` (`google-api-python-client` +
`google-auth`). Do not re-pin them.

### Stripe test

`StripeClient(sk_test_…)`. Hosted Checkout. Entitlement
only from a verified webhook on **raw**
`await request.body()`. Unique `event.id`.
`checkout.session.completed` + `payment_status == "paid"`
→ write entitlement in the same txn as the event row.
`Idempotency-Key` required on checkout (CONTRACTS). Local:
`stripe listen`. Card `4242`. No `sk_live_`. No fake paid.
Package is `auth.payments_test` (`stripe`). Do not re-pin
it. Webhook path is `POST /v1/payments/webhook`.

### Routes

`security: []`: csrf, `*/login`, `*/callback`, native/*,
telegram, payments/webhook. Collab authenticate is **not**
on public Caddy `/v1` — Hocuspocus calls it on Compose DNS
with a distinct m2m secret (constant-time compare). Protected:
me, logout, identities, calendar consent, LiveKit token.
Bot allowlist is a separate Depends, not `CurrentUser`.
`operationId` = `v1-auth-*` / `v1-payments-*`.

`CurrentUser`: `HTTPBearer(auto_error=False,
scheme_name="BearerAuth", bearerFormat="opaque")`. Do not
declare `Cookie()` / `APIKeyCookie`.

### Membership and rooms

Tenant is a **course**. Tables (DATA UUID v7): `courses` +
`course_memberships` unique `(user_id, course_id)` +
`role` (`teacher` / `student` / `staff`). A collab "room"
is a Y.Doc `(document_id, locale)` on a course. A LiveKit
room is a voice session on a course. Neither name is a
capability.

`CurrentUser` loads `course_ids` from memberships each
request. Service filters use that allow-list. Empty
allow-list = no rows. Do not trust `course_id` from the
client, the Y.Doc name, or the LiveKit room string.

Hocuspocus `onAuthenticate` → internal
`POST /v1/auth/collab/authenticate` (Compose DNS, not the
public `/v1` table). Shared m2m secret + the user session
or Bearer it forwards. 401 unsigned, 403 not a member.
Return what the process may open — never "the document
name exists."

LiveKit: AUTH mints a short-lived join token after the
same membership check (`POST /v1/auth/livekit/token`).
Do not put a long-lived key in the bundle. Optional —
INFRA `live` profile / cloud SFU. Do not start it because
the pin names it.

### RLS (later)

Day 1: column + service filter. Do not `ENABLE ROW LEVEL
SECURITY` until membership exists and has tests.

When ENABLE: `FORCE ROW LEVEL SECURITY` on tenant tables;
`app` `NOBYPASSRLS`; `migrate` owns DDL and is the owner;
policies deny-by-default `USING (course_id = ANY
current_setting('app.course_ids')::uuid[])`;
`SET LOCAL app.course_ids` from the membership allow-list
in the session helper — never from the request body.
Service filter stays until ENABLE is proven. Empty GUC =
match-nothing, not a missing policy.

## Done

- Login creates or reuses `(provider, subject)`. No email
  merge.
- Cookie is opaque `sid` on durable Redis. CSRF works.
- Native exchange is single-use, PKCE-bound, 60s.
- initData Ed25519 + `auth_date` on the API; token stayed
  in telegram.
- Calendar scope absent until extra consent.
- Checkout unpaid until signed `checkout.session.completed`.
- Membership allow-list is the only tenant source. Collab
  / LiveKit names are not ACL.
- Dump has no cookie scheme. Tokens absent from logs.
- Logout cleared session + cookie + Bearer.

## Repair

- Starlette cookie session: remove. Redis store.
- `httpx2` in the API env: uninstall.
- Cookie in OpenAPI: delete `Cookie()`, redump.
- Verified-email auto-link: undo. Subject only.
- Live Stripe key: rotate, stay on test.
- Session keys on cache Redis: move to durable.
- Calendar on the login scope: split consent.
- `BOT_TOKEN` in `api_workers`: move to telegram; use
  Ed25519 + a distinct bot principal (`BOT_SERVICE_TOKEN`),
  never the user Bearer map.
- Bot token as `CurrentUser`: split the Depends; allowlist
  routes.
- Document name or LiveKit room as auth: reject; check
  membership.
- ENABLE RLS without FORCE / empty GUC: do not ship.
