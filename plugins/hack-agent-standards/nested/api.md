# API

Read the repository root `AGENTS.md`. This directory is FastAPI +
SQLAlchemy + Alembic + Taskiq (`environments.api_workers`).

Open `$hack-agent-standards:python-api`. Always CORE. QUALITY when proving.
Mixed: CONTRACTS (OpenAPI dump), AUTH (`modules/identity`,
`http/v1/identity.py`, wire `/v1/auth/*`, tag `auth`), DATA, AI,
EDUCATION (OR-Tools in Taskiq).

One app. `include_router` prefix `/v1`. Do not `mount()` a version app.
SSE is `fastapi.sse`. `POST /v1/payments/webhook` lives here.
`BOT_SERVICE_TOKEN` ≠ CurrentUser. User code never runs in this process.
Telegram bot is a sibling graph, not mounted here.
