# Serena-first change procedure

## Establish the semantic workspace

Confirm the exact worktree path and branch. Check the connected Serena project before source edits. Do not activate another developer's checkout or a common Git metadata directory. Use the server's actual advertised tool names and schemas; context/modes can change what is exposed.

Read the installed Serena instructions when needed, and relevant existing project notes. Onboarding or memories are navigation aids, not authority over AGENTS or the current source. Never store credentials, full student documents or unverified claims in memories.

## Choose the narrow operation

| Question | Preferred approach |
|---|---|
| Where is this class/function/component? | Symbol search constrained to likely area |
| What is in this file? | Symbol overview, then relevant bodies |
| What can this change affect? | References/callers/implementations, plus explicit external contract search |
| Change an entire supported symbol body | Symbol replacement after reading current body |
| Rename a supported internal symbol | Semantic rename, then inspect references and diff |
| Change a small expression/import/string | Narrow text patch when it preserves structure better |
| Find route strings, localization keys, env names, configuration values | Bounded text/schema search |
| Edit binary documents or notebook containers | Document-aware tooling, not code-symbol replacement |

Start with symbol names and file constraints rather than dumping the repository. Read enough caller/callee and resource ownership context to establish actual behavior. Avoid full symbol bodies when signatures and references answer the question. Conversely, do not edit a function solely from its name or a truncated result.

## Refactoring boundaries

LSP rename is not a protocol migration. Search serialized field names, routes, SQL columns, reflection, templates, localization keys, events and generated consumers separately. Public API changes use the contracts procedure. Confirm positional encodings on Unicode-containing files before automated offset-based edits.

Do not symbol-edit generated files. Edit the source definition and regenerate. Keep generated declarations discoverable when imports need them; generation ownership and indexing exclusion are different concerns.

## Validation and recovery

After a coherent change, request supported diagnostics for the changed area and run the relevant compiler/parser/runtime check. Distinguish stale results, server failure, unsupported method and a genuine defect. An empty or truncated response is not proof of correctness.

Try one targeted recovery for a stale/broken server: correct root/environment, refresh/restart the affected server when appropriate, and retry the narrow operation. Do not restart every server after each file. If semantic tooling is still unavailable, use an explicit narrow fallback and record the limitation. Keep the project compiler authoritative.

## Parallelism and state

Each session owns its Serena process and worktree-local identity. Shared immutable download caches may be reused safely; do not share mutable active-project state or edit sessions. Do not include sibling worktrees as additional workspace folders. Clear only session-specific ephemeral state, not shared code or another agent's caches.

Memories should describe stable navigation facts with the relevant commit/context and be refreshed after material changes. They cannot override source, contracts or verified current instructions. Keep final handoff facts in versioned project documents when they affect other agents.


## Effective configuration, not merely file content

Inspect effective modes, root, advertised tools and actual child executables. In the selected stable release, project `base_modes` is ignored; global base modes are configured in the isolated Serena home. Its Codex context deliberately delegates generic file/shell operations to native Codex tools. Never invent an absent Serena command just to comply with a preference.

Broad directory-name exclusions can hide authored source or imported declarations. Compare index scope with tracked authored files, and inspect global/project/Git ignore rules before treating no results as proof of absence. Ignore rules are not a security boundary.

If an edit or rename times out, inspect the files and diff first. Only retry when the observed state shows it is appropriate. Keep the server-side execution budget below the MCP caller budget with a measured margin; this reduces ambiguous timeout windows but is not transaction rollback.
