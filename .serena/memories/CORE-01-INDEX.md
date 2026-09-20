<!-- Memory Metadata
Last updated: 2026-09-20
Last commit: bc3c4c3 fix(docs+check): document plugin install steps; scope legacy-profile ban to sol
Scope: AGENTS.md, build/, .agents/, .codex/, plugins/saint-tibo/, plugins/hack-agent-standards/, install/, justfile, docs/adr/
Area: CORE
-->

# CORE-01-INDEX

## Purpose

Index durable knowledge for the Codex 0.155.1 team setup repository. No application code.

## Source Of Truth

- Control loop: pin (`build/codex-pin.json` + `build/stack-pin.json`) → runtime (`.codex/config.toml`) → proof (`just check` / `just gate`) → on-demand frames (`plugins/hack-agent-standards/standards/INDEX.md`). `AGENTS.md` is the router plus Motion kernel.
- Plugin skills: DirectChildren under `plugins/hack-agent-standards/skills/`. Invoke `$hack-agent-standards:<name>`. Pin SoT: `registered.standards_plugin_skills`.
- Nested AGENTS templates: `plugins/hack-agent-standards/nested/`. Copy in the same change that creates `web/` `api/` `mobile/` `desktop/` `telegram/` `infra/`.
- `AGENTS.md`: Codex project instructions. Router to the standards plugin INDEX. Combined cap 32 KiB.
- `plugins/hack-agent-standards/standards/`: on-demand frames. Pin numbers win. Owner turn beats a frame. ADR 0008.
- `docs/adr/0001`–`0009`: accepted decisions. Session law is ADR 0006. Models/context/no-subagents is ADR 0007. Frames plugin is ADR 0008.
- `build/codex-pin.json`: CLI pin plus official installer/package sha256.
- `build/stack-pin.json`: product stack schema 2. `control.rules` is the plugin INDEX.
- `build/stack-standard.md`: generated from the pin via `python3 scripts/check_stack.py --write`.
- `justfile`: project command runner (`just` `1.58.0`). No Makefile.
- Codex surfaces: `mem:CODEX-01-PIN`, `mem:CODEX-02-SURFACES`.
- Stack: `mem:STACK-01-PIN`.
- Bootstrap: `mem:INFRA-01-BOOTSTRAP`.
- Checks: `mem:TEST-01-CHECKS`.

`docs/research/` is an archive. It is not runtime law. `docs/rules/` and `docs/agent-standards/` must not exist.

## Entry Points

- `./setup`: macOS/Linux catalog install after clone.
- `just gate`: AGENTS four-command ready gate.
- `just check`: artifact validator + host doctor.
- `codex --version`: runtime CLI pin proof.

## Current Behavior

Author remote is `NDDev-OpenNetwork/hack-setup`. Later working remote is `BAITC-Hacks/hack-a58598e0-saint-tibo` and is not pushed unless the owner asks. `./setup` installs only Codex plus Node/bun/uv/Python. Isolated Serena and `hooks.json` are not installed by `./setup`. Web typescript is only `7.0.2`. Codex session models are `gpt-6-astra` / `gpt-5.6-sol` at `xhigh`, window `872000` / compact `700000`. Codex subagents are off. Setup owner stream is Danil. This public repo may land setup commits on `main` when Danil asked. The catalogue and layer skills exist. Product trees do not.

## Invariants

- Codex CLI pin is `0.155.1` / `rust-v0.155.1`.
- Root entry is `./setup`, not a file named `install`.
- Project commands are `just`. Do not add a Makefile.
- Repo skill names do not collide with either plugin skill set.
- Marketplace lists `saint-tibo` then `hack-agent-standards`.
- No secrets in the public tree.
- Do not add pnpm, Next.js, R3F, a second JS lockfile, typescript@6 in web, `@hey-api/openapi-ts@next`, `bun add shadcn`, or unconstrained `docling` / `opencv-python`.
- Do not create empty product trees only to hold a frame or nested AGENTS.md.

## Verification

- `just gate`
- `just test`
