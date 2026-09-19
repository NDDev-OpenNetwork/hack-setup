# Standards router

These are repository conventions, not native Codex glob directives. The agent explicitly loads the relevant files. Reuse already-read instructions within the current task unless they changed.

Always read [CORE](CORE.md), [SERENA-WORKFLOW](SERENA-WORKFLOW.md), [QUALITY](QUALITY.md). Then route by the actual files **and** behavior changed:

| Trigger | Load |
|---|---|
| Python, FastAPI, Pydantic, SQLAlchemy, Alembic, Taskiq, aiogram workers | [PYTHON](PYTHON.md) |
| TS/JS/TSX/JSX, React/Vite/TanStack, Tailwind/forms/PWA | [WEB](WEB.md) |
| Dart/Flutter, Rust/Tauri/PyO3, Go, C/C++, Swift/Kotlin bridges | [NATIVE-MOBILE](NATIVE-MOBILE.md) |
| HTTP schemas, events, streaming, generated SDKs, API renames | [CONTRACTS](CONTRACTS.md) |
| SQL, PostgreSQL, Qdrant, Redis, RustFS, DuckDB/Polars/Arrow | [DATA-SEARCH](DATA-SEARCH.md) |
| LLM calls, prompts, embeddings, retrieval, evaluations, educational grading | [AI-EDUCATION](AI-EDUCATION.md) |
| OAuth, sessions, account linking, Calendar, Telegram, Stripe | [AUTH-INTEGRATIONS](AUTH-INTEGRATIONS.md) |
| Compose/Docker/Caddy, OpenObserve/Vector/OTel, deployment | [INFRA](INFRA.md) |
| JSON/JSONC/JSONL, YAML, TOML, Markdown, SQL files, XML, env, shell | [FORMATS](FORMATS.md) |
| PDF/Office, image/media, CSV/XLSX, notebook, exported reports/slides | [DOCUMENTS](DOCUMENTS.md) |
| Tiptap/Yjs, math, diagrams, FSRS, OR-Tools, video, runnable student code | [EDUCATIONAL-MODULES](EDUCATIONAL-MODULES.md) |
| Dependencies, lockfiles, tool versions, code generation | [DEPENDENCIES](DEPENDENCIES.md) |
| Parallel agents, integration, migration heads, merge conflicts | [MULTIAGENT](MULTIAGENT.md) |
| Presentation/demo-video, release handoff | [DELIVERY](DELIVERY.md) |

A `.yaml` file for Vector requires FORMATS and INFRA. A Pydantic change used in generated TS requires PYTHON, CONTRACTS and WEB. An ARB translation change requires NATIVE-MOBILE and FORMATS. A document used as RAG input requires DOCUMENTS, DATA-SEARCH and AI-EDUCATION. File extension alone is not a sufficient classifier.

## Authority and evidence

These normative choices implement the user's hackathon workflow. They do not certify that an external package is installed. Resolve actual API/version behavior through the locked project and primary documentation. The preparation pack's source register and compatibility report should remain available to the setup agent outside the repository or be copied as reference metadata when permitted.

Never require loading this entire catalogue for a one-line change. Never omit a directly affected consumer because it resides in another directory or language.
