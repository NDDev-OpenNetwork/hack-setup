# Host-specific setup report

Status: NOT-EXECUTED template. Replace entries with actual evidence. Do not convert unknown values into success.

## Identity

Host alias, OS/version, CPU architecture, user, authorized setup path, worktree path, branch, commit, check timestamp/timezone, agent/harness version, preparation pack version/hash.

## Toolchain manifest

| Component | Requested version | Actual version / commit | Executable / image digest | Source / integrity | Status |
|---|---|---|---|---|---|
| Codex | reference 0.155.1 | NOT-RECORDED | NOT-RECORDED | official distribution | NOT-TESTED |
| Serena | 1.7.0 / 949a27ef1e5fda1a6e7b561e777bcece345c6ffd | NOT-RECORDED | NOT-RECORDED | source pin + resolved environment | NOT-TESTED |
| Python tool environment | compatible isolated CPython | NOT-RECORDED | NOT-RECORDED | official runtime | NOT-TESTED |
| ty | resolved and pinned | NOT-RECORDED | NOT-RECORDED | official release | NOT-TESTED |
| TS project compiler | native selected version | NOT-RECORDED | NOT-RECORDED | official release | NOT-TESTED |
| TS navigation engine/server | independently compatible pair | NOT-RECORDED | NOT-RECORDED | adapter/upstream release | NOT-TESTED |
| Rust/rust-analyzer | matching selected toolchain | NOT-RECORDED | NOT-RECORDED | rustup/upstream | NOT-TESTED |
| Go/gopls | compatible pair | NOT-RECORDED | NOT-RECORDED | official release | NOT-TESTED |
| Flutter/Dart analyzer | matching bundled SDK | NOT-RECORDED | NOT-RECORDED | checksum-verified artifact | NOT-TESTED |
| Document/schema servers | one row per enabled server | NOT-RECORDED | NOT-RECORDED | official/adapter release | NOT-TESTED |

Also record actual child processes, dependency versions of the isolated Serena environment, selected schemas and formatter versions. Never attach raw environment variables or tokens.

## Configuration diff and ownership

Changed files, merge method, previous backup location, effective configuration layer, trust decisions, skills location, hook events, provider settings preserved, rollback steps.

## Capability results

For each SET case: status, exact command/tool, relevant output excerpt, expected/actual behavior and failure classification. Attach evidence paths with secrets removed. Include two-worktree and Unicode cases.

## Resource observations

Cold startup, warm startup, first semantic query, subsequent query, indexing scope, process RSS and simultaneous-session observations. Measurements are local evidence, not universal performance claims.

## Remaining gaps

Unsupported formats, failed adapters, versions awaiting resolution, unavailable target platforms, skipped checks and reason. State whether a tested fallback exists. External adapters must list their source commit and test evidence separately.

## Final decision

Ready capabilities; restricted/degraded capabilities; deferred optional capabilities. No product source code created during preparation: verify by file inventory rather than assertion alone.


## Historical source and effective configuration additions

Record Codex source `be2951ea34f0d295ed0becf97079f92fa5f6950e` for the reference release, its platform artifact identity, and any deliberate deviation. Record version publication time, historical cutoff, inspection time, selected extras, and each resolved dependency environment separately.

Record actual mode composition, global/local settings ownership, index exclusions, inherited Git ignores, MCP caller/server budgets and optional hook trust state. Do not attach a fabricated trusted hash or raw sensitive configuration.

Use [CAPABILITY-RECORD.md](CAPABILITY-RECORD.md). Include the working tree's dirty diff hash, selected schemas/config hash and dependency/lock identity. A source-supported but unrun capability remains NOT-TESTED for this host.
