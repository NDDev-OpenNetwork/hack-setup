<!-- Memory Metadata
Last updated: 2026-09-21
Last commit: 63ddace docs(serena): record deploy-e2e verification and full issue closure
Scope: .agents/, .codex/, plugins/saint-tibo/, plugins/hack-agent-standards/, plugins/hack-agent-workflow/, plugins/hack-agent-lsp/, AGENTS.md, docs/adr/0005-codex-rule-catalogue.md, docs/adr/0008-agent-standards-plugin.md, docs/adr/0009-agent-workflow-format.md, docs/adr/0011-lsp-matrix.md, build/stack-pin.json registered.standards_plugin_skills + registered.workflow_plugin_skills + registered.lsp_plugin_skills
Area: CODEX
-->

# CODEX-02-SURFACES

## Purpose

Map native Codex 0.155.1 project surfaces in this repo.

## Source Of Truth

- Repo skills: `.agents/skills/{repo-orientation,quality-gate,one-repo-workflow,apply-stack-rule}/SKILL.md`
- Frames: `plugins/hack-agent-standards/standards/` (on-demand; Codex does not auto-load it). ADR 0005 + ADR 0008.
- Nested AGENTS templates: `plugins/hack-agent-standards/nested/` (copy when a product tree is created; do not create empty trees).
- Marketplace: `.agents/plugins/marketplace.json` name `saint-tibo`, plugins `./plugins/{saint-tibo,hack-agent-standards,hack-agent-workflow,hack-agent-lsp,hack-agent-mcp}`
- Team plugin: `plugins/saint-tibo/plugin.json` portable Agent Plugins 1.0.0
- Team plugin skill: `plugins/saint-tibo/skills/saint-tibo/SKILL.md` name `saint-tibo`
- Standards plugin: `plugins/hack-agent-standards/plugin.json` portable Agent Plugins 1.0.0. Skills are DirectChildren `skills/<name>/SKILL.md` only. Pin `registered.standards_plugin_skills` is the skill-set SoT.
- Workflow plugin: `plugins/hack-agent-workflow/plugin.json` portable 1.0.0. Seven skills `session-boot`, `github-flow`, `agent-handoff`, `delegate-worker`, `hack-mode`, `ship-verify`, `debt-ledger`; pin `registered.workflow_plugin_skills` is their SoT. Format: serena-first open, github-first loop, agent-first close. ADR 0009 + orchestration ADR 0014.
- LSP plugin: `plugins/hack-agent-lsp/plugin.json` portable 1.0.0. Skills `lsp-map`, `lsp-setup`; pin `registered.lsp_plugin_skills` + `lsp.*` matrix is the SoT. ADR 0011.
- Config: `.codex/config.toml` is a projection of pin `registered.session` + `models` + `registered.features` (`gpt-6-astra` + `xhigh`, window `872000` / compact `700000`, `agents.enabled=false`). 0.155.1 ignores project-local `profiles` and rejects a legacy `[profiles.sol]` table; module 20 writes `~/.codex/sol.config.toml` (overlay file mechanism) and the checker verifies it.

## Current Behavior

Repo skills load without plugin install. Five plugins are enabled after trust: `saint-tibo@saint-tibo`, `hack-agent-standards@saint-tibo`, `hack-agent-workflow@saint-tibo`, `hack-agent-lsp@saint-tibo`, `hack-agent-mcp@saint-tibo`. INDEX links every catalogue file as `ready`. Root `AGENTS.md` has a Motion kernel and names every standards, workflow, and lsp plugin skill. Codex 0.155.1 matches plugin skills only as `$hack-agent-standards:<name>` / `$hack-agent-workflow:<name>`. Bare `$apply-agent-standard` does not select the plugin skill. Repo alias `$apply-stack-rule` stays unqualified. `./setup` module 40 registers the marketplace and installs all five plugins before the checkers run.

## Contracts And Data

- Skill frontmatter requires `name` (≤64) and `description` (≤1024). Directory name must match `name`.
- Portable plugin root may not set `skills`, `interface`, `apps`, `hooks`, or `mcpServers`.
- Marketplace `source.path` is repo-root relative and starts with `./`.
- Session law is `build/stack-pin.json` `registered.session` and ADR 0006: `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, `allow_login_shell = true`, `web_search = "live"`. Do not set `default_permissions` or `[sandbox_workspace_write]`.
- `approval_policy = "untrusted"` is retired. `web_search` is top-level, not `features.web_search*`. Do not enable `features.network_proxy`.
- Models: primary `gpt-6-astra`, secondary `gpt-6-sol` (since 2026-09-23; `gpt-5.6-sol` is now rejected), both `xhigh`. In a pinned project sol is `/review` (review_model) or `codex -m gpt-6-sol` — project `model` outranks profile overlays. `--profile sol` works in unpinned dirs via managed `~/.codex/sol.config.toml`. Context `872000` / compact `700000`. Usable `/status` `828400`. Tibo 1M/900k is documented but clamped on 0.155.1.
- `agents.enabled = false`. `features.multi_agent` and `features.multi_agent_v2` are false. Do not spawn Codex subagents.
- Do not add `.codex/agents/*.toml`.
- Do not add project `.codex/rules/*.rules`. Execpolicy `~/.codex/rules` still loads under YOLO. `--yolo` does not imply `--ignore-rules`. The ignore flag is `codex exec --ignore-rules` only and is not a `config.toml` key. TUI 0.155.1 has no `--ignore-rules`.
- `$CODEX_HOME/skills` is a deprecated user skill location.
- Do not add `plugins/hack-agent-standards/standards/*` to `project_doc_fallback_filenames`.
- `docs/rules/` and `docs/agent-standards/` are stale and must stay deleted.
- Combined `AGENTS.md` budget is 32 KiB. Walk is git-root → cwd. Nested product `AGENTS.md` is injected only when cwd is that tree or below.

## Invariants

- No skill-name collision between `.agents/skills`, `plugins/saint-tibo/skills`, `plugins/hack-agent-standards/skills`, `plugins/hack-agent-workflow/skills`, and `plugins/hack-agent-lsp/skills`.
- Do not copy repo skill names into either plugin.
- Disk plugin skills must match `registered.standards_plugin_skills` and must include `apply-agent-standard`; workflow skills must match `registered.workflow_plugin_skills`; lsp skills must match `registered.lsp_plugin_skills`.

## Change Rules

- Author new team workflows as `.agents/skills/<kebab-name>/SKILL.md`.
- New plugin convention: name `hack-agent-<suffix>` (or the team plugin), marketplace entry in `.agents/plugins/marketplace.json`, `plugins/<name>/plugin.json` + `skills/`, pin `registered.<suffix>_plugin` (id/path) + `registered.<suffix>_plugin_skills` (saint-tibo uses bare `plugin`/`plugin_skills`), `[plugins."<name>@saint-tibo"] enabled` in `.codex/config.toml`, skill names listed in AGENTS.md. Checker and module 40 iterate the marketplace — no code edits needed.
- Author a new area frame in `plugins/hack-agent-standards/standards/` and link it from INDEX only after the file exists. Add a matching `skills/<name>/SKILL.md` and pin name in the same change.
- Copy `plugins/hack-agent-standards/nested/<layer>.md` to `<layer>/AGENTS.md` in the same change that creates that product tree.
- After surface edits run `just check`.

## Verification

- `just check`
