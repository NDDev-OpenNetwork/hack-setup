# Web

Read the repository root `AGENTS.md`. This directory is the Vite + React
FSD tree (`src/app/routes`).

Open `$hack-agent-standards:web-ui` (or `plugins/hack-agent-standards/standards/WEB.md`).
Always open CORE. Open QUALITY when proving. Mixed: CONTRACTS (generated
client), AUTH (CSRF / Mini App initData), EDUCATION (Tiptap / echarts /
LiveKit chrome).

Pin: `frontend.*`, `runtimes.typescript`. No Next.js. No second JS lockfile.
Browser talks `/v1` with `credentials: 'include'` after `GET /v1/auth/csrf`.
No `Authorization` in this tree. PWA denylist `/v1` and `/otel`. i18n
`ru` / `kk` / `en` on the first user-facing string.
