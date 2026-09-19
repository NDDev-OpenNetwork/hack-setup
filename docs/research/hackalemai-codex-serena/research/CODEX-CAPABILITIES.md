# Codex instruction, policy and language-tool mechanisms

Scope: reference Codex 0.155.1 and official documentation checked 2026-09-20. Release and live-documentation status must not be conflated. Sources: [C1-C6](../SOURCES.md).

## Mechanism map

| Mechanism | Purpose | Use in this setup | Not a substitute for |
|---|---|---|---|
| `AGENTS.md` / `AGENTS.override.md` | Persistent natural-language instructions | Compact common policy and standards router | Machine-enforced validation |
| `.agents/skills/<name>/SKILL.md` | Discoverable task procedures | Semantic change, contract update, artifact validation, integration | Always-loaded mandatory invariants |
| Codex `.rules` | Command execution policy | Preserve intentional existing execution rules | Language style rules, LSP configuration, file-glob instructions |
| `config.toml` MCP entries | Tool-server connections | Serena stdio connection | Direct LSP client configuration |
| Hooks | Lifecycle/tool events | Optional activation reminder/cleanup; none required by default | A complete security boundary or test runner after every tool |
| Compiler/linter/schema/runtime CLI | Deterministic checks | Selected by changed area | Semantic code exploration |

## Instruction discovery

Codex first considers global guidance in its home, preferring AGENTS.override.md over AGENTS.md. Project discovery then follows the project-root-to-startup-working-directory chain: it prefers an override over the ordinary AGENTS file and can use configured project fallback filenames when those are absent. Do not extend the project fallback rule to global discovery without implementation evidence. Only one instruction file is selected per project directory. More specific guidance follows general guidance. The documented default combined project-document budget is 32 KiB. [C1]

**Our rule:** keep the root router small. Explicitly inspect applicable nested instructions before touching a target directory. A root-started session must not assume every descendant AGENTS file was eagerly included. Linked standards are files to read, not a built-in import syntax. Restart or explicitly reload relevant guidance after setup changes.

Do not import Cursor `.mdc` frontmatter, a `globs` field, `.github/instructions` or a directory called `rules/` and claim Codex will enforce it automatically. Such files can be source material for the router, but their interpretation is a setup convention unless the installed Codex explicitly supports it.

## Skills

Use the documented `.agents/skills` discovery layout. A skill has a `SKILL.md` with `name` and `description` frontmatter; task instructions load when the skill is selected. User-level and repository locations have different scope. [C2]

The shipped skills are portable procedures. Resolve repository paths from the real worktree, not from the skill's installation directory. Do not make correctness depend solely on implicit skill selection: common invariants also live in the root AGENTS. Avoid installing identical skills in both user and repo scopes without an explicit ownership decision.

## MCP and LSP

No generic arbitrary-LSP registry was identified in the inspected official Codex configuration. The supported integration selected here is:

```text
Codex client → MCP connection → Serena → SolidLSP adapter → language server
                                 ↓
                      project files in this worktree
```

A language server speaks LSP, not MCP. Installing `rust-analyzer` or `ty` does not by itself expose it to Codex. Do not invent `[lsp_servers]` entries or register a raw LSP executable as a Codex MCP server. Codex supports stdio and HTTP MCP transports; this setup chooses stdio for isolated local sessions. The MCP configuration includes command/args/environment and timeout controls. [C3]

Use the current MCP instructions/tool schemas returned by the installed server. Tool availability varies with Serena version, context and selected modes. Do not blindly reuse historical guidance saying Codex always ignores MCP initialization instructions.

## Execution policy

Codex `.rules` files use an execution-policy DSL, including `prefix_rule` decisions such as allow, prompt and forbidden. They are not a language-lint rule format. [C4]

No blanket shell/interpreter allowlist is supplied. Keep execution permissions and style instructions separate. Preserve the user's existing autonomous authorization for the intended workspace. A permissive shell profile is not a claim that MCP tools, hooks and all other access paths are constrained identically.

## Hooks and trust

The official canonical feature flag is `hooks`; `codex_hooks` is a deprecated alias. Hooks can receive lifecycle events and selected tool calls. User and trusted project configuration have different trust implications. Not every tool path is covered, and a hook is not a universal execution monitor. [C5]

The selected implementation also has a separate trust gate for the normalized non-managed hook definition; project trust and a feature flag do not grant this trust. Its hash is not an automatic verification of the contents of a script at the configured path. [A2,A11]

See the [hook recipe](../setup/HOOKS-AND-EXEC-POLICY.md) for the stable Serena-specific limitations. A `SessionStart` hook may run before MCP is ready: a reminder to activate is not evidence that activation occurred. Keep startup handling idempotent.

Codex project trust and Serena project trust are separate. Inspect effective configuration and permissions, not only the presence of a file. Do not overwrite a permission model or combine mutually exclusive modern and legacy fields. [C6]
