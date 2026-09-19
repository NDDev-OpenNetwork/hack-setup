# Scoped AGENTS templates

These are instruction templates, not product directories or application scaffolding. When the event permits repository metadata and the actual directories exist, adapt the path map and place the relevant content in that directory's AGENTS.md.

| Template | Typical target | Applies to |
|---|---|---|
| [WEB-AGENTS.md](WEB-AGENTS.md) | `apps/web/AGENTS.md` | React web/PWA/Mini App |
| [API-AGENTS.md](API-AGENTS.md) | `services/api/AGENTS.md` and separate Python services | Python backend/workers |
| [MOBILE-AGENTS.md](MOBILE-AGENTS.md) | `apps/mobile/AGENTS.md` | Flutter |
| [NATIVE-AGENTS.md](NATIVE-AGENTS.md) | Actual Rust/Go/native package root | Native modules and Tauri |
| [INFRA-AGENTS.md](INFRA-AGENTS.md) | `infra/AGENTS.md` | Compose/Caddy/telemetry |
| [DOCS-AGENTS.md](DOCS-AGENTS.md) | `docs/AGENTS.md` | Documentation and presentation sources |

Paths inside the templates are repository-root-relative prose references. Resolve the real root before loading files. Do not add native `globs` claims or duplicate the entire standards library into each file. Root-started Codex sessions explicitly read relevant nested guidance through the router; file existence alone is not an activation test.

Preserve any existing directory-specific instructions. If a directory contains multiple technology families, combine only the applicable routing lines and local facts. A general global AGENTS should not force this hackathon stack on unrelated projects.
