# 1. Codex CLI 0.155.1 pin

- Status: accepted
- Date: 2026-09-19
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The team needs one official Codex CLI version and one installer contract
so three people, and later the private hackathon repo, stay compatible.

## Decision Drivers

- Official stable channel, not prerelease
- Pin the official `install.sh` URL and sha256
- Portable Agent Plugins 1.0.0
- Repo skills stay discoverable without plugin install

## Considered Options

- Pin Codex CLI `0.155.1` (`rust-v0.155.1`)
- Track `0.156.0-alpha.*`
- Use the unpinned `chatgpt.com/codex/install.sh`

## Decision Outcome

Chosen option: pin Codex CLI `0.155.1`. That is the current non-prerelease
GitHub release as of 2026-09-18; later `0.156.0-alpha.*` tags stay out.

Author repo skills in `.agents/skills/`. Ship a portable
`plugins/saint-tibo/plugin.json` with one uniquely named plugin skill.
Install the pinned `codex-package-<triple>.tar.gz` after sha256 check
into `~/.local/bin`, then symlink `$REPO/.local/bin/codex`. The hashed
official `install.sh` is the fallback for a platform without a pinned
package entry.

Do not use `$CODEX_HOME/skills`, `approval_policy = "untrusted"`,
`features.web_search*`, the discontinued `Codex.app` cask, or an unpinned
installer URL. Session law is ADR 0006 (`never` +
`danger-full-access`), not `--full-auto`.

## Consequences

`./setup` is the only supported way to get the pinned CLI. Alphas may
move plugin or skill surfaces before the hackathon window.

## Confirmation

- `codex --version` prints `codex-cli 0.155.1`
- `python3 scripts/check_codex_setup.py` exits 0
- `build/codex-pin.json` matches the release tag
- Module `20-codex-cli` verifies `packages.<platform>.sha256` before install

## More Information

- https://github.com/openai/codex/releases/tag/rust-v0.155.1
- https://developers.openai.com/codex/skills
- https://developers.openai.com/plugins/build/plugins
- https://agent-plugins.org/schemas/1.0.0/plugin.schema.json
