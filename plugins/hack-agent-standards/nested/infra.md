# Infra

Read the repository root `AGENTS.md`. This directory is Compose + Caddy
+ Vector + OpenObserve.

Open `$hack-agent-standards:runtime-infra`. Always CORE. QUALITY when
proving. Mixed: FORMATS (YAML / Caddyfile), DATA (two Redis, RustFS).

Hop-split: logs → Vector → OpenObserve; traces/metrics OTLP → OpenObserve.
Only Caddy publishes 80/443. `collab` / `live` / `gpu` are profiles, not
the spine. Browser LiveKit edge is Cloud unless the owner names self-host.
