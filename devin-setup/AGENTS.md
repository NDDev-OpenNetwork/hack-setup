# Saint Tibo Devin setup

Devin CLI twin of the root Codex setup — toolchain and instructions
only. No application source here.

## Operating standards

Standing rules for every session — each line is a standard, not a
suggestion.

- By standard, open state **serena → github → agent**: `.serena/memories/`
  (plus `plans/NEXT-SESSION.md` when present) first, GitHub issues are
  the work queue, and a session closes by writing repo state the next
  agent resumes from — chat memory alone never counts as state.
- By standard, run **full-auto**: session law is already never-approve
  + full access — work end to end, do not pause for permission, and do
  not re-ask what the pin already answers.
- By standard, optimize for **feature velocity**: the laziest working
  solution verified live beats a perfect one that is not shipped — no
  review round, no test suite during the event; every deliberately cut
  corner gets a `hack:` marker for the debt ledger.
- By standard, treat every user request — even an assertion — as a
  hypothesis: verify it against the current code and the pin before
  acting. When the claim and the code disagree, the code wins; say so.
- By standard, before implementing, research everything the change
  touches — read the affected files, trace callers and twins, open the
  matching standards frame. Never edit code you have not read.
- By standard, write optimized, consistent, synchronized code: follow
  existing conventions, reuse what exists, keep the `sh`/`ps1` and
  codex/devin twins consistent, leave no stale references behind.
- By standard, keep state durable: refresh touched `.serena/memories/`
  and docs in the same wave as the change — stale docs are a defect.
- By standard, commit atomically and early — each logical slice lands
  as its own Conventional Commit so GitHub history shows progress;
  implementation, docs, and knowledge sync are separate commits.
- By standard, merge with `git merge --no-ff` only — never squash or
  rebase merges, never rewrite or delete shared history (hooks deny
  them; repo merge buttons are disabled).
- By standard, push early and let **CI/CD run in the background** —
  `.github/workflows/check.yml` verifies every push on all three OSes
  and the deploy watcher ships `dev`/`main` moves on the servers; check
  `gh run list` after pushing, fix red immediately, keep shipping
  meanwhile — do not idle waiting on green.
- By standard, prove before claiming: run the gate the change requires
  (`just check` / `just gate` / `just test`, or live verification) —
  a check counts only when you ran it.

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

- Devin CLI `3000.11.1` via the versioned installer
  (`static.devin.ai/cli/3000.11.1/setup.{sh,ps1}`). `devin --version`
  must print `devin 3000.11.1`.
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
  `DEVIN_PROJECT_DIR` is the nearest `.git` root — nested inside
  hack-setup that is the parent, so the parent carries a forwarder at
  `.devin/hooks/devin_mode.py`. A product repo keeps `.devin/` at its root.

## Team rules

Same as root `AGENTS.md`: one claimed file owner, no secrets in the
public repo, never claim a check you did not run.
