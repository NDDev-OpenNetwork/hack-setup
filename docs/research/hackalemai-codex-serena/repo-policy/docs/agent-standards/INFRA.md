# Infrastructure, deployment and telemetry rules

## Runtime footprint

Use Docker Compose and Caddy on the chosen VPS. Enable only services required by the actual case. The technology catalogue is not a mandate to start every database, editor service and GPU runtime. Keep tool/LSP processes distinct from production app processes.

Pin runtime image versions/digests deliberately and preserve architecture compatibility between Macs and the server. Use multi-stage builds where appropriate, intentional file ownership, a non-root runtime where supported and no secrets baked into build layers. Do not expose database, search, cache or administrative endpoints to the public network by default.

## Configuration

Validate actual Compose configuration with the installed CLI. Parse/schema validation comes before consumer/runtime validation, not instead of it. Keep env examples non-secret and record required variable names without values. Distinguish build-time frontend variables from runtime backend configuration.

Define health/readiness behavior that reflects the service's actual role. Respect connection, CPU, RAM and file-descriptor limits across all workers/processes. Size database pools and background concurrency against the whole deployment. Do not assert capacity solely from a user-count estimate.

## Deployment

Developer branches use their own working state; the integration role owns shared environment updates. Do not let three agents concurrently migrate the same database or replace the same deployed image. Record the source commit/image identity actually deployed and verify the changed path afterwards.

Avoid accidental data deletion from volume teardown. A routine feature deployment must not reset PostgreSQL, RustFS, Qdrant or Redis state as a hidden repair. Keep migrations explicit. Do not introduce complex mandatory runner fleets for this hackathon workflow.

## Observability

Use structured app logs → Vector → OpenObserve and the intentionally configured OTLP path for traces/metrics. Add a Collector only for an actual transformation/routing need; avoid duplicate delivery loops. Carry request/trace/job IDs across HTTP, queues and model calls.

Validate Vector transforms with representative events and actual consumer configuration. Check field types, redaction, timestamps and failure handling. Trace/log correlation must not depend on logging secrets or entire uploaded materials. Metrics labels need bounded cardinality: unbounded user/request/prompt text does not belong in label values.

Instrumentation absence, exporter failure and actual zero traffic are distinct states. Do not claim traces work because an SDK import succeeded. Verify at least one real operation is visible in the configured backend when changing the path.

## Local feedback

Use targeted syntax/consumer checks and the affected container build/start. Full-stack restart is not required for a documentation change. Keep long expensive checks off the per-tool hook path and surface their actual status when they run.
