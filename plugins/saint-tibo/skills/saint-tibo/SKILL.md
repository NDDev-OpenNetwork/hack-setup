---
name: saint-tibo
description: Load the Saint Tibo team plugin. Use when installing the plugin, checking marketplace wiring, or asking how plugin skills relate to repo skills.
---

This plugin is the installable team distribution unit. Repo workflows live
in `.agents/skills/` and keep those names (`repo-orientation`,
`quality-gate`, `one-repo-workflow`, `apply-stack-rule`).

Agent-standard frames live in the sibling plugin
`hack-agent-standards@saint-tibo`
(`plugins/hack-agent-standards/`). Skills are DirectChildren under
`skills/` (INDEX router `apply-agent-standard` plus layer skills).
Invoke `$hack-agent-standards:<name>`. Do not copy those names here.

Do not add plugin skills that reuse repo or standards-plugin names.

Marketplace identity is `saint-tibo@saint-tibo`. Enable it from
`.codex/config.toml` after the project is trusted.
