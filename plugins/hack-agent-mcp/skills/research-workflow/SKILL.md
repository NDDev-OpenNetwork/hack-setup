---
name: research-workflow
description: Research libraries, patterns and best practices through the pinned research MCPs. Use when checking correct API usage for a pinned version, hunting real-world code examples, or understanding an upstream repository.
---

Four read-only research surfaces, all keyless by default. Built-in
`web_search = "live"` stays the baseline for news/changelog questions;
reach for these when you need structured depth.

| Server | Shape | Best question |
| --- | --- | --- |
| `context7` | `resolve-library-id` then `query-docs` | "How does pinned version X of lib Y do Z?" |
| `grep` | `searchGitHub` literal/regex | "How do real repos call/compose this API?" |
| `deepwiki` | `read_wiki_structure`, `read_wiki_contents`, `ask_question` | "How is this repo architected?" |
| `keenable` | `search_web_pages`, `fetch_page_content` | Deep web search + clean markdown fetch |

Rules:

- Context7: always `resolve-library-id` first (max 3 calls), then
  `query-docs` with one concept per call. Pin-aware: use
  `/org/project/version` IDs when the pin fixes a version —
  `build/stack-pin.json` numbers win over whatever the docs imply.
- Grep: query literal code (`useState(`, `createClient(`), not prose.
  Filter with `language`/`repo`/`path`; results are uncurated — weigh
  repo quality before copying a pattern.
- DeepWiki: synthesised, may lag the repo; confirm load-bearing claims
  against source. Public repos only on the keyless endpoint.
- Keenable: 1000 req/h keyless; do not burn it where built-in
  `web_search` already answers. `fetch_page_content` is the clean
  markdown path for a known URL.
- Optional keys via env only: `CONTEXT7_API_KEY`, `KEENABLE_API_KEY`.
