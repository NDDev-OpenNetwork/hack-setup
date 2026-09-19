# Two-pass review of the Codex / Serena preparation pack

Package revision: 1.1. Original: 1.0. Reference date: 2026-09-19, Asia/Almaty. Inspection: 2026-09-20.

## Verdict

The original pack contained useful, largely coherent engineering rules, but it was **not ready for an unqualified statement of complete historical and runtime compatibility**. This review corrected configuration/compatibility gaps and sharpened the evidence boundary. The reviewed pack is suitable as an agent handoff for actual setup and acceptance, not as a certificate that every host and optional module already works.

All **49 original Markdown files** were reviewed. The original ZIP passed its container integrity check and all **48 payload hashes** in its manifest matched. The input ZIP SHA-256 is `a9bdab90ead571e4340f4d71e64190ffcfa809b3956e99ac712d00db607b7858`. Original content was preserved separately rather than overwritten.

The two passes were performed by the same assistant: first source/configuration correctness, then consistency, negative controls and revised artifact verification. They are **not independent reviewers**. Findings are deduplicated by root cause; stronger existing safeguards were retained rather than counted as defects. See [file coverage](FILE-COVERAGE.md), [source evidence](SOURCE-EVIDENCE.md), and [actual validation](../VALIDATION.md).

## Confirmed configuration/documentation gaps

### F01. SessionEnd recipe requested an unsupported effective timeout

**Severity: medium; corrected.** Original `setup/HOOKS-AND-EXEC-POLICY.md:28-35` specifies timeout 5. Codex 0.155.1 normalizes SessionEnd to at most three seconds and emits a warning. A slow cleanup would not receive the documented five-second budget. The old JSON is parseable; it is not accurate to claim that the whole hook necessarily fails to load. Sources A2/A3.

Fix: timeout 3, optional lifecycle ownership, bounded local cleanup and explicit crash limitations. Verification: parse the revised JSON and assert the selected event budget; retain a negative control with timeout 5. Actual hook execution on target hosts remains NOT-TESTED.

### F02. Newer external-LSP API was not identified as absent from stable

**Severity: medium; corrected.** Original `research/LSP-MATRIX.md:60-62`, `research/COMPATIBILITY.md:24-26` and source S10 refer to external registration as the route forward. They caution that compatibility needs testing, but do not identify the specific missing API in the selected release. A9 imports `LanguageServerRegistry` and `ExternalLanguageServerId` from ls_config; the stable file S8 lacks them. A package copied from that guide cannot be treated as a plug-in solution for stable 1.7.0.

Fix: baseline uses existing adapters/CLI fallback; candidate development upgrade or adapter patch is explicitly separate, pinned and acceptance-tested. No such upgrade or adapter is shipped as working. Countercheck: this does not mean the current development version lacks extensibility, nor that all external LSP tools are useless.

### F03. Hook trust explanation omitted the exact-definition gate

**Severity: medium; corrected.** Original `setup/HOOKS-AND-EXEC-POLICY.md:9-11,45-52` mentions configuration trust and feature enablement, but not the Codex normalized-definition trust mechanism. A valid discovered hook can remain unexecuted. Pinned A2/A11 distinguish enabled, managed/trusted and untrusted definitions.

Fix: effective hook discovery/trust check, one intentional configuration location, no fabricated hash or silent bypass. Hooks remain optional, so setup does not become a per-edit approval process. Countercheck: the original did not promise automatic approval; this is an operational completeness gap rather than proof that every installation fails.

### F04. Generic directory exclusions contradicted authored-file visibility

**Severity: medium; corrected.** Original `setup/CONFIG-RECIPES.md:43-55` excludes any build/dist/target/uploads directory while line74 warns not to hide authored build content. A path such as `services/api/build/plan.py` matches the old rule regardless of ownership. The warning alone does not change the executable configuration.

Fix: remove those universal directory-name rules, inspect inherited Git/global exclusions, add only verified generated-output paths. Keep imported generated declarations visible. Countercheck: `target` or `dist` may legitimately be excluded for a known component; no blanket requirement to index all generated artifacts is introduced.

### F05. Client timeout and unspecified server budget allowed ambiguous outcomes

**Severity: medium; corrected.** Original `setup/CONFIG-RECIPES.md:11-15` uses 120 seconds for the MCP caller and leaves Serena's global tool budget unspecified. A5 defaults that budget to240 seconds. An operation outliving its caller can leave an unknown mutation outcome; a blind retry can be incorrect. No actual double-edit incident is asserted.

Fix: explicit isolated global budget 90 < caller 120, coordinated tuning, state inspection before replay of a mutation. This is a defensive starting policy, not proof of hard cancellation, rollback or latency.

### F06. Pyodide wording overstated an execution boundary

**Severity: medium; corrected.** Original `repo-policy/docs/agent-standards/EDUCATIONAL-MODULES.md:29` refers to an isolated browser runtime such as Pyodide. Browser execution and worker responsiveness alone do not specify separation from application credentials, origin or network authority. The adjacent server isolation rules were already useful.

Fix: distinguish worker execution from an explicit restricted-origin/frame capability boundary. Student-code execution remains optional and requires its own negative checks; no security claim is inferred from WebAssembly alone. The isolation policy is this pack's design requirement; A10/A12 document worker mechanics and capabilities, not a security certificate.

## Hardening and completeness improvements (not presented as reproduced production bugs)

### H01. Explicit mode ownership; do not repair it in an ignored field

The original inherited defaults instead of materializing a dedicated autonomous mode selection. The upstream interactive prompt respects explicit no-questions instructions, so it is not a guaranteed blocker. Crucially, A4 ignores project `base_modes` even though template material can mention it. The revised global isolated profile owns editing-only base modes; project default/added modes remain explicit. This source countercheck avoided introducing a new bad fix.

### H02. Portable defaults and shallow local overrides

The old configuration combines developer-specific name/path placeholders with shared project metadata (`setup/CONFIG-RECIPES.md:33,59-64`). It was labelled a template, not blindly deployable. The revision gives it clear shared/local ownership. A4 uses a shallow top-level update; the complete local LS mapping preserves TS settings when overriding ty. Per-host paths remain uncommitted.

### H03. Historical cutoff and source/lock distinction

The original source-date caveat was correct but lacked an exact timezone cutoff and a dereferenced Codex commit. The revision pins the actual code commit, labels live documents separately and defines the cutoff as 18:59:59Z. It does not select today's `latest` as historical evidence. The earlier broad application pin list is not retrospectively certified without an actual per-profile closure. See [version resolution](../setup/VERSION-RESOLUTION.md).

### H04. Non-writing checks and proportional rule loading

Original QUALITY asks for formatter/linter use but does not clearly separate fix commands from verification. Revised check conventions are non-writing; formatting/generation remain deliberate modifications. The root router no longer requires contract+multiagent standards merely because a private change touches two files. Cheap correctness checks remain; no exhaustive per-read suite is introduced.

### H05. Platform and evidence granularity

The Dart adapter table has no Linux arm64 branch, despite having macOS arm64. That is now an explicit platform gate, not a guessed target failure. New per-capability records bind actual process/config/root/dirty state to results. The `codex` context's intentional tool exclusions are documented. Unknown, skipped and unsupported are not converted to green passes.

## Correct decisions retained

Serena-first rather than Serena-only; MCP/LSP/compiler separation; compact AGENTS routing and task-specific skills; one mutable worktree/process per writer; preservation of user provider/autonomy; backend-owned API schema and generated clients; PostgreSQL/Qdrant/RustFS ownership; interpreter/extras isolation; explicit consumer/negative checks for access and grading; real artifact rendering; no product skeleton before the event; no blanket peer-dependency forcing; no claims of executed host tests.

## Industry-practice assessment

The criteria are concrete: reproducible identities, effective rather than merely parseable configuration, small instruction scope, explicit contracts/ownership, bounded retries and resources, meaningful negative controls, non-writing verification and honest runtime evidence. The corrected pack is aligned with those criteria for this team. No universal ranking, formal certification or claim of uniquely best technology follows.

## Release disposition

Use revision 1.1 instead of the previous configuration examples. The target-host setup agent must materialize paths and versions, preserve existing working configuration, then execute the relevant acceptance cases. Unselected optional technologies remain catalogue entries, not dependencies that must all be installed or servers that must all run.
