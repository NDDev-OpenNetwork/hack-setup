# Infra

| Tool | Pin | Role |
| --- | --- | --- |
| Docker | `29.8.1` | Images |
| Compose | `5.5.1` | Local / VPS compose |
| Caddy | stable line, unversioned | Reverse proxy + HTTPS |
| OpenObserve | `1.0.3` | Logs / traces / metrics |
| Vector | `0.58.0` | Log ship |
| OTel API | SDK `1.44.0`, instrumentation `0.65b0` | API process |
| structlog | `26.1.0` | JSON logs |

Pipeline: JSON logs → Vector → OpenObserve. Traces/metrics OTLP → OpenObserve.

Do not mix LiteLLM `proxy-runtime` OTel `1.28.0` pins into the API env.

## This repo

`./setup` installs Codex + Node + bun + uv + CPython only. Rust, Go,
Docker, Postgres, Redis remain declared host tools. An extra
`install/modules/<nn>-*` directory would still be globbed by bootstrap;
the artifact gate must see a matching `catalog.toml` row.

Windows is fail-closed. No root file named `install`.

A “chosen VPS” and an optional OTel Collector are not pinned.
