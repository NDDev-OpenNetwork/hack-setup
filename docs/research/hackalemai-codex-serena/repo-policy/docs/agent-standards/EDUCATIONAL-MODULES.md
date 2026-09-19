# Optional educational module standards

Activate these tools only for the disclosed case. Their presence in the catalogue is not evidence of an implemented feature.

## Content editors and collaboration

Use Tiptap as the selected rich-text editor and Yjs/Hocuspocus when true shared editing is required. Store a versioned document representation rather than losing structure in ad hoc HTML. Validate imported content and render it through the intended policy. Ensure server-side authorization for document/session access; a collaboration room ID is not a permission check.

Handle join/leave, reconnect, persistence and schema compatibility deliberately. A CRDT solves particular merge semantics, not account permissions or every business-rule conflict. Do not persist a partially incompatible document schema after an extension upgrade without a migration plan.

## Mathematics, graphs and boards

Use KaTeX for supported rendering and SymPy/explicit code for the relevant mathematical validation. Define equivalence, units, allowed domains and numerical tolerances. Do not use raw evaluation of user expressions in the application process.

Choose Excalidraw for free-form drawings and React Flow for logical node/edge structures. Validate graph constraints separately from visual layout. ECharts displays analytics; it does not establish data correctness. Direct Three.js integrations need resource disposal, frame lifecycle and actual performance checks on the target client.

## Learning algorithms

FSRS integration needs a clear review event history and algorithm/version identity; it does not replace the educational task definition. OR-Tools problems require explicit variables, constraints and objective. Report infeasibility or unknown solver status instead of inventing a feasible schedule.

Keep algorithm state authoritative in the backend when shared across clients. Include deterministic focused examples for changed scoring, scheduling or progress logic. Do not equate use of a recognized library with validated educational effect.

## Voice and video

LiveKit or a native realtime API must use scoped room/session credentials, deliberate permissions and correct stream cleanup. Camera/microphone errors and disconnects need visible UI states. Do not claim language support or response latency without a relevant trial.

## Student code execution

Pyodide can execute Python in the browser, but it is not by itself an application-security sandbox. Use a dedicated worker for responsiveness and termination; a worker alone does not create a separate origin or remove network/storage authority. For hostile student code, use an explicitly restricted execution origin or a sandboxed frame with narrow message capabilities, no application credentials, suitable network policy and bounded resources. Verify those boundaries rather than relying on the word WebAssembly. Server-side execution requires a separate constrained executor with resource/time/network limits, no application secrets and no Docker socket. gVisor is an additional isolation layer, not proof that any arbitrary executor is safe.

Treat submitted code as hostile to the execution environment. Limit output, termination time and file access. A code runner must report timeout/failure distinctly from a successful incorrect answer. Never run student code inside the FastAPI process simply to finish an integration quickly.
