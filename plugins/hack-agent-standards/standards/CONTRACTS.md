# Contracts

Universe: `build/stack-pin.json` `frontend.api_client`,
`clients.flutter.openapi_generator`, `backend.fastapi`,
`backend.pydantic`, `runtimes.typescript`, `runtimes.node`.

Unless the owner said otherwise this turn.

This file is the wire law. Python authors it. Generated TS and Dart
consume it. AUTH owns how credentials are minted. WEB / CLIENTS
consume the generated packages. Do not create `contracts/`, `api/`,
or a codegen workspace only to hold this file.

## Default move

1. Wire change starts in Python (routes, Pydantic,
   `api/shared/openapi.py`).
2. Dump `app.openapi()` → `contracts/openapi.json` (`indent=2`,
   trailing newline, FastAPI key order). No live URL. No YAML twin.
   No `operationId` rewrite.
3. Regen **both** clients from that file in one wave:
   - TS: pin `@hey-api/openapi-ts` in a tools/codegen workspace
     (`input` = the snapshot, `@hey-api/client-fetch`). Not in
     `web/`. No `@next`. No Vite plugin.
   - Dart: pin `openapi-generator-cli` `-g dart-dio` on the same
     file (`built_value`, `useOptional=true`,
     `enumUnknownDefaultCase=true`). Then `build_runner`. Docker
     or bunx — never web, never a Flutter `pubspec` generator.
4. Fix adapters and callers. Never edit generated output.
5. Proof: dump bytes == committed file; `tsc` 7 on generated TS;
   `dart analyze` on generated Dart. Regenerating is
   a write recipe named `generate-clients` when `api/` exists.
   Check later is tmp-dump + `cmp` + compile of **already
   committed** clients. Never fold regen into `just check`.
   Do not add that recipe in this setup repo.

## Pattern

### Sources

- Authoring SoT: FastAPI + Pydantic (`separate_input_output_schemas`
  stays True). OAS **3.1.0**. Do not set `openapi_version = "3.0.2"`.
- Distribution SoT: one committed `contracts/openapi.json`. Both
  generators read only this. `info.version` is document semver, not
  the URL `/v1`.
- Persistence ≠ public response ≠ form UX Zod ≠ Flutter/freezed
  domain. WEB: local Zod + `formToDto` assignable to the generated
  request type.
- Python impl that leaves `app.openapi()` byte-identical is not a
  contract change. Do not regen.

### URL versioning

One FastAPI app, one spec (PYTHON: `include_router` only — do not
`mount()` a version app).

- `servers[0].url` is the public origin only
  (`https://api.example.com`). Absolute, no trailing slash,
  no `{variables}` as the default. **Never** put `/v1` in
  `servers`. INFRA Caddy serves `/v1/*` on that origin. A
  gateway prefix (`/api`) is an INFRA exception, not the
  default — if you add one, paths stay `/v1/...` and
  `servers` does not also include `/v1`.
- Path keys include the version: `/v1/users`, `/v2/users`.
- Full URL is `servers[].url` + path (literal append). Version in
  both places → `/v1/v1/users`. Fix the spec; do not patch clients.
- Dump `app.openapi()`, not live `/openapi.json` (live prepends
  `root_path` as `servers[0]` when `root_path_in_servers=True`).
- Runtime hosts override `baseUrl` / `basePathOverride`. Do not
  bake localhost as `servers[0]`.
- Do not invent empty `/v2` paths on day 1.

### operationId

Frozen: `vN-tag-name` (`v1-items-list_items`). Unversioned
`/health` `/ready`: `system-{name}`. Regex
`^v[1-9][0-9]*-[a-z][a-z0-9]*-[a-z][a-z0-9_]*$`.

PYTHON emits this at construct. One resource tag, not a version
tag. No decorator `operation_id=`. No FastAPI preprocess that
strips `{tag}-`. No `--remove-operation-id-prefix`. Changing the
function after a client exists is a hard break (alias or `/v2`,
do not rename in place).

hey-api and dart-dio both camelize to `v1ItemsListItems`. Hyphen
is the delimiter so hey-api does not nest and dart-dio does not
strip a `_` prefix.

### Compatibility

Axes: wire | source (regen) | semantic. Generated TS/Dart are
first-class.

**Safe in `/v1`:** optional request field (default ≡ pre-field);
optional response field; new endpoint; request-only enum value;
response enum value only if the field is an open string
(`examples` + “may grow”) **and** apps have an unknown branch;
new 4xx for a **new** failure mode; extra error `details`.

**`/v2` (or dual-write + keep old):** rename / remove field;
change type, format, nullability, requiredness, or semantics;
required request field; closed response enum growth; remove enum
value; change `operationId`; rename error keys; change HTTP
status for the same failure (`422` → `400` is `/v2`).

Never `additionalProperties: false` on response schemas.
`enumUnknownDefaultCase=true` on dart-dio.

### Errors

App errors: `{"detail": "<string>"}` via `HTTPException`. Shared
model `HTTPError`. 422 only: auto `HTTPValidationError`
(`detail` is `ValidationError[]`). Same key, two shapes — branch
on status. No RFC 9457. No `exc.body` on the wire.

Every status you return is in `responses=` with a matching model.
Common 401/403/404/409 on `FastAPI(responses=…)`. Never `4XX` /
`default` / explicit `422`.

### Lists

Paginate every collection on day 1. Unbounded `list[T]` is not a
list contract (adding pagination later is a behavioral break).

```text
GET /v1/{collection}?limit=50&offset=0&sort=-created_at&status=open&q=
```

| Param | Default | Rule |
| --- | --- | --- |
| `limit` | 50 | `ge=1, le=100`. Over-max → 422 |
| `offset` | 0 | `ge=0` |
| `sort` | `-created_at` | OpenAPI enum. Invalid → 422. SQL tie-break on `id` |
| filters | omitted | Allowlisted scalars per resource. No `__gte` soup |

Envelope: `{items, limit, offset, total}`. `items` is a list,
never `null`. Empty page = `[]`. `total` is post-filter count
(always, for classroom size). Optional `has_more` is additive.

Query arrays: avoid, or `style=form, explode=true` only
(`?tag=a&tag=b`). No CSV. No JSON:API `page[size]`. No GET body.
Document filters that will blow the URL → `POST /v1/{res}:search`
with the **same** envelope. Cursor is a second contract (feeds);
do not mix `cursor` and `offset` on one op.

### Headers

Two IDs, never aliased.

`Idempotency-Key`: unquoted `^[A-Za-z0-9._~-]{8,64}$` (UUID v4).
`required: true` only on payment / entitlement / irreversible
create `POST`. Other POST/PATCH: optional, honor if present.
Ignore on GET/HEAD/DELETE. Missing required → 400. In-flight →
409. Fingerprint mismatch → 422. Replay stored `(status, body)`
24h, scoped `(principal, operation, key)`. Mint at the intent
site (button / Riverpod). **No** interceptor. Declare via
`Header(alias="Idempotency-Key")` so it appears in OpenAPI.

`X-Request-Id`: optional inbound, generate if missing, always
echo (document as a **response** header too). New value every
attempt. Interceptor OK. CORS `expose_headers` includes it.
Not an idempotency key. `traceparent` stays OTel.

### Security (schema)

`securitySchemes` in the generator input: `BearerAuth`
(`http` / `bearer` / `opaque`) only. Protected ops:
`security: [{BearerAuth: []}]`. Login, CSRF bootstrap, native
exchange: `security: []`.

Do not emit `APIKeyCookie`, `Cookie()`, or cookie parameters
into this snapshot (hey-api would ask JS for the HttpOnly
value; dart-dio would send it as a header). Web sends the
session via `credentials: 'include'` after `GET /v1/auth/csrf`.
Native uses `setBearerAuth` after `/v1/auth/native/exchange`.
BearerAuth in this dump is native (and bot m2m is not this
scheme). CSRF header name `X-CSRF-Token` is documented; it
is not a security scheme. AUTH owns cookie flags, CSRF
implementation, PKCE, token storage, internal
`POST /v1/auth/collab/authenticate`, and
`POST /v1/auth/livekit/token`. Those two stay HTTP — not
OpenAPI WebSocket ops.

### SSE

`fastapi.sse` (`response_class` + yield). `data` is JSON.
Sentinels use `raw_data`. Annotate `AsyncIterable[Payload]`.
Named events via `ServerSentEvent(event=..., id=..., data=…)`.
Frozen SSE names: `token`, `done`, `error`. Terminal `event: done` +
`raw_data: [DONE]` (and `event: error` for in-band failure).
Closed socket ≠ job success. Browser `EventSource` reconnects;
hey-api fetch-SSE does not. Clients close on `done`. Resume
via `Last-Event-ID` must be idempotent.

FastAPI emits OAS 3.2 `itemSchema` inside a 3.1 document.
Treat payload types as best-effort. Event names in this file
are the contract. Do not downgrade `openapi_version`.

### WebSocket

Not in OpenAPI. Do not invent fake HTTP statuses for messages.
Cookie / `Depends` + `WebSocketException(1008)` before
`accept()`. No query token. Versioned Pydantic envelope
(`schema_version` + `event` discriminator). Frozen events:
`progress`, `result`, `error`. Frozen close: `1008` before
accept (auth/policy), `1000` after a terminal `result` or
`error`. Close / drop ≠ success. AsyncAPI is optional later,
not the default toolchain.

### Codegen

Treat output dirs as a dependency. Merge conflicts: fix
Python / snapshot / generator config, regen, typecheck.

| Predicate | Dump | TS | Dart |
| --- | --- | --- | --- |
| `app.openapi()` unchanged | no | no | no |
| dump differs | yes | yes | yes |
| generator pin / config change | no | that client | that client |
| caller-only | no | no | no |

Do not regen one client “because only web needs it.”
Do not put the generator next to `typescript@7`.
Do not take `@hey-api/openapi-ts@next`.
Do not add `openapi-typescript`.
dart-dio OAS 3.1 nullable is incomplete — inspect `T \| None`
on the first dump. That is a generator issue, not a FastAPI
3.0 downgrade, unless the owner promotes it.

## Done

- Snapshot committed and equals `app.openapi()`.
- Both clients regenerated from it; no hand-edits.
- Adapters compile (`tsc` 7, `dart analyze`).
- `operationId`s match the frozen regex, or `system-{name}`
  on `/health` `/ready`. No `/v1/v1/` URLs.
- Success + one failure shape covered when the envelope or a
  status changed.
- SSE/WS: terminal event (or close code) plus persisted job
  state, not “socket closed.”

## Repair

- Drift dump vs file: redump from the **code**, not from a
  client.
- Dirty generated files: regen; do not merge-edit.
- hey-api next to `typescript@7`: move the generator out of
  web. Do not add TS6 to web. Do not take `@next`.
- One client regenerated: regen the other from the same
  snapshot.
- Duplicate `operationId` or smashed DTO name: fix PYTHON
  emit, then dump + dual regen.
- `/v1/v1/` in a generated URL: `servers` vs paths. Fix the
  spec.
- RFC 9457 / envelope rename: this file + dual regen. Do not
  sneak it into a Python-only change.
