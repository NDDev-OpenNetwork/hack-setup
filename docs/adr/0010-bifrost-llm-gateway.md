# 10. Bifrost replaces LiteLLM as the LLM gateway

- Status: accepted
- Date: 2026-09-20
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

LiteLLM was pinned as a Python SDK (`litellm.Router` in the FastAPI
lifespan) plus an optional proxy-runtime container. It dragged two
caps: `openai>=2.20,<3` in the API env and Python `<3.15`. Bifrost
(maximhq) is a dedicated Go gateway — OpenAI-compatible, with
failover, load balancing, guardrails, and an OTel plugin — and is
substantially faster than the LiteLLM proxy.

## Decision Outcome

- LLM access is `maximhq/bifrost:v2.2.1` (docker tag, tracks GitHub
  `transports/v2.2.1`) in `environments.bifrost`; local runs may use
  `npx -y @maximhq/bifrost` (launcher `1.6.3`).
- The API env carries `openai` `3.16.2` and calls the gateway via
  `base_url=http://bifrost:8080/v1`. No `litellm` package in any env.
- The `openai<3` and `python<3.15` constraints were LiteLLM's and are
  removed. `ai.openai` is reverified against PyPI latest again;
  `ai.bifrost` is reverified against the latest `transports/*` tag.
- Provider keys, failover, semantic cache, and governance/OTel plugins
  live in the gateway config, not the API env.

## Consequences

- AI.md moves from `litellm.Router`/`acompletion` to one
  `AsyncOpenAI` client on the gateway base_url.
- Conflict rows `litellm-otel`/`litellm-python-lt-315` become
  `bifrost-otel`/`bifrost-gateway-not-sdk`; the checker and tests
  enforce the new ids.
- `openai` 2.x joins `do_not_use` (the pin is 3.x now).

## Confirmation

- `just check`, `pytest -q`, `just reverify` pass
