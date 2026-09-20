# Web

Universe: `build/stack-pin.json` `frontend.*`, `runtimes.typescript`,
`locales`, `quality.biome`, `quality.vitest`, `quality.playwright`.
OTel spine: `deploy.pipeline`, `deploy.openobserve`, `deploy.vector`,
`deploy.otel`.

Unless the owner said otherwise this turn.

This file is how to move inside `web/`. It is not a gate. Next.js,
TanStack Start, a second JS lockfile, or a second UI kit are not
refusals — offer the pin-equivalent (Vite + React + bun + shadcn)
and follow the owner's last word.

Do not create `web/` only to hold this file.

## Default move

1. Map `web/src` and the slices the request will touch. Then edit.
2. Cut the screen as FSD. Route files stay thin. UI and Query live
   in `pages` / `features` / `entities`. Shared spine is tokens,
   i18n, shadcn, and the adapter over the generated client.
3. Talk to the API only through that generated client (package
   outside this workspace). Browser: `credentials: 'include'`.
   Mint CSRF via `GET /v1/auth/csrf` (`{csrf_token}`), send
   `X-CSRF-Token` on cookie-auth unsafe methods. Never
   `setBearerAuth` / `Authorization` in this tree. Mini App: send
   raw `Telegram.WebApp.initData` to AUTH once, then the cookie
   session. Tauri branches in CLIENTS (Bearer, not cookie). Do
   not fork generated types. Do not install the OpenAPI generator
   next to the web TypeScript compiler.
4. First user-facing string → keys in `ru` / `kk` / `en` in the
   same change. First visual → tokens, not a one-off palette.
5. Server data → TanStack Query. Interaction → local state or
   TanStack Form. No required global store.
6. Proof: Biome + the project `tsc` (transpile is not types).
   Changed interaction, layout, auth, or streaming → a real
   browser path (Playwright on that path) **when `web/` exists**.

## Pattern

### Folders

FSD layers, TanStack file routes relocated into App (official FSD
move when the router lets you pick the directory):

```text
web/src/
  app/
    providers/              # Query, i18n, auth — wrap RouterProvider
    router.tsx              # createRouter + Register
    routeTree.gen.ts        # generated; do not hand-edit
    routes/                 # createFileRoute only
      __root.tsx
      _authenticated.tsx    # beforeLoad + throw redirect
  pages/<screen>/
  features/<action>/
  entities/<module>/        # DDD box inside this layer
  shared/
    api/                    # adapter; generated package is outside web
    i18n/                   # ru / kk / en dictionaries
    ui/                     # tokens + shadcn/Base UI primitives
```

`widgets/` is optional. FSD now discourages a required widgets layer.
Do not add `src/routes` as a sibling of `app` / `pages`. Do not rename
`pages` to `_pages` (that is a Next/Astro workaround).

A route file: `createFileRoute`, `validateSearch`, `beforeLoad` /
`loader`, and a `component` that renders a page public API. No copy,
no generated-client imports, no DDD logic.

Plugin: file-based router **before** the React plugin.
`autoCodeSplitting` on (v1 default is off). Generated route tree
stays under `app/`. `Register` the router type — file-based does
not remove that.

Auth gate: pathless `_authenticated` `beforeLoad`,
`throw redirect({ to })`. Not a component check (flash). Not a
feature-slice guard. Backend still authorizes the API. Pass
`{ queryClient, auth }` on the root context; hooks cannot run in
`beforeLoad`.

### Data

Query owns the server cache. Route `loader` only
`ensureQueryData` / `prefetchQuery` on shared `queryOptions`.
UI calls `useQuery` / `useSuspenseQuery` on the same options.
Mutations live next to the action (`features/*/api` or
`pages/*/api`). Do not keep a second copy in router cache or a
global store.

`queryOptions` factories: `entities/<x>/api` (or `shared/api` if
there is no entity yet). Identity-scoped keys. Invalidate after
mutations. Clear that cache on logout / account change.

### Forms

Form UX is a local Zod schema passed straight to TanStack Form —
v1 speaks Standard Schema, no resolver adapter. Wire types are the
generated client.

- `useForm({ defaultValues, validators: { onChange: schema } })`;
  the editable shape is `z.input`, submit `value` is `z.output`.
- `<form.Field>` render props: `field.state.value` /
  `handleChange` / `handleBlur`. No `register` / `Controller`.
- `formToDto(output)` is assignable to the generated request type.
  No `as Dto`. Inverse `dtoToForm` for edit `defaultValues`.
- Empty inputs are `""`. JSON DTOs follow the API (`null` / omit),
  not the input. That map lives in the adapter.
- i18n errors in the form schema / render. Generated English Zod
  messages are not UI copy (and have no `kk` locale).
- Optional generated Zod lives **outside** web and validates the
  DTO after the adapter (SDK `validator` / `zBody.parse`). Do not
  pass generated schemas to form validators.

Query mutation takes the **DTO**. `form.Subscribe` on
`isSubmitting` / `canSubmit` disables submit. API field errors come
back through `validators.onSubmitAsync` returning
`{ form?, fields: { <name>: <msg> } }` (nested names like
`items[0].title` work), not per-field state. Form mounts after edit
data exists (or async `defaultValues`).

### UI

shadcn via the pin CLI into `shared/ui`. Modules compose primitives.
They do not invent a second button/form/style system.

`motion` is optional chrome. `prefers-reduced-motion` wins for
nonessential animation. Semantic HTML, labels, focus, keyboard.

Markdown / imported HTML is untrusted. No raw HTML by habit.
Vite env is public. No backend secrets, OO Basic, or collector
passwords in `VITE_*` or the bundle.

### PWA

Online-first installable shell. `generateSW`: precache `js` / `css`
/ `html` (and wasm if present), `navigateFallback` = `index.html`,
denylist `/v1`, `/otel`, and auth/SSE navigations. No
`runtimeCaching` for first-party API, cookies, OpenAPI, or
EventSource.

A service worker is an HTTP cache, not a data model. Dexie stays
in the pin and is imported only when a named feature needs
drafts / local writes. That store is identity-scoped and wiped
on logout. `localStorage` is not the offline store.

### Telemetry

Same spine as QUALITY (`deploy.pipeline`). Browser traces go
OTLP to `/otel/v1/traces`, not through Vector. No second APM
(Sentry, Datadog, OpenObserve `browser-rum`, console-as-done).

Browser SDK ships with the **first user → API journey**, and only
once Caddy (or equivalent) exposes same-origin OTLP
(`/otel/v1/traces`). Until that ingest exists, do not emit and do
not invent a logs-only APM.

When it ships: `WebTracerProvider` + batch OTLP/HTTP + document
load + fetch (ignore the export URL; `traceparent` only to the
API origin) + one router navigation span. Redact `url.full`
query/hash. Do not also patch XHR. Do not wrap the generated
client's fetch a second time. Do not put the SW in front of
`/otel`. Proof is a real navigation + API call in OpenObserve,
not an import.

## Done

- Slice landed in the right FSD layer. Route file stayed thin.
- User-visible strings went through `ru` / `kk` / `en`.
- Look used tokens / `shared/ui`. No one-off kit.
- Server reads/writes went through Query + the generated client.
- Forms had UX Zod, an explicit DTO adapter, i18n errors, and a
  pending/disabled submit.
- PWA did not cache `/v1` or `/otel`. Cookie calls minted
  CSRF from `GET /v1/auth/csrf`, used `credentials: 'include'`,
  and never sent `Authorization`. Dexie only if that feature
  named a local store. Tiptap / echarts / LiveKit UI follow
  EDUCATION; this file stays chrome.
- Browser OTel followed the ingest gate above.
- Biome + `tsc` ran. Browser proof ran when the change needed it.

## Repair

- Red types or lint: fix toward the pin compiler / Biome. Do not
  add `typescript@6` or typescript-eslint to “make it work.”
- Generated client drift: regenerate outside web; do not hand-edit
  `.gen.ts` or the web adapter types.
- Accidental `Authorization` in the browser tree: remove; cookie
  + CSRF only.
- Accidental second stack (Next, Zustand-as-default, extra CSS
  kit, hey-api inside web): offer the pin-equivalent. Owner's last
  word wins (exception this turn, or promote if they said so).
- SW started caching `/v1` or `/otel`: remove that
  `runtimeCaching` / glob.
- Two users sharing one Dexie name: scope or `delete` on logout.
