---
name: quality-gate
description: Run the Saint Tibo Codex setup checks. Use before calling work done, after changing AGENTS.md, skills, plugin, marketplace, agents, or config.
---

Run these commands and quote their output:

```bash
./setup --status
python3 scripts/check_codex_setup.py
codex --version
```

`codex --version` must be `codex-cli 0.155.1`. After clone, `./setup` is
the installer; `. install/env.sh` puts the pinned binary first.

If any command fails, fix the artifact or the local CLI. Do not claim a
pass without running the commands.
