# 8. Agent-standards Codex plugin

- Status: accepted
- Date: 2026-09-20
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

Codex 0.155.1 has no Cursor-style `.mdc` / glob / `alwaysApply` loader.
The first catalogue lived in `docs/rules/`. A second draft started under
`docs/agent-standards/`. Two trees is a fork. Setup components are
plugins. Frames need one portable home the control loop can name.

## Decision Outcome

- Ship agent-standard frames as Codex Agent Plugins 1.0.0 plugin
  `hack-agent-standards` at `plugins/hack-agent-standards/`.
- Content SoT is `plugins/hack-agent-standards/standards/`. INDEX links
  only files that exist. CORE, QUALITY, and the area files listed in
  INDEX are the catalogue. Nested `AGENTS.md` templates live in
  `plugins/hack-agent-standards/nested/` and are copied only when the
  product tree is created.
- Marketplace lists `saint-tibo` then `hack-agent-standards`. Enable
  key is `hack-agent-standards@saint-tibo`.
- Pin `control.rules` points at the plugin INDEX.
  `registered.standards_plugin` records the plugin.
  `registered.standards_plugin_skills` is the skill set SoT.
- Playbook: plugin skills under `skills/<name>/SKILL.md` (INDEX
  router `apply-agent-standard` plus one skill per area file).
  Invoke `$hack-agent-standards:<name>`. Repo skill
  `apply-stack-rule` stays as the unqualified INDEX alias.
- Frames, not guards. Owner text this turn beats a standard. The pin
  is the universe of versions. A forgotten read is a process miss.
- Delete `docs/rules/` and `docs/agent-standards/`. Do not keep a
  parallel catalogue.
- Do not add the catalogue to `project_doc_fallback_filenames`.
- Do not put `skills` / `hooks` / `mcpServers` on the plugin root.

ADR 0005 still holds: on-demand load, AGENTS stays a router. The
storage path is this file.

## Consequences

- Positive: one tree, installable like the team plugin, validator can
  reject leftover catalogues.
- Negative: Codex still does not auto-open INDEX. The model must read.
- Neutral: INDEX links only files that exist. Nested product
  `AGENTS.md` is cwd-chain only.
