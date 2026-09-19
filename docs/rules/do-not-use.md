# Do not use

Banned by `build/stack-pin.json` `do_not_use` and ADRs 0001–0004, 0007. If a
tool would be easier with one of these, stop and keep the pin.

- pnpm. npm as the project installer. A second JS lockfile.
- Next.js.
- `openapi-typescript` as the primary OpenAPI generator.
- React Three Fiber / `@react-three/drei`. Use `three` `0.186.0` if 3D is needed.
- LangChain or LlamaIndex as required orchestration.
- Elasticsearch or pgvector. Qdrant is the derived index.
- asyncpg. PostgreSQL driver is psycopg 3 `3.3.6`.
- Independent Dart newer than the Flutter bundle.
- Tauri 3 alpha. Desktop is Tauri 2 (`@tauri-apps/cli` `2.11.4`).
- Node 26 Current. Node is `24.21.0` Active LTS.
- openai Python 3.x in the API env. API pin is `2.54.0` (`>=2.20,<3`).
- LiteLLM `proxy-runtime` extra in the API env.
- `opencv-python`. The only `cv2` is `opencv-python-headless` `5.0.0.93`.
  Default `docling` extra `standard` pulls RapidOCR → `opencv-python` +
  torch. Constrain it; do not `uv add docling` unconstrained into API.
- GNU make / Makefile as the project command runner. Use `just` `1.58.0`.
- Codex `0.156.0-alpha.*`. Codex.app / discontinued `codex-app` cask.
- `gpt-5.6-luna` / `gpt-5.6-terra`. Session models are `gpt-6-astra`
  and `gpt-5.6-sol` only. Do not use bare `gpt-5.6` as the session slug.
- Codex subagents (`features.multi_agent`, `features.multi_agent_v2`,
  `agents.enabled`). Single-agent only.
- `model_reasoning_effort` `extra-high` / `x-high`. Wire value is `xhigh`.

Conflicts that are not “latest wins”:

- `@hey-api/openapi-ts@next`. `0.99.0` must not sit next to `typescript@7` in web.
- `typescript@6` or `@typescript/typescript6` in the web workspace.
- `typescript-eslint` in the web workspace.
- `bun add shadcn`. CLI only: `bunx shadcn@4.21.0` (the package nests Zod 3).
- `@types/node` `26.x` until Node 26 is LTS. Types stay `24.13.6`.
- `httpx` 1.x. FastAPI extras require `httpx<1`. Pin is `0.28.1`.
- SQLAlchemy `2.1` rc or Pydantic `2.14` beta.
- LiteLLM `1.101.0` needs Python `>=3.10,<3.15`. Stay on `3.14.7`.
- Telegram env redis-py `7.4.1` vs API/workers `8.1.0`. Do not merge those lockfiles.
- Product TypeScript is `7.0.2` only. No second compiler in web.
