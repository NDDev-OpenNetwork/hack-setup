<!-- Memory Metadata
Last updated: 2026-09-19
Last commit: b0d6d67 docs: document one-command clone-and-setup flow
Scope: .agents/, .codex/, plugins/saint-tibo/, AGENTS.md
Area: CODEX
-->

# CODEX-02-SURFACES

## Purpose

Map native Codex 0.155.1 project surfaces in this repo.

## Source Of Truth

- Repo skills: `.agents/skills/{repo-orientation,quality-gate,one-repo-workflow}/SKILL.md`
- Marketplace: `.agents/plugins/marketplace.json` name `saint-tibo`, path `./plugins/saint-tibo`
- Plugin: `plugins/saint-tibo/plugin.json` portable Agent Plugins 1.0.0
- Plugin skill: `plugins/saint-tibo/skills/saint-tibo/SKILL.md` name `saint-tibo`
- Config: `.codex/config.toml`
- Custom agents: `.codex/agents/{mapper,reviewer,implementer}.toml`

## Current Behavior

Repo skills are the workflow source of truth and load without plugin install. The plugin is the installable unit and has one uniquely named skill. Project `.codex/` loads only after the project is trusted. Plugin enable key is `saint-tibo@saint-tibo`.

## Contracts And Data

- Skill frontmatter requires `name` and `description`.
- Portable plugin root may not set `skills`, `interface`, `apps`, `hooks`, or `mcpServers`.
- Marketplace `source.path` is repo-root relative and starts with `./`.
- Config uses `sandbox_mode = "workspace-write"` and must not also set `default_permissions`.
- `approval_policy = "untrusted"` is retired. `web_search` is top-level, not `features.web_search*`.
- `$CODEX_HOME/skills` is a deprecated user skill location.

## Invariants

- No skill-name collision between `.agents/skills` and `plugins/saint-tibo/skills`.
- Do not copy repo skill names into the plugin.

## Change Rules

- Author new team workflows as `.agents/skills/<kebab-name>/SKILL.md`.
- Keep plugin skills uniquely named.
- After surface edits run `python3 scripts/check_codex_setup.py`.

## Verification

- `python3 scripts/check_codex_setup.py`
