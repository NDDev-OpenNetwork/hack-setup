# ADR 0016: Hook trust is self-managed by repair

Date: 2026-09-21. Status: accepted. Extends ADR 0015.

## Context

Codex 0.155.1 runs a non-managed hook only when a `trusted_hash`
recorded in config state matches the hook definition hash
(`codex-rs/hooks` `engine/discovery.rs`: `enabled && (bypass ||
trust_status ∈ {Managed, Trusted})`). Trust is read **only** from the
User and SessionFlags config layers — project layers can declare hooks
but cannot self-trust (`config_rules.rs` comment). Editing
`.codex/hooks.json` therefore silently disables every hook until a human
re-trusts it via `/hooks`.

Verified on a live host: `codex exec` prints `hook: <Event> Completed`
only after the managed state block exists; before that the hooks were
skipped without an error.

Also learned from upstream issues:

- openai/codex#34428 — `compact_prompt` is ignored on the remote
  compaction path used by the default OpenAI provider; it only applies
  to local compaction. Our real compaction protection is the
  `SessionStart` `compact` matcher re-injecting the ruleset.
- openai/codex#33238, #11004 — Codex App/Desktop shadows project
  `developer_instructions` with a host-generated thread value. The
  reliable channel in App threads is `AGENTS.md` (`<INSTRUCTIONS>`
  block); `developer_instructions` still helps CLI sessions.
- `SessionEnd`/`Interrupt` clamp hook `timeout` to 3 s; larger values
  warn at startup.

## Decision

`scripts/repair_setup.py` (`fix_hook_trust`) ports
`hook_hash`/`version_for_toml` to Python: sha256 over the canonical JSON
of the normalized hook identity `{event_name, matcher?, hooks:[handler]}`.
It writes one managed block per handler into `~/.codex/config.toml`:

```toml
[hooks.state."<abs hooks.json path>:<event>:<group>:<handler>"]  # hack-setup
trusted_hash = "sha256:…"  # hack-setup
```

Only keys prefixed with this repo's `hooks.json` path are ever touched;
foreign state (e.g. cmux's user hooks) is left alone. Module 20 calls
`repair_setup.py --only hook-trust` at install; `just repair` re-trusts
after any hook edit, so the loop is: edit hooks → `just repair` →
trusted again. `--root <repo>` targets other checkouts (vibestrap).

Timeouts for `SessionEnd`/`Interrupt` are pinned at 3 s in
`.codex/hooks.json`.

## Consequences

- Hooks are live from the first session on a fresh host — no manual
  `/hooks` review step in the setup flow.
- The trust gate still protects against *unmanaged* hook changes; our
  block only certifies the pinned definitions this repo ships.
- A teammate pulling hook changes must run `just repair` once (or the
  hooks stay skipped until `/hooks` review). AGENTS.md states this.
