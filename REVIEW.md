# Review rules

- Confirm `build/codex-pin.json` still says `0.155.1` and `codex --version` matches.
- Confirm app versions come from `build/stack-pin.json` schema 2, not ad-hoc latest.
- Confirm `python3 scripts/check_stack.py` reports required host tools OK.
- Reject Next.js, pnpm, and a second JS lockfile.
- Confirm `./setup` is the entry and `install/catalog.toml` matches `install/modules/`.
- Reject a root file named `install` (conflicts with `install/` on macOS).
- Reject `approval_policy = "untrusted"` and `features.web_search*`.
- Reject mixing `default_permissions` with `sandbox_mode` in `.codex/config.toml`.
- Portable `plugins/saint-tibo/plugin.json` must keep `$schema` and `name` only from the Agent Plugins 1.0.0 root set. Skills belong in `skills/`, not a root `skills` field.
- Repo skill names in `.agents/skills/` must not collide with plugin skill names.
- Marketplace `source.path` values start with `./` and resolve from the repo root.
- No secrets, tokens, or hackathon-private strategy in this public tree.
- Do not push `BAITC-Hacks/hack-a58598e0-saint-tibo` from review comments.
