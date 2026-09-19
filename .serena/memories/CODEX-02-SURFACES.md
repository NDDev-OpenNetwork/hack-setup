<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: 2d182e1 docs(plugin): list apply-stack-rule among repo skill names
Scope: .agents/, .codex/, plugins/saint-tibo/, AGENTS.md, docs/rules/, docs/adr/0005-codex-rule-catalogue.md
Area: CODEX
-->

# CODEX-02-SURFACES

## Purpose

Map native Codex 0.155.1 project surfaces in this repo.

## Source Of Truth

- Repo skills: `.agents/skills/{repo-orientation,quality-gate,one-repo-workflow,apply-stack-rule}/SKILL.md`
- Tech rules: `docs/rules/INDEX.md` (on-demand; Codex does not auto-load it). ADR 0005.
- Marketplace: `.agents/plugins/marketplace.json` name `saint-tibo`, path `./plugins/saint-tibo`
- Plugin: `plugins/saint-tibo/plugin.json` portable Agent Plugins 1.0.0
- Plugin skill: `plugins/saint-tibo/skills/saint-tibo/SKILL.md` name `saint-tibo`
- Config: `.codex/config.toml` is a projection of pin `registered.session` + `models` + `registered.features` (`gpt-6-astra` + `xhigh`, window `872000` / compact `700000`, `[profiles.sol]`, `agents.enabled=false`)

## Current Behavior

Repo skills load without plugin install. The plugin is the installable unit and has one uniquely named skill. Project `.codex/` loads only after the project is trusted. Plugin enable key is `saint-tibo@saint-tibo`. `./setup` does not run `codex plugin marketplace add`.

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
- Do not add `docs/rules/*` to `project_doc_fallback_filenames`.

## Invariants

- No skill-name collision between `.agents/skills` and `plugins/saint-tibo/skills`.
- Do not copy repo skill names into the plugin.

## Change Rules

- Author new team workflows as `.agents/skills/<kebab-name>/SKILL.md`.
- After surface edits run `just check`.

## Verification

- `just check`
