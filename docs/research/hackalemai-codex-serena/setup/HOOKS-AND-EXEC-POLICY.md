# Hooks and execution policy

## Default: instruction routing, no new mandatory hook

Root instructions and skills are sufficient to establish the Serena-first convention. Hooks are an **optional measured convenience**, not a prerequisite for normal autonomous development. Do not add blocking reminders, per-read indexing, formatters, or full test runs.

Stable Serena 1.7.0 exposes `activate`, `cleanup`, `remind`, and `auto-approve`; there is no `reset`. `remind` can emit a deny decision. `auto-approve` targets particular Claude Code modes and is not a universal Codex bypass. `activate` returns a reminder, not evidence of a successful MCP activation. [S7]

## Optional lifecycle setup

Choose one ownership location: the actual worktree's `.codex/hooks.json` when that metadata is permitted, or a dedicated preparation Codex home. Do not add this to unrelated global projects. Codex merges hook sources additively; duplicate global/project/inline copies can execute twice. Preserve existing unrelated hooks, and use only one representation of this definition.

Codex 0.155.1 has **separate content-hash trust for non-managed hooks**, in addition to configuration/project trust. Inspect `/hooks` and the exact command definition through the installed supported UI. Until trusted, a discovered hook can be skipped. A changed normalized definition needs its own trust decision. Do not fabricate `trusted_hash`, claim `hooks=true` approves a hook, or silently add a trust-bypass flag. This is a one-time setup capability issue, not a manual approval requirement for normal source edits. Hooks may remain disabled and development can still proceed. The hash is of the normalized hook definition, not an automatic attestation of the script or binary named by its command. Record executable/script provenance separately. [A2]

The following command strings target POSIX hosts (the user's macOS/Linux machines), explicitly align `SERENA_HOME`, and quote path placeholders. Materialize actual paths safely; do not interpolate untrusted project/document content into a shell command.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "env SERENA_HOME='/ABSOLUTE/PATH/TO/PREPARATION/serena-homes/worktree-a' '/ABSOLUTE/PATH/TO/serena-hooks' activate --client=codex",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "env SERENA_HOME='/ABSOLUTE/PATH/TO/PREPARATION/serena-homes/worktree-a' '/ABSOLUTE/PATH/TO/serena-hooks' cleanup --client=codex",
            "timeout": 3
          }
        ]
      }
    ]
  }
}
```

In Codex 0.155.1, `SessionEnd` defaults to one second and is clamped to a maximum of three with a warning. The old five-second example did not buy five seconds and was not necessarily a parse error. Keep cleanup local, small, and best-effort. It only removes this session's hook bookkeeping, not the repository or all caches. Do not rely on lifecycle cleanup as guaranteed after a crash. [A2,A3]

Use `SessionEnd`, not `Stop` after every agent reply. Do not call Serena via an MCP SessionEnd hook: the pinned implementation does not support that hook type. SessionStart can happen before MCP readiness, so normal startup must still verify the actual active project. Never download/install dependencies inside either hook.

## Feature flag

The documented canonical feature is `hooks`, and the deprecated alias is not a reason to duplicate settings. The current official documentation says hooks are enabled by default; installed-release configuration decides effective behavior. Add a feature switch only when needed, without overriding managed settings. [C5]

```toml
[features]
hooks = true
```

## Optional advisory routing

Implement only after observing a routing failure that the instructions do not solve. Verify the exact selected Codex event's input and output schema before returning additional context. Do not assume every event accepts `additionalContext`. No blocking deny, source rewriting, repeated suite execution, or broad shell interception. Record actual event coverage and failure behavior.

## Execution policy is separate

Language conventions belong in Markdown; deterministic validation belongs in compiler/consumer configuration; process authorization belongs in Codex execution policy. Do not forbid `rg`, `cat`, or shell tools to enforce Serena preference. Do not convert a permissive interpreter command into a misleading claim of narrowly limited permissions.

Sources: [C4,C5,S7,A2,A3](../SOURCES.md). No hooks in this file have been installed or run on the user's hosts.
