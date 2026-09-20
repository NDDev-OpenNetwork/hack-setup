---
name: agent-handoff
description: Close a Saint Tibo session so any agent can resume. Use before ending work, after a commit wave, or when state changed materially.
---

A session is done only when another agent can resume from repo state
alone.

1. Update the serena memory for each touched area
   (`.serena/memories/`, or `write_memory` when the MCP is attached):
   Current Behavior, Known Gaps, and the `Last commit:` metadata field.
2. Update `.serena/plans/NEXT-SESSION.md`: current law, the done list
   with commit ids, and what is blocked on the user.
3. Prove it: run the gate that covers your change
   (`just check` / `just gate` / `just test`) and quote the output.
   Never claim a pass you did not run.
4. Commit the knowledge sync as its own commit
   (`docs(serena): ...`), separate from code.
5. Release claimed files and state exactly what is uncommitted and why.

If a teammate or a fresh agent cannot reconstruct "what next" from
NEXT-SESSION + `git log` + issues, the handoff is not done.
