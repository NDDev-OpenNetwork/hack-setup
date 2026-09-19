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
  only files that exist. CORE and QUALITY are the first two frames.
  Area files are written one at a time later.
- Marketplace lists `saint-tibo` then `hack-agent-standards`. Enable
  key is `hack-agent-standards@saint-tibo`.
- Pin `control.rules` points at the plugin INDEX.
  `registered.standards_plugin` records the plugin.
- Playbook: plugin skill `apply-agent-standard`. Repo skill
  `apply-stack-rule` stays as a loader and points at the same tree.
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
- Neutral: planned area names stay unlinked until the file exists.
