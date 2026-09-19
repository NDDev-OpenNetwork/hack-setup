# 5. Codex on-demand rule catalogue

- Status: accepted
- Date: 2026-09-20
- Decision-Makers: Danil Silantyev

## Context and Problem Statement

The team needs durable technology, format, and document rules for the
frozen stack. Codex CLI is pinned at `0.155.1`. That release has no
Cursor-style `.mdc` / `alwaysApply` / glob loader. Root `AGENTS.md` is
capped at a combined 32 KiB and is always injected for the cwd chain.

Dumping an 18-file always-on catalogue into `AGENTS.md` or
`project_doc_fallback_filenames` would truncate, pollute every setup
turn, and smuggle unpinned topics.

## Decision Outcome

- Keep root `AGENTS.md` as a router plus non-negotiables.
- Store the catalogue in `docs/rules/`. Codex does not auto-load it.
- Load rules through `$apply-stack-rule` and explicit path reads.
- Write rules from `build/stack-pin.json` and ADRs 0001–0004, 0006–0007. The
  reviewed pack under `docs/research/` is research, not runtime.
- Add nested `AGENTS.md` only when a product directory exists.
- Do not use hooks, memories, or `.codex/rules` as a style-guide loader.
  In 0.155.1, `.codex/rules` is not an AGENTS-equivalent surface.

## Consequences

- Positive: setup turns stay small; product rules exist before code.
- Negative: the model must actually open the matching file. A forgotten
  read is a process miss, not a loader miss.
- Neutral: Cloud code review only sees `## Code Review Rules` in
  `AGENTS.md`, not the whole catalogue.
