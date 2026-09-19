# Data, Qdrant search, cache and file rules

## Ownership and integrity

PostgreSQL owns authoritative transactional entities and access metadata. Qdrant holds rebuildable search representations. RustFS stores original/generated binary objects with metadata in PostgreSQL. Redis stores specifically designated ephemeral state, sessions or jobs. DuckDB/Polars/Arrow serve analytical processing rather than becoming a second transactional authority.

Use explicit uniqueness, foreign keys and domain constraints where applicable. Protect asynchronous writes with transactions and idempotency. Do not treat a successful write to one of several stores as atomic completion across all of them; use a visible ingestion state and repairable workflow.

## Qdrant

Use Qdrant for semantic/hybrid retrieval with named dense/sparse representations as required. Exact IDs and authorized metadata lookups do not become approximate semantic searches. Define collection configuration, metric, embedding model/version/dimension, normalization and chunking policy explicitly.

Filter by actual backend-derived access scope before giving retrieved content to a model or client. Do not trust client-supplied tenant/user IDs as authorization. Keep payload indexes for frequently filtered fields when the measured query pattern justifies them. Citations retain document ID, source version and page/offset/time range.

A changed embedding model/dimension or incompatible chunking scheme requires a new index/versioned rebuild, not silent writes into the existing space. Avoid arbitrary automatic embedding-provider fallback if vectors would become incompatible. Preserve old/new mapping during reindexing, then switch intentionally.

Measure retrieval on RU/KK/EN materials and exact-name queries. Use hybrid fusion and reranking only when they improve the actual evidence set. Do not let a high similarity score be displayed as probability that the answer is correct.

## Redis and jobs

Define persistence/eviction expectations per workload. An evictable cache and an important queue should not share an accidental policy. Use scoped key names and TTLs where appropriate; avoid exposing Redis publicly. Cache results must include all identity/permission/model-version inputs that affect their validity.

Retry idempotently and expose failed/cancelled job status. A lock expiry is not proof the original worker stopped. Protect irreversible external side effects using domain-level idempotency rather than only a volatile lock.

## RustFS/S3

Keep object keys server-generated and ownership-aware. Do not interpret uploaded filenames as filesystem paths. Enforce explicit size/type limits, safe metadata and controlled access. Signed URLs are capabilities: scope and expire them deliberately; never treat possession of an arbitrary object key as user authorization.

Track checksum, size, source, owner and processing status. Delete or supersede derived chunks and artifacts consistently when a source is removed or replaced. Do not log signed URLs containing sensitive query parameters.

## Analytics and files

Preserve data types across PostgreSQL, Arrow/Parquet and CSV/XLSX exports. Keep IDs as IDs, not approximate floats. Handle missing values, locale, decimal precision, timezone and spreadsheet-formula interpretation explicitly. Bound memory use and read large datasets in appropriate batches.

Verification covers the changed data invariant, dialect and retrieval/access path, not only a parseable configuration or a working connection.
