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
- Web: React 19.3.0 + Vite 8.3.0. No Next.js.
- API contract: FastAPI OpenAPI → `@hey-api/openapi-ts` 0.99.0.
  Clients are generated.
- Data: PostgreSQL is SoT, Qdrant is a derived index, RustFS holds
  objects, DuckDB is analytics only.
- Taskiq uses RedisStreamBroker. Cache Redis and queue Redis may be
  split if eviction is allowed on cache.
- Isolated Python envs: API/workers (`redis` 8.1.0), Telegram
  (`redis` 7.4.1), GPU/ML, optional LiteLLM proxy-runtime.
- OpenAI Python SDK in the API env is `2.9.0` because LiteLLM 1.101.0
  requires `openai>=2.20,<3`.
- Flutter pin is `3.47.5` (current stable on 2026-09-18) with bundled
  Dart `3.13.4`, not an independently upgraded Dart.
- Desktop web shell is Tauri 2 (`@tauri-apps/cli` 2.11.4). Tauri 3
  alpha is out.
- 3D is direct `three` 0.186.0. React Three Fiber 9.7 rejects React
  19.3.
- User code never runs in the API process.

Conflicts are listed under `conflicts` in the pin file.

Host doctor: `scripts/check_stack.py`. Required after `./setup`:
Codex, Node, bun, Python, uv. Declared host tools are reported until
their installer modules exist. `--strict` fails on declared drift.

`build/stack-standard.md` is generated from the pin. Refresh with
`python3 scripts/check_stack.py --write`.

## Confirmation

- `python3 scripts/check_codex_setup.py`
- `python3 scripts/check_stack.py`
- `python3 scripts/reverify_stack_pin.py`
