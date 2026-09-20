# Formats

Universe: `build/stack-pin.json` `quality.biome`, `quality.just`,
`backend.pydantic`, `backend.pydantic_settings`, `backend.alembic`,
`backend.fastapi`, `deploy.compose`, `deploy.vector`. Pin files
themselves are JSON. Caddy is a Caddyfile (INFRA).

Unless the owner said otherwise this turn.

This file is how authored text is cut. The consumer is the
parser. A second formatter fleet is not required. Secrets
never appear in examples. Do not create product trees only
to hold this file.

A Vector YAML file also needs INFRA. A Pydantic model on
the wire also needs PYTHON and CONTRACTS.

## Default move

1. Name the consumer. Then write that consumer's syntax.
2. Parse with that consumer. A valid parse is not schema
   validity.
3. Check does not rewrite. Format is a separate intentional
   write owned by the consumer (Biome only for JS/TS JSON
   in `web/`).
4. Examples use placeholders. Never real tokens or DSNs.

## Pattern

UTF-8. LF. Final newline. No BOM on JSON.

Do not add Prettier, Taplo, SQLFluff, shfmt, or
markdownlint as required.

| Owner | Files | Write | Non-write check |
| --- | --- | --- | --- |
| FastAPI dump | `contracts/openapi.json` | dump `app.openapi()` (CONTRACTS) | tmp dump + `cmp` |
| Client regen | generated TS + Dart | write recipe `generate-clients` (when `api/` exists; not in this repo) | `tsc` / `dart analyze` on committed clients |
| `json` stdlib | pin, plugin, marketplace | author | `json.loads` |
| Biome | JS/TS JSON in `web/` | `biome check --write` | `biome check` |
| Compose | `compose.yaml` | author | `docker compose config -q` |
| Vector | `vector.yaml` | author | `vector validate` |
| Caddy | `Caddyfile` | `caddy fmt --overwrite` | `caddy validate` |
| `tomllib` | `.codex/config.toml` | author | `tomllib.loads` |
| Alembic | `api/alembic/` | `alembic revision` | `alembic check` |
| just | `justfile` | `just --fmt` | `just --fmt --check` |
| Ruff | `.py` | `ruff format` | `ruff check` (no `--fix`) |

`just --fmt --check` and `caddy fmt` are optional until
QUALITY names them in `just check`.

### JSON

Strict JSON. No comments. No trailing commas. `json.loads`
keeps the last duplicate key — that is not a uniqueness
check. OpenAPI: dump `app.openapi()` only (CONTRACTS). No
YAML twin. Pin and OpenAPI never JSONC. Do not Biome-rewrite
them. `SecretStr` dumps as `"**********"`.

### YAML

Compose: `compose.yaml`. `version:` is obsolete. Duplicate
keys error. Secrets: top-level `secrets:` → `/run/secrets`.
Never a password literal. Project `.env` is interpolation;
service `env_file` is container env.

Vector: YAML recommended (`vector.yaml`). Do not twin as
TOML/JSON. Secrets: `SECRET[backend.key]` or `${NAME}`.

Untrusted YAML: no unrestricted object construction.

### Caddyfile

Native config is JSON. Humans write a `Caddyfile`. YAML is
an optional xcaddy adapter. Do not author Caddy as YAML.
`caddy validate` is the proof. INFRA owns the routes.

### TOML

Pin is JSON. Do not twin it as TOML. `.codex/config.toml`:
Codex `toml` crate; check with `tomllib` (read-only).
`install/catalog.toml`, `bunfig.toml`, `mise.toml`: that
tool is the consumer. Do not add Taplo.

### Markdown

UTF-8, LF, final newline. Fences are examples until the
owner authorizes execution. Skill frontmatter must parse;
`name` matches the directory. Product render: `react-markdown`
+ `remark-gfm`. Linked markdown is not an import (INDEX).

### SQL

Alembic owns schema SQL. `alembic check` is the non-writing
proof. App queries: bound parameters (PYTHON). DuckDB SQL
only in a worker (DATA). A formatted revision is not a safe
migration.

### Env

pydantic-settings + python-dotenv. `extra='forbid'` on
dotenv. Process env extras are ignored. `secrets_dir` is
lowest precedence.

| File | Commit | Contents |
| --- | --- | --- |
| `.env` | no | real values |
| `.env.example` | yes | names + empty / `changeme` |
| Compose `secrets:` | yes | path / env name |

just dotenv is opt-in. This `justfile` does not enable it.

### Shell

`justfile` sets `shell := ["bash", "-eu", "-o", "pipefail",
"-c"]`. `install/bootstrap.sh` is POSIX `sh` + `set -eu`.
Quote expansions. No shfmt as required.

## Done

- The consumer parsed the file. Schema / native check ran
  when that consumer exists. Check did not write.
- Pin stayed JSON. OpenAPI stayed one JSON dump.
- Caddy stayed a Caddyfile. Not YAML.
- Examples have no live secrets.
- No second formatter fleet appeared.

## Repair

- Second formatter rewriting the same files: remove it.
- Pin / OpenAPI pretty-printed by Biome: redump from the
  owner.
- Caddy authored as YAML: rewrite as Caddyfile.
- Secret in an example or committed `.env`: rotate, strip.
- Owner wants Prettier / Taplo / SQLFluff as default:
  update the pin and INDEX “Not yet”, then this file.
