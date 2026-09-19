# Agent standards

First setup component. Lives in this plugin. Codex 0.155.1 does not
auto-load these files. Open one standard that matches the change.

English is the language of these files. The pin is the universe of
versions. This catalogue is how to move inside that universe.

Owner of this setup stream: Danil. Product trees are not created here.

## Priority

Highest first:

1. This turn's owner message.
2. The opened standard in this directory (defaults).
3. `build/stack-pin.json` (what exists and which version).
4. Model invention.

Defaults exist so the model does not invent a stack or inflate scope.
If the owner changes the task, follow the owner. Do not ask permission.

- Task-local exception: follow the owner. Do not rewrite the pin.
  Name the exception in the report.
- Durable change: update the pin and the matching standard first,
  then continue.

On a mixed request: the parts the owner specified follow the owner.
The parts they did not specify follow these frames.

## Layers

| Layer | Path | Job |
| --- | --- | --- |
| Universe | `build/stack-pin.json` | Identity. Versions live only here. |
| Frames | `plugins/hack-agent-standards/standards/` | How to move. This tree. |
| Playbook | `skills/apply-agent-standard` | Opens INDEX, then one file. |
| Proof | `just check` / later product checks | Compass after a change. |
| Compass | root `AGENTS.md` | Always-on router. Keep small. |

Linked markdown is not an import. A forgotten read is a process miss.

## Catalogue

Link only files that exist. Planned names are not links yet.

| File | When to open | Status |
| --- | --- | --- |
| [INDEX.md](INDEX.md) | Choosing a frame | writing |
| [CORE.md](CORE.md) | How to move, cut modules, finish, and merge | writing |
| [QUALITY.md](QUALITY.md) | How to prove; wrap work in observability | writing |
| DEPENDENCIES.md | Adding or changing a pin path | planned |
| WEB.md | React, Vite, TypeScript 7, TanStack, Tailwind, shadcn, PWA | planned |
| PYTHON.md | FastAPI, Pydantic, SQLAlchemy, Alembic, Taskiq, aiogram, uv | planned |
| CONTRACTS.md | OpenAPI, generated TS/Dart clients, SSE, WebSocket | planned |
| DATA.md | PostgreSQL, Qdrant, Redis, RustFS, DuckDB, Polars, Arrow | planned |
| CLIENTS.md | Flutter, Tauri 2, Telegram bot / Mini App | planned |
| AI.md | LiteLLM, openai 2.x, embeddings, GPU/ML isolates | planned |
| AUTH.md | OIDC/OAuth, sessions, Calendar, Stripe test | planned |
| FORMATS.md | JSON, YAML, TOML, Markdown, SQL, env, shell | planned |
| DOCUMENTS.md | PDF, Office, OCR, media, reports | planned |
| EDUCATION.md | Tiptap, Yjs, KaTeX, FSRS, Pyodide, student executor | planned |
| INFRA.md | Docker, Compose, Caddy, Vector, OpenObserve, OTel | planned |

A Pydantic model used by a generated TS client needs PYTHON and
CONTRACTS. A Vector YAML file needs FORMATS and INFRA. File extension
alone is not enough.

## File contract

Every area file uses this shape. Versions are pin paths, not copied
numbers.

```text
# <Area>
Universe: pin `<section.*>`

Unless the owner said otherwise this turn.

## Default move
The first action in this layer.

## Pattern
How this layer is cut.

## Done
What a finished slice includes.

## Repair
Check is red → return the world to the pin, or promote if the owner
asked for a durable change.
```

## Not yet

- Nested product `AGENTS.md` (only when `web/`, `api/`, or `mobile/` exist)
- Empty product trees
- Prettier, Taplo, SQLFluff, Modal, Drift, reveal.js, OBS as required
- `docs/research/` as runtime law
- Ban-list file (prefer language lives in the area file and the pin)
