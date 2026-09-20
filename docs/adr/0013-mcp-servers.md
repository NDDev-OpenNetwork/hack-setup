# 13. Six MCP servers wired through project config, skills via plugin

- Status: accepted
- Date: 2026-09-21
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The workflow needs MCP tooling: serena for semantic code work and
durable memories, shadcn for component registries, and research surfaces
for versioned docs, real-world code patterns, repo comprehension and
general web search. Two vehicles exist: plugin `mcp.json` (bundled with
a plugin) and project `.codex/config.toml` `[mcp_servers.*]` (loaded for
trusted projects).

## Decision Outcome

All six servers are declared once in `build/stack-pin.json`
`registered.mcp_servers` and projected into `.codex/config.toml`
`[mcp_servers.*]`. `scripts/check_codex_setup.py` enforces
pin == config. `plugins/hack-agent-mcp` carries only skills
(`mcp-usage`, `serena-workflow`, `research-workflow`,
`component-workflow`) — the same shape as `hack-agent-lsp`.

Servers: `serena` (stdio `uvx serena-agent==1.7.0`, `codex` context),
`shadcn` (stdio `bunx shadcn@4.21.0 mcp`), `context7`, `grep`,
`deepwiki`, `keenable` (remote streamable-HTTP, keyless).
`CONTEXT7_API_KEY` / `KEENABLE_API_KEY` are optional env-var references —
never literals in the repo.

## Why not plugin `mcp.json`

Read of `codex-rs` at the pinned commit (`be2951ea`): the portable Agent
Plugins MCP schema forces stdio `cwd` inside the plugin root, has no
timeout fields, and strips client-owned headers. Serena's project
detection and shadcn's `components.json` lookup both need the session
cwd, and env-referenced secrets are not expressible. Project config is
the correct vehicle for wiring; the plugin is the correct vehicle for
skills.

## Consequences

- `./setup` pre-warms the stdio servers (uvx/bunx caches) in module 30,
  so the first MCP spawn is fast.
- `bunx`/`uvx` links are now guaranteed on all three OS — the POSIX
  module previously skipped `bunx` (the zip ships only `bun`) and `uvx`
  (early-return paths).
- serena 1.7.0 predates `--project-from-cwd`; sessions call
  `activate_project` once. `.serena/` stays file-based SoT.
- Adding a seventh server = edit `registered.mcp_servers` + config +
  a checker row; the pin rejects literal credential fields.
