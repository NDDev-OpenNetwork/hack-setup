# Revision 1.1 changes

Original revision 1.0 is preserved separately. This update does not contain product implementation or install anything on the user's hosts.

## Configuration and source corrections

- SessionEnd timeout 5 changed to 3, matching Codex's clamp rather than pretending5 seconds is honored.
- Optional hook location, additive discovery and exact-definition trust are explicit; no automatic bypass.
- Stable1.7.0 external registry gap is distinguished from the source-pinned development feature.
- Isolated global Serena config owns base modes and coordinated timeouts. Project base_modes is deliberately not used because stable code ignores it.
- Shared project configuration is portable; local path overrides retain complete settings under shallow merge semantics.
- Universal build/dist/target/uploads exclusions removed; index completeness and generated import resolution are checked.
- Pyodide worker execution is not presented as a security sandbox by itself.

## Evidence and workflow refinements

Historical cutoff and dereferenced Codex commit added. Per-host capability evidence separates source, installation, handshake and behavior. Check commands are non-writing. Contract/multiagent rule loading depends on actual boundaries, not file count. Target-platform limitations and Codex-context tool exclusions are explicit. Existing useful rules and selected stack are retained.

## New documents

Audit report, source evidence, per-file review coverage, version-resolution procedure, per-capability evidence record, and reproducible local validation procedure. Updated validation results and manifest describe this exact revision.

See [AUDIT-REPORT.md](audit/AUDIT-REPORT.md) for original locations, counterchecks, fixes and limits.
