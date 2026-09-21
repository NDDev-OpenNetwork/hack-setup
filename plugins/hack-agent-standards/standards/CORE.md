# Core

Universe: `build/stack-pin.json` (whole pin). Locales `locales`.
Observability `deploy.openobserve`, `deploy.vector`, `deploy.otel`.
Data ownership `data.*`.

Unless the owner said otherwise this turn.

The agent develops. These frames stop invented scope and a second
architecture. They are not permission gates.

This repository is still setup. Apply the same motion to setup
components (`install/`, `plugins/`, pins, checks). Do not create
product trees to hold a standard.

## Default move

1. Read the owner message. Where it specifies a path, follow it.
   Where it does not, use this file and the matching area standard.
2. Map what already exists and what the request will touch. Do not
   start writing before that map.
3. If the module is missing, build the whole module: complete,
   consistent with the rest of the tree, no hollow stubs that the
   next turn must invent around.
4. If the module exists, finish the touched piece to the same bar:
   structure, behavior, dictionaries, telemetry, proof.
5. Work on an agent-owned branch. Do not enter another person's
   named branch (`danil` / `artem` / `ivan`) or a foreign agent
   branch. Setup on this public repo may land on `main` when Danil
   asked for that.
6. When the piece is ready, merge it into the owner's named branch.
7. Owner merge beacons — «слить», «лить», «залить», «закинуть»,
   «отправить в дев», «можем вливать»: update the named branch from
   `dev`, resolve conflicts on our side, keep the piece working,
   merge that named branch into `dev`.
8. Owner says ship / «в прод»: treat current `dev` as the candidate.
   Read GitHub history on `dev`, verify the candidate, merge `dev`
   into `main`. Deploy is from `main` only.

Do not push `main` or merge to `dev` unless the owner asked for that
step.

## Pattern

One modular monorepo. Cut **layers first** (folders such as `web/`,
`api/`, workers, clients, `infra/`). Inside a layer, cut **product
modules** as isolated DDD units so a fix or an extension stays inside
one box.

A request is implemented **through the layers it needs**, not as a
copy of the same rule in every client.

### Shared kernel (one place, no copies)

Think of this as the spine. Modules plug in. They do not fork it.

| Shared | Lives once | Modules do |
| --- | --- | --- |
| API contract | Backend OpenAPI; generated TS/Dart clients | Consume the generated client |
| Auth / session | One identity story | Use it; do not invent a second login |
| i18n | Separate dictionaries `ru` / `kk` / `en` | Add keys to those dictionaries on the first user-facing change |
| Look | Design tokens / shell | Use tokens; no one-off palette per module |
| Data truth | PostgreSQL SoT; Qdrant derived; RustFS objects | Own their tables/collections; do not add a second source of truth |
| Telemetry | `deploy.pipeline`: logs → Vector → OpenObserve; traces/metrics OTLP → OpenObserve | Emit; do not add a second APM |
| User-run code | Isolated executor | Never inside the API process |

If a new shared thing appears, put it on the spine first, then use it.
Do not paste a private copy into the module «to ship faster».

### Module bar

A module is self-contained enough to change without editing neighbors,
and complete enough that the next change is an extension, not a rescue.
Empty product trees are not created only to hold this file.
Nested `AGENTS.md` templates: `plugins/hack-agent-standards/nested/`.
Layer skills: `plugins/hack-agent-standards/skills/` (`core-motion`
loads this file).

## Done

The owner did not give a shorter stop line. Then all of this is true:

- The map from step 2 was done before the edit.
- New work landed in the right layer and the right module.
- User-visible strings went through i18n dictionaries for `ru`, `kk`,
  and `en` in the same change (skip when the change has no UI).
- Runtime work emits on `deploy.pipeline` (logs via Vector; traces
  / metrics OTLP). Setup-only work has no runtime — skip this.
- Related callers and the generated contract stayed consistent.
- Proof ran on what changed. The piece works, not only sits in folders.
- Git motion matches the owner step (agent branch → named branch;
  `dev` or `main` only when asked).

## Repair

- Check or the piece is red: fix toward the pin and this file. Do not
  invent a parallel stack.
- Owner exception this turn: keep it. Do not rewrite the pin. Name it
  in the report.
- Owner wants a new default: update the pin and the matching standard,
  then continue.
- Merge conflict with `dev`: take their incoming tree, re-apply our
  piece, keep our module consistent. Do not drop i18n or telemetry to
  «win» the merge.
