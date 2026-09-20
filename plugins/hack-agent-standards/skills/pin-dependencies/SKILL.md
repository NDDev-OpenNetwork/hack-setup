---
name: pin-dependencies
description: Load DEPENDENCIES.md. Use when adding a package, changing a pin path, lock vs pin, uv/bun graphs, do_not_use, or conflicts.
---

# pin-dependencies

Frames, not guards. Owner text this turn wins. Versions live in
`build/stack-pin.json`. Catalogue: `standards/` next to this skill.

1. Confirm the worktree. This staging repo has no application source
   unless the owner opened the product remote.
2. Session, models, context, or spawn: edit `build/stack-pin.json`
   and `.codex/config.toml` together, then `just check`.
3. Open DEPENDENCIES.md and build/stack-pin.json. Then the area file that will install the package.
4. Named dep → pin path first. Offer the pin-equivalent if it fights do_not_use / conflicts.
5. Open `build/stack-pin.json` for the exact version.

Do not load the rest of the catalogue. Do not copy `docs/research/` into
the change. Prefer `$hack-agent-standards:pin-dependencies` (plugin). Repo alias
`$apply-stack-rule` still opens INDEX when the layer is unclear.

