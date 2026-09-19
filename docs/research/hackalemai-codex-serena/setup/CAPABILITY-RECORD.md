# Per-host capability evidence record

Fill one record per capability and actual target host. This is a template, not a passed test.

| Field | Required value |
|---|---|
| Capability / adapter | Concrete operation and exact adapter ID |
| Historical cutoff / inspection time | Both, with timezone |
| Release/source identity | Exact tag plus dereferenced commit where relevant |
| Artifact identity | Executable path, version, target architecture, hash/integrity |
| Environment | Interpreter/runtime, selected extras, dependency/lock identity |
| Working state | Real worktree path, branch, commit, dirty diff hash or equivalent evidence |
| Effective configuration | Redacted config identity, roots, active modes, trust state, relevant exclusions |
| MCP / LSP discovery | Actual tools/capabilities returned, not assumed names |
| Semantic result | Query, expected definition/reference, actual result |
| Mutation result | Disposable rename/edit, resulting diff, or a justified unsupported operation |
| Negative control | Deliberately invalid input rejected for the intended reason |
| Consumer result | Exact non-writing compiler/parser/runtime check and exit/result |
| Performance | Observed cold/warm startup and selected operation; no invented measurements |
| Outcome | SOURCE-VERIFIED / INSTALLED / HANDSHAKE-PASSED / BEHAVIOR-PASSED / FAIL / NOT-TESTED / UNSUPPORTED / NOT-APPLICABLE |
| Residual scope | Specific operations/hosts not established by this result |

SOURCE-VERIFIED is not a successful host installation. HANDSHAKE-PASSED is not reliable references, rename or diagnostics. A real behavioral result is scoped to its input and recorded tree; it does not establish universal correctness. SKIP and NOT-APPLICABLE are not PASS.

For optional hooks, record discovery, exact-definition trust, event, observed execution count and effective timeout. For a timed-out mutation, record state inspection before any retry. If student code execution is used, distinguish responsiveness from the origin/credential/network boundary.
