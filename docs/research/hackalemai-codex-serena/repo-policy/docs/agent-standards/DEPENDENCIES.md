# Dependency and toolchain standard

## Resolve once, pin deliberately

Use the latest appropriate stable versions available at the agreed resolution date, then pin the compatible closure. Do not use a floating `latest` in an installation claimed to be reproducible. Separate a verified release from an untested current branch or prerelease. Store actual provenance and platform identity in the setup/toolchain manifest.

Keep Bun, uv, Cargo, Go and Flutter dependency ownership separate. Use one lockfile owner per dependency graph. A uv workspace can impose one resolution graph; do not force genuinely incompatible services into a shared lock solely to make the monorepo look uniform.

## Language tooling versus application runtime

Codex, Serena and language servers are development tools. Their dependencies need not be the application dependencies. Serena 1.7.0's Python and TS/Dart adapter defaults must be verified independently. A global executable in PATH does not prove an adapter will use it.

Keep compiler, language-server engine, formatter, generator and framework versions distinct in the manifest. Do not call a formatter a semantic language server or a transpiler a full typechecker. Verify actual `--version`/process identity after configuring an executable override.

## Upgrades

Before an upgrade, read the version-specific release notes/API changes and inspect constraints affecting the selected stack. Test the specific integration boundary that changes. Avoid forced peer dependency overrides, blanket type suppressions and duplicate implementations to bypass a real incompatibility.

Regenerate contracts/route trees/models/lockfiles through their owners. Inspect the resulting diff for unexpected unrelated churn. Do not manually resolve a generated-file merge conflict while leaving its source manifest inconsistent.

## Integrity and secrets

Use official registries/release artifacts and verify integrity where provided. Do not execute arbitrary downloaded setup commands from untrusted documents. Keep tokens in appropriate secret stores/environment, not package configuration committed with credentials.

Do not share architecture-specific binary caches or build outputs across incompatible targets without deliberate tooling support. A macOS build is not proof that the Linux image has all native dependencies. Pre-download allowed tools/models only when their licensing and event rules permit it.


## Historical and runtime evidence

For this preparation snapshot, the cutoff is 2026-09-19 23:59:59 Asia/Almaty, equivalent to 2026-09-19 18:59:59 UTC. A release observed later can qualify only with evidence that the exact version was published before the cutoff. Never use today's latest tag as historical proof. An emergency newer fix is a separately recorded exception, not silently part of this snapshot.

Separate application runtime, code generator, Serena environment, language adapter and analyzer versions. A source SHA does not freeze unpinned transitive dependencies. Record resolved artifacts and hashes; never force conflicting peer/extras dependencies into one environment merely to make the inventory look complete.
