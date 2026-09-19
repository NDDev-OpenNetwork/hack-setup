# Language servers, formats and validation matrix

Baseline: Serena 1.7.0 at `949a27ef1e5fda1a6e7b561e777bcece345c6ffd`. Built-in identifiers come from the inspected catalogue/template; actual capabilities are negotiated and tested on the host. Sources: [S2,S4-S10,L1-L13](../SOURCES.md).

**Built-in** means a SolidLSP adapter exists in the inspected release. It does not mean all LSP methods work or that the server is already installed. **External** means an optional server/adapter integration, not an invented Serena language identifier. **CLI** means deliberately using a deterministic format-specific tool without pretending it is LSP.

## Source languages

| Files / technology | Serena identifier and primary server | Provisioning decision | Authoritative validation / caveat |
|---|---|---|---|
| `.py`, `.pyi`: FastAPI, SQLAlchemy, Taskiq, aiogram, AI/data code | `python_ty` → Astral ty (explicit secondary/experimental adapter) | Pin selected ty, set documented `ls_path` or `ty_version` | `ty check`, Ruff; preserve each service's import environment |
| Python fallback | `python` → Pyright; `python_basedpyright` alternative | Activate one fallback only if ty behavior fails | Do not run several type systems as mandatory competing gates |
| `.ts`, `.tsx`, `.js`, `.jsx`, module variants: React/Vite/TanStack/Tauri UI | `typescript` → typescript-language-server + tsserver | Adapter defaults are 5.1.3/5.9.3; manage navigation engine separately | Native project TS compiler + Biome; COMP-02/03 |
| TypeScript alternative | `typescript_vts` → vtsls | Optional tsserver-based alternative, not native TS7 support by name | Separate behavior test; do not enable alongside primary |
| `.rs`: native services, Tauri, extensions | `rust` → rust-analyzer | Matching toolchain, rust-src, correct Cargo workspace | cargo check, rustfmt; selective Clippy; build scripts may execute |
| `.go`; Go workspace/module configuration is companion input | `go` → gopls | Pin gopls compatible with selected Go; resolve modules | gofmt, go vet/test for affected packages; toolchain/module consistency |
| `.dart`: Flutter and Dart packages | `dart` → Dart language server | Align to Flutter SDK, not default downloaded 3.7.1 | flutter analyze, dart format; COMP-04/05 |
| `.sh`, Bash scripts | `bash` → bash-language-server | Pin server and shell tools; declare actual shell dialect | ShellCheck, shfmt, syntax check; zsh syntax is not automatically Bash |
| `.c/.h/.cc/.cpp` when native integrations require them | `cpp` → clangd | Optional; compile_commands.json and matching headers/toolchain | Actual compiler + clang-format; `cpp_ccls` is an alternative, not additional primary |
| `.swift` native plugin code | `swift` → SourceKit-LSP | Optional, matching Xcode/Swift build context | Native target build; no assumption that a Linux host can validate iOS |
| `.kt/.kts`, `.java` native plugin code | `kotlin`, `java` | Optional only when authored native sources exist; adapter prerequisites | Gradle/JDK and platform build; do not index generated caches |
| `.tex/.bib` | `latex` → texlab | Explicit opt-in document profile | Build/render plus reference validation; no need for ordinary web reports |
| Shader sources | `hlsl` adapter family | Conditional, match actual shader dialect | Compile using target graphics pipeline; adapter name is not universal support proof |

## Text configuration and documentation

| Files | Serena path | Correct validation and limits |
|---|---|---|
| `.md`, `.markdown`, instructions and SKILL.md | `markdown` → Marksman, explicitly configured | Headings/links, markdownlint, frontmatter parsing; not TypeScript semantics inside code fences |
| `.yaml/.yml`, Compose, CI, Serena config | `yaml` → Red Hat YAML LS, explicit selection | Strict duplicate-key policy, selected schema, then native consumer CLI |
| `.json/.jsonc`, package/config schemas | `json` → extracted VS Code JSON LS | Explicit schema association; JSONC only where the consumer permits it |
| `.toml`, pyproject/Cargo/Codex config | `toml` → LSP-enabled Taplo | Parse, schema where maintained, then actual consumer; npm Taplo is insufficient for LSP |
| `.html/.htm` | `html` → extracted VS Code HTML LS | In-file structure; browser/render validation; no guarantee of useful cross-file references |
| `.css/.scss/.sass` | `scss` → Some Sass language server | Explicitly enable; validate Tailwind syntax with actual Tailwind build |
| Tailwind classes in JSX | TS adapter for code; Tailwind LS is external/editor capability | Do not claim class semantics are provided by ordinary TS or CSS adapters |
| `.arb`, `.webmanifest` | JSON-compatible validation; Serena extension matching must be verified | ARB placeholder/locale rules and PWA manifest checks, not just JSON syntax |
| `.jsonl/.ndjson`, `.csv/.tsv` | No selected built-in semantic adapter | Per-record schema and deliberate delimiter/encoding/null handling |
| `.env`, `.env.example` | No selected semantic adapter | Parse names/placeholder contract; never index or print real secret values |
| `.sql`: PostgreSQL / DuckDB | No built-in SQL adapter selected | SQLFluff with the correct dialect plus actual DB prepare/migration validation |
| `Dockerfile`, `Containerfile`, `.dockerignore` | No built-in Docker adapter selected | Hadolint + BuildKit/build check; image build for affected configuration |
| `Caddyfile` | No built-in adapter selected | `caddy fmt`, `caddy validate` with actual modules/config context |
| Vector `.vrl` | No built-in adapter selected | Vector validation/unit tests for transforms and example events |
| XML/SVG/plist | No built-in XML adapter selected | Secure XML parser, optional XSD, SVG/browser visual check; plist native validator |
| Jinja templates, MDX | Host-language partial coverage only | Template/compiler check; do not mark full semantic support by mapping extension to HTML/Markdown |
| `justfile`, Makefile, lockfiles | Text/native-tool validation | Actual task parser; generated lockfiles updated only by owner tool |
| GraphQL / protobuf if later introduced | External adapter evaluation only | Schema compiler/lint and generated-client consistency; not part of baseline architecture |

## Binary or structured artifacts: not code LSP tasks

| Format | Agent operation | Verification |
|---|---|---|
| PDF | Extract text/layout, render pages, preserve provenance | Page review, no clipped/overlapping content, compare extraction with render |
| DOCX/PPTX | Edit through document object model, render final output | Tables, overflow, fonts, images, links, reading order |
| XLSX | Workbook-aware editing | Formula correctness, types, totals, cached/recalculated results where relevant |
| Images | Image-aware transformation/inspection | Dimensions, transparency, orientation, legibility; SVG also needs XML checks |
| Audio/video/subtitles | FFmpeg/ffprobe and appropriate transcription tools | Duration, streams, timestamps, language and synchronization |
| `.ipynb` | Notebook-aware cell processing | nbformat validation and Python checks on appropriate cells; do not symbol-rewrite notebook JSON |
| Parquet/Arrow/DuckDB files | Schema-aware data tools | Column/null/type correctness, readback, domain constraints |

## Optional external language servers

Tailwind language-server, Dockerfile language servers, XML LemMinX and SQL-oriented servers can be useful in an editor or through a tested bridge. Installing them is not enough to use them via Serena. The referenced registration guide describes an API absent from the selected stable 1.7.0 source. Thus the baseline route is CLI/editor-only tooling. An external package using that API needs a separately selected, source-pinned Serena upgrade or an audited adapter patch plus behavioral acceptance; installing it into stable 1.7.0 is not sufficient. No such adapter is bundled or certified here. [S8,A9]

## Adapter maturity

The stable source classifies `python_ty` and other alternative Python backends, `typescript_vts`, and several document adapters as experimental/secondary. This is a Serena adapter classification, not a blanket statement about the maturity of the upstream language or tool. Explicit configuration and behavior acceptance are required; Pyright remains Serena's ordinary Python default.

## Code navigation is not the product search index

Serena's selected semantic workflow uses language-server symbol information. Qdrant remains the application retrieval/search technology, not a prerequisite for this LSP connection. Do not create a redundant embedding index of the codebase merely to enable Serena-first navigation.

## Primary selection and cost

Start with the languages the active worktree actually contains. Keep the broad catalogue installed/cached where useful, but do not start every server. Python alternatives and TS alternatives overlap: select one primary. Schema servers are explicit capabilities, not proof that every schema is configured. Unknown extensions must use the validator route rather than the first server's misleading fallback.

For each enabled server record the executable, version, adapter ID, root, workspace folders, import configuration and supported operations. Verify definitions/references/rename separately. An empty diagnostics response is not proof that analysis completed or that the project is correct.


## Deployment evidence beyond the table

Use [capability evidence records](../setup/CAPABILITY-RECORD.md) for each enabled adapter. An extension matcher and a successful initialize response are separate from references, rename, diagnostics, and consumer correctness. Do not route `.arb`, `.webmanifest`, notebook JSON or embedded code to a generic language adapter and claim that this adds the missing domain semantics.

The stable Dart adapter has no Linux arm64 download entry; platform support must be assessed explicitly. The selected Codex context excludes Serena's generic file and shell tools, so their absence is expected rather than a broken MCP connection. See [configuration recipes](../setup/CONFIG-RECIPES.md).
