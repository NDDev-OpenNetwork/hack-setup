# Review rules

- Confirm `build/codex-pin.json` still says `0.155.1` and `codex --version` matches.
- Confirm `build/stack-pin.json` `control` still names pin → `.codex/config.toml` → `just check`.
- Confirm app versions come from `build/stack-pin.json` schema 2, not ad-hoc latest.
- Confirm `python3 scripts/check_stack.py` reports required host tools OK.
- Reject a Makefile. Project commands are `just` / `justfile`.
- Reject Next.js, pnpm, a second JS lockfile, `typescript@6` in web,
  `@hey-api/openapi-ts@next`, `bun add shadcn`, and `opencv-python`.
- Confirm `./setup` is the entry and `install/catalog.toml` matches `install/modules/`.
- Reject a root file named `install` (conflicts with `install/` on macOS).
- Reject `approval_policy = "untrusted"` and `features.web_search*`.
- Require `.codex/config.toml` to match `build/stack-pin.json`
  `registered.session`: `approval_policy = "never"`,
  `sandbox_mode = "danger-full-access"`, `allow_login_shell = true`,
  `web_search = "live"`. Reject `default_permissions`,
  `[sandbox_workspace_write]`, `features.network_proxy`,
  `.codex/agents/*.toml`, and project `.codex/rules/*.rules`.
- Require models ADR 0007: `gpt-6-astra` + `gpt-5.6-sol` at `xhigh`,
  window `872000` / compact `700000`,
  `agents.enabled = false`, `features.multi_agent` and
  `features.multi_agent_v2` false. Reject luna/terra and bare `gpt-5.6`.
- Portable `plugins/saint-tibo/plugin.json` must keep `$schema` and `name` only from the Agent Plugins 1.0.0 root set. Skills belong in `skills/`, not a root `skills` field.
- Repo skill names in `.agents/skills/` must not collide with plugin skill names.
- Marketplace `source.path` values start with `./` and resolve from the repo root.
- No secrets, tokens, or hackathon-private strategy in this public tree.
- Do not push `BAITC-Hacks/hack-a58598e0-saint-tibo` from review comments.
