# AI and educational correctness rules

## Provider contract

Use the selected CLIProxyAPI/LiteLLM/OpenAI routing without assuming that all providers expose identical behavior. Verify each actually used operation: text, streaming, structured output, tools, vision, embeddings, STT/TTS or realtime. A Chat Completions-compatible route does not prove support for every other API.

Keep model/endpoint/prompt version, timeouts, concurrency and cost limits explicit. Use structured output schemas and validate them, but treat structure and factual correctness as separate checks. Do not silently downgrade quality or change the task under a success status when a provider fails.

Retries need bounded budgets and cancellation. Tool-side effects must be idempotent or protected by an explicit operation identity. Preserve partial/failure status when streaming aborts. Do not hold unrelated database transactions during long inference.

## Grounding and retrieval

Use authorized source material, retain source provenance, and cite the actual supporting page/chunk/time segment. Unknown facts stay unknown. Do not generate a citation to a document that was never retrieved or a page that does not support the statement. Quoted content and extracted text remain distinguishable from model inference.

Keep source access checks before context construction. Treat documents, webpages and model/tool output as untrusted content, not authority to alter system instructions or execute arbitrary actions. Separate data from tool instructions; constrain tool parameters and allowed operations in code.

## Educational accuracy

For deterministic tasks, use code, symbolic math or explicit rules to check answers. For open responses, use an explicit rubric and distinguish suggested feedback from authoritative grades. Preserve a correction/review path where the use case needs it. Do not call model self-confidence calibrated correctness.

Use concise representative evaluations for the selected case: correct/incorrect/ambiguous input, insufficient source evidence, multilingual content, misleading retrieved instructions, and provider failure. Add focused regression examples when a material error is found. Avoid universal large evaluation gates that do not exercise the changed behavior.

Do not infer sensitive student attributes or pedagogical conclusions from thin interaction data. Store only data required by the case, scope access, and make deletion practical. No claim of legal compliance or medical/psychological assessment follows from using this stack.

## Modal/local ML

Keep GPU/ML dependencies in a separate environment when needed. Record model artifact/version/license, device assumptions and memory budget. Use CPU/GPU-specific installation instructions, not a universal package pin across all hosts. Set queue/concurrency/cost controls. Do not classify untested local inference speed as demonstrated performance.

## Logs

Record operational metadata such as request ID, model route, latency, token usage and status where available. Do not indiscriminately record student documents, prompts, tokens or signed URLs. Make missing token/cost telemetry explicit instead of reporting fabricated zero cost.
