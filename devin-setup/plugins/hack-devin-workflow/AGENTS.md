# hack-devin-workflow

Saint Tibo delivery workflow for Devin sessions. Invoke as
`/hack-devin-workflow:<skill>`.

- `session-boot` — open a session serena-first (state lives in the repo).
- `github-flow` — issues are SoT; lanes `feat/<issue>` → `<user>` → `dev` → `main`.
- `herdr-handoff` — spawn/steer workers as real Devin sessions in herdr
  panes; close your own session so the next one resumes from repo state.
- `hack-mode` — laziest working solution; done means live on the server.
- `ship-verify` — build+restart on the server, verify the real surface.
- `debt-ledger` — harvest `hack:`/`ponytail:` markers into one ledger.

Law lives in `devin-setup/build/devin-pin.json` + `build/stack-pin.json`.
The project hook (`.devin/hooks.v1.json` → `devin_mode.py`) injects the
ruleset, guards protected-branch pushes, and logs sessions.
