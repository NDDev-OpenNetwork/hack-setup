# Auth and integrations

Pin: Authlib `1.8.0`. Provider SDKs are unversioned in the pin.

## Identity

Internal PostgreSQL user + linked provider identities. Providers: Google
OIDC, GitHub OAuth2, Yandex OAuth2.

Web session: server session + Redis + HttpOnly cookie + CSRF. Do not store
session tokens in localStorage.

## Native / Telegram

- Mobile OAuth: system browser + backend callback + one-time return code.
- Telegram account link and Mini App `initData` verification happen on the API.

## Other

- Google Calendar: google-api-python-client + google-auth, explicit scopes.
- Stripe: test / sandbox only (Stripe Python SDK + Checkout + Stripe CLI).
  No live keys in this public tree.

Do not commit cookies, refresh tokens, or provider client secrets.
