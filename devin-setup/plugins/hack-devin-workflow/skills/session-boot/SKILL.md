---
name: session-boot
description: Open a Saint Tibo Devin session the serena-first way. Use at the start of any task, on resume (`devin --resume`), or when the current state is unclear.
---

State lives in the repo, not in chat. Before touching code:

1. Read `.serena/plans/NEXT-SESSION.md` when present (transient handoff
   state — absent after a clean close), then open only the
   `.serena/memories/` notes for the areas you will touch. If the Serena
   MCP is attached, prefer `list_memories` / `read_memory` over raw
   file reads; use its symbol tools (`find_symbol`,
   `get_symbols_overview`, `search_for_pattern`) instead of brute grep
   when a code tree exists.
2. Ground truth: `git status`, `git log --oneline -5`, and
   `gh issue list --assignee @me`. Your named issues are the queue —
   no issue, no work (see `/hack-devin-workflow:github-flow`).
3. Announce the files you will claim before editing. One claimed file
   owner at a time.
4. Load the frame: the layer standards plugin (`apply-agent-standard`
   INDEX, then one area file) when the repo carries it; on a lane-guarded
   product checkout the SessionStart hook already injected hack-mode.
5. Report: current state, task, claimed files, which gate proves done
   (`just check` / `just gate` / `just test` in the setup repo; live
   verification in a product checkout — `/hack-devin-workflow:ship-verify`).

## Domain memories (write side)

Memories are per-domain, not per-session: name them
`.serena/memories/<DOMAIN>-<NN>-<TOPIC>.md` — `API`, `WEB`, `DB`,
`AUTH`, `INFRA`, `MODELS`, `DEVIN`, `STACK`, `TEST`. After a feature
lands, write or refresh the note for each domain it touched: the
decision, the file paths that carry it, the migration/convention it
added. `DB-*` covers migrations and schema shape — the next worker
reads it before touching models. Keep each note under ~60 lines; the
index of what exists lives in `NEXT-SESSION.md`.

Never resume from chat memory alone — if NEXT-SESSION disagrees with
`git status`, the repo wins and the plan file gets fixed. `devin -c` /
`devin --resume <id>` restores the chat; this skill restores the state.
