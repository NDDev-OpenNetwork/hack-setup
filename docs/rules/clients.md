# Clients

## Flutter

Pins: Flutter `3.47.5`, bundled Dart `3.13.4` (stable as of 2026-09-18),
flutter_riverpod `3.4.3`, go_router `18.0.1`, dio `5.11.1`.

- Do not upgrade Dart independently of Flutter.
- Generated API client is dart-dio from the same FastAPI OpenAPI document.
- Also expected, unversioned in the pin: freezed, flutter_localizations,
  intl, ARB, flutter_secure_storage, app_links.
- OAuth: system browser → backend callback → one-time return code.
- Do not add Drift. Do not add C/C++/Swift/Kotlin bridge rules unless the
  pin grows that surface.

Serena’s stable Dart adapter (when Serena is installed later) is not this
product SDK. macOS arm64 is in that adapter table; Linux arm64 is not.

## Tauri 2

`@tauri-apps/cli` `2.11.4`, `@tauri-apps/api` `2.11.1`, crates.io `tauri`
`2.11.5`. Reuse the React/Vite UI. Reject Tauri 3 alpha.

## Telegram

aiogram `3.31.0` in the Telegram Python env (redis-py `7.4.1`). Mini App is
the same web app. Verify `initData` on the API.

Do not create `mobile/`, `desktop/`, or `telegram/` in this staging repo.
