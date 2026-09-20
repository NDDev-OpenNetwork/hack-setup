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
5. Why: ADRs 0001–0008

Do not fork numbers into frames, skills, or memories first. Edit pin +
config together, then `just check`.

## Current law (from the pin)

- CLI `0.155.1` / `rust-v0.155.1` / `be2951ea…`
- Session: `never` + `danger-full-access` + `web_search=live` (ADR 0006)
- Models: `gpt-6-astra` + `--profile sol` (`gpt-5.6-sol`), both `xhigh`
- Context `872000` / compact `700000` / usable `828400` (ADR 0007)
- Subagents off. No `.codex/agents/*.toml`. No `model_catalog_json`
- Commands: `justfile` only
- Web TS `7.0.2` only. bun installer. No Next.js / pnpm
- Forms: `@tanstack/react-form` `1.33.5` + Standard Schema (zod direct,
  no adapter). No react-hook-form / @hookform/resolvers / zod-form-adapter
- Frames plugin: `hack-agent-standards@saint-tibo` (ADR 0008)
- Plugin skill set: `registered.standards_plugin_skills` (15 names)

Tibo 1M/900k is documented, not runtime. Catalog max is 872000.

## Repo

This tree is `NDDev-OpenNetwork/hack-setup` on `main`.
`.codex/` is only `config.toml`.
Later remote (no git remote): `BAITC-Hacks/hack-a58598e0-saint-tibo`.
Setup owner stream: Danil.

## Done (committed on `main`, not pushed)

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
- Host codex: project trusted, `marketplace add .` done — config and both
  plugins are live on this host

## Next (blocked on user)

Product trees (`web/`, `api/`, …) and nested `AGENTS.md` copies only
when that code is authored. Copy from `nested/` in the same change.

Not requested: BAITC remote, push to origin, Serena/hooks install.
