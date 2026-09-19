# AI

| Piece | Pin | Role |
| --- | --- | --- |
| CLIProxyAPI | `7.3.9` | GitHub release (`router-for-me/CLIProxyAPI`), not PyPI |
| LiteLLM | `1.101.0` | SDK / Router in the API. Python `>=3.10,<3.15` |
| openai (API env) | `2.54.0` | `>=2.20,<3`. Not 3.x |
| Codex models | primary `gpt-6-astra`, secondary `gpt-5.6-sol` (`--profile sol`), both `xhigh` | `.codex/config.toml` |

## Codex session models

- Effort is `xhigh`. Not `extra-high`. Astra rejects `none`.
- Window `872_000`, compact at `700_000`. Catalog max is `872000`;
  usable `/status` is `828400`. `700000` is below the 90% compact cap
  (`784800`), so it applies as written.
- Do not spawn Codex subagents. Do not use luna/terra.

## Orchestration

Plain Python + Pydantic + explicit steps. No required LangChain / LlamaIndex.

Accuracy checks are separate: schema validity, subject correctness, source
citation. Do not collapse them into one “the model said so” flag.

## Isolates

- API may import LiteLLM. It must not install the `proxy-runtime` extra.
- Optional LiteLLM proxy container keeps its own OTel `1.28.0` pins.
- `gpu_ml`: faster-whisper `1.2.1`, CTranslate2, PyTorch, ONNX Runtime, FastEmbed.
- Modal is not pinned.

## Transports

Token streams: SSE. Optional live classroom/voice: LiveKit (unversioned).
Do not invent a generic “realtime API” product besides SSE / WebSocket / LiveKit.
