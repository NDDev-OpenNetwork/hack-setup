---
name: quality-proof
description: Load QUALITY.md. Use when proving a change, just check/test, observability, OpenObserve, Vector, OTel, or required_gates after product trees exist.
---

# quality-proof

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Open CORE.md then QUALITY.md. Hop-split: logs → Vector →
   OpenObserve; traces/metrics OTLP → OpenObserve. INFRA when the
   slice is Compose/Caddy `/otel` or Vector. Setup proof is
   `just check` / `just test`. Product `required_gates` wait for trees.
4. Do not invent a CI fleet. Do not add generate-clients in this
   setup repo. No Collector as the log hop.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:quality-proof` (plugin). Repo alias
`$apply-stack-rule` still opens INDEX when the layer is unclear.

