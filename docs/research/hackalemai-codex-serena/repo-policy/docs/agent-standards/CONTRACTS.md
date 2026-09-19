# Contract-first consistency rules

## Canonical definitions

The Python backend owns HTTP API schemas. OpenAPI is generated from those definitions; TypeScript and Dart consumers are generated from the same versioned schema using the selected tools. Do not maintain independent handwritten copies of an API DTO. Persistence models, public response models, form input state and domain entities are not automatically identical.

Define stable operation IDs, route/version convention, error envelope, pagination shape, identifiers, nullability, timestamps and enum semantics. Preserve compatibility deliberately. A internal symbol rename does not authorize a wire-field rename.

## Change procedure

Before changing a schema, inspect endpoints, serializers, clients, callers, persisted records and fixtures. Record the proposed externally visible change and an integration owner. Make the smallest coherent change across source contract and directly affected consumers, regenerate once the source is stable, then inspect generated diffs.

Do not hand-edit a generated client, route tree or localization output. Resolve merge conflicts in generator inputs, regenerate and typecheck. If a generator does not support the selected compiler/API version, repair the toolchain boundary instead of force-installing incompatible packages.

## Data semantics

Represent unknown data as missing/null according to the schema; never invent default facts. Distinguish an empty list, absence, zero and false. Use stable IDs, an explicit precision strategy for large integers/monetary values and a timezone-aware representation for instants. Treat localized display values separately from machine values.

Validate untrusted requests and provider responses at boundaries. Reject malformed or unexpected enum/state transitions with a meaningful contract, not a success-shaped error. Do not expose secrets or internal stack traces in API responses.

## Streaming and asynchronous work

Define SSE/WebSocket event schemas, ordering, completion, cancellation and error events. A closed connection does not prove the job succeeded. Preserve partial output semantics explicitly. Reconnection and retries must not duplicate writes or grading attempts.

Jobs and events carry stable identity and schema version where needed. Keep frontend status consistent with persisted job state. Do not leave one client using an old event name while the backend silently changes it.

## Verification

Use generated-client compile checks and targeted API tests on the changed contract. Exercise at least the meaningful success and failure shape for risky changes. Validate actual OpenAPI output, not only Python annotations. Include the generated schema/client identity in integration handoffs.

Coordinate migrations and clients together when persistence and wire schemas change. Do not require a broad approval gate for every edit, but do not merge independently inconsistent contract fragments into the shared dev state.
