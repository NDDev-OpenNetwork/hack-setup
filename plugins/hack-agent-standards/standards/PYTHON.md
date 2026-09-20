# Python

Universe: `build/stack-pin.json` `runtimes.python`, `runtimes.uv`,
`backend.*`, `environments.*`, `deploy.otel`, `deploy.structlog`,
`quality.ruff`, `quality.pytest`, `quality.pytest_asyncio`.

Unless the owner said otherwise this turn.

This file is how to move inside `api/` and the worker that shares
`environments.api_workers`. It is not a gate. Django / Litestar /
asyncpg / Celery are not refusals — offer the pin-equivalent
(FastAPI + psycopg + Taskiq + uv) and follow the owner's last word.

Do not create `api/` only to hold this file. Telegram `Bot` /
`Dispatcher` / polling / webhook live in CLIENTS, not here.

## Default move

1. Map `api/` and the modules the request will touch. Then edit.
2. One FastAPI app. Versioned HTTP via `include_router(...,
   prefix="/v1")` (later `/v2`). `include_router` only. Do not
   `mount()` a second FastAPI app for a feature or a version (own
   OpenAPI, lifespan does not run).
3. Process-wide clients live in `FastAPI(lifespan=...)`: engine,
   redis, `httpx.AsyncClient`. Close them on shutdown. Do not use
   `@app.on_event`. Do not start aiogram here.
4. HTTP in/out is a Pydantic `BaseModel`. Persistence is a mapped
   class. Settings is `BaseSettings`. Do not use one class for all
   three. Do not serialize a mapped instance as the public schema.
5. One `AsyncSession` per request and per Taskiq job. Do not hold
   that transaction across LLM / httpx. Durable work is Taskiq, not
   FastAPI `BackgroundTasks`.
6. Talk SQL as `postgresql+psycopg`. Bound parameters only.
   Student / user code never `exec`s in this process.
7. Proof: Ruff (no `--fix` in check) + the relevant tests. Check
   does not migrate, format, rewrite locks, or dump OpenAPI.

## Pattern

### Graphs

API and Taskiq workers share one uv project / one lock /
`environments.api_workers`. Telegram and GPU/ML are sibling projects
with their own locks; the Bifrost gateway is a container
(`environments.bifrost`), not a uv project. A workspace
that members those graphs together is the official uv anti-pattern
(one resolve, one `.venv`). Shared libraries stay redis-agnostic.
Serena / ty as tools: `uvx`, not app deps.

Telegram talks HTTP to this API on Compose DNS with
`BOT_SERVICE_TOKEN`. That is a bot principal (AUTH), not
the web cookie/`CurrentUser` story. Generated OpenAPI is
the wire shapes only. It does not import `SessionDep`,
mapped models, or the API sessionmaker. `initData` verify
is a route in this process (AUTH owns the algorithm).

### Folders

Layers first (`api/`), DDD boxes inside (Dispatch shape, official
`APIRouter` compose). Version lives in HTTP only:

```text
api/
  main.py                 # FastAPI() + include_router + lifespan
  shared/
    deps.py               # SessionDep, CurrentUser
    auth.py
    openapi.py            # generate_unique_id_function, HTTPError
    otel.py               # one FastAPIInstrumentor.instrument_app
  http/
    v1/
      __init__.py         # compose module routers (no prefix here)
      <name>.py           # thin HTTP + v1 DTOs
                              # AUTH exception: identity.py, router
                              # prefix="/auth", tag auth → /v1/auth/*
                              # (AUTH.md). Do not emit /v1/identity.
    v2/                   # only after a wire break — not day 1
  modules/<name>/
    service.py            # public module API (unversioned)
    domain/
    models.py             # ORM — never the wire schema
  alembic/                # one history
worker/                   # separate process; no SessionDep
```

`main.py` includes `http.v1` at `prefix="/v1"`. Health / ready stay
unversioned (`/health`, `/ready`) and are the only path operations
in `main.py`. Cross-module: `from api.modules.other.service import …`
only. `__init__.py` exports the public API. Worker talks HTTP or the
queue — it does not import the API sessionmaker.

Do not put `router.py` under `modules/` once `http/v*` exists.
Do not invent empty `http/v2/` on day 1. Breaking wire change:
new router + new DTO class names under `http/v2`, include at
`prefix="/v2"`, keep v1. Mark the v1 include `deprecated=True`
when v2 ships. Drop v1 when the owner says. No Sunset / RFC 9745
headers. No Cadwyn. Same router on `/v1` and `/v2` is an alias,
not a break.

### Session and pool

`create_async_engine("postgresql+psycopg://…")` +
`async_sessionmaker(..., expire_on_commit=False)`.
`SessionDep = Annotated[AsyncSession, Depends(get_session)]` with
`async with factory() as session: yield session`.
Commit in the path operation (default yield teardown is after the
response). Taskiq: yield, commit on success, rollback on error.
Engine on worker startup / dispose on shutdown (after fork/spawn).

`AsyncSession` per task — not across `asyncio.gather`.
Pool budget: `(uvicorn_workers + taskiq_workers) * (pool_size +
max_overflow)` under Postgres `max_connections`.
`pool_pre_ping=True`. `await engine.dispose()` on shutdown.

Alembic: `init -t async`. Revisions stay sync (`connection.run_sync`).
Read every autogenerate candidate. Naming convention on constraints.
Committed revisions are immutable; integrator `merge heads`.
`alembic upgrade head` is one migrate job **before** new API/worker
processes. Not lifespan. Not every replica. Local Compose may use a
one-shot migrate service. `alembic check` is the non-writing proof.

### Jobs

`RedisStreamBroker` + result backend with an expiry. URL is
`redis-durable` (DATA), never `redis-cache`. Stock
`backend.taskiq_redis` only `XACK`s — bound the stream
(`maxlen` and/or delete-on-ack). Start the broker in API lifespan
only when `not broker.is_worker_process`.

Jobs: explicit input schema, idempotent side effects, retries only
on transient exceptions. Stream redelivers (XAUTOCLAIM / SmartRetry
keep the same `task_id`). `RedisStreamBroker` ignores `delay` —
real backoff needs a schedule source. Progress via Taskiq
`ProgressTracker`. No in-flight cancel API; use timeout / reject /
an application flag. Failed parse is FAILURE, not SUCCESS empty.

`BackgroundTasks`: tiny, same-process, may vanish (log a line,
close a socket). Everything else is Taskiq — including anything
that must survive a reload or a second replica.

### HTTP contract (emit)

Return-type annotation is the FastAPI default. `response_model`
when the function returns a mapped row or a richer internal model.
Raise `HTTPException`. Register Starlette's `HTTPException`.
Do not stringify `RequestValidationError`. Do not put `exc.body`
on the wire. Do not adopt RFC 9457 here (that is a CONTRACTS
change + dual client regen).

Shared OpenAPI error model `HTTPError` with `detail: str`. Pass
common 401/403/404/409 on `FastAPI(responses=…)`. Every other
status you actually return is in `responses=` with a model that
matches the body. Do not declare `422`, `"4XX"`, or `"default"`
(those suppress the auto-422 schema). Body must match
`{"detail": …}` — the tutorial `{message}` example is wrong for
this stack.

`FastAPI(generate_unique_id_function=…)` at construct. Frozen
rule (CONTRACTS): `vN-tag-name` from `route.path_format` first
segment (`/v1/...` → `v1`), the sole resource tag, and
`route.name`. Unversioned allowlist `/health` `/ready`:
`system-{name}`. One tag per op. Never `tags=["v1"]` on
`include_router` (it prepends and steals `tags[0]`). Never set
`operation_id=` on the decorator. Same `def` name across v1/v2
is fine; same `(vN, tag, name)` is not — fail startup. DTO
**class names** must differ across versions (`UserRead` vs
`UserReadV2`) or OpenAPI `$ref`s smash. Changing the function
after clients exist is a hard break.

SSE: native `fastapi.sse` (`response_class` + yield, not
`return EventSourceResponse`). Annotate `AsyncIterable[Payload]`.
WebSocket: cookie / `Depends` and `WebSocketException(1008)`
**before** `accept()`. No query access token. Event names live
in CONTRACTS.

List ops: paginate on day 1. CONTRACTS owns the envelope
(`items` / `limit` / `offset` / `total`) and query names.

### Observability

Same spine as QUALITY. First route that a client will hit, and
only once ingest exists: `FastAPIInstrumentor.instrument_app`
(exclude receive/send + health/docs) **before** lifespan.
SQLAlchemy / httpx / redis instrumentors when those clients
exist. JSON logs → stdout → Vector with `trace_id`. No
`ConsoleSpanExporter` as done. No second APM. No OTLP-log
structlog instrumentor (second pipeline). No secrets on spans
or log lines.

### Tests

When `api/` exists: install pin `quality.pytest_asyncio` in the
API env (not a host probe, not a stack-pin quality gate until
the tree exists). Mode `auto`, function loop scopes,
`httpx.AsyncClient` + `ASGITransport` on the **same** loop as the
`AsyncSession`. Isolation:
`join_transaction_mode="create_savepoint"`, rollback the outer
txn. Do not share that session with `TestClient`'s anyio portal.
`TestClient` only for sync HTTP with no loop-bound resources.
Do not also run AnyIO in auto. Check does not `alembic upgrade`
and does not dump OpenAPI.

A slice is one request + contract + one DB assertion — not a
fleet.

## Done

- Module landed under `api/modules/<name>` with HTTP in
  `api/http/v1/<name>.py` and a service public API.
- Public paths that are not health/ready live under `/v1`.
- Lifespan owns process clients. Session scope is request/job.
- Public schema cannot emit ORM internals or secrets.
- Owner-named durable work has a Taskiq task, not a vanishing
  background function.
- Migrations are a reviewed revision, not `create_all` / rebuild.
- User code stayed out of this process. The bot process stayed out
  of this graph.
- Ruff + the relevant tests ran. Check did not write.

## Repair

- Red types or lint: fix toward Ruff / the pin interpreter. Do
  not add a second type-checker policy.
- Session-across-tasks or idle-in-transaction across LLM: split
  into two short sessions.
- Accidental second stack (asyncpg, Celery, Django, lifespan
  migrate, mounted version app): offer the pin-equivalent.
  Owner's last word wins.
- Two locks forced into one uv workspace: split the graphs.
- Duplicate `operationId` or smashed DTO `$ref`: fix names in
  Python, then CONTRACTS dump + dual regen.
