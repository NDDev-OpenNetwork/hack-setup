# Data

| Store | Pin | Role |
| --- | --- | --- |
| PostgreSQL | `18.6` | Source of truth |
| Qdrant | `1.19.1` + `qdrant-client` `1.19.1` | Derived dense/sparse index |
| Redis | server `8.10.2` | Sessions, cache, Taskiq streams |
| RustFS | `1.0.0` | S3-compatible objects |
| boto3 | `1.43.98` | Object client |
| DuckDB | `1.5.5` | Analytics / Parquet only |
| Polars | `1.44.2` | Analytics frames |
| PyArrow | `25.0.1` | Arrow / Parquet |

## Ownership

- Application writes go to PostgreSQL (and objects to RustFS).
- Qdrant is rebuilt or updated from SoT. It is not a second user database.
- DuckDB must not become OLTP.
- Redis cache may evict. Taskiq streams must not share an evicting cache
  instance if that would drop jobs.

## Search

dense + sparse/BM25 → RRF → optional reranker. Apply access, locale, course,
and source filters before context assembly. Local embeddings: FastEmbed in
the `gpu_ml` env, not in the Telegram env.

## Drivers

psycopg 3. No asyncpg. redis-py versions stay env-specific (`python.md`).
