# Saint Tibo Devin setup

Self-contained twin of the root Codex setup for **Devin CLI** — same law
model, same module mechanism, same member/OS flags, same lane guard.
Orchestration differs by design: Codex spawns `codex_app` threads from
the main chat; Devin workers are real `devin` sessions driven through
**herdr** panes (with cmux for the outer window layout on macOS).

## Install

```bash
cd devin-setup
./setup --member danil|ivan|artem        # macOS/Linux/WSL2
.\setup.ps1 -Member artem                # native Windows
./setup --os ubuntu --dry-run            # preview another family
```

Modules (sh + ps1 twins, discovered from `install/modules/<nn>-*`):

| Module | Does |
| --- | --- |
| `10-prereqs` | tar/git/gh/curl/python3 — shared with the codex setup |
| `15-member` | per-member git identity via `gh api user` — shared |
| `20-devin-cli` | managed user config (model, subagents off, auto_update off, imports off), pinned Devin `3000.11.1`, sha256-verified herdr `0.9.1`, `herdr integration install devin` |
| `30-runtimes` | uv/Python 3.14, bun, Node 24, just — shared |
| `40-devin-verify` | `devin plugins install --local` for `hack-devin-workflow`, repair + checker |

## Law → runtime → proof

1. Law: `build/devin-pin.json` + `build/stack-pin.json` (generated copy
   of the root stack pin — `just sync-pin`, drift is a checker FAIL).
2. Runtime: `.devin/config.json` + `.devin/mcp_config.json` +
   `.devin/hooks.v1.json`, and a managed block in the Devin user config.
3. Proof: `just check` (`scripts/check_devin_setup.py`) → `just gate`.
   Host repair/diagnostics: `python3 scripts/repair_devin_setup.py`.

## Session law (projection of the codex registered.session)

- `DEVIN_PERMISSION_MODE=bypass` exported by `install/env.sh` —
  approval_policy-never + no OS sandbox equivalent.
- `subagents_enabled=false` in the user config — workers are real
  sessions via herdr, never subagents.
- `auto_update=false` — background updates would drift the CLI pin.
- `read_config_from` all false — no silent imports from
  `.claude`/`.cursor`/`.windsurf`/copilot/opencode config.
- `attribution=false` — no "Generated with Devin" / Co-Authored-By on
  commits and PRs (team law: no AI attribution).
- Model `swe-2-max` ONLY: user config `agent.model` +
  `preferred_family_models`, `DEVIN_MODEL=swe-2-max` exported by
  `install/env.sh` (herdr workers inherit it), and the hook's model law
  blocks agent-launched `devin --model <other>` / `DEVIN_MODEL=<other>`.
  Do not use `/model`, `/fusion` or Adaptive; org-wide lock is Devin
  Team Settings.

## Orchestration — herdr, not threads

```bash
herdr agent start worker-ivan-1 --kind devin --pane <id>
herdr agent prompt worker-ivan-1 "Read the brief at …" --wait
herdr agent read worker-ivan-1 --lines 80
herdr agent wait worker-ivan-1 --until idle --timeout 120000
devin -c                       # resume last session in a pane
```

Skills: `/hack-devin-workflow:session-boot|github-flow|herdr-handoff|
hack-mode|ship-verify|debt-ledger`. The project hook
(`.devin/hooks/devin_mode.py`) injects the ruleset on lane-guarded
checkouts, guards `dev`/`main` pushes for any repo carrying a
`lanes.json` (`.devin/` or `.codex/` — both honored), nudges ship-verify
after pushes, and logs sessions to `.agent/session-log.ndjson`.
