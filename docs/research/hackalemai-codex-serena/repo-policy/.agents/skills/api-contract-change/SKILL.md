---
name: api-contract-change
description: "Use when changing API schemas, routes, serialized fields, streaming events or generated TypeScript and Dart clients."
---

# Change an API contract coherently

Load CONTRACTS, the producer/consumer language standards and MULTIAGENT from the repository standards directory.

Identify the backend source of truth, affected endpoints/events and the actual generated consumers. Search string-driven protocol uses in addition to semantic references. Establish an integration owner for shared schema changes.

Modify source definitions and required domain/persistence behavior. Review migration impact. Generate OpenAPI and client outputs using the pinned tools, inspect their diffs and compile affected consumers. Resolve conflicts in source inputs, not generated files.

Verify the relevant success/error/stream shapes and at least the material compatibility risk. Update the compact contract handoff with commit identity and checks. Do not hand-maintain duplicate DTOs, force incompatible generator dependencies or rename public fields merely because an internal symbol changed.
