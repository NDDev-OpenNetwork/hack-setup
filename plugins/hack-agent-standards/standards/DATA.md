# Data

Universe: `build/stack-pin.json` `data.*`, `backend.sqlalchemy`,
`backend.alembic`, `backend.psycopg`, `backend.taskiq_redis`,
`environments.api_workers`, `environments.telegram`, `auth.web`.

Unless the owner said otherwise this turn.

This file is how stores are cut. PostgreSQL is SoT. Qdrant, Redis,
RustFS, and DuckDB are derived or ephemeral. It is not a gate.
Do not create `api/` or Compose services only to hold this file.

## Default move

1. Name which store owns the write. Then edit that store. Do not
   invent a second SoT to ship a slice.
2. Postgres entities go through SQLAlchemy + one Alembic history
   (PYTHON). Qdrant is upsert/delete from that truth. Objects:
   metadata in Postgres, bytes in RustFS. Cache/session/stream:
   the matching Redis instance.
3. A successful write to one store is not atomic across all of
   them. Persist an ingest/job status and a repair path.
4. Filters and signed URLs are capabilities. Do not trust a
   client-supplied tenant id or an object key as authorization.
5. Proof: the changed invariant (constraint, filter, HeadObject,
   eviction topology) — not “the client connected.”

## Pattern

### PostgreSQL

One database. `public` only. One `DeclarativeBase` / one
`MetaData` (naming convention on). DDD boxes are Python packages,
not schemas and not extra databases. Cross-module FK is allowed.
Prefix a table name only on collision.

Roles: `migrate` owns DDL + `alembic_version`. `app` is
USAGE + DML. `REVOKE CREATE ON SCHEMA public FROM PUBLIC`.
`ALTER DEFAULT PRIVILEGES FOR ROLE migrate … GRANT … TO app`.
API / Taskiq use the app DSN. The migrate job uses the migrate
DSN. Leave `search_path` at `"$user", public`. Do not
`SET search_path`. Do not set `schema=` on tables.

Entity PK is UUID v7: `default=uuid.uuid7` +
`server_default=text("uuidv7()")`. Not `Identity()`. Not v4.
Not `func.uuidv7(monotonic=True)` (SQLAlchemy 2.1). Closed
vocabularies may use a `TEXT` code PK.

Tenant column is `course_id` on every tenant table. Qdrant
payload uses the same key. AUTH owns membership and later
RLS. Day 1: filter in the service from the membership
allow-list. Do not `ENABLE` policies until AUTH says so.

Migrate stays PYTHON: one job `alembic upgrade head` before
new API/worker processes. `alembic check` is the non-writing
proof. Do not `create_all`.

### Redis

Two Compose services, both `data.redis_server`. Not one. Not
three. Do not fake the split with `SELECT` (shared
`maxmemory` / eviction / AOF).

- `redis-durable`: sessions, aiogram FSM, Taskiq stream +
  results + schedules, Hocuspocus Redis extension (`yjs:`).
  `noeviction`. AOF +
  RDB. Set `maxmemory`. Internal only.
- `redis-cache`: application cache only. `allkeys-lru`.
  `--save "" --appendonly no`. Set `maxmemory`.

`volatile-*` on one box evicts sessions (they have TTL).
`allkeys-*` on one box can drop the Taskiq stream (no TTL).

Keys, `db=0`: `session:{id}`, `fsm:`, `yjs:`, Taskiq
`queue_name` + `result_ex_time` + `maxlen` (`backend.taskiq_redis`
`XACK`s only),
`schedule:`. Cache instance: `cache:` only. Cache key
includes identity, permission, and model version.
Session `SET` failure → 503 (AUTH). Never a memory fallback.

API redis-py talks to both Compose services (two URLs).
Telegram `environments.telegram.redis_py` talks durable only
(FSM). Same image
pin, two processes. Do not merge the client pins. Official
`library/redis` may lag the pin tag — name the lag, do not
silently substitute.

AUTH owns cookie flags. Session payload lives on durable,
never on cache.

### Qdrant

Derived. Point id = Postgres `chunk.id` (UUID). Score is not
a probability. `query_points` only. Do not `search` /
`recommend` / `recreate_collection`.

One alias `chunks`. Physical name encodes embedding identity:
`chunks__{dense_id}__d{dim}__{chunker}__v{n}`. Vectors:
`dense` (Cosine, identity from AI) + `sparse` (BM25,
`Modifier.IDF`). `{chunker}` is AI’s identity string
persisted on the Postgres chunk row — not a local constant.
Chars `[a-z0-9_]`. No `.` / `..`. Not a collection per course
or locale.

`ensure_chunks()` on API lifespan and worker boot: create
physical if missing, payload indexes **before** first upsert,
alias if missing. Not Alembic. Not per request.

Indexes: `course_id` uuid, `locale` keyword, `source_id` uuid,
`source_type` keyword if used. Never `is_tenant` on
`user_id`. Do not add an org key. `MatchAny` on `course_id`
is the access filter — not `is_tenant`.

Same embedding identity → upsert that UUID. Postgres gone →
delete. Model / dim / chunker / BM25 options → new physical,
re-embed, atomic alias swap. BM25: `stemmer=none`, empty
stopwords, `tokenizer=multilingual` at index **and** query.

Every `query_points` has a required root filter. Access is
`course_id` `MatchAny` from session + Postgres, never from
client ids. Empty allow-list = match-nothing, not a missing
filter. Private student artifacts do **not** enter the
shared `chunks` alias; they stay Postgres + object keys.
Then locale, course, source. Prefetch dense + sparse,
`Fusion.RRF`. Re-check hit ids in Postgres before context.
Optional reranker only after ru/kk/en eval. Exact id lookups
stay in Postgres.

### Objects (RustFS)

Postgres owns metadata and ACL. RustFS stores bytes. A
successful `PutObject` is not a completed ingest.

Never public-read. Never canned ACL. Never `Principal: "*"`.
After `CreateBucket`: all four public-access blocks, then
bucket default SSE-S3. ACL auth is excluded on RustFS.

FastAPI authorizes, then issues a capability:

- upload: `generate_presigned_url` `put_object`,
  `ExpiresIn<=300`, signed `ContentType` + `ContentLength`
  (cap from settings). Reject unsigned-payload PUTs.
- download: `get_object`, `ExpiresIn<=300`.

Do not `generate_presigned_post` (POST checksums not in the
1.0.0 gate). Sign with the public path-style host (`s3v4`,
`us-east-1`). Workers use the internal endpoint. boto3 is
blocking: `anyio.to_thread` or a worker. Do not stream
student media through uvicorn as the default path.
`request_checksum_calculation=when_required`. Do not log the
query string.

One private bucket. Server UUID keys only. Prefix is
`course_id` (AUTH tenant), not a second org:

```text
c/{course}/sub/{assignment}/{user}/{id}
c/{course}/mat/{id}
c/{course}/drv/{source}/{kind}/{id}
u/{user}/ava/{id}
```

Filename is metadata. Track checksum, size, mime, owner,
status. Complete path: `HeadObject` then Postgres `ready`
then Taskiq. Delete derived objects when the source goes.

HTTPS on the public S3 host. SSE via `RUSTFS_KMS_*`. Do not
enable insecure KMS defaults. Do not expose `:9001`. Browser
PUT: exact web origin on CORS; prove `OPTIONS`/`PUT`.

### Analytics

DuckDB / Polars / Arrow scan Parquet on RustFS. Not a second
OLTP. Not a cache of Postgres.

Instantiate them only in a Taskiq worker. Never in the
request process. Never in `BackgroundTasks`. API enqueues and
reads job metadata. One in-memory `duckdb.connect()` per
task; close it. No `duckdb.sql()`, no persistent `.duckdb`,
no Quack / DuckLake for product data. Do not write entities
through `postgres_scanner`.

Workers Range-GET via DuckDB `httpfs` / Polars
`scan_parquet` / PyArrow `S3FileSystem` (path-style). Filter
and project before collect. `sink_parquet` / `COPY TO` /
streaming collect. Temporary DuckDB secrets only.

Polars: typed pipelines on one Hive tree. DuckDB: SQL,
multi-file joins, windows. Arrow: filesystem and interchange.
Preserve types: IDs stay IDs, not floats. Cap engine threads
per job.

## Done

- The write landed in the owning store. Derived stores have a
  status and a repair path.
- Tenant tables have `course_id`. Qdrant queries carry a
  backend `course_id` access filter from membership.
- Two Redis URLs in settings. Stream `maxlen` + result TTL
  set. Session keys not on the cache instance.
- Object keys are server UUIDs. Presigns expire. Anonymous
  GetObject is 403. Checksum/size in Postgres match
  `HeadObject`.
- Analytics ran in a worker and wrote a derived object + a
  Postgres row. Check did not migrate or flush stores.

## Repair

- Second Postgres / schema-per-module / `create_all`: return
  to one `public` + Alembic.
- One Redis with `allkeys-*` or `volatile-*`: split.
- Missing `maxlen` on `backend.taskiq_redis`: bound the stream.
- Query without access filter, or `recreate_collection` on
  the live name: fix the function, rebuild if the space is
  contaminated.
- Public bucket / ACL header / logged presign: close the
  bucket, rotate keys, rewrite the path.
- DuckDB in uvicorn: move the job to Taskiq.
