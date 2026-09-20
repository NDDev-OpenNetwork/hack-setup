# 9. Agent workflow format: serena-first, github-first, agent-first

- Status: accepted
- Date: 2026-09-20
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

Standards say *what* the stack is; nothing yet says *how* an agent
session runs. Three people plus agents share one repo, so the working
format must survive handoffs between agents and sessions without chat
context.

## Decision Outcome

Ship `plugins/hack-agent-workflow` (portable Agent Plugins 1.0.0) with
three skills, invoked as `$hack-agent-workflow:<name>`:

- `session-boot` — serena-first open: read `.serena/memories/` +
  `plans/NEXT-SESSION.md` (via the Serena MCP when attached), then
  `git status`/`log` and `gh issue list --assignee @me`; announce
  claimed files; load the matching standards frame.
- `github-flow` — github-first loop: issues are the task SoT; named
  issue → work branch → merge into the personal named branch; on the
  owner's "merge" rebase onto `dev` and PR into `dev`; on "release"
  `dev` → `main` plus deploy — both owner calls.
- `agent-handoff` — agent-first close: update memories +
  NEXT-SESSION with commit ids, quote the gate output, commit the
  knowledge sync separately, release claimed files.

Registration follows the standards-plugin pattern:
`registered.workflow_plugin` + `registered.workflow_plugin_skills` in
`build/stack-pin.json`, a marketplace row after `hack-agent-standards`,
`enabled` in `.codex/config.toml`, and checker coverage — portable
manifest, marketplace order, disk == pin skill set, unique names across
all skill groups, AGENTS.md naming, installed-cache byte parity.

## Consequences

- Sessions open and close through the format; state is resumable from
  the repo alone.
- Repo rules file `~/.codex/rules/` keeps governing exec policy; the
  workflow governs session shape, not permissions.
- New workflow skills are added by editing the pin list and the plugin
  tree together, then `just check`.

## Confirmation

- `just check` passes with the plugin installed
- `codex plugin list` shows `hack-agent-workflow@saint-tibo` installed
  and enabled
