# 15. Persistent instructions, compaction prompt, tool-guard hooks, notify

- Status: accepted
- Date: 2026-09-21
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

ADR 0014 wired orchestration but left frame-survival gaps: a long worker
session auto-compacts at 700k and can lose lane/issue context; a worker
could `git push` straight to `dev`/`main` or `gh pr merge`; and the
ruleset lived only in injected context, not in the base instruction
chain.

## Decision

Verified against pinned `be2951ea` and the config reference:

- `developer_instructions` (project config, additive developer-role
  block, survives compaction because it is part of the instruction
  chain, not history) carries the one-paragraph operating law:
  YAGNI ladder, no review/tests, done = live, lanes, `hack:` markers.
  `model_instructions_file` was rejected — it *replaces* built-in
  instructions and degrades the model; `instructions` is reserved.
- `compact_prompt` overrides the default checkpoint prompt to preserve
  active issues, branch, worktree path, lane name, done-state and
  `hack:` markers verbatim. The `SessionStart` matcher `compact`
  additionally re-injects the full ruleset after each compaction.
- `check_for_update_on_startup = false` — the CLI is pinned.
- `notify` is ignored in project config (host-owned), so module 20
  writes a managed `# hack-setup: notify` block into the user-level
  `~/.codex/config.toml` pointing at `install/notify.sh` (POSIX) /
  `install/notify.ps1` (Windows): turn-complete toast, silent no-op
  otherwise.
- Hook surface grows to five events. `PreToolUse` (Bash matcher)
  enforces lanes mechanically: in a repo that carries tracked
  `.codex/lanes.json`, pushes to `protected_branches` and `gh pr merge`
  are denied unless the checkout has the untracked
  `.agent/orchestrator` marker — worker worktrees never have it, the
  orchestrator's main checkout does. `PostToolUse` (Bash) adds a
  ship-verify reminder after `git push`. `SessionEnd` appends
  `.agent/session-log.ndjson`. `additionalContext` only lands on
  PreToolUse/PostToolUse/SessionStart/UserPromptSubmit/SubagentStart —
  PostCompact cannot inject context, which is why compaction survival
  moved into `compact_prompt` + the `compact` SessionStart matcher.
- No user-defined slash commands exist in 0.155.1 (the command enum is
  compiled in); `/worktree`, `/fork`, `/app` cover the manual paths.

## Consequences

- Lane law is mechanical, not advisory, in repos that opt in via
  `.codex/lanes.json`. hack-setup itself carries no lanes.json and
  pushes freely.
- The marker is a guardrail against accidents, not a security boundary —
  a worker could fabricate it; the rules text forbids that.
- `just check` enforces presence + marker substrings for the new config
  keys (`registered.session.*_markers`).
