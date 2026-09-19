# Host acceptance matrix

Run in disposable non-product inputs outside the submission repository when allowed, then repeat relevant cases against the real repository after the event begins. This is a setup verification procedure, not a requirement for heavy tests on every product edit.

Use statuses `PASS`, `FAIL`, `NOT-TESTED`, `UNSUPPORTED`, `NOT-APPLICABLE`. A status needs evidence and a host/commit identity. Deliberately invalid negative controls must fail for the expected reason.

| ID | Case | Acceptance evidence |
|---|---|---|
| SET-01 | Installed identity | Codex version, Serena commit/distribution, actual executable paths and dependency environments |
| SET-02 | Config preservation | Redacted before/after diff; existing provider/auth still works; no duplicate connection |
| SET-03 | Instruction discovery | Root session follows router; nested task loads relevant rules; unrelated language rules are not loaded wholesale |
| SET-04 | Skills | Skill name/description discovered; an explicit selection loads its procedure and resolves repository paths |
| SET-05 | MCP initialization | Real connection and tools/list; context and root are correct; no assumed tool names |
| SET-06 | Project activation | Returned project identity/path matches this worktree, not common Git directory or another branch |
| SET-07 | LSP source navigation | Real definition + cross-file reference results for each enabled source language |
| SET-08 | Rename/edit | An isolated symbol rename updates expected callers, preserves unrelated text and passes relevant compiler/parser |
| SET-09 | Unicode positions | Cyrillic/Kazakh and a non-BMP character preceding an edit do not corrupt offsets or adjacent content |
| SET-10 | Uncommitted changes | A new/edited symbol is discoverable without stale results after normal refresh; no unnecessary full reindex |
| SET-11 | Worktree isolation | Two independent roots containing different uncommitted marker symbols never return or modify each other's files |
| SET-12 | TS native/tsserver split | Report compiler version and actual navigation engine; exercise real TSX/imports/configuration/features |
| SET-13 | Flutter/Dart alignment | Record Flutter-bundled Dart and launched analyzer; verify Flutter imports and generated declarations |
| SET-14 | Python environment | Imports resolve in each service environment without adding unrelated packages to suppress errors |
| SET-15 | Format/schema checks | Invalid JSON/YAML/TOML is rejected; schema-invalid but parseable consumer config is also detected |
| SET-16 | Markdown | Broken local link or heading reference is detected through selected check; code fences remain intact |
| SET-17 | Generated consumer | Source contract change regenerates the expected client; no hand-edited generated file; references still resolve |
| SET-18 | Hooks | Real lifecycle events execute once as intended; no reset command, deny reminder, full test or destructive cleanup |
| SET-19 | Unsupported format | Agent explicitly selects appropriate CLI/text path and does not pretend fallback Python LSP validated it |
| SET-20 | Runtime consumer | Compose/Caddy/Vector/OpenAPI checks use the installed consumer versions where applicable |
| SET-21 | Failure handling | Missing server produces a clear degraded capability and bounded recovery, not an endless install/reindex loop |
| SET-22 | Secret handling | Only deliberate synthetic canaries are used; canaries do not enter committed logs/memories; no real credential probing |
| SET-23 | Cost of setup | Cold/warm startup, indexing latency and RSS measured for actual selected server set, including concurrent sessions |
| SET-24 | Reproducibility | Second configuration application changes nothing unintentionally; manifest and actual process identity agree |

## Minimal proof per server

Record adapter ID, executable/version, root, initialize capabilities, one semantic operation, one mutation where appropriate, and the relevant external validation. For Markdown/HTML/JSON, report structural capabilities rather than claiming code-grade rename semantics. Do not require unsupported operations just to fill the table with green cells.

## Important negative controls

A typo in a known JSON schema field must not be called valid merely because parsing succeeds. A native-TypeScript project configuration or API compatibility case must not be declared understood merely because old tsserver initializes. A Flutter import must not be silently suppressed because an independent Dart SDK cannot find it. A compiler error in an unedited dependency must be distinguished from a new regression, not ignored globally.

## Completion

The setup is ready for a capability only after its required cases pass. Other catalogue items remain available/planned with explicit status. Successful package installation is an intermediate state, not final acceptance.


## Added acceptance cases from the second review

These extend the one-time setup matrix; they are not per-edit CI gates.

| ID | Case | Acceptance evidence |
|---|---|---|
| SET-25 | Historical selection | Version publication time <= cutoff, immutable source/artifact identity, separate inspection date |
| SET-26 | Effective autonomous modes | `base_modes` is configured globally, not ignored in project.yml; active combination matches this profile |
| SET-27 | Local override merge | Applying a local ty path retains required TypeScript settings; shared file has no host paths |
| SET-28 | Hook trust and timeouts | Optional hooks discovered once and trusted through the real mechanism; SessionEnd budget <=3; changed definition not assumed trusted |
| SET-29 | Mutating timeout | A disposable interrupted mutation is inspected before retry; no assumption of rollback or exactly-once behavior |
| SET-30 | Index scope | Authored `build/`/`dist/`/`target/` examples remain visible unless deliberately excluded with a reason; imports to generated declarations still work |
| SET-31 | Stable adapter boundary | Stable release does not claim the newer registry API; candidate upgrade has separate recorded source and acceptance |
| SET-32 | Non-writing verification | Check commands leave authored sources and locks unchanged; deliberate formatting/generation is reported separately |
| SET-33 | Native-platform support | Actual OS/architecture is supported by selected adapter and artifact; Linux arm64 Dart gap is not hidden |
| SET-34 | Browser code execution, only if used | Worker responsiveness is tested separately from origin/network/credential restrictions and termination |

See [CAPABILITY-RECORD.md](CAPABILITY-RECORD.md) for per-host proof. No negative-control test may access actual secrets, damage unrelated state or create product source before the event.
