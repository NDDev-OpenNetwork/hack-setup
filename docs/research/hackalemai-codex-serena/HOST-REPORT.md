# Host-specific setup report

Status: PARTIAL. Required Codex/runtime pins were measured on this Mac.
Isolated Serena 1.7.0, hook trust, Flutter-via-Serena, Unicode rename,
and two-worktree isolation were not executed. Pack capability text is
not treated as a working system.

## Identity

| Field | Value |
| --- | --- |
| Host | rldyourmnd Mac |
| OS | macOS 26.7 (25G224) Darwin arm64 |
| Worktree | `/Users/rldyourmnd/Developer/NDDev-OpenNetwork/hack-setup` |
| Branch | `main` tracking `origin/main` |
| HEAD | `072c97bcf0110b70a00fda051172cb1f420df7c9` |
| Tree | dirty; 29 tracked diffs + untracked standards/skills/pack (this session plus prior pin/gate work) |
| Check time | 2026-09-20 01:29:05 +05 (Asia/Almaty) |
| Pack | v1.1 at `docs/research/hackalemai-codex-serena/` |
| Zip | `hackalemai-codex-serena-2026-09-19-reviewed-v1.1.zip` sha256 `cdd7dee30440a68096c894bbf1318fde57e36e420132cd3c5e6f8668283f2326` (gitignored, still on disk) |
| Codex source | pin `0.155.1` / `rust-v0.155.1` / commit `be2951ea34f0d295ed0becf97079f92fa5f6950e` |
| Cutoff in pack | 2026-09-19 23:59:59 Asia/Almaty |
| Inspection | 2026-09-20 |

## Toolchain manifest

| Component | Requested | Actual | Executable | Status |
| --- | --- | --- | --- | --- |
| Codex CLI | 0.155.1 | `codex-cli 0.155.1` | `$REPO/.local/bin/codex` | PASS |
| Node | 24.21.0 | v24.21.0 | `$REPO/.local/bin/node` | PASS |
| bun | 1.4.2 | 1.4.2 | `$REPO/.local/bin/bun` | PASS |
| CPython | 3.14.7 | 3.14.7 | `$REPO/.local/bin/python3` | PASS |
| uv | 0.12.17 | 0.12.17 | `$REPO/.local/bin/uv` | PASS |
| Isolated Serena 1.7.0 | `949a27ef1e5fda1a6e7b561e777bcece345c6ffd` | no `serena` on PATH; not in `uv tool list` | — | NOT-TESTED |
| Cursor Serena MCP | n/a | plugin `plugin-rldyour-mcps-serena` in this session | MCP, not `uv tool` | NOT the Codex isolated install |
| ty (pin / Serena) | 0.0.82 | brew `ty 0.0.56` at `/opt/homebrew/bin/ty` | Homebrew, not the pin | DRIFT / unused by this repo |
| TS product compiler | 7.0.2 | no app sources | — | NOT-APPLICABLE |
| TS Serena navigator | adapter default 5.9.3 / tsserver 5.1.3 | typescript language not enabled | — | NOT-APPLICABLE |
| Flutter (pin) | 3.47.5 / Dart 3.13.4 | host Flutter 3.44.5 / Dart 3.12.2 | `/opt/homebrew/bin/flutter` | DRIFT; Serena `dart` not enabled |
| rustc (declared) | 1.98.1 | 1.96.1 Homebrew | `/opt/homebrew/bin/rustc` | DRIFT |
| go (declared) | 1.27.1 | 1.26.4 | `/opt/homebrew/bin/go` | DRIFT |
| ruff (declared) | 0.16.8 | 0.15.17 | `~/.local/bin/ruff` | DRIFT |
| pytest (declared) | 9.1.1 | 9.0.2 | `~/.local/bin/pytest` | DRIFT |
| `hooks.json` | optional, omitted | absent; `~/.codex/hooks` absent | — | NOT-APPLICABLE |

No MCP `command = /ABS/serena` was written into shared `.codex/config.toml`.
No hook `trusted_hash` was invented.

## Configuration diff and ownership

Live integration from pack 1.1 (this session):

- `docs/agent-standards/` — 18 standards, router `INDEX.md`
- `.agents/skills/` — 10 repo skills
- `AGENTS.md` — compact Serena-first router; 5264 bytes
- `.serena/project.yml` — `languages: [python_ty, markdown, json, yaml, toml]`; `ty_version: "0.0.82"`; no `base_modes`; no blanket `**/build/**`
- `.serena/project.local.yml` — comment-only, no host paths; shallow-merge warning
- `scripts/check_codex_setup.py` — skills, standards, Serena project constraints
- Pack dump: `docs/research/hackalemai-codex-serena/`
- Zip gitignored at repo root

Not applied:

- isolated `SERENA_HOME` / `serena_config.yml` `base_modes: [editing]` + `tool_timeout: 90`
- Codex MCP Serena stanza (host-owned, absolute paths)
- `hooks.json` / hook-definition trust
- typescript / dart language servers
- product source, generated clients, second worktree

`~/.serena` exists as a user home. It is not the isolated preparation profile and was not treated as accepted Codex config.

## Capability results

Statuses are `PASS` / `FAIL` / `NOT-TESTED` / `UNSUPPORTED` / `NOT-APPLICABLE`.
Static file presence is not Codex/Serena runtime proof.

| ID | Status | Evidence |
| --- | --- | --- |
| SET-01 | PARTIAL | Codex/Node/bun/Python/uv PASS. `serena` binary MISSING. |
| SET-02 | NOT-TESTED | Isolated Serena home not created; existing Cursor/home Serena not overwritten. |
| SET-03 | PARTIAL | Router files exist. Codex session load of nested rules not exercised. |
| SET-04 | PARTIAL | Ten skill names on disk. Codex skill discovery not exercised. |
| SET-05 | NOT-TESTED | No Codex MCP Serena connection. |
| SET-06 | NOT-TESTED | Isolated project activation not run. |
| SET-07 | NOT-TESTED | No Serena LSP navigation run against this tree. |
| SET-08 | NOT-TESTED | No isolated rename. |
| SET-09 | NOT-TESTED | No Unicode offset case. |
| SET-10 | NOT-TESTED | No Serena refresh against uncommitted symbols. |
| SET-11 | NOT-TESTED | Single worktree only. |
| SET-12 | NOT-APPLICABLE | typescript not enabled; no app TSX. |
| SET-13 | NOT-TESTED | Host Flutter/Dart exist but drift from pin; Serena dart off. |
| SET-14 | NOT-APPLICABLE | No API/Telegram/GPU lockfiles in this staging repo. |
| SET-15 | PARTIAL | Artifact validator parses repo JSON/YAML/TOML. Schema-invalid consumer configs not run. |
| SET-16 | NOT-TESTED | No Markdown language-server case. INDEX links checked statically. |
| SET-17 | NOT-APPLICABLE | No OpenAPI clients. |
| SET-18 | NOT-APPLICABLE | Hooks omitted on purpose. SessionEnd 3s rule is documentation only. |
| SET-19 | NOT-TESTED | No unsupported-format runtime case. |
| SET-20 | NOT-APPLICABLE | No Compose/Caddy/Vector stack running here. |
| SET-21 | NOT-TESTED | Missing-server recovery not run. |
| SET-22 | PASS | No real credentials probed; no canaries written. |
| SET-23 | NOT-TESTED | No startup/RSS measurements. |
| SET-24 | NOT-TESTED | Isolated config not reapplied. |
| SET-25 | PARTIAL | Pack/pin cutoff and Codex commit recorded. Serena source install not present. |
| SET-26 | PARTIAL | `project.yml` omits `base_modes`. Isolated global `base_modes: [editing]` not installed. |
| SET-27 | PARTIAL | Shared YAML has no host paths. Local override merge not executed. |
| SET-28 | NOT-APPLICABLE | No hooks to trust. |
| SET-29 | NOT-TESTED | No timed-out Serena mutation. |
| SET-30 | PASS | No blanket `**/build/**` / `**/dist/**` / `**/target/**` / `**/uploads/**`. |
| SET-31 | PASS | No `LanguageServerRegistry` / `ExternalLanguageServerId` in live config. |
| SET-32 | PASS | `make gate` + `pytest -q` left authored sources/lockfiles unchanged. Declared host ruff 0.15.17 / pytest 9.0.2 drift from pin 0.16.8 / 9.1.1; checks did not upgrade them. |
| SET-33 | PARTIAL | Host is macOS arm64 (Dart adapter table includes it). Analyzer not launched. Linux arm64 Dart remains unsupported in stable adapter. |
| SET-34 | NOT-APPLICABLE | No student/browser runtime. |

## Resource observations

NOT-TESTED. No isolated Serena cold/warm start.

## Remaining gaps

1. Install isolated Serena 1.7.0 (`uv tool`, commit `949a27ef…`) with its own `SERENA_HOME`.
2. Host-local Codex MCP stanza only; never commit absolute paths.
3. Materialize ty 0.0.82 for the adapter; do not treat brew 0.0.56 as the pin.
4. Optional hooks only if SessionEnd ≤ 3s and real hook-definition trust is performed.
5. Run SET-07..11 on disposable inputs, then on this repo.
6. Do not enable typescript/dart until those sources exist and the host Flutter/Dart match the pin or the pin is deliberately changed.
7. Declared brew Rust/Go/Flutter currently drift from `build/stack-pin.json`. Default doctor ignores declared drift; `--strict` would fail.

## Final decision

Ready now: Codex 0.155.1 project surfaces, Serena-first instruction router,
ten repo skills, portable `project.yml`, artifact gates, required host
runtimes.

Not ready: isolated Codex↔Serena MCP, semantic rename/Unicode/two-worktree
proof, Flutter/TS adapters, hook execution, student-code isolation.

No product source was added. This report does not certify application
library compatibility.
