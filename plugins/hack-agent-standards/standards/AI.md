# AI

Universe: `build/stack-pin.json` `ai.*`, `environments.gpu_ml`,
`environments.bifrost`, `backend.fastapi`, `backend.pydantic`,
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
   `AsyncOpenAI` client on FastAPI lifespan pointed at the
   Bifrost gateway (`base_url=http://bifrost:8080/v1`,
   `ai.bifrost`). Provider keys, failover, load balancing,
   and guardrails live in the gateway config, not in the API
   env. Model ids are gateway aliases.
3. Official OpenAI-only typed parse / Responses
   `text_format`: the same client through Bifrost when the
   provider supports it; direct `AsyncOpenAI` origin only as
   a named exception. Do not wrap one call in both.
4. Product dense vectors: Taskiq job in `gpu_ml` (FastEmbed).
   DATA upserts. Not a gateway `embeddings.create` call in
   the request path. Not the Qdrant Fastembed mixin. Not
   CLIProxyAPI.
5. Proof: schema + subject + citation as **separate** checks.
   Tokens/latency logged. Prompt/content not logged.

## Pattern

### Graphs

- `api_workers`: `openai` 3.x only (`ai.openai`). No `litellm`
  in any Python env.
- `gpu_ml`: FastEmbed, faster-whisper, torch, ONNX.
- `bifrost`: gateway container only (`maximhq/bifrost:v2.2.1`,
  `environments.bifrost`). Own OTel plugin line. Never merge
  into the API lock.
- CLIProxyAPI: GitHub release binary. Not a uv extra.

### Bifrost gateway

Default: every LLM call goes through Bifrost
(OpenAI-compatible `/v1`). It owns the provider catalogue,
keys, failover, semantic cache, and governance plugins.
CLIProxyAPI is an upstream the gateway can route to, not a
second stack.

Direct provider SDK calls only when all of these hold: a
single official origin, no failover, and an operation Bifrost
cannot express (named exception in the PR).

A Chat Completions 200 does not prove tools, json_schema,
vision, Responses, or embeddings. Probe the op you ship.

### Streaming

CONTRACTS is the wire. Native `fastapi.sse` (`response_class`
+ yield, not `return EventSourceResponse`).
`data` = JSON. Sentinels = `raw_data`. Terminal `event:
done` + `raw_data: [DONE]`. In-band fail: `event: error`.
Closed socket ≠ job success.

openai SDK: `async with client.chat.completions.stream(...)`.
Yield deltas. Do not buffer-then-fake.
No `AsyncSession` across the generator.

### Structured output

1. Probe the provider model for `response_format` /
   `text_format` support through the gateway. Else do not
   claim strict.
2. `.parse()` → `parsed` or `refusal`, else
   `response_format=Model` then `Model.model_validate_json`.
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
— not a gateway `embeddings.create` in the API request path.
Gateway embeddings are a different product feature.
Ban: `QdrantClient.set_model` / mixin `Document` embed.

### CLIProxyAPI

Optional sidecar. Bind localhost. `request-log: false`.
`/v1/chat/completions` + `/v1/responses`. No embeddings
route. Probe the shipped op.

### Logs / PII

Gateway logging is configured in the Bifrost container (its
own OTel/logging plugins), not in the API. On the API side
log request id, model alias, latency, tokens, status. Do not
log messages, completions, tool args, student text,
embeddings. No Langfuse I/O callbacks.
No `OPENAI_LOG=debug`. QUALITY spine only.

### STT

faster-whisper in `gpu_ml`. API enqueues. Do not import
whisper / torch / FastEmbed in uvicorn.

## Done

- Call site is the Bifrost client or a named direct-provider
  exception.
- No `litellm` / `litellm[proxy-runtime]` in any env; openai
  is `ai.openai` (3.x).
- Stream uses `fastapi.sse` + terminal events + job row.
- Schema, subject, and citation stayed separate.
- Index vectors came from `gpu_ml` with the alias identity.
  Qdrant still has DATA's access filter.
- Logs have route metadata and no prompt/PII.

## Repair

- `litellm` import or proxy config in API lock: remove; call
  the gateway base_url.
- openai pinned back to 2.x: repin to `ai.openai` 3.x.
- FastEmbed / torch in API: move to `gpu_ml`.
- Mixin embed written into `chunks`: stop, rebuild if
  contaminated.
- Prompt in OpenObserve: wipe that stream, keep redaction
  on.
- Schema-valid treated as graded: split the checks.
- LangChain as orchestration: remove; keep Pydantic steps.
