# Agent standards

First setup component. Lives in this plugin. The Codex CLI pin
does not auto-load these files. Read INDEX, then CORE, QUALITY
when proving, and one matching area file.

English is the language of these files. The pin is the universe of
versions. This catalogue is how to move inside that universe.

Owner of this setup stream: Danil. Product trees are not created here.

Invoke plugin skills as `$hack-agent-standards:<name>`. Codex 0.155.1
does not match a namespaced plugin skill on a bare `$name`. The repo
alias `$apply-stack-rule` stays unqualified.

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
| Playbook | `$hack-agent-standards:<name>` | INDEX / CORE / QUALITY / one area. Skills in `../skills/`. |
| Nested AGENTS | `../nested/` | Copy into `web/` `api/` `mobile/` … when that tree is created. |
| Proof | `just check` / `just test` / later product checks | Compass after a change. |
| Compass | root `AGENTS.md` | Always-on router. Keep small. |

Linked markdown is not an import. A forgotten read is a process miss.

## Catalogue

Link only files that exist.

| File | When to open | Status |
| --- | --- | --- |
| [INDEX.md](INDEX.md) | Choosing a frame | ready |
| [CORE.md](CORE.md) | How to move, cut modules, finish, and merge | ready |
| [QUALITY.md](QUALITY.md) | How to prove; wrap work in observability | ready |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Adding or changing a pin path | ready |
| [WEB.md](WEB.md) | React, Vite, TypeScript 7, TanStack, Tailwind, shadcn, PWA | ready |
| [PYTHON.md](PYTHON.md) | FastAPI, Pydantic, SQLAlchemy, Alembic, Taskiq, uv | ready |
| [CONTRACTS.md](CONTRACTS.md) | OpenAPI, generated TS/Dart clients, SSE, WebSocket | ready |
| [DATA.md](DATA.md) | PostgreSQL, Qdrant, Redis, RustFS, DuckDB, Polars, Arrow | ready |
| [CLIENTS.md](CLIENTS.md) | Flutter, Tauri 2, Telegram bot / Mini App | ready |
| [AI.md](AI.md) | Bifrost gateway, openai 3.x, embeddings, GPU/ML isolates | ready |
| [AUTH.md](AUTH.md) | OIDC/OAuth, sessions, Telegram identity, membership, RLS later, collab/LiveKit mint, Calendar, Stripe test | ready |
| [FORMATS.md](FORMATS.md) | JSON, YAML, TOML, Markdown, SQL, env, shell | ready |
| [DOCUMENTS.md](DOCUMENTS.md) | PDF, Office, OCR, media, reports | ready |
| [EDUCATION.md](EDUCATION.md) | Tiptap, Yjs, KaTeX, FSRS, Pyodide, executor, LiveKit, echarts, OR-Tools | ready |
| [INFRA.md](INFRA.md) | Docker, Compose, Caddy, Vector, OpenObserve, OTel, collab/live/gpu profiles | ready |

## Skills

Thin loaders. Invoke `$hack-agent-standards:<name>`. Pin list:
`registered.standards_plugin_skills`.

| Skill | Opens |
| --- | --- |
| `apply-agent-standard` | INDEX, then CORE / QUALITY / one area |
| `core-motion` | CORE |
| `quality-proof` | QUALITY |
| `pin-dependencies` | DEPENDENCIES |
| `web-ui` | WEB |
| `python-api` | PYTHON |
| `wire-contracts` | CONTRACTS |
| `data-stores` | DATA |
| `native-clients` | CLIENTS |
| `ai-models` | AI |
| `identity-auth` | AUTH |
| `text-formats` | FORMATS |
| `file-documents` | DOCUMENTS |
| `education-lessons` | EDUCATION |
| `runtime-infra` | INFRA |

## Mixed

A Pydantic model used by a generated TS client needs PYTHON and
CONTRACTS. A Vector YAML file needs FORMATS and INFRA. Telegram
`initData` needs AUTH, CLIENTS, and WEB. Live classroom voice
is EDUCATION + INFRA (`live`) + AUTH (`/v1/auth/livekit/token`).
Hocuspocus is EDUCATION + INFRA (`collab`) + AUTH
(internal `/v1/auth/collab/authenticate`). OR-Tools is EDUCATION +
PYTHON (Taskiq). echarts is EDUCATION (WEB chrome). File
extension alone is not enough.

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

- Nested product `AGENTS.md` inside `web/`, `api/`, `mobile/` (copy from
  `plugins/hack-agent-standards/nested/` in the same change that creates
  the tree)
- Empty product trees
- Prettier, Taplo, SQLFluff, Modal, Drift, reveal.js, OBS as required
- `docs/research/` as runtime law
- Ban-list file (prefer language lives in the area file and the pin)
