# Python backend and worker rules

## Environment and typing

Use uv-managed, locked environments. The backend and a worker may share an environment when dependencies genuinely agree; ML, Telegram or proxy processes may need separate environments. Do not merge Serena's pinned dependencies into the application environment. Use the project interpreter and import roots in language tooling, not an arbitrary global Python.

Use Python's current supported syntax for the selected runtime, typed public boundaries and explicit return shapes. Avoid unbounded `Any`, broad ignores and blanket missing-import suppression. Configure ty for the real source roots and environment; Ruff owns Python formatting and lint. A fallback navigation provider must not silently replace the agreed compiler/type-check policy.

## FastAPI and Pydantic

Define request/response models deliberately. Validate untrusted boundaries; avoid repeated serialization/revalidation in a hot internal path without need. Do not expose ORM internals or secrets through response serialization. Use explicit response status/error contracts and stable operation IDs where required by client generation.

Create reusable HTTP/DB/provider clients with clear application lifecycle ownership and close them. Put domain behavior outside HTTP handlers where it is shared by workers or clients. Keep dependency injection explicit and small.

## Async and resources

Async is not a license to call blocking libraries in the event loop. Offload bounded blocking I/O appropriately; CPU/OCR/video/ML work belongs in a worker or designated execution process. Set timeouts on network calls and preserve cancellation. Bound concurrency instead of gathering an arbitrary number of document/model requests.

Do not share a mutable SQLAlchemy AsyncSession among concurrent tasks. Give each request/job its transaction scope and deterministic cleanup. Do not hold a database transaction across a long LLM or external API call unless the consistency design explicitly requires and budgets it. Size pools against all API/worker processes, not a single instance.

## Migrations and SQL

Alembic owns schema changes. Read generated migrations; verify constraints, indexes, existing-data handling and ordering. Keep committed integration migrations immutable. Coordinate multiple heads through the integrator. Rebuilding a database is not an acceptable hidden fix for migration mistakes.

Use bound query parameters. Keep PostgreSQL and DuckDB dialect assumptions separate. Avoid N+1 access, accidental relationship loading and unbounded result lists; use appropriate pagination and batch operations.

## Jobs and integrations

Taskiq jobs have stable identity, explicit input schema, idempotent side effects and visible status. Retry transient failures within a bounded budget; do not retry a non-idempotent external write blindly. Progress/cancellation should reflect actual work. Failed parsing or model output is not a completed job with an empty result.

For boto3 or other blocking clients, use a bounded worker/thread boundary rather than calling them directly in an async request handler. aiogram lifecycle and polling/webhook choice are explicit; do not accidentally run competing consumers for the same update stream.

## Verification

Run affected Ruff checks and the relevant ty project scope. Use narrow pytest/HTTPX or integration tests for changed business invariants, transaction boundaries and failure handling. Avoid a large mandatory test pipeline, but never weaken typing or error handling merely to obtain a passing label.
