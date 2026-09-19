# Contracts

FastAPI OpenAPI is the only HTTP contract source. Clients are generated.

## Generators

| Consumer | Tool | Pin / note |
| --- | --- | --- |
| Web / desktop webview | `@hey-api/openapi-ts` | `0.99.0` is the intended stable. Not a web workspace dep. No `@next`. Output is typechecked by `tsc` 7. |
| Flutter | dart-dio | Same OpenAPI document. |

Do not add `openapi-typescript`. Do not hand-edit generated files. Do not
keep a parallel DTO layer “for clarity”.

## Transports

- CRUD / commands: HTTP + OpenAPI.
- Model tokens: SSE.
- Realtime rooms: WebSocket. Optional live classroom: LiveKit, unversioned.

A rename in the Python schema is unfinished until the OpenAPI document and
every generated client are regenerated and the diff is reviewed.

## This repo

No OpenAPI document exists yet. Do not invent one. When `api/` exists, the
contract file is generated from FastAPI, not written first.
