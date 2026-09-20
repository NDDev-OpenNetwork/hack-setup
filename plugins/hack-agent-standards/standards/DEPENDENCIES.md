# Dependencies

Universe: `build/stack-pin.json` (whole pin). Read `policy`,
`package_manager`, `environments`, `do_not_use`, `conflicts`, and the
versioned sections (`runtimes.*`, `frontend.*`, `backend.*`, `ai.*`,
`auth.*`, `clients.*`, `data.*`, `education.*`, `media.*`,
`quality.*`, `deploy.*`).

Unless the owner said otherwise this turn.

This file is how to move versions. It is not a gate. Do not refuse a
named request.

## Default move

1. The owner named a package, a pin path, or a tool → it is in project
   scope. Write it into the pin, then into the matching graph.
   Do not invent a dependency the owner did not name. Use what the pin
   already has for everything they left unspecified.
2. Open the pin first. If the path exists, install that identity.
   Do not copy the number into this file.
3. If the path does not exist: pick latest-compatible-stable that still
   satisfies existing `conflicts`, add the pin path, refresh
   `build/stack-standard.md`, then install.
4. If the named thing sits in `do_not_use` or fights a `conflicts` row:
   do not block. Offer the pin-equivalent that already fits this stack
   (the reason the row exists). If the owner still wants the named
   thing after that, follow them — exception this turn, or promote if
   they said this is the new default.
5. Each graph has one owner: bun (JS), uv (Python env), Flutter pub,
   cargo, Go modules. Install with that owner. A second JS installer or
   a second JS lockfile is a second stack unless the owner just overrode
   that.

Hackathon day the owner re-verifies the universe (`just reverify`, pin
`policy`). Everyday work does not bump a pin path only because a newer
tag exists.

## Pattern

**Pin vs lock.** The pin is identity: what we chose and which version.
A lockfile is the resolved closure of one graph. This setup repo has no
product lockfiles yet; the pin is enough. After product trees exist:

- A lock-only refresh that does not move a pin-path version and does
  not pull a known conflict stays a lock change. Do not add a pin row
  for every transitive.
- A resolve that would move a pin-path version, or pull something the
  pin already decided against, is not a silent lock edit. Promote the
  pin (or keep the lock on the pin).

**One identity.** Prefer one version of a package across the repo.
Do not open a second version of the same library to ship a slice.
`environments.*` splits a *graph* when two chosen pins cannot share one
resolver (the existing redis-py / cv2 rows). That is a
recorded conflict, not a habit. Do not add a new isolate because a
stack is “heavy” if the versions already unify.

**Graphs.** API and Taskiq may share `environments.api_workers`.
Telegram stays on `environments.telegram` while that redis-py conflict
holds. GPU/ML extras stay in `environments.gpu_ml` so torch / cv2 /
RapidOCR do not land in the API env. The Bifrost gateway
stays in `environments.bifrost` (a container, not a lock). Web is one bun graph. Flutter
owns Dart; do not bump Dart beside Flutter.

**Provenance.** Official installer / registry / hash already named by
the pin is the install source. A random script is not a pin.

## Done

- Every owner-named addition has a pin path (or is named in the report
  as a task-local exception).
- The graph that installs it uses that identity.
- Unspecified slices used existing pin paths. No extra stack appeared
  to fill a gap.
- If the ask fought `do_not_use` / `conflicts`, the pin-equivalent was
  offered and the owner's last word was followed.
- Pin edits refreshed the generated standard. Proof ran (`just check`
  here; later, the graph's own lock/test).

## Repair

- Red proof: put pin and lock back on the same identity. Do not
  peer-override a conflict away.
- Accidental second version: unify to the existing pin path.
- Owner exception this turn: keep it. Do not rewrite the pin. Name it.
- Owner wants a new default: update the pin (and `do_not_use` /
  `conflicts` / `environments` if those rows change), then continue.
  Touch this file only when the *rule* changed, not when a number did.
