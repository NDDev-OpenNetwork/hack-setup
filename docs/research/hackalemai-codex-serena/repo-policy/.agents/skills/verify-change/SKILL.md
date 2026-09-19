---
name: verify-change
description: "Use before completing a feature slice or reporting a bug fixed, to choose and run narrowly meaningful verification."
---

# Verify changed behavior with evidence

Load QUALITY and the relevant language/domain standards. Inventory changed files, including tests, schemas, config and generated consumers; note directly affected unchanged callers.

Choose the smallest meaningful formatter/parser/type/build check, plus a targeted regression or negative case for the actual risk. Do not introduce a broad gate unrelated to the feature. Do not suppress real errors to make the check green.

Run the selected checks against the recorded worktree/commit. Read the diff and assess resource, concurrency and authorization boundaries where changed. Separate existing failures from new defects using evidence.

Return changed behavior, actual commands/tools and results, skipped coverage and material limits. A running LSP or no returned diagnostics is not a successful build. Background work is pending until its output is actually available.



Use non-writing check modes. Record commit and dirty-tree identity. A timed-out mutation must be inspected before retry. Do not describe two passes by this same agent as independent verification.
