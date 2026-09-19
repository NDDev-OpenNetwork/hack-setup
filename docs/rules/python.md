# Python / API

Pins: CPython `3.14.7`, uv `0.12.17`, FastAPI `0.141.1`, Uvicorn `0.53.0`,
Pydantic `2.13.5`, pydantic-settings `2.15.0`, SQLAlchemy `2.0.54`,
psycopg `3.3.6`, Alembic `1.20.0`, httpx `0.28.1`, Taskiq `0.12.6`,
taskiq-redis `1.2.3`, aiogram `3.31.0`, PyO3 `0.29.2`, maturin `1.15.0`,
structlog `26.1.0`.

## Environments

Keep lockfiles separate:

| Env | redis-py | Role |
| --- | --- | --- |
| API / workers | `8.1.0` | FastAPI, Taskiq RedisStreamBroker |
| Telegram | `7.4.1` | aiogram |
| GPU / ML | isolated | whisper, CTranslate2, torch, ONNX, FastEmbed |
| LiteLLM proxy-runtime | optional container | not an API extra |

Do not add redis 8 to Telegram to “make versions match”.

## API

- FastAPI owns the HTTP contract. No handwritten parallel DTO layer.
- SQLAlchemy is async-primary on `2.0.54`. Do not take `2.1` rc.
  Driver is psycopg 3, not asyncpg.
- Pydantic stays `2.13.5`. Do not take `2.14` beta.
- httpx stays `0.28.1`. FastAPI extras require `httpx<1`.
- Alembic is the only schema migration path. One head owner at a time.
- Settings via pydantic-settings. No secrets in git.
- Taskiq uses RedisStreamBroker. Cache Redis and queue Redis may be split
  if the cache may evict.
- User-submitted code never runs in the API process. See `education.md`.

## Bot

aiogram `3.31.0` lives in the Telegram env. Mini App `initData` is verified
on the backend. See `auth.md` and `clients.md`.

## Native

PyO3 + maturin for Rust extensions. That is not a second HTTP backend.
