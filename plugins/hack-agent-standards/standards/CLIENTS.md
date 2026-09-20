# Clients

Universe: `build/stack-pin.json` `clients.flutter.*`, `clients.tauri.*`,
`clients.telegram.*`, `auth.native`, `auth.web`, `locales`,
`environments.telegram`.

Unless the owner said otherwise this turn.

This file is how to move inside `mobile/`, `desktop/`, and
`telegram/`. WEB owns the React tree Tauri and the Mini App embed.
AUTH mints credentials. CONTRACTS owns the wire client. PYTHON
does not start the bot. Do not create those trees only to hold
this file.

## Default move

1. Map `mobile/lib`, `desktop/src-tauri`, or `telegram/` and the
   slices the request will touch. Then edit.
2. Flutter: FSD (`pages` / `features` / `entities`). Thin
   `GoRouter`. Talk through the generated dart-dio package
   (path dep, outside `mobile/`). Do not run the generator from
   a Flutter `pubspec`.
3. First user-facing string → ARB `ru` / `kk` / `en` (Flutter)
   or web i18n (Tauri / Mini App) in the same change.
4. Native login (Flutter and Tauri): system browser + one-time
   `code` → `/v1/auth/native/exchange` → Bearer. Deep links are
   untrusted.
5. Telegram: one consumer, poll XOR webhook. Mini App is `web/`.
   `initData` verify is AUTH on FastAPI. Bot talks HTTP to
   `/v1` with `BOT_SERVICE_TOKEN` (API settings), never
   `BOT_TOKEN` and never a user session.
6. Proof: `dart analyze` / `tsc` 7 / Ruff on the touched graph.
   Deep link or plugin → the real target.

## Pattern

### Flutter folders

```text
mobile/
  l10n.yaml
  lib/
    app/                 # bootstrap, theme, GoRouter
    pages/<screen>/
    features/<action>/
    entities/<module>/
    shared/api/          # adapter; generated package is outside
    shared/ui/
    l10n/                # app_en.arb + app_ru.arb + app_kk.arb
packages/openapi_dart/   # dart-dio; generator-owned
```

No Flutter desktop / web. Tauri owns desktop. No
`go_router_builder`. Material / Cupertino from
`package:material_ui` (`clients.flutter.go_router` +
`clients.flutter`). Add
`material_ui` and `url_launcher` to the pin when `mobile/`
lands.

### Flutter data

Generated `built_value` models are the wire types. Providers
return them. Freezed is for session / form drafts that are
**not** a DTO clone. No Drift, sqflite, Hive, Isar, Riverpod
`persist`. Tokens only in `flutter_secure_storage`.

`Openapi(basePathOverride=…)` + `setBearerAuth('BearerAuth',
token)`. No second Bearer interceptor. Mint
`Idempotency-Key` at the mutation. `X-Request-Id`
interceptor is allowed. Logout: clear token, wipe storage,
invalidate providers.

### Flutter i18n

`l10n.yaml`: `arb-dir: lib/l10n`, `template-arb-file:
app_en.arb`, `preferred-supported-locales: [ru, kk, en]`.
`AppLocalizations.delegate` + Material delegates from
`material_ui`.

### Flutter auth + deep links

1. `url_launcher` `LaunchMode.externalApplication` →
   `/v1/auth/native/{provider}/login`.
2. Return via App Link / Universal Link / custom scheme with
   a one-time `code`.
3. `app_links` `uriLinkStream` owns **all** inbound URIs.
4. Exchange via generated client (`security: []`). Store the
   opaque Bearer. `setBearerAuth`. Drop the `code`.

Engine deep links **off** (Flutter ≥3.27 defaults them on;
they fight `app_links`):

- Android: `flutter_deeplinking_enabled=false`
- iOS: `FlutterDeepLinkingEnabled=false`

`GoRouter(overridePlatformDefaultLocation: true,
initialLocation: '/')`. Top-level `redirect` is the auth
gate. No WebView. No `flutter_appauth`. No IdP secrets.

### Tauri

```text
desktop/src-tauri/          # Rust, capabilities, tauri.conf.json
web/                        # same Vite/React tree
```

`frontendDist` = `../web/dist`. AUTH treats Tauri as **native**
(Bearer, not cookie). Webview origin is not first-party to
the API.

| | Browser | Tauri |
| --- | --- | --- |
| Credential | HttpOnly cookie + CSRF | opaque Bearer |
| `fetch` | `credentials: 'include'` | `omit` + `Authorization` |
| Login | same-origin | opener → system browser |
| Store | Redis session | OS keyring via **one** Rust command |

Plugins: `opener`, `deep-link`, `single-instance` (`deep-link`
feature, registered first). `opener` allowlist = auth origin
only. No `plugin-store` for tokens. No Stronghold on day 1.
No `tauri-plugin-http` unless CORS blocks; then scope to the
API origin. CSP `connect-src` includes the API and `ipc:`.
No second frontend. No Flutter desktop window.

### Telegram

Sibling uv graph `telegram/` (`environments.telegram`). One
`Bot`, one `Dispatcher`, one replica. Mode XOR.

```text
telegram/
  main.py                    # XOR entry only
  settings.py
  factory.py                 # Bot + Dispatcher + RedisStorage
  routers/
  http.py                    # process-wide httpx → /v1
```

Do not `mount()` this aiohttp app on FastAPI. Do not serve
`web/` from aiohttp. Do not use `TokenBasedRequestHandler`.

Shared construct: `RedisStorage.from_url(durable_url,
key_builder=DefaultKeyBuilder(prefix="fsm",
with_bot_id=True))`. Never `MemoryStorage` outside a test.
Never `redis-cache`.

Poll: `await bot.delete_webhook(...)` then
`start_polling`. `clients.telegram.aiogram` `start_polling`
does **not**
delete the webhook.

Webhook: bind `127.0.0.1`, Caddy terminates TLS.
`set_webhook(..., secret_token=)` and
`SimpleRequestHandler(..., secret_token=)` use the **same**
value. `secret_token=None` accepts every POST — forbidden.
`handle_in_background=True`. Do not also poll.

Mini App is `web/`. Official script before other scripts.
Bot opens `WebAppInfo(url=WEB_PUBLIC_ORIGIN)`. Web sends
raw `Telegram.WebApp.initData`. Never `initDataUnsafe`.
Empty `initData` (keyboard button) is not a session — use
Menu Button / direct link. Verify is AUTH on FastAPI. Do
not import `aiogram.utils.web_app` into `api/`.

httpx to `/v1` with the service Bearer. Close on shutdown.
Identity link is AUTH, not a display-name match. Token /
secret_token / initData stay off logs and spans. The bot
is not a user principal.

## Done

- Slice landed in the right tree. Router / `main.py` stayed
  thin.
- Strings went through `ru` / `kk` / `en`.
- Server I/O went through the generated client or httpx to
  `/v1`. No DTO clones. No ORM import in the bot.
- Flutter/Tauri used system browser + one-time code. Bearer
  in secure storage / keyring. Tauri did not use cookies.
- Engine deep links were off. Codes were untrusted.
- Telegram: one mode, one replica. FSM on durable. Mini App
  verify stayed on FastAPI. Bot used the service token.
- No Drift / local SQL.

## Repair

- Dirty generated Dart: regen from the snapshot; do not
  merge-edit.
- Flutter `material.dart` + `clients.flutter.go_router` + `ShellRoute`:
  switch to `material_ui`.
- Deep links fire twice: engine flag is still on.
- Tauri talking cookie/CSRF: treat as native.
- Poll 409 / leftover webhook: delete webhook or stop the
  extra consumer.
- FSM lost: you left `MemoryStorage` or pointed at cache.
- initData / aiogram extra in `api/`: move verify to AUTH.
- Bot using `BOT_TOKEN` or a user cookie against `/v1`:
  switch to `BOT_SERVICE_TOKEN`.
- Flutter desktop window: delete it. Tauri owns desktop.
