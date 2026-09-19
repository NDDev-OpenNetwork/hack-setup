# Coverage of the agreed technology catalogue

This map connects product technology to instructions and validation. It does not create a dedicated LSP for each framework: many frameworks use the same language server, while runtime behavior needs separate checks.

| Technology group | Rule owner under `repo-policy/docs/agent-standards` | Navigation / correctness evidence |
|---|---|---|
| Node LTS, Bun, native TypeScript | DEPENDENCIES, WEB | TS semantic adapter plus actual selected runtime/compiler |
| Python, uv | PYTHON, DEPENDENCIES | ty/Pyright path, real interpreter/import graph |
| React, Vite, TanStack Router/Query | WEB, CONTRACTS | TSX references, generated routes/client, native typecheck, browser scenario |
| Tailwind, shadcn/ui, RHF, Zod, Lucide, Motion | WEB, FORMATS | TS/CSS partial semantic coverage plus UI/build validation |
| i18next/react-i18next, RU/KK/EN | WEB, FORMATS | Resource/schema/placeholder and rendered-language checks |
| react-markdown/remark, Tiptap | WEB, DOCUMENTS, EDUCATIONAL-MODULES | TS navigation; safe rendering and content-schema checks |
| Hey API/OpenAPI, Dart client generation | CONTRACTS, DEPENDENCIES | Source schema → generated consumer → compile/behavior |
| FastAPI/Uvicorn/Pydantic/settings/HTTPX | PYTHON, CONTRACTS | Python navigation plus request/lifecycle/timeout behavior |
| SQLAlchemy/Psycopg/Alembic/PostgreSQL | PYTHON, DATA-SEARCH | Python nav, actual SQL/migration/constraint checks |
| Taskiq/taskiq-redis/Redis | PYTHON, DATA-SEARCH | Python nav, worker idempotency/state/config checks |
| Qdrant/qdrant-client/FastEmbed | DATA-SEARCH, AI-EDUCATION | Python nav, index/version/access/retrieval checks |
| RustFS/S3/boto3 | DATA-SEARCH, PYTHON | Ownership/URL/metadata and actual operation checks |
| DuckDB/Polars/PyArrow/CSV/Parquet | DATA-SEARCH, DOCUMENTS, FORMATS | Typed data schema and round-trip/precision checks |
| Flutter/Dart/Riverpod/go_router/Dio/Freezed | NATIVE-MOBILE, CONTRACTS | Matching Dart analyzer plus Flutter/generator/platform checks |
| Flutter ARB/intl/localizations | NATIVE-MOBILE, FORMATS | JSON plus locale/placeholder and generated-code checks |
| flutter_secure_storage/app_links/Drift | NATIVE-MOBILE, AUTH-INTEGRATIONS | Lifecycle, deep-link, local-data and actual device behavior |
| PWA/Workbox/Dexie | WEB, AUTH-INTEGRATIONS | Browser/service-worker/storage identity and update behavior |
| Tauri/Rust/Cargo | NATIVE-MOBILE, DEPENDENCIES | TS/Rust LSP and target build/IPC capability checks |
| PyO3/maturin, optional optimized Rust | NATIVE-MOBILE, PYTHON | Rust/Python boundary, ABI and actual performance evidence |
| Go/gopls, conditional native code | NATIVE-MOBILE | Go/module or native compile context |
| aiogram/Telegram Bot/Mini App | PYTHON, WEB, AUTH-INTEGRATIONS | Python/TS navigation plus delivery/signature/account checks |
| Authlib/Google/GitHub/Yandex | AUTH-INTEGRATIONS, PYTHON | Actual provider flow and server authorization, not LSP-only |
| Google Calendar, Stripe test mode | AUTH-INTEGRATIONS | Scopes, signature/idempotency and sandbox behavior |
| CLIProxyAPI/LiteLLM/OpenAI | AI-EDUCATION, PYTHON, DEPENDENCIES | Actual endpoint capability and structured/domain checks |
| Modal/PyTorch/ONNX/local ML | AI-EDUCATION, DEPENDENCIES | Independent environment/device/artifact validation |
| Docling/pypdf/Tesseract/Pillow/OpenCV | DOCUMENTS, AI-EDUCATION | Extracted structure/provenance and visual/domain checks |
| python-docx/python-pptx/openpyxl | DOCUMENTS | Format-aware editing, rendering, formulas/types |
| HTTPX/Trafilatura/Playwright page extraction | DOCUMENTS, WEB | URL/input controls and actual extracted/rendered content |
| FFmpeg/ffprobe/faster-whisper/CTranslate2 | DOCUMENTS, AI-EDUCATION | Stream/timestamp/transcription and worker checks |
| LiveKit/realtime audio/video | EDUCATIONAL-MODULES, AUTH-INTEGRATIONS | Session access, stream lifecycle and actual client behavior |
| Yjs/Hocuspocus collaboration | EDUCATIONAL-MODULES, WEB | Shared-document schema, authorization and reconnect/persistence |
| KaTeX/SymPy | EDUCATIONAL-MODULES, DOCUMENTS | Rendering and deterministic symbolic/domain checks |
| Excalidraw/React Flow/ECharts/Three.js | EDUCATIONAL-MODULES, WEB | TS navigation plus actual graph/data/render/resource behavior |
| FSRS/OR-Tools | EDUCATIONAL-MODULES, QUALITY | Deterministic history/constraints/status cases |
| Pyodide/gVisor student-code execution | EDUCATIONAL-MODULES, INFRA | Explicit execution isolation/resource checks |
| Docker/Compose/Caddy | INFRA, FORMATS | Consumer validation and affected image/service path |
| OpenTelemetry/Vector/OpenObserve/structlog | INFRA, PYTHON | Valid config and actual correlated telemetry delivery |
| Codex/Serena/Context7/Playwright MCP | SERENA-WORKFLOW, DEPENDENCIES | Actual MCP tool discovery and capability-specific proof |
| Ruff/ty/Biome/pytest/Vitest/Playwright | QUALITY, language-specific rules | Narrow actual checks, not mandatory exhaustive pipeline |
| Git worktrees/just | MULTIAGENT, FORMATS | Isolation, task parser and concrete integration evidence |
| reveal.js/OBS/FFmpeg demo delivery | DELIVERY, DOCUMENTS | Rendered slides and honest playable recording |

## Formats without a framework-specific server

API schemas, ORM models and UI components inherit their source-language navigation. JSON/YAML/TOML can have schema-aware assistance, but format validity does not prove framework correctness. PDF/Office/media require their artifact tools. The exact matrix and known adapter gaps remain in [LSP-MATRIX.md](LSP-MATRIX.md).
