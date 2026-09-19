# Technology rule catalogue

Projection of `build/stack-pin.json`, not a second source of truth.
On-demand only. Codex 0.155.1 does not auto-load this directory. Open
only the files that match the change. Session/models/context edits go
to the pin and `.codex/config.toml`, then `just check`.

Versions in these files must match the pin. If they drift, the pin wins; fix
the rule file. Do not import `docs/research/hackalemai-codex-serena/` as
runtime law. That pack is research.

## Load

| Change | Read |
| --- | --- |
| Banned libraries, alphas, second lockfiles | [do-not-use.md](do-not-use.md) |
| JSON, YAML, TOML, Markdown, SQL, env, shell | [formats.md](formats.md) |
| Ruff, ty, pytest, Biome, tsc 7, Vitest, Playwright, just | [quality.md](quality.md) |
| FastAPI, Pydantic, SQLAlchemy, Alembic, Taskiq, aiogram, uv | [python.md](python.md) |
| React, Vite, TypeScript 7, Tailwind, shadcn, TanStack, PWA | [web.md](web.md) |
| OpenAPI, generated TS/Dart clients, SSE, WebSocket | [contracts.md](contracts.md) |
| PostgreSQL, Qdrant, Redis, RustFS, DuckDB, Polars, Arrow | [data.md](data.md) |
| Flutter, Tauri 2, Telegram bot / Mini App | [clients.md](clients.md) |
| LiteLLM, openai 2.x, embeddings, GPU/ML isolates | [ai.md](ai.md) |
| OIDC/OAuth, sessions, Calendar, Stripe test | [auth.md](auth.md) |
| PDF, Office, OCR, media ingest, reports | [documents.md](documents.md) |
| Tiptap, Yjs, KaTeX, FSRS, Pyodide, student executor | [education.md](education.md) |
| Docker, Compose, Caddy, Vector, OpenObserve, OTel | [infra.md](infra.md) |

A Pydantic model used by a generated TS client needs `python.md` and
`contracts.md`. A Vector YAML file needs `formats.md` and `infra.md`.
File extension alone is not enough.

## Not in this catalogue

Nested product `AGENTS.md` files do not exist yet. Add them only when the
matching directory exists. Do not create empty `web/`, `api/`, or `mobile/`
trees in this staging repo.

XML, notebooks, Modal, Drift, reveal.js, OBS, C/C++/Swift/Kotlin bridges,
and extra formatters (Prettier, Taplo, SQLFluff) are not pinned. Do not
write rules that treat them as required.
