# Source evidence and temporal boundary

Reference cutoff: **2026-09-19T23:59:59+05:00**, Asia/Almaty. Equivalent UTC cutoff: **2026-09-19T18:59:59Z**. Inspection: 2026-09-20. Package: reviewed revision 1.1.

## What each evidence class means

**Pinned-source:** a concrete upstream file/ref establishes implementation or declared metadata. **Live-document:** an official page observed during inspection supports current documentation, but is not by itself a historical snapshot. **Local-static:** the supplied package bytes were parsed/checked here. **Normative:** an engineering choice proposed for this team's goals. **Host-runtime:** actual installation/connection/behavior on a target host; no such result is claimed in this audit.

## Immutable reference identities

| Component | Identity | Evidence |
|---|---|---|
| Original user archive | See SHA-256 in the audit report | Local bytes preserved; original manifest verified |
| Serena stable | tag v1.7.0 -> commit `949a27ef1e5fda1a6e7b561e777bcece345c6ffd` | Git ref response, source files S2-S8 and A4-A8 |
| Codex stable | rust-v0.155.1 -> annotated tag `4e21628f9ec9ee656650cd2b62ef92225725b5ac` -> commit `be2951ea34f0d295ed0becf97079f92fa5f6950e` | Release/tag metadata and pinned source A1-A3,A11 |
| Codex publication | 2026-09-18T20:03:04Z, equivalent to 2026-09-19T01:03:04+05:00 | Official release `published_at`, before cutoff |
| Serena comparison branch | `c4dc91a7dac4ea560dc7658581a63dac33a76e6c` | Development-source guide/API only, not selected stable runtime |

References resolve through [SOURCES.md](../SOURCES.md). An upstream tag is resolved to its actual commit; an annotated tag object is not mistakenly used as the code commit.

## Claims double-checked against implementation

| Claim | Evidence and countercheck |
|---|---|
| SessionEnd budget | A3 declares maximum 3; A2 normalizes/clamps and warns. This is not a claim that timeout=5 makes the JSON invalid. |
| Hook execution trust | A2 gates executable handlers by enabled/trusted state; A11 handles allowed preference layers. JSON validity and repo trust alone are insufficient. |
| External adapter registration | A9 imports registry types from `solidlsp.ls_config`; stable S8 has an enum-based registry and lacks those named types. No plugin from that guide is claimed ready on stable. |
| Project base modes | A4 explicitly warns/ignores project `base_modes`, despite template commentary; A5 establishes global base ownership. A6 respects user no-questions intent. |
| Local merge | A4 uses top-level dictionary update for local config; A8 describes override purpose. A partial nested LS map is not a deep merge. |
| Dart platform/version | S5 embeds 3.7.1 defaults and a limited platform table. Version agreement alone is not Flutter analysis or Linux arm64 support. |
| Codex-context tools | A7 intentionally excludes six generic file/shell operations; a smaller tools/list need not be a connection failure. |
| Timeout ordering | A5 default240 versus original client120. The revised90/120 choice is normative, not measured performance or guaranteed cancellation. |

## Broader stack and industry-practice interpretation

The supplied archive is a setup/rule pack, not an application or a dependency lock. This audit covers every local Markdown file, the decisive configuration/adapter interfaces above, and rule coherence for the agreed catalogue. It does **not** re-resolve and execute all optional application libraries on all target platforms. Any exact version in an earlier conversation that lacks a current checked release record remains an input candidate, not inherited evidence.

No single public source establishes that a stack is universally the industry's best. Here the choices are assessed against reproducibility, precise contracts, one source of generated truth, bounded automation, least unintended scope, explicit capability evidence and proportional checks. These are normative engineering criteria applied to the user's constraints, not a performance ranking or vendor guarantee.

The OpenAI AGENTS/skills/rules/MCP/hooks pages were read as official live documentation; their relevant version-sensitive hook details were cross-checked against the selected Codex implementation. We did not archive the entire documentation site as it appeared at the historical cutoff.

## What remains unproven

No target Mac/VPS installation; no target MCP initialization; no target LSP rename/diagnostic execution; no product dependency solver; no Flutter native build; no load/GPU benchmark; no official competition permission review. The local report is not a security audit of the entire upstream projects. A passed local static check is narrowly scoped to the artifact and the explicitly implemented assertions.

## Selected upstream Git blob identities

These are Git blob IDs returned by the source service, not SHA-256 artifact checksums and not executed-binary attestations.

| Source | Git blob |
|---|---|
| Codex hook discovery A2 | `5003dbd24f081d1bc56a2f897fa51ef557a8caab` |
| Codex SessionEnd A3 | `708d0e53d98a5743b76d284a4de261ed320de3e3` |
| Serena config loader A4 | `9a169962443bfe5efd1bf6372429a8e0df6455cd` |
| Serena global template A5 | `369166a7fcdc6347a558f11bdd2f128fe2a1b6c2` |
| Serena Codex context A7 | `2dbd870aaedd13d42cdce0da948c27f016797d28` |
| Serena stable enum S8 | `67d77b02e5c9bde0cce7365f813ece7950194dfe` |
| Serena Dart adapter S5 | `553d753bb7be970d77d9da7b072bdd81231a7d37` |
| Development registration guide A9 | `6baa16cfcf38388af14df586e182f1aa70175597` |
