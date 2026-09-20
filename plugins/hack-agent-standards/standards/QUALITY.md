# Quality

Universe: `build/stack-pin.json` `quality.*`, `deploy.pipeline`,
`deploy.openobserve`, `deploy.vector`, `deploy.otel`.

Unless the owner said otherwise this turn.

Quality here means the change is complete, consistent with the rest of
the tree, and observable. It does not mean extra product scope.

## Default move

1. After the CORE map, decide the smallest proof that the changed
   behavior is real.
2. Run that proof. Setup today: `just check` and `just test` when
   pins, plugins, scripts, or tests moved. Do not invent a CI fleet.
3. Join `deploy.pipeline`: JSON logs → Vector → OpenObserve;
   traces/metrics OTLP → OpenObserve. A new running piece emits
   on that spine. It does not add a second APM, a second log
   format, or a silent code path.
4. If proof is red, repair toward the pin. Then re-run the same
   proof. Do not swap in a weaker check to look green.

## Pattern

Checks do not write. A command named check must not format, rewrite
lockfiles, regenerate clients, or apply migrations. Those are
separate intentional edits. When `api/` exists, contract proof is
a tmp dump of `app.openapi()` compared to committed
`contracts/openapi.json`, then typecheck of already-generated
clients. Regen is a write recipe named `generate-clients`
(add it when `api/` exists). CONTRACTS owns the dump. Do not
add that recipe in this setup repo.

Report what actually ran: command, tree, pass / fail / skip. Do not
claim a test, deploy, or host probe that has no output.

Observability is part of done, not a later wrap. Pipeline is JSON
logs → Vector → OpenObserve; traces and metrics OTLP → OpenObserve
(`deploy.pipeline`). Versions stay in the pin.

Setup-only work has no product runtime yet. Then quality is: the
tree stays synchronized (pin, config, generated standard, this
catalogue), the piece is complete, and the next module can plug into
the same telemetry spine. Pin `quality.required_gates` (OpenAPI
sync, `tsc` 7, Alembic, frontend + backend build) apply **when
product trees exist**. They are not `just check` in this repo.

## Done

- Proof matches the change. Setup gates are green when this plugin,
  the pin, or the checks moved.
- New behavior is consistent with callers and generated contracts.
- Telemetry is on the shared spine, or the change has no runtime.
- The report names commands and results. Unverified stays unnamed
  as success.

## Repair

- Red proof: fix the piece or the pin. Do not delete the check.
- Owner asked to skip a proof this turn: skip, name it, do not
  rewrite QUALITY.
- Owner wants a new default proof: update the pin and this file,
  then continue.
