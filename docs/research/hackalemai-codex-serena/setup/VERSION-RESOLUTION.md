# Historical version and dependency resolution

## Cutoff and claims

This snapshot targets **2026-09-19 23:59:59 Asia/Almaty**, i.e. **2026-09-19 18:59:59 UTC**. Inspection takes place on 2026-09-20. Use precise publication timestamps when a release falls near the boundary. If only a calendar date is available, report the temporal uncertainty instead of assuming the release existed at the cutoff.

A moving documentation page or a current registry `latest` label is not a historical release record. Record exact immutable references for behavior claims. Keep `published_at`, `inspected_at`, `source_ref`, and `resolved_artifact` separate. Never silently replace a historical baseline with an emergency newer fix; document a deliberate exception if required for actual deployment.

## Separate dependency graphs

Maintain separate identities for the application runtime, code generators, Codex, Serena tool environment, each managed LSP environment and optional GPU/ML profiles. Do not co-install incompatible extras merely to claim one universal environment. Node/npm provisioning inside an LSP is separate from the product's Bun lockfile.

Before a feature/profile is activated, resolve the actual selected graph using its package manager, retain its lock, inspect relevant engines/peer dependencies/extras/native wheels, and perform the narrow consumer check. An inventory of named products is not a dependency closure. A source pin alone does not freeze all dependency artifacts.

## Procedure

1. Inventory requested component, purpose, host OS/architecture and ownership of its dependency graph.
2. Obtain the exact release record from the official repository/registry. For a historical selection, filter publication times before choosing a version.
3. Check the relevant declared compatibility bounds and actual adapter implementation. Do not treat a package's marketing support list as proof of every LSP method.
4. Resolve and record the dependency closure with exact versions/integrity where supplied. Record selected optional extras and target wheels. Do not claim `uv tool install` from a Git SHA is fully locked if resolution remains dynamic.
5. Resolve the actual executable/image used by the running process. Validate the relevant capabilities, not just `--version`.
6. Keep a read-only selection record and a per-host acceptance record. Fresh inspection can reveal a historical fact, but cannot manufacture runtime evidence.

## Reference identities

| Layer | Reference | Evidence class |
|---|---|---|
| Codex | 0.155.1; commit `be2951ea34f0d295ed0becf97079f92fa5f6950e` | Release metadata and selected source inspected |
| Serena | 1.7.0; commit `949a27ef1e5fda1a6e7b561e777bcece345c6ffd` | Release ref and selected source inspected |
| Serena TS baseline | TypeScript 5.9.3 + LS 5.1.3 | Adapter defaults, not project-compiler recommendation |
| Serena ty baseline | 0.0.25 | Adapter default, not an assertion of latest ty |
| Serena Dart baseline | 3.7.1 | Adapter default; must align/qualify against actual Flutter |
| Newer external registry API | Compared Serena commit `c4dc91a7dac4ea560dc7658581a63dac33a76e6c` | Development-source feature, not stable/host-certified |
| Other application and optional LSP versions | Resolve per component/host/profile | NOT a certified universal pin list |

The official TypeScript 7 announcement documents the native compiler/LSP and the Compiler API compatibility break. That supports separating a native project compiler from older tsserver tooling; it does not qualify every plugin or generated client in this product. [L4]

Sources: [SOURCES.md](../SOURCES.md) and [the evidence ledger](../audit/SOURCE-EVIDENCE.md).
