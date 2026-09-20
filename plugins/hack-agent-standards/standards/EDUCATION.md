# Education

Universe: `build/stack-pin.json` `education.*`, `media.sympy`,
`media.livekit`, `locales`, `environments.api_workers`,
`environments.gpu_ml`. AUTH owns courses / rooms. INFRA
hosts `collab` and `live` profiles.

Unless the owner said otherwise this turn.

This file is how lessons, boards, spaced repetition, and
student code are cut. WEB owns chrome. AUTH owns rooms.
Do not create `web/` / `api/` only to hold this file.

## Default move

1. Map the slice to one box: editor, collab process, trusted
   compute, FSRS, playground, executor, live voice, chart,
   or scheduling. Then edit.
2. Lesson chrome → i18next `ru`/`kk`/`en`. Lesson body → a
   document keyed by locale. Do not put bodies in
   dictionaries.
3. Student / unsanitized expressions never `exec` /
   `parse_expr` / SymPy in the API or Taskiq worker.
4. Proof: schema round-trip, auth on the room, timeout ≠
   wrong, FSRS identity stored, locale identity on grades.

## Pattern

### Boxes

| Box | Process | May | Must not |
| --- | --- | --- | --- |
| Editor | `web/` | Tiptap JSON, KaTeX paint, Excalidraw, xyflow, three, echarts display | Grade, exec, FSRS SoT, merge locales, prove data via a chart |
| Collab | Hocuspocus (INFRA `collab`) | Sync Yjs, `onAuthenticate`→AUTH, persist binary | Python, ACL by room id, filter updates as security |
| Compute | FastAPI | Trusted SymPy on teacher keys, FSRS `review_card` | Student code, `fsrs[optimizer]`, KaTeX-as-CAS |
| Jobs | Taskiq `api_workers` | Orchestrate executor, FSRS `reschedule_card` | `exec` user_code, torch Optimizer |
| Optimizer | `gpu_ml` | `fsrs[optimizer]` | Live in API env |
| Playground | Pyodide worker | Low-stakes run | Grade SoT, claim sandbox |
| Executor | own image + gVisor extra | Hostile student code | docker.sock, API secrets, egress, share API process |
| Live | LiveKit (INFRA `live`) | Short-lived AUTH token, course room | Room name as ACL, long-lived key in bundle |
| Schedule | OR-Tools in Taskiq | Only when the owner names scheduling | Live in uvicorn, silent extra |

Collaboration is a process. It is not a Python replacement.

### Editor

Tiptap. Versioned schema. Import through the schema, not
raw HTML. Mathematics: store `attrs.latex`. KaTeX paints
it (`trust: false`, cap `maxSize` / `maxExpand`). SymPy is
the other door (`equals` / `simplify`, never `==` as grade,
never `parse_expr` on student input in this process).

Excalidraw = scene JSON (`education.excalidraw`). xyflow =
nodes/edges; pedagogy is not `isValidConnection`. three
direct; dispose; no R3F. ECharts (`education.echarts`)
displays; it does not prove data. WEB owns the import;
this file owns the meaning.

### Collab

Hocuspocus + Yjs. Compose profile `collab` (INFRA).
`onAuthenticate` hits internal AUTH (Compose DNS). Document
name includes locale + course. Persist Yjs update bytes
**through the API** (course-scoped Postgres row / object).
Hocuspocus does not get the app DSN. Redis extension uses
`redis-durable` prefix `yjs:` if more than one instance
(DATA). Never `redis-cache`. Caddy `/collab/*` is WebSocket,
unstripped, Origin-allowlisted. Yjs does not authorize —
write-peers can corrupt the CRDT. Untrusted users get a
fork. Schema bump → migrate in `onLoadDocument`.

### i18n

Chrome dictionaries (WEB). Content: `(id, locale)`. One
Y.Doc per pair. Graded material: missing locale is
missing — no silent fallback to `ru`. Search already
filters `locale` first (DATA).

### FSRS

`education.fsrs` without `[optimizer]` in `api_workers`.
`review_card` on the review POST, same txn as
`ReviewLog`+`Card`. Persist package version + the 21
parameters + retention. `reschedule_card` on Taskiq.
Optimizer (torch) only in `gpu_ml`. UTC. Tests:
`enable_fuzzing=False`. FSRS is not the educational task.
Do not re-pin `fsrs`.

### Live / schedule

LiveKit is optional. Token from AUTH. Browser edge is
LiveKit Cloud unless the owner names self-host (INFRA
`live`, internal net, no Caddy UDP by default). Camera/mic
UI in WEB; fail closed if the token route 403s. Track
cleanup on leave. Room string is not ACL.

OR-Tools (`education.ortools`) only when the owner names
a scheduling slice. Run in Taskiq, not the request
process. Do not add it to fill a gap.

### Executor

Treat code as hostile. Worker/API talk HTTP/queue + job
id. Own allowlisted image. No `docker.sock`. No API
secrets. No egress (`network=none` / no IMDS). Read-only
root. Dropped caps. Host cgroup: memory, CPU, pids,
wall-clock, output bytes. gVisor is extra, not proof.
Statuses: timeout / runtime error / wrong / correct.
Pyodide worker is playground; iframe + origin if the
browser path is hostile. WASM is not a trust boundary.

## Done

- Slice landed in one box; neighbors consume public APIs.
- Locale identity on documents and grades.
- No user_code in API/worker env. Executor has no egress.
- No SymPy via KaTeX.
- FSRS history + algorithm identity stored.
- Collab / LiveKit auth is AUTH membership, not the room
  string.

## Repair

- Exec in FastAPI: move to the executor image.
- `fsrs[optimizer]` in `api_workers`: move to `gpu_ml`.
- Locales merged in one CRDT: split documents.
- R3F appeared: pin is direct three.
- Timeout reported as wrong: split the statuses.
- LiveKit or Hocuspocus started on the spine: move to
  `live` / `collab` profiles.
- OR-Tools in uvicorn: move to Taskiq.
