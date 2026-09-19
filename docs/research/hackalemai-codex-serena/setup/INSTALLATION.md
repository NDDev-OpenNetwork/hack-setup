# Installation and activation plan

All commands below are setup recipes, not evidence they were executed. Resolve absolute paths and versions on the host. Do not run a recursive setup over unrelated repositories. Sources: [C3,C6,S1-S10,L1-L13](../SOURCES.md).

## 1. Inventory and preserve

Record OS/architecture, `codex --version`, `uv --version`, Node/Bun/Go/Rust/Flutter versions, working directory, active branch and PATH. Inspect installed CLI help before relying on subcommand flags. Back up the Codex files being changed. Never copy auth.json, provider keys, shell secrets or document contents into the report.

Check both global and project configuration, duplicate MCP servers and user/repository skills. Preserve the existing working model/provider and autonomous permission settings. Keep this pack outside the competition application until repository metadata is allowed.

## 2. Isolated Serena installation

The inspected release is Python-compatible with 3.14, but its package dependencies must not be merged into the application environment. A reproducible source pin is:

```sh
uv tool install --python "/ABSOLUTE/PATH/TO/VERIFIED/PYTHON" 'git+https://github.com/oraios/serena@949a27ef1e5fda1a6e7b561e777bcece345c6ffd'
```

Resolve that interpreter path to an exact verified supported Python release first; a floating `--python 3.14` selector can fetch a patch newer than the historical cutoff. Use a supported installer date filter where available, and record any remaining unpinned closure. This uses distribution `serena-agent`, which exposes `serena` and `serena-hooks`. It is a source-pinned installation, not a fully frozen transitive-environment claim. Resolve and record the tool environment, executable paths, Python patch version, and installed dependencies. Reuse a matching installation rather than replacing it blindly. Inspect `uv tool install --help` when adapting existing installations.

Use the actual resolved absolute `serena` executable in MCP configuration. The uv tool binary directory may not be in a GUI application's PATH. Do not guess that `/usr/local/bin`, `/opt/homebrew/bin` or `$HOME/.local/bin` is always correct.

## 3. Server provisioning ownership

| Family | Who provisions it | Required action |
|---|---|---|
| Python ty | Setup-owned isolated tool, or Serena-managed pin | Choose exact ty version; set `python_ty.ls_path` to executable only, or set `ty_version`; adapter appends `server` |
| Python fallback | Serena adapter or explicit supported installation | Read the selected adapter's settings before assigning paths; do not activate fallback simultaneously |
| TypeScript navigation | Serena-managed compatible TypeScript + LS packages | Record engine and server pins separately; the inspected defaults are TS 5.9.3 / LS 5.1.3 |
| Rust | Toolchain-owned rust-analyzer/rust-src | Install for the selected toolchain; verify what executable the Serena adapter actually starts |
| Go | Toolchain/setup-owned gopls | Install a verified exact release compatible with Go; verify adapter process identity |
| Dart | Stable Serena adapter downloads SDK | Set exact Flutter-matching `dart_sdk_version`, verify checksum and Flutter import behavior |
| Bash/JSON/YAML/HTML/SCSS | Selected Serena adapter dependency mechanism | Let the inspected adapter provision or use only its documented override; do not create duplicate global/latest packages |
| Markdown | Marksman binary/adapter-managed dependency | Record actual release, architecture and executable; behavior-test links |
| TOML | LSP-enabled Taplo binary | Verify language-server component, not just CLI formatter |
| Native mobile/C++/LaTeX | Conditional explicit profile | Install SDK/JDK/Xcode/compilation database only when needed |

When a release is not fixed in this document, follow [VERSION-RESOLUTION.md](VERSION-RESOLUTION.md): filter by the historical cutoff before selecting a stable release, compare with adapter expectations, pin the artifact and record both release and inspection dates. Never fill the manifest with an invented version. An adapter-managed default is not necessarily the latest upstream release.

For setup-owned ty, a command form is `uv tool install ty==<verified-version>`; for gopls use `go install golang.org/x/tools/gopls@<verified-tag>`. Angle-bracket placeholders are **not executable pins**. Rust components are installed into the selected rustup toolchain. Use upstream platform instructions and integrity verification for standalone binaries.

## 4. Worktree-local activation

Start Codex in the intended worktree. Give each session its own stdio Serena process and an unambiguous root. Do not reuse one HTTP Serena instance with a mutable active project across three developers. The server and tools must read/write the same files as Codex.

Generate project metadata from the installed Serena template using verified CLI help, or merge only documented keys. The field is `language_servers`. Enable languages present in the project; `ls_workspace_folders` must refer to existing directories inside this worktree. Configure import/module roots rather than indexing dependency/build caches.

If isolation uses `SERENA_HOME`, make it stable for a worktree and shared by that worktree's MCP process and hook commands. Copy or merge necessary trusted configuration into that home. Prefer selective per-project settings rather than a process-wide broad trust pattern. Never use another developer's checkout as an additional workspace folder.

## 5. Install instruction layers

Merge the global snippet into the existing user guidance. Keep the preparation library and its source register together. Once permitted, copy `repo-policy/AGENTS.md`, its `docs/agent-standards` directory and selected `.agents/skills` into the repository as a coherent set. Install scoped templates only after adapting path mappings to actual directories.

For pre-event use, install generic skills in the user skill directory or keep them in the preparation workspace. Do not populate an application skeleton. A project rule cannot be considered loaded solely because it exists on disk: test the router and discovery from the actual startup directory.

## 6. Warm-up without product code

Resolve allowed tool dependencies and caches. Use disposable, non-product verification inputs outside the submission repository where event rules permit. Exercise MCP and LSP, then run the acceptance matrix. No full application build or authored product feature is part of pre-event preparation.

Do not keep download/install commands on each agent startup, every hook, or every edit. If cold-start takes long, fix provisioning; do not turn every runtime tool call into an unlimited timeout.

## Provisioning versus product package-manager policy

Keep Node's supporting package tooling available when the selected Serena adapter uses npm internally to provision a language server. The product can still use Bun as its single JS dependency manager. Do not remove npm merely to enforce an application lockfile convention; tool-owned dependency provisioning is a separate graph. Record what the adapter actually installs.


## Source, configuration and platform traps found during review

Before enabling a profile, inspect [the audit report](../audit/AUDIT-REPORT.md). In particular: stable project `base_modes` is ignored, project.local mappings replace top-level values, SessionEnd is capped at three seconds, hook trust is separate, and the newer external-LSP registration API is not in stable 1.7.0. The reviewed [configuration recipes](CONFIG-RECIPES.md) separate shared defaults from host-local paths.

Record native host architecture without guessing from laptop branding or VPS size. Do not assume Linux arm64 support from macOS arm64 support. A portable source pin is not proof of a prebuilt binary for every platform.

For multi-environment Python projects, one server cannot be presumed to infer every service's environment. Verify each selected service import path and interpreter. Use documented per-project configuration or separate, explicitly selected project roots when necessary; do not install all product dependencies into one tool environment to conceal resolution errors.
