# 4. Product stack standard

- Status: accepted
- Date: 2026-09-20
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The hackathon product needs one frozen technology standard: languages,
web/PWA, Python backend, data, clients, auth, AI, media, deploy, and
agent-quality gates. Versions are chosen at prep time and only change
on purpose.

## Decision Outcome

`build/stack-pin.json` schema 2 is the source of truth.

- JS: Node 24.21.0 LTS for tool compatibility, bun 1.4.2 for the
  project. No pnpm. No second lockfile.
- Web: React 19.3.0 + Vite 8.3.0 + TypeScript 7.0.2 only. No Next.js.
  No `typescript@6` and no `@typescript/typescript6` in the web workspace.
  `@types/node` stays on the 24.x line (`24.13.6`). Install shadcn with
  `bunx shadcn@4.21.0`; do not `bun add shadcn` (nests Zod 3).
- API contract: FastAPI OpenAPI. Intended TS generator is
  `@hey-api/openapi-ts` `0.99.0`. Clients are generated. That package
  must not be installed next to `typescript@7.0.2`. Do not take `@next`.
- Data: PostgreSQL is SoT, Qdrant is a derived index, RustFS holds
  objects, DuckDB is analytics only.
- Taskiq uses RedisStreamBroker. Cache Redis and queue Redis may be
  split if eviction is allowed on cache.
- Isolated Python envs: API/workers (`redis` 8.1.0), Telegram
  (`redis` 7.4.1), GPU/ML, plus the Bifrost LLM gateway container.
- LLM access goes through Bifrost `maximhq/bifrost:v2.2.1`
  (OpenAI-compatible on `:8080/v1`); the API env carries `openai`
  `3.16.2` pointed at the gateway `base_url`. LiteLLM is removed;
  the `openai<3` cap is gone (superseded by ADR 0010).
- CLIProxyAPI is `7.3.9`, an optional sidecar upstream of the
  gateway.
- PostgreSQL driver is psycopg 3. Do not add asyncpg.
- `@hey-api/openapi-ts` `0.99.0` is latest stable (2026-06-22). It
  crashes if it resolves `typescript@7.0.2` (`ts.SyntaxKind`). Keep
  it out of the web workspace. Do not add a second TypeScript to web
  to make the generator start. Do not take `@next` (maintainer still
  pointed at a dated nightly on 2026-09-18). Generated client source
  is typechecked by `tsc` 7. Revisit when a stable Hey API release
  has no Compiler API dependency. Do not add `openapi-typescript`.
- Flutter pin is `3.47.5` (current stable on 2026-09-18) with bundled
  Dart `3.13.4`, not an independently upgraded Dart.
- Desktop web shell is Tauri 2 (`@tauri-apps/cli` 2.11.4,
  `@tauri-apps/api` 2.11.1, crates.io `tauri` 2.11.5). Tauri 3
  alpha is out.
- 3D is direct `three` 0.186.0. `@react-three/fiber` 9.7 and the v10
  canary still peer `react <19.3` (issue 3915).
- `httpx` stays `0.28.1`. FastAPI extras require `httpx<1`. Do not take
  SQLAlchemy `2.1` rc or Pydantic `2.14` beta.
- CLIProxyAPI `7.3.9` is a GitHub release, not a PyPI package.
- Docling `2.129.0` default extra `standard` pulls RapidOCR →
  `opencv-python` and torch. The only `cv2` is
  `opencv-python-headless` `5.0.0.93`. Constrain `opencv-python`. Keep
  that torch graph out of the API env. `pypdf` `6.19.0` is a separate
  path; Docling rasterizes through pypdfium2.
- User code never runs in the API process.

Conflicts are listed under `conflicts` in the pin file.

Project commands: `just` `1.58.0` (`justfile`). Do not add a Makefile.

Host doctor: `scripts/check_stack.py`. Required after `./setup`:
Codex, Node, bun, Python, uv. Declared host tools are reported until
their installer modules exist. `--strict` fails on declared drift.

`build/stack-standard.md` is generated from the pin. Refresh with
`python3 scripts/check_stack.py --write`.

## Confirmation

- `python3 scripts/check_codex_setup.py`
- `python3 scripts/check_stack.py`
- Hackathon-day only: `just reverify`
