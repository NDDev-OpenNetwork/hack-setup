# Three-agent monorepo coordination

## Workspace ownership

Each developer/agent uses a separate worktree or clone and its own branch. Never run multiple independent writers in the same checkout. Each owns a Serena process, language-server state and appropriate local environment. Shared immutable caches are acceptable; shared mutable active project state is not.

Integration flows developer branches → `dev` → `main`. The integration responsibility can rotate, but only one designated process applies shared deployment and schema migrations at a time. This is an ownership rule, not a request for manual approval on each edit.

## Task slices

Before concurrent work, define the boundary and expected public contracts. Record who owns changes to API schemas, migration heads, root dependency manifests, generation configuration and shared localization conventions. Agents can work independently inside agreed boundaries and publish small coherent slices.

A shared contract change requires a compact explicit handoff: source schema change, affected endpoints/events, generated consumers, migration impact and verification. Avoid independent redesigns of the same DTO or auth flow.

## Git discipline

Inspect status before modifying or committing. Stage intentional files, not unrelated work by default. Preserve another person's changes; do not hard reset, delete worktrees or force-push a shared branch as a cleanup shortcut. Follow the project's selected merge/rebase policy rather than changing it mid-task.

Resolve generated artifacts from their source inputs and regenerate. Resolve migration heads through an intentional sequence or merge migration. Do not renumber or rewrite migrations already used by the shared environment to make history appear linear.

## Serena and build state

Do not register sibling agent worktrees as additional language workspaces. Use unique project identity where necessary. After merging a material change, refresh only the affected semantic state and generators. Avoid a full reindex/build of every language on every merge.

Separate ports, temporary outputs and preview data for parallel execution. Shared dev data must not be overwritten by fixture seeding from another branch. An agent's local test result applies to its recorded tree/commit, not automatically to a later merge.

## Handoff

Provide changed behavior, public-contract/schema effects, generated outputs, exact checks, commit identity and unresolved risks. Do not attach private chain-of-thought, secrets or full raw tool logs. A short factual handoff is preferable to a repeated narrative of the entire task.


## Local configuration ownership

Keep machine paths and worktree-specific names in local overrides, not the shared portable defaults. In the selected stable Serena, local overrides replace top-level values; a partial nested settings map can remove another language's explicit configuration. Inspect effective configuration after a local override or merge.

Generated files and migration results must be associated with the source/config/lock identity that produced them. Record dirty changes when reporting a local pass. Do not reuse a capability report from another worktree as evidence that the current root and state are correct.
