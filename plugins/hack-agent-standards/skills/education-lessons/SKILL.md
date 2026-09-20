---
name: education-lessons
description: Load EDUCATION.md. Use when changing Tiptap, Yjs, Hocuspocus, KaTeX, FSRS, Pyodide, student executor, LiveKit classroom, echarts, or OR-Tools.
---

# education-lessons

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Open CORE.md, EDUCATION.md. AUTH for
   `/v1/auth/collab/authenticate` and `/v1/auth/livekit/token`.
   INFRA collab/live. WEB for chrome. PYTHON+Taskiq for OR-Tools.
   DATA redis-durable `yjs:` never cache.
4. Executor: no egress, no docker.sock, no API secrets. Yjs persist
   through the API, not a Node DSN. Browser LiveKit edge is Cloud
   unless the owner names self-host. Collab onAuthenticate is
   Compose DNS, not public Caddy `/v1`.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:education-lessons` (plugin). Repo alias
`$apply-stack-rule` still opens INDEX when the layer is unclear.

