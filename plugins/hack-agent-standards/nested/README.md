# Nested AGENTS.md templates

Copy a file from this directory into a product tree **in the same
change that creates that tree**. Do not create empty `web/`, `api/`,
`mobile/`, `desktop/`, `telegram/`, or `infra/` only to hold a template.

Codex 0.155.1 walks project root → cwd and loads at most one of
`AGENTS.override.md` / `AGENTS.md` per directory (32 KiB combined).
Root `AGENTS.md` stays the router. These files are directory-local.

| Template | Drop as |
| --- | --- |
| `web.md` | `web/AGENTS.md` |
| `api.md` | `api/AGENTS.md` |
| `mobile.md` | `mobile/AGENTS.md` |
| `desktop.md` | `desktop/AGENTS.md` |
| `telegram.md` | `telegram/AGENTS.md` |
| `infra.md` | `infra/AGENTS.md` |

Frames: `$hack-agent-standards:<skill>` plus `standards/*.md`.
Versions: `build/stack-pin.json`.
