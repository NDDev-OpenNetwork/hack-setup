# Web

Pins: React / react-dom `19.3.0`, Vite `8.3.0`, TypeScript `7.0.2`,
TanStack Router `1.170.38`, TanStack Query `5.103.1`, Tailwind `4.3.3`,
`@tailwindcss/postcss` `4.3.3`, shadcn `4.21.0`, `@base-ui/react` `1.8.0`,
react-hook-form `7.88.0`, `@hookform/resolvers` `5.9.1`, Zod `4.6.5`,
i18next `26.4.2`, react-i18next `17.0.14`, lucide-react `1.47.0`,
motion `13.4.0`, react-markdown `10.1.0`, remark-gfm `4.0.1`,
vite-plugin-pwa `1.3.0`, Dexie `4.4.6`.

## Architecture

- Feature-Sliced Design when `web/` exists. Do not create `web/` here.
- Tokens: W3C DTCG / Tailwind v4 CSS variables. No ad-hoc color hex sprawl.
- shadcn v4 + Base UI `1.8.0`. Install with `bunx shadcn@4.21.0`.
  Do not `bun add shadcn`.
- No required global client store. Server/async state is TanStack Query.
- Locales: `ru`, `kk`, `en`.
- PWA via vite-plugin-pwa. Offline drafts: Dexie, not Drift.
- Telegram Mini App reuses this React/Vite app. Verify `initData` on the API.

## TypeScript

- Product typecheck is TypeScript `7.0.2` (`tsc` only). One `typescript`
  in web. No `@typescript/typescript6`. Lint is Biome, not eslint.
- Generated client is typechecked by the same `tsc` 7. Do not install
  `@hey-api/openapi-ts` `0.99.0` in the web workspace. See `contracts.md`.

## Do not

Next.js. pnpm. R3F / Drei (`@react-three/fiber` still peers `react <19.3`).
A second JS lockfile. `@types/node` 26.x. Hand-written API types that
duplicate OpenAPI. `bun add shadcn`.
