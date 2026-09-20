---
name: component-workflow
description: Browse and install shadcn/ui components through the shadcn MCP server. Use when picking registry components, reading their source/examples, or composing add commands in the product repo.
---

`shadcn` MCP runs `bunx shadcn@4.21.0 mcp` (pin: `frontend.shadcn`).
It reads `components.json` from the session working directory, so the
tools only produce registry answers inside the product repo. In
hack-setup they return "no components.json" — that is correct, not a
fault.

Flow inside the product repo:

1. `search_items_in_registries` (fuzzy) or `list_items_in_registries`
   to find candidates across configured registries (`@shadcn` built-in).
2. `view_items_in_registries` for the item source, or
   `get_item_examples_from_registries` for full demo code (`*-demo`,
   `example-*` items).
3. `get_add_command_for_items` returns the CLI command; run it yourself:
   `bunx shadcn@4.21.0 add <item>`. Never `bun add shadcn` — the package
   is CLI-only per the pin.
4. `get_audit_checklist` after adding components.

Registry config (registries, auth headers) lives in the product repo's
`components.json`, not in this setup repo. Style primitives come from
`@base-ui/react@1.8.0` per the pin — do not hand-install radix shims.
