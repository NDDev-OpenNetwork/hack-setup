---
name: saint-tibo
description: Load the Saint Tibo team plugin. Use when installing the plugin, checking marketplace wiring, or asking how plugin skills relate to repo skills.
---

This plugin is the installable distribution unit. Repo workflows live in
`.agents/skills/` and keep those names (`repo-orientation`, `quality-gate`,
`one-repo-workflow`).

Do not add plugin skills that reuse those names.

Marketplace identity is `saint-tibo@saint-tibo`. Enable it from
`.codex/config.toml` after the project is trusted.
