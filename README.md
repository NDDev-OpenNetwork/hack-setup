# hack-setup

Shared Codex `0.155.1` setup for a three-person team that will later work in
one private repo: `BAITC-Hacks/hack-a58598e0-saint-tibo`.

This public staging repo holds the project surfaces. Do not push the
hackathon repo until the owner says go.

## Install the pinned CLI

The first `codex` on `PATH` must be `0.155.1`:

```bash
# current machine uses bun global
bun add -g @openai/codex@0.155.1

# official channels
brew install --cask codex
# or
npm install -g @openai/codex@0.155.1
# or
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

```bash
codex --version
# expected: codex-cli 0.155.1
```

Desktop is the ChatGPT app (`brew install --cask chatgpt`). Do not install
the discontinued `codex-app` cask.

## After clone

1. Trust this project in Codex so `.codex/config.toml` loads.
2. Run `python3 scripts/check_codex_setup.py`.
3. Use repo skills from `.agents/skills/` (`/skills` or `$name`).
4. Custom agents: `mapper`, `reviewer`, `implementer`.

## Layout

See `AGENTS.md`. Pin and rationale: `build/codex-pin.json`,
`docs/adr/0001-codex-cli-155-pin.md`.
