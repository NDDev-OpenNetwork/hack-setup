# Fast, evidence-based verification

## Principle

Select checks by changed behavior and risk. Avoid percentage coverage goals, mandatory full test fleets or format/test hooks on every read. Do not skip a necessary cheap check simply because the overall project favors speed.

## Check ladder

For authored code, inspect the diff and run the selected non-writing formatter/linter check for affected files, then the relevant incremental compiler/typecheck or parser scope. Formatting/fixing and code generation are separate intentional mutation steps; inspect their diffs and verify afterward. A command named check must not silently fix code, update locks, regenerate clients or apply migrations. For cross-boundary changes, regenerate and compile the affected consumer. For authentication, persistence, grading, billing or retrieval access, add a focused behavior/negative test. For UI/artifacts, inspect the actual rendered path.

Run a broader suite only when the scope or a failure justifies it. Existing unrelated failures should be reported with evidence and separated from new regressions. Do not hide them using blanket exclusions, but do not rebuild the entire testing architecture to complete an unrelated feature.

## Tests worth keeping

A regression test should reproduce the actual trigger and assert a meaningful invariant. Avoid snapshots of unstable timestamps/model prose and mocks that only prove the mock was called. Use deterministic fixtures for parsers/algorithms and a small representative evaluation set for AI. External-provider integration tests must be clearly distinguished from offline contract tests.

Tests, schemas, migrations and generated consumers are part of review scope. Do not exclude them automatically because they are not runtime source files.

## Review

Trace actual inputs, callers/callees, resource ownership, concurrency and trust boundaries before declaring a defect. A finding includes its path, trigger, impact, minimal fix and appropriate verification. Separate confirmed defects from risks or style preferences. Do not claim exhaustive review solely because no issue was found.

Prefer one targeted independent check of a material change to multiple redundant broad reviews. Deduplicate root causes. Preserve useful tests and existing contract assertions when simplifying code.

## Evidence format

Report commands/tools actually executed, working directory, relevant version and pass/fail/skip result. State exactly what remains unverified. `LSP started`, `no diagnostics received`, `build not run`, and `production scenario passed` are different statements.

Do not invent elapsed times, coverage, successful deployment or completed background results. A narrow verified change can be completed without claiming the entire platform is proven correct.


## Identity and timeout discipline

A result belongs to its working tree, dependency/config identity and changed-file state. Record the commit plus dirty diff identity when uncommitted work was checked. Re-run the relevant cheap check after changes that invalidate it; a previous branch's result is not proof for a merge result.

On a timeout, distinguish a read from a mutation. Inspect current state before replaying a mutation or external side effect. A retry is not automatically safe, and absence of a returned result does not imply rollback.

Two review passes by one agent are not independent reviewers. Static, source-level and host/runtime verification must remain separately labelled.
