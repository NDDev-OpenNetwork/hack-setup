# Primary-source register

Reference date: 2026-09-19. Inspection date: 2026-09-20. Live documentation can describe a newer branch than a pinned release. Facts below are distinguished from the pack's own normative recommendations. No host installation is implied by reading a source.

## Codex

| ID | Source | Used for |
|---|---|---|
| C1 | [Official AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md) | Discovery order, overrides, startup directory, size budget |
| C2 | [Official skills guide](https://developers.openai.com/codex/skills) | Skill layout, frontmatter and discovery |
| C3 | [Official MCP guide](https://developers.openai.com/codex/mcp) | MCP transports/config, environment and tool controls |
| C4 | [Official execution rules](https://developers.openai.com/codex/rules) | Command policy versus natural-language instructions |
| C5 | [Official hooks guide](https://developers.openai.com/codex/hooks) | Canonical `hooks`, lifecycle, matchers and event limitations |
| C6 | [Official config reference](https://developers.openai.com/codex/config-reference) | Effective configuration, trust, permissions and documented fields |
| C7 | [Codex 0.155.1 release](https://github.com/openai/codex/releases/tag/rust-v0.155.1) | Stable reference release published 2026-09-18 |

The official developer pages currently redirect to the corresponding ChatGPT Learn documentation. Their title/URL changes do not make old local setup snippets current automatically. The final setup must validate fields against the installed release.

## Serena pinned source

Release **1.7.0**, published 2026-08-09. Tag resolves to commit **949a27ef1e5fda1a6e7b561e777bcece345c6ffd**. Source references below use that commit rather than a moving branch.

| ID | Source | Used for |
|---|---|---|
| S1 | [Release 1.7.0](https://github.com/oraios/serena/releases/tag/v1.7.0) | Stable baseline identity |
| S2 | [Project configuration template](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/serena/resources/project.template.yml) | `language_servers`, scope, workspace and trusted settings |
| S3 | [pyproject.toml](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/pyproject.toml) | Python bounds, dependency pins, distribution/entrypoints |
| S4 | [TypeScript adapter](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/solidlsp/language_servers/typescript_language_server.py) | TS 5.9.3/LS 5.1.3 defaults and documented override fields |
| S5 | [Dart adapter](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/solidlsp/language_servers/dart_language_server.py) | SDK 3.7.1 default, version override, download/checksum behavior |
| S6 | [ty adapter](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/solidlsp/language_servers/ty_server.py) | ty 0.0.25 default, `ls_path`/`ty_version`, server command |
| S7 | [Stable hooks implementation](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/serena/hooks.py) | Available commands, blocking reminder behavior, lifecycle output |
| S8 | [Language-server identifiers](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/solidlsp/ls_config.py) | Built-in identifiers versus unsupported/invented identifiers |
| S9 | [Adapter directory](https://github.com/oraios/serena/tree/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/solidlsp/language_servers) | Presence of relevant built-in adapter implementations |
| S10 | [External registration guide](https://oraios.github.io/serena/03-special-guides/external_language_server_registration.html) | Newer-feature guide; API absent from stable 1.7.0, comparison pinned in A9 |

Additional Serena documentation:

- [Supported languages](https://oraios.github.io/serena/01-about/020_programming-languages.html): capability catalogue and limitations.
- [Connecting clients](https://oraios.github.io/serena/02-usage/030_clients.html): MCP/context integration. Verify hook examples against pinned code.
- [Configuration](https://oraios.github.io/serena/02-usage/050_configuration.html): global/project/local configuration and trust.
- [Workflow](https://oraios.github.io/serena/02-usage/040_workflow.html): semantic workflow and indexing.
- [Tools](https://oraios.github.io/serena/01-about/035_tools.html): tool catalogue; do not assume every current page feature exists in 1.7.0.

The inspected moving main branch was `c4dc91a7dac4ea560dc7658581a63dac33a76e6c`. It was used for comparison, not selected as the install pin. Main-only/next-version functionality must be tested separately rather than silently mixed into the stable profile.

## Language servers and validators

| ID | Primary source | Used for |
|---|---|---|
| L1 | [Astral ty editor integration](https://docs.astral.sh/ty/editors/) | ty language-server role and invocation |
| L2 | [Astral Ruff editor integration](https://docs.astral.sh/ruff/editors/) | Native Ruff server; distinction from semantic navigation |
| L3 | [typescript-language-server](https://github.com/typescript-language-server/typescript-language-server) | tsserver protocol bridge and native TypeScript distinction |
| L4 | [Microsoft TypeScript 7 announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/) | Native implementation and compatibility considerations |
| L5 | [gopls](https://go.dev/gopls/) | Official Go language-server guidance |
| L6 | [rust-analyzer installation](https://rust-analyzer.github.io/book/installation.html) | Toolchain and component setup |
| L7 | [Taplo language-server usage](https://taplo.tamasfe.dev/cli/usage/language-server.html) | LSP-enabled binary, npm limitation, stdio |
| L8 | [Marksman](https://github.com/artempyanykh/marksman) | Markdown language-server capability |
| L9 | [Red Hat YAML LS](https://github.com/redhat-developer/yaml-language-server) | YAML schema language tooling |
| L10 | [Tailwind language server](https://github.com/tailwindlabs/tailwindcss-intellisense/tree/main/packages/tailwindcss-language-server) | External Tailwind-specific tool, not a built-in Serena assumption |
| L11 | [SQLFluff getting started](https://docs.sqlfluff.com/en/stable/gettingstarted.html) | Dialect-aware SQL checks |
| L12 | [Docker Compose config](https://docs.docker.com/reference/cli/docker/compose/config/) | Consumer configuration validation |
| L13 | [Biome language support](https://biomejs.dev/internals/language-support/) | Formatter/lint scope, not a universal semantic LSP |

## Interpretation boundaries

Language/framework rules in `repo-policy/docs/agent-standards` are proposed engineering policies for the user's stated case, not quoted vendor guarantees. They should be evaluated against actual locked dependency versions and the disclosed product requirements. Installation procedures and acceptance cases are instructions to the local agent, not claims that those commands were executed during this research.

Exact application-library versions from earlier chat messages are intentionally not restated as a newly certified compatible closure. The local agent must resolve any such pins and report observed incompatibilities before claiming a working toolchain.


## Additional sources verified during the second review

| ID | Primary source | Verified use / limitation |
|---|---|---|
| A1 | [Codex annotated release tag](https://api.github.com/repos/openai/codex/git/tags/4e21628f9ec9ee656650cd2b62ef92225725b5ac) | Dereferences to `be2951ea34f0d295ed0becf97079f92fa5f6950e`; release is not a moving branch |
| A2 | [Pinned Codex hook discovery](https://github.com/openai/codex/blob/be2951ea34f0d295ed0becf97079f92fa5f6950e/codex-rs/hooks/src/engine/discovery.rs) | Hook source combination, normalization, timeout clamping and trust gating |
| A3 | [Pinned SessionEnd implementation](https://github.com/openai/codex/blob/be2951ea34f0d295ed0becf97079f92fa5f6950e/codex-rs/hooks/src/events/session_end.rs) | Default 1 second, maximum 3, advisory completion semantics |
| A4 | [Pinned Serena configuration loader](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/serena/config/serena_config.py) | Project base_modes ignored, top-level local overrides, normalization/writeback |
| A5 | [Pinned Serena global template](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/serena/resources/serena_config.template.yml) | Base modes, tool timeout and loopback dashboard defaults |
| A6 | [Pinned interactive mode](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/serena/resources/config/modes/interactive.yml) | Clarification preference includes an explicit user-no-questions exception |
| A7 | [Pinned Codex context](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/serena/resources/config/contexts/codex.yml) | Deliberate exclusion of generic file/shell tools |
| A8 | [Pinned project.local template](https://github.com/oraios/serena/blob/949a27ef1e5fda1a6e7b561e777bcece345c6ffd/src/serena/resources/project.local.template.yml) | Purpose of non-versioned local overrides; merge semantics come from A4 |
| A9 | [Development-source external registry guide](https://github.com/oraios/serena/blob/c4dc91a7dac4ea560dc7658581a63dac33a76e6c/docs/03-special-guides/external_language_server_registration.md) | New API import location compared with stable S8; not a stable feature |
| A10 | [Pyodide worker documentation](https://pyodide.org/en/stable/usage/webworker.html) | Browser worker execution and communication; does not certify an app security sandbox |
| A11 | [Codex pinned hook state configuration](https://github.com/openai/codex/blob/be2951ea34f0d295ed0becf97079f92fa5f6950e/codex-rs/hooks/src/config_rules.rs) | User/session hook trust preferences; project layers cannot grant their own trusted hash |

| A12 | [MDN Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers) | Worker capabilities, network/storage and separate global scope; not a separate application trust origin |

S10 is a live newer-feature guide, not evidence that its API exists in stable Serena 1.7.0. A9 anchors the comparison to a concrete development commit. Source observations do not imply we executed these packages.
