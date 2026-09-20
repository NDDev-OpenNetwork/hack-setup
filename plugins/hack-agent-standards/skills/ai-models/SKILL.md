---
name: ai-models
description: Load AI.md. Use when changing the Bifrost gateway client, openai 3.x, embeddings, FastEmbed, CLIProxyAPI, STT, gpu_ml, or structured output checks.
---

# ai-models

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Open CORE.md, AI.md, pin ai.* / environments.gpu_ml. DATA for Qdrant upsert. INFRA gpu profile for query-time HTTP encode. CONTRACTS for SSE names.
4. No litellm in any env; the API calls the Bifrost gateway (`environments.bifrost`) via `openai` 3.x `base_url`. Product dense vectors are gpu_ml, not gateway `embeddings.create`.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:ai-models` (plugin). Repo alias
`$apply-stack-rule` still opens INDEX when the layer is unclear.

