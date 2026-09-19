# Education modules

Unversioned in the pin unless noted.

| Piece | Note |
| --- | --- |
| Tiptap | Lesson editor in `web/` |
| Yjs / Hocuspocus | Collaboration process. Not a Python replacement |
| KaTeX | Display only |
| sympy `1.14.0` | Compute. Never via KaTeX |
| Excalidraw | Diagrams |
| `@xyflow/react` `12.11.6` | Flows |
| ECharts | Charts |
| FSRS | Spaced repetition, Python |
| OR-Tools | Scheduling |
| Pyodide | In-browser student Python |
| three.js `0.186.0` | 3D. No R3F (`fiber` still peers `react <19.3`) |
| LiveKit | Optional live classroom |

## Student code

Runs in an isolated executor. gVisor is an extra isolation layer, not a
default that exists today. Never in the API process.

Pyodide / WebAssembly / a Web Worker is not an application security
boundary. Responsiveness, termination, and origin/network/credential
restrictions are separate checks. Do not claim “isolated like Pyodide”
as a security pass.

reveal.js, OBS, and judge-slide delivery are not pinned.
