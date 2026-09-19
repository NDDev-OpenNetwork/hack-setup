# Compatibility findings and decisions

This is a source-level compatibility assessment, not an executed integration certification. `PASS` belongs in a host report only after the corresponding acceptance case. References resolve through [SOURCES.md](../SOURCES.md).

| ID | Verified observation | Decision | Required host proof |
|---|---|---|---|
| COMP-01 | Serena 1.7.0 pins dependencies including Pydantic 2.12.5 and has Python `>=3.11,<3.15`. [S3] | Isolated uv tool environment, not FastAPI's dependency graph | Import/start command and exact resolved environment |
| COMP-02 | Stable TypeScript adapter defaults to TypeScript 5.9.3 and typescript-language-server 5.1.3. [S4] | Record separate project compiler and navigation engine; do not assume native TS7 is the LSP engine | Definitions/references on real TSX, imports, generated types and current project syntax |
| COMP-03 | The native TypeScript implementation and a tsserver-based LSP are different interfaces. [L3,L4] | Keep native project compiler; use compatible tsserver navigation only where it works; native-LSP SolidLSP adapter is a separately tested integration task | No unsupported config options, reliable navigation and native compiler result |
| COMP-04 | Stable Dart adapter downloads SDK 3.7.1 by default and exposes `dart_sdk_version`, not a binary-path override. [S5] | Resolve bundled Flutter Dart and align the adapter; do not rely on PATH or invent `dart.ls_path` | Flutter package imports, generated Dart references and matching analyzer behavior |
| COMP-05 | Stable Dart adapter only embeds archive checksums for its bundled known versions. [S5] | Verify a custom SDK archive against an authoritative checksum before use | Artifact URL, checksum and SDK identity |
| COMP-06 | Stable `python_ty` defaults to ty 0.0.25, supports `ls_path` or `ty_version`, and is classified as a secondary/experimental adapter. [S6,S8] | Use one pinned ty executable for navigation and CLI checks; validate before upgrading the adapter default | Correct Python environment, symbols, references, rename and type diagnostics |
| COMP-07 | Current stable project template uses `language_servers`, not the older `languages` spelling. [S2] | Generate settings from the installed template and inspect warnings | Effective loaded server set, not just valid YAML |
| COMP-08 | Stable `serena-hooks` exposes activate, cleanup, remind and auto-approve; no reset command. `remind` can return deny. [S7] | Activation/cleanup only in the fast profile; no main-branch hook snippets blindly copied | Real SessionStart/SessionEnd events and absence of blocking reminders |
| COMP-09 | Canonical Codex hook feature key is `hooks`; old alias remains documented. [C5] | Use canonical key when this setting is needed; preserve existing hooks | Installed Codex accepts config and executes intended events |
| COMP-10 | Serena server selection gives a file to the first matching configured server. [S2] | One primary provider per extension family | No duplicate Python/TS ownership or accidental fallback for unsupported files |
| COMP-11 | Taplo's npm distribution does not include its LSP component. [L7] | Install an LSP-enabled Taplo binary for `toml` | `taplo lsp stdio` handshake, not only formatting |
| COMP-12 | The stable built-in catalogue does not list SQL, Dockerfile, XML or Tailwind-specific identifiers, and stable 1.7.0 lacks the newer external registry API. [S8,A9] | Baseline uses CLI validators; bridge/upgrade is a separate qualified capability | Do not mark installed editor-only servers as agent-connected |
| COMP-13 | Global/process settings and active-project state can leak between wrongly shared sessions. | One stdio process and local project identity per worktree | Two worktrees return their own uncommitted code only |
| COMP-14 | MCP environment settings configure its child process, not arbitrary Codex shell hooks. [C3] | Set shared `SERENA_HOME` in the launching environment or explicitly in both hook commands and MCP | Activation and cleanup address the same session data home |

## TypeScript resolution policy

The project uses its selected native compiler as the authoritative type/build check. Serena 1.7.0's `typescript` adapter expects the tsserver-based ecosystem; changing `typescript_version` to a package without the required tsserver interface is not an upgrade path.

First evaluate a pinned tsserver-compatible engine supported by the adapter. Treat the inspected 5.9.3/5.1.3 pair as the reproducible adapter baseline, **not a claim that it supports every TypeScript 7 project**. If navigation breaks on current syntax or configuration, record the exact gap. A compatible side configuration may narrow navigation scope but must not hide compiler errors. A native-LSP adapter remains a separate integration candidate. Stable Serena 1.7.0 does not expose the `LanguageServerRegistry`/`ExternalLanguageServerId` mechanism described by the newer external-registration guide. Do not install that entry-point package into stable 1.7.0 and claim it is integrated. Use a separately audited source-pinned upgrade or adapter patch, with its own acceptance; otherwise use bounded text exploration for the failing area and keep compiler verification intact. No forced peer dependencies and no silent product downgrade.

## Dart/Flutter resolution policy

Read the actual Flutter installation's SDK metadata. If the same Dart version is published in the standalone stable archive, configure `dart_sdk_version` and verify its artifact. Then verify Flutter imports against the package configuration created by Flutter. Matching a version string alone is insufficient.

If this does not resolve Flutter analysis correctly, the alternatives are an audited SolidLSP adapter that explicitly launches Flutter's bundled Dart, or a documented native Flutter-analysis fallback while the adapter is unavailable. Do not fake support by placing an unsupported executable-path key in YAML.

## What this pack does not certify

It does not re-certify every application-library pin listed in earlier chat messages. It does not establish that all optional LSPs should run together, that every format supports rename, or that an 8-vCPU server can serve a particular inference workload solely because the user count is small. It does not treat current `main` documentation as the schema of release 1.7.0.

The implementation agent must retain release provenance and distinguish `source-verified`, `installed`, `handshake-passed`, `behavior-passed`, `unsupported` and `not-tested`.


## Additional source-level results from the second review

| ID | Observation | Decision / acceptance |
|---|---|---|
| COMP-15 | Codex 0.155.1 clamps SessionEnd/Interrupt timeout to 1..3 seconds, warning on larger values. [A2,A3] | Use a maximum of 3; test the real event and do not assume cleanup survives a crash |
| COMP-16 | Non-managed hooks are collected but are only runnable with matching trust (or explicit supported bypass/managed policy). [A2] | Inspect effective hook trust; do not infer execution from JSON syntax or feature enablement |
| COMP-17 | Stable project `base_modes` is explicitly ignored; the global config owns it. [A4,A5] | Editing-only base in the isolated SERENA_HOME; inspect final mode composition |
| COMP-18 | Stable project.local override is top-level `dict.update`, not recursive merge. [A4] | A local LS settings map must retain all selected entries |
| COMP-19 | Default Serena tool budget is 240 seconds; the original MCP caller budget was 120. [A5] | Select coordinated budgets and inspect mutation outcome before retry after timeout |
| COMP-20 | Stable Dart download table has no Linux arm64. [S5] | Record unsupported on that target until a separately tested adapter path exists |
| COMP-21 | Codex context deliberately excludes Serena's general file/shell tools. [A7] | Use native Codex tools for those operations; semantic-first is not tool-name invention |

### Stable versus development feature line

The compared development commit `c4dc91a7dac4ea560dc7658581a63dac33a76e6c` contains the external registration guide/API. It is **not** the stable installation pin and is not marked host-tested here. A newer feature existing before the historical cutoff does not make it part of release 1.7.0. Record both the baseline and any deliberately selected replacement; never conceal an upgrade inside a language-server installation.

### Product dependency closure

The technology coverage map is an architecture/rule inventory, not a solver-generated dependency lock. Exact earlier application pins are not carried forward as certified merely because they appeared in the conversation. See [historical version resolution](../setup/VERSION-RESOLUTION.md) and the [evidence boundary](../audit/SOURCE-EVIDENCE.md). Source metadata can prove declared bounds; runtime behavior, optional extras and native wheels still need the selected host/profile.
