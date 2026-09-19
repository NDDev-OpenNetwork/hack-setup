# 6. Codex YOLO session

- Status: accepted
- Date: 2026-09-20
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The team setup must run Codex without an OS sandbox and without
per-command approval prompts. 0.155.1 `--full-auto` is a deprecated
`workspace-write` compatibility flag, not that mode.

## Decision Outcome

Project session law lives in `build/stack-pin.json`
`registered.session` and `.codex/config.toml`:

- `approval_policy = "never"`
- `sandbox_mode = "danger-full-access"`
- `allow_login_shell = true`
- `web_search = "live"`

Use the older `sandbox_mode` path. Do not set `default_permissions` or
`[sandbox_workspace_write]`. Do not enable `features.network_proxy`.

Spawn tools are off (ADR 0007). Do not add `.codex/agents/*.toml`.

Do not add project `.codex/rules/*.rules`. Those files are execpolicy,
not style rules. `--yolo` does not load `--ignore-rules`. The ignore
switch is `codex exec --ignore-rules` only and is not a `config.toml`
key. User-layer `~/.codex/rules` can still forbid a command; a `prompt`
rule under `approval never` becomes a hard deny.

`approval_policy = "untrusted"` stays retired.

## Confirmation

- `python3 scripts/check_codex_setup.py`
- `.codex/config.toml` matches `registered.session`
