# Saint Tibo Devin setup

Devin CLI twin of the root Codex setup — toolchain and instructions
only. No application source here.

## Mechanism

Same loop as the root setup; do not fork numbers outside the pin.

1. Law: `build/devin-pin.json` + `build/stack-pin.json` (generated copy
   of `../build/stack-pin.json`; `just sync-pin` refreshes, the checker
   fails on drift).
2. Runtime: `.devin/config.json` + `.devin/mcp_config.json` +
   `.devin/hooks.v1.json` (project layer) and the managed block in the
   Devin user config (written only by `scripts/repair_devin_setup.py`).
3. Proof: `just check` → `just gate` (`./setup --status`, checker,
   `devin --version`, `herdr --version`).
4. Shared code: `install/lib/*` and modules `10|15|30` are byte-identical
   to `../install/` — edit the root copy, re-copy, let the checker's
   shared-sync guard confirm.

## Pin

- Devin CLI `3000.10.31` via the versioned installer
  (`static.devin.ai/cli/3000.10.31/setup.{sh,ps1}`). `devin --version`
  must print `devin 3000.10.31`.
- herdr `0.9.1` from sha256-verified release assets (all five platforms
  in the pin). Windows x86_64 zip keeps its ConPTY runtime beside
  `herdr.exe`; ARM64 Windows is emulation, not a pin target.
- Session law: `DEVIN_PERMISSION_MODE=bypass` (env — there is no config
  key for the default mode), `subagents_enabled=false`,
  `auto_update=false`, `read_config_from` all false, model `swe-2-max`.
- Orchestration: workers are real Devin sessions in herdr panes
  (`herdr agent start/prompt/read/wait`, `devin -c`/`--resume`). Do NOT
  enable subagents — that is the codex no-subagents law, ported.
- Hooks: `.devin/hooks.v1.json` → `.devin/hooks/devin_mode.py`. Devin
  protocol: stdin JSON, `decision:block`, `hookSpecificOutput.
  additionalContext`, exit 2 blocks. Lane guard honors `.devin/lanes.json`
  and `.codex/lanes.json`.

## Team rules

The root `AGENTS.md` `## Operating standards` list applies here
unchanged — read it first (serena→github→agent state, full-auto,
hypothesis-verified requests, research before edits, consistent synced
code, durable state, atomic commits, merge commits only, proof before
claims). One claimed file owner, no secrets in the public repo, never
claim a check you did not run.
