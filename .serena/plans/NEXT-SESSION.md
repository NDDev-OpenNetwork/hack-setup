# Next session — 2026-09-20

Resume here. Chat is Russian. Repo files stay English. Do not add the
BAITC remote. No application source. Do not commit unless the owner asks.

## Mechanism

One loop. `build/stack-pin.json` `control` names it.

1. Law: `build/codex-pin.json` + `build/stack-pin.json`
2. Runtime: `.codex/config.toml` (projection of session + models + features)
3. Proof: `just check`. Ready: `just gate`
4. Detail: `plugins/hack-agent-standards/standards/INDEX.md` → CORE,
   QUALITY when proving, one area file. Prefer
   `$hack-agent-standards:<layer-skill>`. Router
   `$hack-agent-standards:apply-agent-standard`. Repo alias
   `$apply-stack-rule`. Pin numbers win. Owner turn beats a frame.
5. Why: ADRs 0001–0011

Do not fork numbers into frames, skills, or memories first. Edit pin +
config together, then `just check`.

## Current law (from the pin)

- CLI `0.155.1` / `rust-v0.155.1` / `be2951ea…`
- Session: `never` + `danger-full-access` + `web_search=live` (ADR 0006)
- Models: `gpt-6-astra` + `gpt-5.6-sol`, both `xhigh`. In-repo sol =
  `/review` or `codex -m gpt-5.6-sol` (project `model` outranks profile
  overlays). Module 20 writes `~/.codex/sol.config.toml` for unpinned
  dirs and strips legacy `[profiles.sol]` from the user config
- Context `872000` / compact `700000` / usable `828400` (ADR 0007)
- Subagents off. No `.codex/agents/*.toml`. No `model_catalog_json`
- Commands: `justfile` only
- Web TS `7.0.2` only. bun installer. No Next.js / pnpm
- Forms: `@tanstack/react-form` `1.33.5` + Standard Schema (zod direct,
  no adapter). No react-hook-form / @hookform/resolvers / zod-form-adapter
- LLM gateway: Bifrost `maximhq/bifrost:v2.2.1` (ADR 0010). API calls it
  via openai `3.16.2` `base_url`. No litellm in any env
- Frames plugin: `hack-agent-standards@saint-tibo` (ADR 0008)
- Workflow plugin: `hack-agent-workflow@saint-tibo` (ADR 0009) —
  serena-first `session-boot`, github-first `github-flow`,
  agent-first `agent-handoff`; invoke `$hack-agent-workflow:<name>`
- LSP plugin: `hack-agent-lsp@saint-tibo` (ADR 0011) — `lsp-map`
  + `lsp-setup`; the `lsp.*` matrix pins one server per language
- Plugin skill sets: `registered.{standards,workflow,lsp}_plugin_skills`

Tibo 1M/900k is documented, not runtime. Catalog max is 872000.

## Repo

This tree is `NDDev-OpenNetwork/hack-setup` on `main`.
`.codex/` is only `config.toml`.
Later remote (no git remote): `BAITC-Hacks/hack-a58598e0-saint-tibo`.
Setup owner stream: Danil.

## Done (committed and pushed on `main`)

- `9732012` catalogue: INDEX + CORE + QUALITY + 12 area files, all `ready`;
  15 layer skills; nested AGENTS templates; Motion kernel in `AGENTS.md`
- `2410c1c` module 20 installs the pinned `codex-package-<triple>.tar.gz`
  (verifies `packages.<platform>.sha256`); `install.sh` is fallback.
  ADRs 0001+0002 updated
- `06ace13` serena memories synced
- `c8ceb4b` forms switched to `@tanstack/react-form` + Standard Schema;
  `reverify` watches the new package; stale RHF refs removed
- Checker fails on `standards/*.md` orphans not linked in INDEX
- Host: all declared tools match the pin (`--strict` 14/14); Devin stale
  locks, research zip, merged branch cleaned
- Host codex: project trusted, `marketplace add .` done — config and all
  three plugins are live on this host
- `bc3c4c3` plugin install steps documented; legacy-profile ban scoped
  to `sol`
- `af3f9dd` checker enforces plugin cache parity with the repo
- `a0dba2e` `ty` `0.0.82` declared as a host tool
- `bdd614a` `hack-agent-workflow` plugin (ADR 0009): session-boot /
  github-flow / agent-handoff
- `1222e53`..`a5fa77d` LiteLLM → Bifrost gateway (ADR 0010); CI
  `check.yml` with artifacts + setup-e2e on ubuntu+macos; `dev` branch
  live; module 40 installs all plugins

## Next (blocked on user)

Product trees (`web/`, `api/`, …) and nested `AGENTS.md` copies only
when that code is authored. Copy from `nested/` in the same change.

Not requested: BAITC remote, push to origin, Serena/hooks install.
