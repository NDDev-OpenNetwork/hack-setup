# Text formats, schemas and formatter ownership

## General

Use UTF-8, consistent LF and a final newline for authored text unless an external format specifically requires otherwise. Preserve user content and intentional whitespace where semantically significant. Detect a file's actual consumer before deciding its syntax and schema. Secrets and binary objects are not ordinary text-search targets.

| Family | Formatting owner | Additional validation |
|---|---|---|
| JS/TS/TSX/JSX/JSON in configured scope | Biome | Native TS compiler / consumer schema |
| Python | Ruff | ty / application behavior |
| Rust | rustfmt | Cargo |
| Go | gofmt | Go build/vet/test as relevant |
| Dart | dart format from Flutter SDK | Flutter analyzer/build |
| TOML | Taplo | Consumer schema and CLI |
| Markdown/YAML/HTML/CSS where not otherwise owned | Prettier, narrowly scoped | Markdownlint/schema/browser or style build |
| Shell | shfmt | ShellCheck and actual shell syntax |
| SQL | SQLFluff with explicit dialect | Actual database/migration semantics |

Do not let two formatters repeatedly rewrite the same files. Generated sources and lockfiles are owned by their generators; formatter coverage must respect this. Configure Tailwind-aware CSS handling for the installed syntax rather than disabling all CSS validation.

## JSON, JSONC, JSONL, ARB

Strict JSON has no comments or trailing commas. JSONC is only allowed when the actual consumer accepts it. JSONL is a sequence of individually validated records, not one ordinary JSON document. Validate IDs/numbers without losing precision, reject malformed record boundaries and define missing/null semantics.

Use the correct versioned schema for config/contract files. A valid JSON parse is not schema validity. ARB resources additionally require locale and placeholder metadata consistency; webmanifest files require the intended PWA fields and asset paths. Do not assume Serena's JSON adapter matches these extensions automatically.

## YAML and TOML

Reject accidental duplicate keys and malformed indentation. Quote ambiguous strings where the consumer/version could reinterpret them. Do not perform unrestricted YAML object construction on untrusted input. Treat schema version and actual native consumer as part of validation.

Use `language_servers` for the inspected Serena release, not a remembered legacy key. Preserve Codex TOML table structure and do not overwrite model/provider/trust settings while adding MCP. `pyproject.toml`, Cargo.toml and Codex config share TOML syntax, not a common schema.

## Markdown, rules and skills

Use descriptive headings, complete local links, valid fenced blocks and meaningful examples. Separate verified facts, choices and pending checks. Avoid duplicated giant rule text across global AGENTS, root AGENTS, nested files, skills and memories. Keep the root instruction chain small.

Skill frontmatter must parse, its name must match its intended identity and its description must state the trigger. `globs` in an ordinary Markdown file is not native Codex rule enforcement. Do not print invented command output as if it were evidence. Render mathematical notation/diagrams when the output will be shown to judges or users.

## SQL, XML, shell and templates

Choose PostgreSQL versus DuckDB dialect explicitly. Use parameterized SQL in application code. Alembic owns schema migrations; SQL formatting does not establish migration safety.

Disable external entity/network expansion when parsing untrusted XML unless a narrowly authorized use requires it. SVG must also be checked for unsafe active/external content and visually rendered. Validate plist through the native platform where relevant.

Declare Bash versus POSIX sh versus zsh. Quote expansions and handle failures/cancellation deliberately. ShellCheck/Bash LS do not certify arbitrary zsh. Do not paste heredoc data into executable shell positions.

Templates need their actual Jinja/MDX/compiler check; HTML/Markdown navigation is only partial coverage. Keep template escaping and data/instruction separation explicit. For Caddyfile, VRL, Dockerfile, justfile and environment files use the native consumer rather than a fabricated universal LSP.


## Checks must not silently rewrite

Choose explicit non-writing checks for validation. Run formatting/fixing as a separate intentional step and inspect the result. Reject duplicate JSON/YAML keys when the project contract prohibits them; a parser that silently keeps the last value is not that check. YAML syntax, JSON Schema validity and native consumer acceptance are three different results.

Instruction Markdown has no native permission to execute fenced commands. Treat snippets as documented examples until the task authorizes execution and placeholders and version-specific arguments have been resolved.
