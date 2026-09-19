# Formats

Parse with the real consumer. A file that parses is not automatically valid.

## JSON

Used now: `build/*.json`, `package.json`, plugin and marketplace schemas.
Product later: OpenAPI, PWA manifest.

- UTF-8. No comments unless the consumer is JSONC and that consumer is pinned.
- JSONC and JSONL are not pinned. Do not require them.
- Plugin root must stay Agent Plugins 1.0.0 portable keys only.
- `package.json` `packageManager` must be `bun@1.4.2`.

## YAML

Used now: `.serena/project.yml`. Product later: Vector.

- Quote globs that start with `*`.
- Duplicate keys are invalid. Do not “merge” them by last-wins guesswork.
- Vector YAML also needs `infra.md`.

## TOML

Used now: `.codex/config.toml`, `bunfig.toml`, `install/catalog.toml`, `mise.toml`.
Product later: `pyproject.toml`, `Cargo.toml`.

- Do not mix `default_permissions` with `sandbox_mode`. Session law is
  `sandbox_mode` only. Do not set `[sandbox_workspace_write]`.
- `approval_policy = "untrusted"` is retired.
- Project session is YOLO (`registered.session`, ADR 0006):
  `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`,
  `allow_login_shell = true`, `web_search = "live"`. `--full-auto` is
  deprecated workspace-write, not this.
- Do not add project `.codex/agents/*.toml`. Spawn tools are off.
- Do not add project `.codex/rules/*.rules`. Execpolicy `*.rules` are
  not turned off by YOLO. `approval never` + a `prompt` rule becomes a
  hard deny. Skip user/project `.rules` only with
  `codex exec --ignore-rules` (not a `config.toml` key; TUI 0.155.1 has
  no `--ignore-rules`).
- `web_search` is top-level, not `features.web_search*`. Do not enable
  `features.network_proxy`.
- `.codex/config.toml` is a projection of `build/stack-pin.json`
  `registered.session`, `models`, and `registered.features`. Do not
  invent a number that is not in the pin.
- Models/context: ADR 0007. `model = "gpt-6-astra"`,
  `model_reasoning_effort = "xhigh"`,
  `model_context_window = 872_000`,
  `model_auto_compact_token_limit = 700_000`,
  `[profiles.sol]` = `gpt-5.6-sol` + the same window/effort.
  `[agents] enabled = false`. `features.multi_agent` and
  `features.multi_agent_v2` are false.
- Catalog `schema_version` is 1. `entry` is `./setup`.

## Markdown

Used now: `AGENTS.md`, ADRs 0001–0007, this catalogue, skills.

- Root `AGENTS.md` stays a router. Do not paste this catalogue into it.
- Fences must close. Local links in `INDEX.md` must resolve.
- Product lesson Markdown is rendered with `react-markdown` `10.1.0` + `remark-gfm` `4.0.1`.

## SQL

No `.sql` in this repo yet.

- OLTP dialect is PostgreSQL `18.6` via Alembic. Analytics dialect is DuckDB `1.5.5`.
- Do not run analytics SQL against Postgres SoT tables as a second writer.
- SQLFluff is not pinned.

## Env

- No committed `.env` or secrets. Names only in a future `.env.example`.
- API settings are pydantic-settings `2.15.0`.

## Shell

Used now: `./setup`, `install/**/*.sh`, `justfile`.

- Bootstrap is bash. `install/env.sh` is sourced from bash or zsh.
- POSIX `sh` / dash must fail closed on `env.sh`.
- Do not create a root file named `install`.
- Do not add a Makefile. Commands live in `justfile`.
- shfmt / ShellCheck are not pinned gates.
