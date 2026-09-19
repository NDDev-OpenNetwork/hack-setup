# Quality

Pins: Biome `2.5.14`, TypeScript `7.0.2`, Vitest `5.0.1`, Playwright `1.63.0`,
Ruff `0.16.8`, ty `0.0.82`, pytest `9.1.1`, just `1.58.0`.

## This staging repo

```bash
./setup --status
python3 scripts/check_codex_setup.py
python3 scripts/check_stack.py
codex --version
```

`just gate` is those four. `just check` is the two Python scripts only.
Do not add a Makefile.
`just reverify` is hackathon-day / network.

Do not claim a pass without running the command.

## Check vs fix

Check commands must not silently format, rewrite lockfiles, generate
clients, or apply migrations. Those are intentional edits with a diff.

## When product code exists

- JS/TS lint+format: Biome. Types: `tsc` 7, not Biome.
- Web unit: Vitest. Web e2e and HTML reports: Playwright.
- Python lint: Ruff. Python types: ty `0.0.82`.
- Required product gates: OpenAPI contract sync, `tsc` 7, Alembic heads,
  frontend build, backend build.

Host brew/uv-tool ruff or pytest may drift. That does not rewrite the pin.
`--strict` fails declared host drift; the default doctor does not.
