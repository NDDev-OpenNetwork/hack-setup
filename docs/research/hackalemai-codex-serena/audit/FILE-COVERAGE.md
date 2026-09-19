# File-by-file review coverage

Original files: 49/49 read and reviewed; no original file excluded. Pass 1 checked source/configuration facts and intended scope; pass 2 checked cross-document consistency, version boundaries and revised local invariants. Both passes were performed by the same assistant. For rule-only files, review means a design/content check, not exhaustive execution of each referenced framework.

All original byte identities are preserved below. The revised package manifest, not this table, is authoritative for revised hashes. Current static results are in [VALIDATION.md](../VALIDATION.md).

| Original file | Original SHA-256 | Pass 1 / pass 2 | Disposition / specific check |
|---|---|---|---|
| `BOOTSTRAP-PROMPT.md` | `241519a0442bca279a21fdd77a43341c554eeb55a94b2fd77070bfe945091fc3` | Reviewed / reviewed | Updated. Authority, no-product-code boundary, source pins and host execution status; updated entry instructions. |
| `MANIFEST.md` | `bc732bd37d60c630677c5dcc150bf3a234b2d82556d9b417cdcb1363fd69477b` | Reviewed / reviewed | Updated. All 48 original entries matched; regenerated for exact revised payload; excludes itself. |
| `README.md` | `0b68c8d51e7b22994d7cd4e970c9e66a33090e1a8d0473b9fe5919b919e67fa3` | Reviewed / reviewed | Updated. Claims, navigation and date boundary; explicitly distinguishes reviewed docs from working host setup. |
| `SOURCES.md` | `7c9c3c72e195bb33684ecabd93e8d1b6a850b7736856d1f93037d118da69165f` | Reviewed / reviewed | Updated. Pinned versus live sources, adapter release drift, Git blob identity; corrected external-guide classification. |
| `VALIDATION.md` | `d4fd834f627820689ed3aa75d99e4dfb09875eedaf6354c8eb1da339b3507161` | Reviewed / reviewed | Updated. Original static-only scope retained; rebuilt from actual revised validator output. |
| `repo-policy/.agents/skills/api-contract-change/SKILL.md` | `c3ff39ba15b470fc0ca256d574d52f1aff358174d52659d30b83616d81629ede` | Reviewed / reviewed | Retained. Trigger, schema source, generation and consumer verification; frontmatter valid. |
| `repo-policy/.agents/skills/evaluate-grounded-answer/SKILL.md` | `b129ab758288915651f90f9f08d8c727dcc59197cc166d181b69e5503fff751f` | Reviewed / reviewed | Retained. Evidence/citations, insufficient-data cases and domain versus schema checks; frontmatter valid. |
| `repo-policy/.agents/skills/integrate-worktree/SKILL.md` | `f316a97ad8e055a8fd687412c2ff591520489c56456166338ac3a778baa9f8d5` | Reviewed / reviewed | Retained. Ownership, source regeneration and integration identity; frontmatter valid. |
| `repo-policy/.agents/skills/serena-first-change/SKILL.md` | `842041ef004e1fdeb28db013a22a96a6498c329d882c25865eb3293a59aebadf` | Reviewed / reviewed | Updated. Available tool schema and root checks, precise edit, read-after-timeout; frontmatter valid. |
| `repo-policy/.agents/skills/setup-serena-toolchain/SKILL.md` | `0f79d960882929159e58d77e419d17aaecc1fc59eed09e51261f279a7bba4b86` | Reviewed / reviewed | Updated. Setup scope, source/version/config traps and actual host acceptance; frontmatter valid. |
| `repo-policy/.agents/skills/validate-formats-artifacts/SKILL.md` | `f6b526eb0928d89c82ab72a09071a88ba2cc89439fb74bd19b761b4834c33a80` | Reviewed / reviewed | Updated. Syntax/schema/render distinction, non-writing checks and security boundary caveat; frontmatter valid. |
| `repo-policy/.agents/skills/verify-change/SKILL.md` | `7289f6e58457a4763b22d0f3d661a24983c3e50ad5a9c7ed0031c46b3410c31a` | Reviewed / reviewed | Updated. Narrow meaningful checks, exact evidence and no claim of independent review; frontmatter valid. |
| `repo-policy/AGENTS.md` | `0381a95b3ad93434cdc20efbd4fe6cb282860b6f41d66f5dcd40fb23cd0798bc` | Reviewed / reviewed | Updated. Compact always-on router, explicit files, autonomy and source-truth; narrowed unnecessary multi-file routing. |
| `repo-policy/docs/agent-standards/AI-EDUCATION.md` | `2af738b0c267409bd4342ca0f54ee684b0db73e6139007b7bc7a5155ced1ac78` | Reviewed / reviewed | Retained. Provider capability evidence, structured versus factual checks, provenance, grading and small representative evals. |
| `repo-policy/docs/agent-standards/AUTH-INTEGRATIONS.md` | `ef6eb96c655bcacf29220836d7d74dbfecb96a63faca9262d98e41ff99540281` | Reviewed / reviewed | Retained. Provider identity, session/access checks, redirects/scopes and test-payment boundaries. |
| `repo-policy/docs/agent-standards/CONTRACTS.md` | `22177f77bc55e5cccde68a48878854565c74012ebc814dc2719669f77f5979a7` | Reviewed / reviewed | Retained. Backend source of schema, generated consumers and public protocol changes beyond LSP rename. |
| `repo-policy/docs/agent-standards/CORE.md` | `bbf4b0e4053b57a19e0e2c6958e6f97d8eb96f787585401b81baec90447d27ff` | Reviewed / reviewed | Retained. Incremental scope, no competing architecture, no instruction authority from retrieved data. |
| `repo-policy/docs/agent-standards/DATA-SEARCH.md` | `70ee6c799ccc5fc7b4bd24a751a43057588af2e5106c89fa8b79e0f18e83b768` | Reviewed / reviewed | Retained. Postgres/Qdrant/RustFS authority, access filtering, index identity, idempotency and analytical types. |
| `repo-policy/docs/agent-standards/DELIVERY.md` | `1305a0aeadc57fae9eb1f782b9fa65df68d0baa7d539b99398389b9e7220b20a` | Reviewed / reviewed | Retained. Actual demo flow and honest recording/claims; no invented live results. |
| `repo-policy/docs/agent-standards/DEPENDENCIES.md` | `ebe8c0399a99a618182cc8bfa5bb93fba70ba0f5999f6476a6087c6426cb3c8b` | Reviewed / reviewed | Updated. Isolated graphs, no peer forcing, historical cutoff and source versus resolved artifact distinction. |
| `repo-policy/docs/agent-standards/DOCUMENTS.md` | `4df3ac0a45d447031832c33749e05b07ff66f0161ac722f093ae25dd973a9645` | Reviewed / reviewed | Retained. Original data/provenance, format-aware changes, rendering and numerical/formula correctness. |
| `repo-policy/docs/agent-standards/EDUCATIONAL-MODULES.md` | `652adc51e17f4a761eab871084983bf6ce7291d9c982dd29cb90e166fabca3ad` | Reviewed / reviewed | Updated. Conditional module behavior; corrected Pyodide worker versus app security isolation. |
| `repo-policy/docs/agent-standards/FORMATS.md` | `794e9606d8cc1c783694e71370df91ba29ed7db2436d13a4ebe4e823cf91e4aa` | Reviewed / reviewed | Updated. Consumer-specific schemas, secure parsing, duplicate keys, no accidental rewrites; correct non-LSP routes. |
| `repo-policy/docs/agent-standards/INDEX.md` | `55a2f6626cafe0700f846bccd1b8ec0ba67df186f2a33f05093eff6a203a920b` | Reviewed / reviewed | Retained. Behavior-and-extension routing, relevant consumers, bounded instruction loading. |
| `repo-policy/docs/agent-standards/INFRA.md` | `53c3e9e2f28dbb28c8bb0acb7ccd83c09a124a4bc17fe290913533887164db42` | Reviewed / reviewed | Retained. Consumer config validity, private data/service exposure, bounded resources and correlation without secret logging. |
| `repo-policy/docs/agent-standards/MULTIAGENT.md` | `364e9526f9e48f81e8287d5da7ec39659feab2fcef35fc5cab88796f3c638d69` | Reviewed / reviewed | Updated. Separate writers/worktrees/processes, shared contract/lock/migration ownership and local config merge semantics. |
| `repo-policy/docs/agent-standards/NATIVE-MOBILE.md` | `9c4af221265df65561da4d24784c99b176f4c5efc6a1bcc1bbc78ee3940fda1e` | Reviewed / reviewed | Retained. Bundled Flutter/Dart, native target toolchains, safe IPC/FFI, generated code ownership. |
| `repo-policy/docs/agent-standards/PYTHON.md` | `acccfc3176a8e0a8dc8de5414ae298ea2583360c155ac07b9937dad5cb019222` | Reviewed / reviewed | Retained. Async resource lifecycle, separate AsyncSession ownership, bounded I/O and job idempotency. |
| `repo-policy/docs/agent-standards/QUALITY.md` | `b65e68d8adcea3752a3fe305a4c174b6dd3f4ce41553f343aca9d2339a070dfd` | Reviewed / reviewed | Updated. Risk-proportional check ladder, deterministic regression evidence, non-writing checks and exact tree identity. |
| `repo-policy/docs/agent-standards/SERENA-WORKFLOW.md` | `b7ebed54180cc06e6e3e0928cf6d8f918194fb975980314c4a4d7cbbd7677916` | Reviewed / reviewed | Updated. Semantic-first with valid fallback, current bodies/references, missing capabilities and timed-out mutation handling. |
| `repo-policy/docs/agent-standards/WEB.md` | `5773f6ee3ceed072f31ea856989084c5482e0137063b93bf85139847e04e7af7` | Reviewed / reviewed | Retained. Server/local state boundary, React effects, accessible localized UI, browser/PWA behavior beyond TS. |
| `research/CODEX-CAPABILITIES.md` | `28c1e6a62bc87dada57586837f807b6e6404aec96536ee2a4528c328c5790708` | Reviewed / reviewed | Updated. AGENTS/skills/exec-policy/MCP separation, project-only fallback scope, optional hooks and trust distinction; live-doc evidence is labelled in audit ledger. |
| `research/COMPATIBILITY.md` | `036c55fa73ab1d93e8a82d70f7e24a4054d3cb98b722a0bc9b735f7f88ece19e` | Reviewed / reviewed | Updated. TS/Dart/ty compatibility boundaries, version-specific hooks and registry gaps; no runtime certification. |
| `research/LSP-MATRIX.md` | `d32f008d4c905300250e46451fc427bfdc189ecce8d84325be0ec99076379f6a` | Reviewed / reviewed | Updated. Adapter IDs, partial format capabilities, secondary maturity and external API availability; platform/context gaps added. |
| `research/TECHNOLOGY-COVERAGE.md` | `f487f633f3ced0cd9a6764237653fc6da43670ab7d0d8c555d5ecd9b4f6df810` | Reviewed / reviewed | Retained. Every agreed technology group routed to existing policies; catalogue remains distinct from install closure. |
| `scoped-templates/API-AGENTS.md` | `bd0b2d69013bd3c83fa33c297ede6e6a71d5c5d89c97ee9b6ff0627b394f9fbe` | Reviewed / reviewed | Retained. Existing-directory/path adaptation, root authority and small local instruction scope; no product directory scaffold. |
| `scoped-templates/DOCS-AGENTS.md` | `19c98d2e8bb7d65e167076d158c301edb684f456938666bcf9d54b3f1af00a30` | Reviewed / reviewed | Retained. Existing-directory/path adaptation, root authority and small local instruction scope; no product directory scaffold. |
| `scoped-templates/INFRA-AGENTS.md` | `cbd2bdd891c645835c84b07342d62af207777ebc401cea6d09f4f1dd9cb0564d` | Reviewed / reviewed | Retained. Existing-directory/path adaptation, root authority and small local instruction scope; no product directory scaffold. |
| `scoped-templates/MOBILE-AGENTS.md` | `f133307cbe527863cba78eef3076a1fa5302125d4ab44d98ac7373dfc4174293` | Reviewed / reviewed | Retained. Existing-directory/path adaptation, root authority and small local instruction scope; no product directory scaffold. |
| `scoped-templates/NATIVE-AGENTS.md` | `ac541baad5f73ced9e51210e9d7f45c71b9b4597dfa52a94c4f8147de4aac088` | Reviewed / reviewed | Retained. Existing-directory/path adaptation, root authority and small local instruction scope; no product directory scaffold. |
| `scoped-templates/README.md` | `db54bc3c54434cb8d37cc35dc504e9881f02cb624a08c7eda9fdebf3874933ce` | Reviewed / reviewed | Retained. Existing-directory/path adaptation, root authority and small local instruction scope; no product directory scaffold. |
| `scoped-templates/WEB-AGENTS.md` | `7ef85995b91a87a01b81002e57fc66f2df12f7980167ebffcf71e7f2c2fa5d20` | Reviewed / reviewed | Retained. Existing-directory/path adaptation, root authority and small local instruction scope; no product directory scaffold. |
| `setup/ACCEPTANCE.md` | `b8ea0197d034ea3cfe268abfc1e03c8caa416f1ea265bc8c1686fb31163273a8` | Reviewed / reviewed | Updated. Real operations and negative controls, Unicode/root visibility, new config traps; not per-edit gates. |
| `setup/CONFIG-RECIPES.md` | `bbc93762eb2e842c641316006c0efa998900ad5cb470b197cddbce199ef61e8d` | Reviewed / reviewed | Updated. Pinned loader behavior, base modes scope, local shallow merge, actual timeout budgets and index scope. |
| `setup/GLOBAL-AGENTS-SNIPPET.md` | `784a59b33aef560b3933bc5f346d3bfda96dfbbd0380753681b2fdceda7f6b1e` | Reviewed / reviewed | Retained. Preserve existing global guidance; no broad overwrite or implicit Markdown loading. |
| `setup/HOOKS-AND-EXEC-POLICY.md` | `debede4d6ba0ba9125c7b9a75889fa6af0a6a4c4b51e134bbf1b377e8d0be27c` | Reviewed / reviewed | Updated. Optional ownership, hash trust, actual clamp, no deny/reset, lifecycle versus per-turn events. |
| `setup/HOST-REPORT-TEMPLATE.md` | `c5163b5ef59aebf19d0b29a7d8c5e3a0db286dd73eeb72201aec25a50126d1d4` | Reviewed / reviewed | Updated. NOT-EXECUTED status, effective tool/config/root/dirty identity and no invented results. |
| `setup/INSTALLATION.md` | `ba830d248962159c3dae2f3d31d7532d35591c0e89aa7174ea569506fe77f9a3` | Reviewed / reviewed | Updated. Interpreter identity, isolated dependencies, host paths, historical selection and idempotent warm-up. |
| `setup/LOAD-AND-DEPLOY-MAP.md` | `1212ad965dc02c9eaa6bf01e8f300398c50b9259f6002d73291bf4daa8d2b773` | Reviewed / reviewed | Updated. Pre-event boundaries, nonduplicate installation and portable versus local ownership. |

## New revision files

New audit/setup documents were also reviewed for local link consistency, factual scope, template placeholders and absence of claimed host execution. The included validator is a read-only preparation utility supplied inside Markdown, not application implementation. The new material does not become always-loaded product context.

| New file | Review scope |
|---|---|
| `CHANGES.md` | Evidence boundary, source identity or setup procedure; static checks applied where relevant |
| `audit/AUDIT-REPORT.md` | Evidence boundary, source identity or setup procedure; static checks applied where relevant |
| `audit/SOURCE-EVIDENCE.md` | Evidence boundary, source identity or setup procedure; static checks applied where relevant |
| `audit/VALIDATOR.md` | Evidence boundary, source identity or setup procedure; static checks applied where relevant |
| `setup/CAPABILITY-RECORD.md` | Evidence boundary, source identity or setup procedure; static checks applied where relevant |
| `setup/VERSION-RESOLUTION.md` | Evidence boundary, source identity or setup procedure; static checks applied where relevant |
| `audit/FILE-COVERAGE.md` | Original inventory and evidence identity; no claim of independent reviewer or host execution |
