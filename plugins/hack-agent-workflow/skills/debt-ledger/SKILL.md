---
name: debt-ledger
description: Harvest every `hack:`/`ponytail:` marker comment into a debt ledger so hackathon shortcuts get tracked instead of rotting. Use when the user says "debt ledger", "what did we defer", "list the shortcuts", "hack debt", or before post-hackathon hardening. One-shot report, changes nothing. Adapted from ponytail-debt (MIT).
---

# Debt ledger

Every deliberate hackathon shortcut is marked inline with a `hack:`
comment naming its ceiling and upgrade path. This collects them into one
ledger so a deferral cannot quietly become permanent.

## Scan

Grep the tree, skipping `node_modules`, `.git` and build output:

`grep -rnE '(#|//) ?hack:' .` — plus `ponytail:` for older markers.

## Output

One row per marker, grouped by file:

`<file>:<line> — <what was simplified>. ceiling: <limit>. upgrade:
<trigger to revisit>.`

Flag `no-trigger` on any marker that names no upgrade path — those are
the ones that silently rot. Rank rot-risk first.

End with `<N> markers, <M> with no trigger.` Nothing found:
`No hack: debt. Clean ledger.`

## Boundaries

Reads and reports only. To persist, ask, then write the ledger to
`.serena/plans/` (not a repo-root doc). One-shot.
