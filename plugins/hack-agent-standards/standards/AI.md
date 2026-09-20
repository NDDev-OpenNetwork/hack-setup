# AI

Universe: `build/stack-pin.json` `ai.*`, `environments.gpu_ml`,
`environments.litellm_proxy`, `backend.fastapi`, `backend.pydantic`,
`deploy.otel`. DATA owns Qdrant. CONTRACTS owns SSE names.
PYTHON owns lifespan and sessions.

Unless the owner said otherwise this turn.

This file is how models are called. It is not a gate. Do not
create `api/` only to hold this file. Orchestration is plain
Python + Pydantic steps. LangChain / LlamaIndex are not
refusals — offer the pin-equivalent and follow the owner.

## Default move

1. Name the operation: chat / stream / structured / embed /
   STT. Then pick the client below. Do not invent a second
   router.
2. Chat, tools, vision, fallbacks, CLIProxyAPI: one
   `litellm.Router` on FastAPI lifespan.
   `await router.acompletion(...)`. Base `ai.litellm` only.
   No `[proxy]`. No `[proxy-runtime]`.
3. Official OpenAI-only typed parse / Responses
   `text_format`: `AsyncOpenAI` from `ai.openai`. Same
   process, different call site. Do not also wrap that call
   in Router.
4. Product dense vectors: Taskiq job in `gpu_ml` (FastEmbed).
   DATA upserts. Not LiteLLM `embedding()`. Not the Qdrant
   Fastembed mixin. Not CLIProxyAPI.
5. Proof: schema + subject + citation as **separate** checks.
   Tokens/latency logged. Prompt/content not logged.

## Pattern

### Graphs

- `api_workers`: `litellm` + `openai` 2.x (`<3`).
- `gpu_ml`: FastEmbed, faster-whisper, torch, ONNX.
- `litellm_proxy`: optional container only. Own OTel line
  (`environments.litellm_proxy`). Never merge into the API lock.
- CLIProxyAPI: GitHub release binary. Not a uv extra.

`openai` 3.x is HTTPX2. LiteLLM requires `openai<3`. FastAPI
extras require `httpx<1`. Do not put 3.x in the API env.

### LiteLLM vs raw openai

Default: one Router (`simple-shuffle`). CLIProxyAPI is a
deployment (`model: openai/<alias>`,
`api_base: http://127.0.0.1:8317/v1`), not a second stack.

Raw `AsyncOpenAI` only when all of these hold: single
official OpenAI origin, no fallback, and you need `.parse()`
/ `message.parsed` / `refusal` / Responses `text_format`.

A Chat Completions 200 does not prove tools, json_schema,
vision, Responses, or embeddings. Probe the op you ship.
Do not `OpenAI(base_url=litellm-proxy)` in this API.

### Streaming

CONTRACTS is the wire. Native `fastapi.sse` (`response_class`
+ yield, not `return EventSourceResponse`).
`data` = JSON. Sentinels = `raw_data`. Terminal `event:
done` + `raw_data: [DONE]`. In-band fail: `event: error`.
Closed socket ≠ job success.

LiteLLM: `acompletion(..., stream=True)` then
`async for chunk`. Yield deltas. Do not buffer-then-fake.
Raw openai: `async with client.chat.completions.stream(...)`.
No `AsyncSession` across the generator.

### Structured output

1. Probe `supports_response_schema` (or a documented official
   model). Else do not claim strict.
2. Router: `response_format=Model` then
   `Model.model_validate_json`. Official OpenAI:
   `.parse()` → `parsed` or `refusal`.
3. Three checks, three outcomes: schema / subject /
   citation. Citation only if a retrieved id supports the
   sentence. No cite → unknown, not a fake id.
4. Stream tokens for chat UX. Structured product results
   are non-stream (or a terminal event after validate).

### Embeddings vs DATA

| Concern | Owner |
| --- | --- |
| model id, dim, normalize, chunker | AI (identity string; persist it) |
| encode dense vectors | AI, `gpu_ml` FastEmbed (INFRA `gpu` HTTP) |
| collection, alias, BM25, filters | DATA (reads the identity string) |
| Postgres chunk row | DATA / DOCUMENTS (copy identity + `prov`) |

Same identity → upsert that UUID. Identity change → DATA
rebuild. Query-time embed uses the **same** identity as the
alias, via INFRA `gpu` internal HTTP (`environments.gpu_ml`)
— not LiteLLM `embedding()` in the API. Hosted LiteLLM embed
is a different product feature.
Ban: `QdrantClient.set_model` / mixin `Document` embed.

### CLIProxyAPI

Optional sidecar. Bind localhost. `request-log: false`.
`/v1/chat/completions` + `/v1/responses`. No embeddings
route. Probe the shipped op.

### Logs / PII

On start: `litellm.turn_off_message_logging = True`,
`set_verbose = False`. Log request id, alias, latency,
tokens, status. Do not log messages, completions, tool
args, student text, embeddings. No Langfuse I/O callbacks.
No `OPENAI_LOG=debug`. QUALITY spine only.

### STT

faster-whisper in `gpu_ml`. API enqueues. Do not import
whisper / torch / FastEmbed in uvicorn.

## Done

- Call site is Router or a named raw-openai exception.
- No `litellm[proxy-runtime]` / openai 3.x in API.
- Stream uses `fastapi.sse` + terminal events + job row.
- Schema, subject, and citation stayed separate.
- Index vectors came from `gpu_ml` with the alias identity.
  Qdrant still has DATA’s access filter.
- Logs have route metadata and no prompt/PII.

## Repair

- `proxy-runtime` or the proxy OTel line in API lock: split.
- openai 3.x resolved: pin back to `ai.openai` 2.x.
- FastEmbed / torch in API: move to `gpu_ml`.
- Mixin embed written into `chunks`: stop, rebuild if
  contaminated.
- Prompt in OpenObserve: wipe that stream, keep redaction
  on.
- Schema-valid treated as graded: split the checks.
- LangChain as orchestration: remove; keep Pydantic steps.
