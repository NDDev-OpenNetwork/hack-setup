# Actual validation results: reviewed revision 1.1

Reference cutoff: 2026-09-19T23:59:59+05:00. Inspection: 2026-09-20. These are local artifact checks, **not a target-host installation report**.

## Original artifact

The supplied ZIP was integrity-tested and extracted with path inspection. All 49 Markdown files were inventoried and reviewed. All 48 payload entries in its SHA-256 manifest matched the original bytes. No original file was excluded from content review. Two passes were performed by the same assistant, not independent reviewers.

## Revised local checks

The exact same validator source included in [audit/VALIDATOR.md](audit/VALIDATOR.md) was extracted and executed for the final pass. It does not run any setup command from a code fence.

| Check | Result |
|---|---|
| Markdown payload | 56 files; all UTF-8 with LF and final newline |
| Internal Markdown file/anchor links | 82 references checked by parser and target resolution |
| Skill frontmatter | Seven skills; names, directory identity and descriptions valid |
| Fenced syntax | JSON: 1, YAML: 3, TOML: 2, Python: 1 parse successfully; other fences checked for closure |
| Recipe-specific source constraints | Coordinated timeout policy, global/project mode scope, selected adapter IDs, local merge preservation, index scope and hook budget pass |
| Deliberate negative controls | 16/16 rejected by the local validator for the intended class of problem |
| Root AGENTS size | 3031 bytes |
| Largest supplied root plus one scoped template | 3808 bytes; not a measurement of the user's complete global instruction chain |
| Revised payload manifest | 55 payload entries; all bytes and SHA-256 verified after report generation; manifest excludes itself |
| ZIP round trip | Integrity test and extraction followed by the same final validator |

The expected-rejection controls cover duplicate JSON/YAML/TOML keys, an escaping link, a missing file, the old five-second SessionEnd budget, ignored project base_modes, an invented adapter ID, competing Python providers, a hidden authored build file, a shallow override dropping TS settings, an oversized server budget, wildcard trust, an unclosed fence, JSON NaN and a boolean hook timeout.

Two cases were reproduced directly from the original package, not only synthetic mutations: the SessionEnd budget and authored-directory exclusion. This reproduction uses explicit static assertions derived from inspected source and path matching; it is not execution of Codex's or Serena's own configuration loader.

## Tooling identity and interpretation

Validation ran with Python 3.13.5, PyYAML 6.0.3, markdown-it-py 4.2.0 and pathspec 1.1.1 in the artifact-review environment. These are the tools used to check this package, not recommended runtime versions for the hackathon product. The script requires Python 3.11+ because it uses tomllib.

Selected semantic assertions are deliberately narrower than full upstream schemas. Positive syntax/shape checks do not prove an upstream consumer accepts all options. Placeholders remain intentionally unresolved in templates and must be materialized on the real host. Known invalid negative controls are not deployable examples.

## Explicitly not executed or certified

Codex/Serena/LSP installation on the user's Mac or VPS; MCP initialize/tools calls; LSP reference/rename/diagnostics against a live server; every optional application dependency resolution; target builds or load/GPU benchmarks; the competition's official pre-event permissions; a security audit of complete upstream projects. These remain NOT-TESTED or out of scope, not PASS.

The seven new documents and the original payload were checked again after modification. The source-level conclusions and limitations are in [audit/AUDIT-REPORT.md](audit/AUDIT-REPORT.md); file coverage is in [audit/FILE-COVERAGE.md](audit/FILE-COVERAGE.md). The original archive is preserved separately.
