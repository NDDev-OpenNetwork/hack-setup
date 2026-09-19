# Configuration recipes, reviewed revision 1.1

These are **templates**, not a configuration installed or accepted on your host. Resolve every placeholder, preserve existing configuration, and inspect the effective configuration and warnings. Baselines: Codex 0.155.1 and Serena 1.7.0, with immutable commits in [the evidence ledger](../audit/SOURCE-EVIDENCE.md).

## 1. Codex MCP connection: host/session-owned

Register one intentional Serena connection, bound to this exact worktree. Do not commit absolute machine paths into shared project configuration.

```toml
[mcp_servers.serena]
command = "/ABSOLUTE/PATH/TO/serena"
args = ["start-mcp-server", "--context", "codex", "--project", "/ABSOLUTE/PATH/TO/WORKTREE"]
startup_timeout_sec = 120
tool_timeout_sec = 120

[mcp_servers.serena.env]
SERENA_HOME = "/ABSOLUTE/PATH/TO/PREPARATION/serena-homes/worktree-a"
```

The timeouts are this pack's starting choices, not benchmark results. Warm dependencies before normal sessions. A global `--project-from-cwd` alternative is acceptable only after testing the child process working directory in the actual CLI/app/IDE. Do not register both alternatives accidentally.

`SERENA_HOME` above reaches the MCP child, not other shell processes or Codex hooks. The optional hook recipe explicitly supplies the matching home. Separate project/worktree state; record the actual root returned by tools. No wildcard trust or credentials are implied.

## 2. Serena global configuration, inside that isolated SERENA_HOME

Merge these keys into `SERENA_HOME/serena_config.yml` for this preparation profile. They must not replace an unrelated global configuration.

```yaml
language_backend: LSP
line_ending: lf
base_modes:
  - editing
default_modes: []
tool_timeout: 90
web_dashboard: true
web_dashboard_open_on_launch: false
web_dashboard_listen_address: 127.0.0.1
web_dashboard_trusted_hosts:
  - 127.0.0.1
  - localhost
trace_lsp_communication: false
trusted_project_path_patterns:
  - "/ABSOLUTE/PATH/TO/WORKTREE"
```

**Scope matters:** in Serena 1.7.0 the project loader explicitly warns that `base_modes` in `project.yml` is deprecated and ignored. Set it in this isolated **global** configuration. Project `default_modes`/`added_modes` can still add modes; inspect the effective combination. Never infer behavior just from a template comment. [A4,A5,A6]

The upstream default interactive mode asks for clarification but expressly respects a user instruction to proceed without questions. It was not a guaranteed blocker. The explicit editing-only base removes ambiguity for this team's autonomous profile; it does not disable runtime permissions or necessary correctness checks.

Budget ordering is intentional: Serena tool budget 90 seconds is below Codex's 120-second tool budget, leaving a response margin. This does not guarantee cancellation or rollback. A timed-out mutation has an unknown outcome until current files and the diff are inspected. Do not blindly replay it. Adjust budgets together using host observations.

The dashboard stays loopback-only and does not open a new browser tab per session. Indexing/logging preferences are not access-control boundaries.

## 3. Portable shared project metadata

Apply only when the real project exists and metadata is permitted. This example assumes Python and TypeScript sources. For a different scope, generate the installed template and keep only relevant languages.

```yaml
project_name: hackalemai
language_backend: LSP
language_servers:
  - python_ty
  - typescript
encoding: utf-8
line_ending: lf
default_modes: []
added_modes: []
ignore_all_files_in_gitignore: true
ls_workspace_folders:
  - .
ls_additional_workspace_folders: []
ignored_paths:
  - "**/node_modules/**"
  - "**/.venv/**"
  - "**/__pycache__/**"
  - "**/.dart_tool/**"
  - "**/.git/**"
  - "**/.worktrees/**"
  - "**/.env"
  - "**/.env.*"
read_only: false
excluded_tools: []
included_optional_tools: []
ls_specific_settings:
  typescript:
    typescript_version: "5.9.3"
    typescript_language_server_version: "5.1.3"
initial_prompt: >-
  Work autonomously within the authorized task and this exact worktree.
  Read applicable repository instructions. Prefer supported symbolic
  exploration and precise edits; use native Codex text/shell tools where
  the codex context excludes Serena equivalents or semantic coverage is
  absent. Validate changed behavior using the actual compiler or consumer.
  Report unsupported or untested capabilities without inventing success.
```

The TypeScript pair reproduces the stable adapter defaults, **not full native-TypeScript compatibility**. `python_ty` without a local override uses the adapter default; it must not be silently accepted as the selected up-to-date project checker. Resolve the selected ty version in the local profile below, then test it.

Remove or narrow an ignore rule that hides authored sources. In particular, do **not** add universal `**/build/**`, `**/dist/**`, `**/target/**`, or `**/uploads/**` rules. Add verified output directories individually after ownership inspection. Review inherited `.gitignore` and global Serena exclusions too. Dependency directories above are conventional starting assumptions, not exceptions to this rule.

Generated API clients/declarations can be needed for import resolution. Do not blanket-exclude them or delete them to reduce index size. Excluding secrets reduces incidental indexing; it does not stop an authorized shell or another tool from accessing them. An explicit non-secret `.env.example` can be read with a text tool.

Project-specific LS settings require Serena project trust. The `codex` context excludes Serena `read_file`, `find_file`, `list_dir`, `create_text_file`, `replace_content`, and `execute_shell_command`; use Codex native tools for those operations, while preserving semantic-first exploration. [A7]

## 4. Worktree-local overrides, not committed

Write `.serena/project.local.yml` alongside the shared file; verify that Git excludes it. Serena 1.7.0 applies this with a **top-level dictionary update**, not recursive deep merge. Therefore a local `ls_specific_settings` mapping replaces the entire shared mapping. Include every still-required entry, not just the changed language. [A4,A8]

```yaml
project_name: hackalemai-worktree-a
ls_specific_settings:
  python_ty:
    ls_path: "/ABSOLUTE/PATH/TO/PINNED/ty"
  typescript:
    typescript_version: "5.9.3"
    typescript_language_server_version: "5.1.3"
```

Use the resolved ty executable path, not a shell command ending with `server`. Record its exact selected version and hash. Replace TS navigation pins only after the compatibility procedure. Keep a clear source of ownership for shared defaults and local materialization so they do not drift unnoticed.

Serena can normalize an incomplete configuration and save defaults during activation. Inspect the resulting diff; do not confuse this with a read-only operation. Generate the full installed template first when preparing a real configuration.

## 5. Optional document and infrastructure language servers

The available candidate IDs include `bash`, `markdown`, `yaml`, `json`, `toml`, `html`, and `scss`. Add only needed and behavior-tested providers to the existing language list. The `.scss` identifier covers the built-in CSS/SCSS/Sass adapter. Schema association remains a separate configuration task. No competing Python/TypeScript providers should own the same files.

## 6. Flutter/Dart

Do not provide a deploy-looking YAML block with an invented version. First read the actual Flutter-bundled Dart version, verify a matching standalone archive exists for the host architecture, verify its integrity, then add that exact value as `ls_specific_settings.dart.dart_sdk_version` and enable `dart`. When updating a local mapping, retain the other required LS entries.

The stable Dart adapter has no demonstrated `ls_path` override. Its download table includes macOS x64/arm64 and Linux x64 but **no Linux arm64 entry**. A missing platform is unsupported in this adapter, not a reason to substitute an x64 binary blindly. Matching a version string does not prove Flutter package analysis. [S5]

A native adapter integration is separate work. The current external-registration guide does not apply unchanged to stable 1.7.0; see [the versioned adapter decision](../research/COMPATIBILITY.md).

## 7. Permissions

Preserve the user's already authorized autonomous execution profile. Do not mix mutually incompatible old/new permission models, add generic interpreter allowlists, bypass hook trust silently, or change unrelated accounts. Runtime autonomy, hook trust, project trust, and language-analysis behavior are separate controls.

Sources [S2,S4-S8,A2-A8] resolve through [SOURCES.md](../SOURCES.md). Local behavioral acceptance remains mandatory before a capability is marked ready.
