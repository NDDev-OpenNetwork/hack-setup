# 7. Codex models, context, no subagents

- Status: accepted
- Date: 2026-09-20
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The team setup must use two models only, extra-high reasoning, a
catalog-honest Codex context budget, and no Codex subagents.

## Decision Outcome

`build/stack-pin.json` `models` is the SoT. `.codex/config.toml` must
match.

- Primary: `gpt-6-astra` + `model_reasoning_effort = "xhigh"`.
- Secondary: `gpt-5.6-sol` + `xhigh` via `--profile sol`.
- `/review` uses `review_model = "gpt-5.6-sol"`.
- Reject `gpt-5.6-luna`, `gpt-5.6-terra`, bare `gpt-5.6` / `gpt-6` as
  session slugs. Wire effort is `xhigh`, not `extra-high`.
- Write the values 0.155.1 actually honors for both slugs:
  `model_context_window = 872_000`,
  `model_auto_compact_token_limit = 700_000`.
  Same pair on `[profiles.sol]`.
- Tibo's public recipe is `1000000` / `900000`
  (`@thsottiaux`, 2026-08-16,
  https://x.com/thsottiaux/status/2089082893804896524). Those keys are
  correct; those numbers are not runtime on this pin. Bundled + live
  remote catalog max is `872000`. CLI would clamp `1000000` → `872000`
  and `900000` → `784800` (`min(requested, resolved * 9 / 10)`).
  `700000` is below that 90% cap, so it applies as written.
- Usable `/status` is `872000 * 95 / 100` = `828400`. Compact at
  `700000` fires before that hard cap. API cards remain `1,050,000` /
  128k output.
- ChatGPT-auth remote catalog is authoritative over a patched bundled
  catalog ([openai/codex#41325](https://github.com/openai/codex/issues/41325)).
  Do not add `model_catalog_json` or a forged catalog to fake 1.05M.
- Subagents off: `agents.enabled = false`,
  `features.multi_agent = false`, `features.multi_agent_v2 = false`.
  Do not add `.codex/agents/*.toml`. `ultra` is a multi-agent effort;
  do not use it.

Astra is in the 0.155.1 bundled catalog (`visibility: list`,
`minimal_client_version` `0.153.0`). Access is still account-gated.
Astra safety monitoring can end a CLI task; that is not a project-config
switch.

## Confirmation

- `python3 scripts/check_codex_setup.py`
- `.codex/config.toml` matches `models`
- `codex debug models --bundled` still shows max `872000` for both slugs
