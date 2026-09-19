---
name: one-repo-workflow
description: Coordinate three people in one Codex repo. Use when claiming files, splitting work, committing, or deciding whether to push the hackathon remote.
---

Rules:

- After clone, run `./setup` then `. install/env.sh` on macOS/Linux.
  Ready gate is `just gate`. Do not use `make`.
- Author in this repo now. The later single working remote is `BAITC-Hacks/hack-a58598e0-saint-tibo`.
- Do not push that remote unless the owner explicitly asked.
- This staging repo is public. Keep secrets and private hackathon strategy out.
- One claimed file owner at a time. Announce the files you will edit before changing them.
- Use Conventional Commits. Split implementation, tests, docs, and knowledge sync.
- Single-agent only. Do not spawn Codex subagents. Models are `gpt-6-astra` and `--profile sol` (`gpt-5.6-sol`), both `xhigh`. Context `872000` / compact `700000`.
