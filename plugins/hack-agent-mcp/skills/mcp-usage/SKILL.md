---
name: mcp-usage
description: Route between the six pinned MCP servers and verify they are alive. Use when unsure which MCP tool fits, when a server looks dead, or when wiring/limits need explaining.
---

Six MCP servers are wired in `.codex/config.toml` `[mcp_servers.*]`,
projected from `build/stack-pin.json` `registered.mcp_servers`. Do not
add a seventh server without a pin entry. Servers load only after the
project is trusted.

| Server | Transport | Use it for |
| --- | --- | --- |
| `serena` | stdio `uvx serena-agent==1.7.0` | Semantic code tools + durable `.serena/` memories |
| `shadcn` | stdio `bunx shadcn@4.21.0 mcp` | Component registry search inside the product repo |
| `context7` | remote `mcp.context7.com/mcp` | Versioned library documentation |
| `grep` | remote `mcp.grep.app` | Real code usage across public GitHub |
| `deepwiki` | remote `mcp.deepwiki.com/mcp` | Repo architecture Q&A (public repos) |
| `keenable` | remote `api.keenable.ai/mcp` | General web search + page fetch |

Verify and debug:

```bash
codex mcp list          # all six should read enabled
codex mcp get serena    # per-server detail
```

- stdio servers need `uvx`/`bunx` on PATH — source `install/env.sh`
  (POSIX) or `. install/env.ps1` (Windows) before launching codex.
- First serena spawn is warm: `./setup` pre-caches `serena-agent` via uvx.
- Keys are optional upgrades, never literals in config:
  `CONTEXT7_API_KEY` (bearer) and `KEENABLE_API_KEY` (X-API-Key header)
  are read from the environment when set.
- Workflow details live in the sibling skills: `serena-workflow`,
  `research-workflow`, `component-workflow`.
