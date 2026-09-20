# Infra

Universe: `build/stack-pin.json` `deploy.*`, `data.*`,
`environments.*`. Pipeline: JSON logs → Vector → OpenObserve;
traces/metrics OTLP → OpenObserve.

Unless the owner said otherwise this turn.

This file is how the runtime is cut. The catalogue is not a
mandate to start every service. Do not create Compose files
only to hold this file.

## Default move

1. One `compose.yaml`. Profiles are the cut. `docker compose
   up` is the spine, not the pin list.
2. Only Caddy publishes. Everything else `expose` + internal
   networks.
3. Secrets from Compose `secrets:` / gitignored `env_file`.
   Never `ENV` in a Dockerfile. Never `latest`.
4. Proof: `docker compose config`, `caddy validate`,
   `vector validate`, then one real `/v1` + `/otel/v1/traces`
   row in OpenObserve — **when Compose exists**. Import ≠
   done. This setup repo has no Compose yet; then proof is
   `just check`.

## Pattern

### Compose cut

No `version:` key. Always-on: Caddy, api, migrate (one-shot),
postgres, `redis-durable`, `redis-cache`, rustfs,
openobserve, vector. Profiles: `search` (qdrant), `jobs`
(worker), `telegram`, `gpu` (`environments.gpu_ml` encode
HTTP on an internal net — not Caddy; health; no host
publish), `ai` (proxy-runtime /
CLIProxyAPI), `dev` (Vite behind Caddy), `obs-ui`
(optional; default is SSH tunnel), `collab` (Hocuspocus;
joins Caddy `edge` + path to api; persist via API, not a
Node DSN), `live` (optional self-hosted SFU on an internal
net; **browser edge is LiveKit Cloud** unless the owner
names self-host + a UDP exception).

Do not compose Flutter, Tauri, Pyodide, or the student
executor “because they’re in the pin.” Do not start
`collab` / `live` on the spine. Executor, if composed later:
own profile, `network=none`, no `docker.sock`, no API
secrets, never published.

`migrate`: `alembic upgrade head`, `restart: "no"`,
`service_completed_successfully` before api. `compose down`
must not wipe Postgres / RustFS / Qdrant / durable Redis
volumes. Cache Redis: tmpfs / no persist is fine.

Official `library/redis` may lag the pin tag — name the lag.

### Networks

`edge` (Caddy 80/443). `data` internal (stores + writers).
`obs` internal (Vector, OO, OTLP, Caddy `/otel`). Caddy
joins `edge` + `obs`. api/worker join all three. rustfs
joins `data` + `edge` (S3 host). `gpu` encode joins `data`
only. `collab` joins `edge` + a path to api. Vector may mount
`docker.sock` ro for `docker_logs` only.

### Health

Role-shaped. postgres `pg_isready`. Both Redis `PING`.
rustfs `:9000/health`. OO `/healthz`. Vector API
`127.0.0.1:8686/health` (not published). api `/health` +
`/ready` (CONTRACTS; exclude from OTel). qdrant: TCP 6333
in Compose (`/readyz` is the meaning; image has no curl).
migrate: exit 0.

### Caddy

Stable line (`caddy:2`). Digest-pin on hackathon day.
`CADDY_ADMIN=off`. Public host: ACME + HTTP→HTTPS. Local:
`tls internal`.

**Do not `handle_path /v1`.** That strips `/v1`. CONTRACTS
path keys include the version.

```text
/health /ready     → api (unversioned)
/v1/*              → api:8000/v1/*   (keep Host; WS/SSE flush)
/collab/*          → hocuspocus WS   (profile collab; keep path;
                     Origin = WEB_PUBLIC_ORIGIN)
POST /otel/v1/traces
                   → uri replace /otel /api/default
                     → openobserve:5080 + inject Basic
/                  → SPA files
$S3_HOST           → rustfs:9000     (path-style; do not log query)
```

Browser SDK: `url: '/otel/v1/traces'` (WEB). Same-origin.
SW must not cache `/otel`. Internal API OTLP **bypasses
Caddy**:
`OTEL_EXPORTER_OTLP_ENDPOINT=http://openobserve:5080/api/default`
+ Basic. SDK appends `/v1/traces`. No `/otel/v1/logs`
(second log pipeline). No Collector.

S3: workers `http://rustfs:9000`; presign `https://$S3_HOST`.
`RUSTFS_CONSOLE_ENABLE=false`. CORS = exact web origin.
KMS on; no insecure defaults. Volume owner `10001`.

### Vector

`docker_logs` (project label, exclude self) → parse JSON →
redact (`authorization`, `cookie`, `token`, `secret`,
`X-Amz-*`, URI query, request/response bodies) →
drop `/health` `/ready` → HTTP `_multi` NDJSON to
`/api/default/logs/_multi`. Basic auth. Do not use `_json`
(array) with Vector’s object wrapper. Cap cardinality: no
user/prompt text as labels. No OTLP source on Vector.

### OTel

API: pin `deploy.otel` (`api_sdk` / `instrumentation`).
`FastAPIInstrumentor.instrument_app` before lifespan
(exclude health/docs + receive/send). Batch OTLP/HTTP. No
`ConsoleSpanExporter` as done. No OTLP-log instrumentor.
No `litellm[proxy-runtime]` in the API image.

Browser packages are a different version line. No emit
until Caddy `/otel/v1/traces` exists.

OO first boot requires root email/password. Org `default`.
Do not publish 5080/5081.

### Secrets / images

Compose `secrets:` files. Multi-stage. Non-root. No
secrets in layers. `.env.example` names only (FORMATS).

### What not to expose

Host publish **only** Caddy 80/443. Never publish postgres,
Redis, Qdrant, rustfs 9000/9001, OO, Vector API, Caddy
admin, api 8000, migrate, worker, bot, gpu. Never
public-route `/docs`, `/redoc`, `/openapi.json`, OO UI,
RustFS console. `/otel` is ingest with injected Basic —
not the UI.

## Done

- `docker compose up` starts the spine only. `collab` /
  `live` stay off until named.
- Two Redis. One migrate job that exits. RustFS unreleased
  on 9000/9001.
- Caddy: `/v1` unstripped, `/otel` rewritten, S3 host
  path-style.
- Vector: parse → redact → `_multi`. No OTLP-log hop.
- API OTLP HTTP to OO on `obs`. Browser silent until
  `/otel` exists.
- No secrets in layers. Volumes survive `down`.

## Repair

- Second APM / Collector / OTLP logs: delete.
- `handle_path /v1`: fix the route, don’t patch clients.
- One Redis + `allkeys-*`: split (DATA).
- Published 5432/6379/6333/9001/5080: unpublish, rotate if
  reachable.
- Public bucket / `CORS=*`: close, rotate keys.
- `create_all` or restarting migrate: back to one-shot.
- OO `:latest`: name the Hub lag; don’t silently roll.
