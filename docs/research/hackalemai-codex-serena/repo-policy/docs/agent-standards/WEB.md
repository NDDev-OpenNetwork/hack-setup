# React, TypeScript and web client rules

## Ownership

Use pure React with Vite, the selected native TypeScript compiler, TanStack Router and Query. Do not introduce Next.js/SSR/server actions by habit. Bun owns JS dependency management and the lockfile; Node remains the compatible runtime for selected tooling. Native TS compilation and Serena's navigation engine are separate versioned components.

Generated API clients own transport DTOs. Local forms may have distinct Zod schemas for input interaction, but their mapping to API contracts must remain explicit. Do not manually fork generated types to silence a mismatch.

## Data and state

Use TanStack Query for server state and deliberate query keys, including user/organization scope where relevant. Invalidate related data after mutations. Clear identity-scoped cache on logout/account change. Do not duplicate fetched data into unrelated global stores or effects without a specific lifecycle reason.

Use local component state for local interaction. Model loading, empty, error, retry and disabled-submit states. Prevent accidental duplicate writes. Optimistic updates need a rollback/reconciliation path. Authorization is enforced by the backend, not by hidden navigation elements.

## Components and rendering

Keep rendering free of observable side effects. Use effects for actual external synchronization, not derived values that can be computed directly. Keep keys stable and preserve correct focus behavior. Do not suppress hook/dependency problems globally. Prefer composition and shared primitives to a large bespoke UI framework.

Use the agreed Tailwind/shadcn system and React Hook Form/Zod. Do not add a second competing component/style/validation system for an isolated screen. Load expensive editors, diagrams, 3D and media functionality on demand. Dispose GPU/media resources and subscriptions on unmount.

## Security, localization and accessibility

Do not expose backend secrets through Vite variables, browser bundles or local storage. Treat model Markdown and imported HTML as untrusted; render through an explicit safe policy rather than enabling arbitrary HTML by default. URL opening and downloads must use the intended origin/allowlist and ownership rules.

Use i18next resources for RU/KK/EN text. Preserve interpolation keys, pluralization and formatting. Avoid hardcoded English errors and locale-dependent logic. Format dates/numbers using an explicit locale/timezone policy; retain machine values separately.

Use semantic elements, labels, keyboard navigation, focus states and accessible feedback for asynchronous operations. Motion must not prevent interaction; support reduced motion for nonessential animation.

## PWA and browser storage

A service worker is not automatically an offline data model. Cache static assets deliberately; never cache authenticated API responses or private files by a generic catch-all policy. Identify cache/version ownership and update behavior. Dexie data must be scoped to the active identity, migrated deliberately and cleared appropriately on logout.

Use a single defined API origin/proxy policy in dev and deployment. Verify cookies, OAuth redirects, SSE and WebSocket paths against the actual Caddy deployment, not only the Vite server.

## Checks

Biome owns configured JS/TS/JSON formatting/lint. The project compiler owns TypeScript acceptance. A successful Vite transpile alone does not prove type correctness. Verify changed UI behavior in a real browser when it affects interaction, layout, auth or streaming; keep Playwright coverage focused on the changed path.
