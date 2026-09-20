---
name: serena-workflow
description: Work through the serena MCP server for semantic code navigation, edits and durable memories. Use when moving through a codebase by symbol, persisting findings across sessions, or deciding between serena tools and shell reads.
---

Serena runs as `uvx serena-agent==1.7.0` (pin: `mcp.serena`) with the
built-in `codex` context. The pinned release has no `--project-from-cwd`,
so a session starts with no active project.

Boot sequence:

1. Call `activate_project` with the repository root path once per
   session. The project keeps its `.serena/` directory — `project.yml`,
   `memories/`, `plans/` — which stays the source of truth on disk.
2. Read `read_memory`/`list_memories` for prior session state before
   planning. Write outcomes back with `write_memory`; the files are
   plain markdown and are committed.

Tool selection:

- `get_symbols_overview` + `find_symbol`/`find_referencing_symbols` beat
  reading whole files when the task is about specific definitions.
- Edit through `replace_symbol_body`, `insert_after_symbol`,
  `insert_before_symbol`; use `replace_content` (regex) only when a
  symbol-level edit does not fit.
- `search_for_pattern`/`read_file`/`execute_shell_command` exist but
  plain shell tools are usually faster for broad text search.
- `think_about_*` tools structure the reasoning audit trail; they do not
  replace real verification.

Notes:

- The server also opens a local dashboard on a free port; the browser
  is not auto-opened (`--open-web-dashboard false` in the pin).
- Do not start a second serena for the same project in parallel
  sessions; the `.serena` cache serialises per project.
