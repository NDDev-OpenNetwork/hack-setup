# Where each preparation file belongs

## During preparation

Keep the complete research/setup library in an authorized preparation directory outside the competition submission repository. Give the local agent BOOTSTRAP-PROMPT.md and the complete directory. The agent may configure Codex home, isolated tools and permitted generic skills while preserving existing personal settings.

`repo-policy` is an instruction payload, not an application scaffold. It contains no runtime modules, endpoints, UI implementation or business fixtures. Do not create product directories simply to install a scoped instruction template.

## When project metadata is permitted

| Payload | Destination / action |
|---|---|
| `repo-policy/AGENTS.md` | Merge at actual repository root |
| `repo-policy/docs/agent-standards/` | Copy as the canonical standards library; preserve relative links |
| Selected `repo-policy/.agents/skills/*/SKILL.md` | Repository `.agents/skills` or an intentional user-level installation, not duplicate uncontrolled copies |
| `scoped-templates/*-AGENTS.md` | Merge content into existing actual area directories, adapting the path map |
| `setup/GLOBAL-AGENTS-SNIPPET.md` guidance | Merge into existing global AGENTS, not blindly into an override |
| Config recipes | Resolve real paths, validate against installed CLI, then merge only the needed tables/keys |
| Research, source register, acceptance | Keep available as reference metadata; not all of it belongs in always-loaded instructions |

## Do not load the whole pack automatically

The root router selects a small set of relevant standards. Skills package repeated procedures and do not replace direct rule loading. The setup agent can read all research once; a product agent should not spend each feature turn re-reading the entire preparation library.

Keep one canonical version of a policy. If a user-level generic skill needs repository rules, it resolves the actual root and reads that repository's policy. Do not embed stale copies of the whole stack into every skill or Serena memory.


## Shared/local ownership in revision 1.1

The shared `.serena/project.yml` contains portable conventions. `.serena/project.local.yml` owns machine-specific overrides and is not committed. A local `ls_specific_settings` mapping replaces the complete shared mapping in stable 1.7.0; materialize every required entry. Isolated `SERENA_HOME/serena_config.yml` owns base modes, tool budget and exact project trust. Codex MCP paths belong in the chosen host/session configuration layer, not a copy of another developer's absolute paths.

Keep the audit/source/version documents outside always-loaded context. They are setup evidence, not extra instructions to read on each feature turn. Only install project metadata when competition rules permit it.
