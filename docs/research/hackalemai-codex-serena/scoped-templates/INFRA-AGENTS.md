# Infrastructure scope

Read the repository root AGENTS.md and applicable parent guidance. Resolve all following paths from the repository root. Load `docs/agent-standards/INDEX.md`, then the INFRA, FORMATS and MULTIAGENT standards. CORE, SERENA-WORKFLOW and QUALITY still apply.

Validate the actual config consumer, not only YAML/TOML parsing. Preserve data volumes and unrelated services. Coordinate shared migrations/deployment through the integrator and record deployed image/commit identity. Keep secrets out of artifacts and public endpoints limited to intended services.

Work only in your assigned worktree. Check the actual diff and report precise validation results and any unsupported capability.
