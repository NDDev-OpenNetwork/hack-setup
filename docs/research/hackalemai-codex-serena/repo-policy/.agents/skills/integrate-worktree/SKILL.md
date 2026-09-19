---
name: integrate-worktree
description: "Use when synchronizing a developer branch into dev or main, resolving shared contracts, migrations or generated-file conflicts."
---

# Integrate a coherent worktree change

Load MULTIAGENT, CONTRACTS, DEPENDENCIES and QUALITY. Confirm your authorized integration role and the exact source/target branch state.

Inspect working-tree status and preserve unrelated work. Review the change's contract/migration/generator implications. Follow the established Git policy; do not use destructive cleanup or force-push shared history as a convenience.

Merge source definitions deliberately, resolve migration heads, regenerate owned outputs and run the smallest relevant checks against the resulting integrated tree. A check on a pre-merge branch is not proof for the merge result.

If deployment belongs to this task, serialize shared migrations and rollout, record image/commit identity and verify the affected path. Do not operate in another agent's checkout or share its active Serena process. Produce a concise factual integration handoff.
