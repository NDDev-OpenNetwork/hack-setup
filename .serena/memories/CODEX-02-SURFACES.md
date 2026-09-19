<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 53d8d31 docs: accept ADR 0008 and retarget routers to the plugin
Scope: .agents/, .codex/, plugins/saint-tibo/, plugins/hack-agent-standards/, AGENTS.md, docs/adr/0005-codex-rule-catalogue.md, docs/adr/0008-agent-standards-plugin.md
Area: CODEX
-->

# CODEX-02-SURFACES

## Purpose

Map native Codex 0.155.1 project surfaces in this repo.

## Source Of Truth

- Repo skills: `.agents/skills/{repo-orientation,quality-gate,one-repo-workflow,apply-stack-rule}/SKILL.md`
- Frames: `plugins/hack-agent-standards/standards/` (on-demand; Codex does not auto-load it). ADR 0005 + ADR 0008.
- Marketplace: `.agents/plugins/marketplace.json` name `saint-tibo`, plugins `./plugins/saint-tibo` then `./plugins/hack-agent-standards`
- Team plugin: `plugins/saint-tibo/plugin.json` portable Agent Plugins 1.0.0
- Team plugin skill: `plugins/saint-tibo/skills/saint-tibo/SKILL.md` name `saint-tibo`
- Standards plugin: `plugins/hack-agent-standards/plugin.json` portable Agent Plugins 1.0.0
- Standards plugin skill: `plugins/hack-agent-standards/skills/apply-agent-standard/SKILL.md`
- Config: `.codex/config.toml` is a projection of pin `registered.session` + `models` + `registered.features` (`gpt-6-astra` + `xhigh`, window `872000` / compact `700000`, `[profiles.sol]`, `agents.enabled=false`)

## Current Behavior

Repo skills load without plugin install. Two plugins are enabled after trust: `saint-tibo@saint-tibo` and `hack-agent-standards@saint-tibo`. Existing frames are INDEX, CORE, QUALITY. Planned area names are not markdown links until the file exists. `./setup` does not run `codex plugin marketplace add`.

## Contracts And Data

- Skill frontmatter requires `name` and `description`. Directory name must match `name`.
- Portable plugin root may not set `skills`, `interface`, `apps`, `hooks`, or `mcpServers`.
- Marketplace `source.path` is repo-root relative and starts with `./`.
- Session law is `build/stack-pin.json` `registered.session` and ADR 0006: `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, `allow_login_shell = true`, `web_search = "live"`. Do not set `default_permissions` or `[sandbox_workspace_write]`.
- `approval_policy = "untrusted"` is retired. `web_search` is top-level, not `features.web_search*`. Do not enable `features.network_proxy`.
- Models: primary `gpt-6-astra`, secondary `gpt-5.6-sol` via `--profile sol`, both `xhigh`. Context `872000` / compact `700000`. Usable `/status` `828400`. Tibo 1M/900k is documented but clamped on 0.155.1.
- `agents.enabled = false`. `features.multi_agent` and `features.multi_agent_v2` are false. Do not spawn Codex subagents.
- Do not add `.codex/agents/*.toml`.
- Do not add project `.codex/rules/*.rules`. Execpolicy `~/.codex/rules` still loads under YOLO. `--yolo` does not imply `--ignore-rules`. The ignore flag is `codex exec --ignore-rules` only and is not a `config.toml` key. TUI 0.155.1 has no `--ignore-rules`.
- `$CODEX_HOME/skills` is a deprecated user skill location.
- Do not add `plugins/hack-agent-standards/standards/*` to `project_doc_fallback_filenames`.
- `docs/rules/` and `docs/agent-standards/` are stale and must stay deleted.

## Invariants

- No skill-name collision between `.agents/skills`, `plugins/saint-tibo/skills`, and `plugins/hack-agent-standards/skills`.
- Do not copy repo skill names into either plugin.

## Change Rules

- Author new team workflows as `.agents/skills/<kebab-name>/SKILL.md`.
- Author the next area frame in `plugins/hack-agent-standards/standards/` and link it from INDEX only after the file exists.
- After surface edits run `just check`.

## Verification

- `just check`
