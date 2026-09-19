# 1. Codex CLI 0.155.1 pin

- Status: accepted
- Date: 2026-09-19
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The team needs one Codex CLI version and one artifact contract so three
people and later the private hackathon repo stay compatible. The previous
NDDev baseline was `0.146.0`. Local PATH had `0.153.2`.

## Decision Drivers

- Official stable channel agreement (GitHub, npm, Homebrew cask)
- Avoid prerelease churn during a hackathon
- Prefer current portable Agent Plugins 1.0.0 over the compatibility overlay
- Keep repo skills always discoverable without plugin install

## Considered Options

- Pin Codex CLI `0.155.1`
- Track `0.156.0-alpha.*`
- Keep `0.146.0` / `nddev-builder` checkers as source of truth

## Decision Outcome

Chosen option: pin Codex CLI `0.155.1` (`rust-v0.155.1`).

Author repo skills in `.agents/skills/`. Ship a portable root
`plugins/saint-tibo/plugin.json` with one uniquely named plugin skill.
Do not use `$CODEX_HOME/skills`, `approval_policy = "untrusted"`,
`features.web_search*`, or the discontinued `Codex.app` cask.

## Consequences

The team must upgrade local CLI copies to `0.155.1`. NDDev `0.146.0`
checkers are not the contract for new artifacts. Alphas may move plugin
or skill surfaces before the hackathon window.

## Confirmation

- `codex --version` prints `codex-cli 0.155.1`
- `python3 scripts/check_codex_setup.py` exits 0
- `build/codex-pin.json` matches the release tag

## More Information

- https://github.com/openai/codex/releases/tag/rust-v0.155.1
- https://developers.openai.com/codex/skills
- https://developers.openai.com/plugins/build/plugins
- https://agent-plugins.org/schemas/1.0.0/plugin.schema.json
