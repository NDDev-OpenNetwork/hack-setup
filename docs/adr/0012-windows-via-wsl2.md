# ADR 0012: Windows support is native PowerShell

Date: 2026-09-20. Status: accepted (supersedes the earlier WSL2-only
decision taken the same day).

## Context

Team hosts are Ubuntu desktop (x86_64), Windows (x86_64), and macOS
(arm64). The first pass routed Windows through WSL2 Ubuntu; the owner
rejected that — Windows must be a first-class native target. Codex
`0.155.1` ships real Windows artifacts
(`codex-package-x86_64-pc-windows-msvc.tar.gz`, `install.ps1`,
win_amd64 wheels), Node ships `node-v24.21.0-win-x64.zip`, bun ships
`bun-windows-x64.zip`, and uv ships `uv-installer.ps1`, so every pinned
runtime has an official native asset.

## Decision

Windows gets a parallel PowerShell hierarchy that mirrors the POSIX one
file-for-file — shared pin files, shared catalog, shared module ids:

| POSIX | Windows |
| --- | --- |
| `./setup` | `.\setup.ps1` |
| `install/bootstrap.sh` | `install/bootstrap.ps1` |
| `install/env.sh` | `install/env.ps1` |
| `install/lib/{common,os,download}.sh` | `install/lib/{common,os,download}.ps1` |
| `install/modules/<nn>-*/module.sh` | `install/modules/<nn>-*/module.ps1` |

Key mappings:

- Pin reads use `ConvertFrom-Json` — no host python is required to
  bootstrap on Windows.
- sha256 via `Get-FileHash`; downloads via `curl.exe` (ships in
  Windows 10+) or `Invoke-WebRequest`; tarballs via `tar.exe`, zips via
  `Expand-Archive`.
- Codex installs through the pinned official `install.ps1`
  (`installer_ps1` in `codex-pin.json`), which manages
  `%LOCALAPPDATA%\Programs\OpenAI\Codex\bin`, junctions, and the
  persistent user PATH — the same layout the npm/native installers use.
- uv installs through the pinned `uv-installer.ps1`
  (`UV_INSTALL_DIR=$HOME\.local\bin`, `UV_NO_MODIFY_PATH=1`), then
  `uv python install 3.14.7 --default` writes real
  `python.exe`/`python3.exe` launchers into the same bin dir.
- bun's Windows zip ships only `bun.exe`; `bunx.exe` is a hardlink of
  the same file (bun dispatches on argv[0]).
- node installs from the official `win-x64.zip`; `node.exe` links into
  `~/.local/bin`, `npm.cmd`/`npx.cmd` become shims pointing into the
  extracted tree (parity with the POSIX symlinks — npm stays banned as
  the project installer).
- `.gitattributes` forces `eol=lf` so a Windows-side checkout cannot
  inject CRLF into shell scripts.
- WSL2 Ubuntu still works unchanged (it is the POSIX path) and remains
  the fallback for Windows arm64, which has no pinned packages.

Team notes for Windows:

- Prereqs: `git`, `gh` (`winget install GitHub.cli`, then
  `gh auth login`), `tar.exe` and PowerShell 5.1+ (both ship in-box).
- Run `powershell -ExecutionPolicy Bypass -File .\setup.ps1`, then
  `. .\install\env.ps1` per shell (or rely on the persistent user PATH
  the Codex installer manages).
- `codex` auth, `~/.codex` config, and the plugin cache are per-user on
  Windows, independent of WSL.

## Consequences

- Three native targets are CI-proven: `ubuntu-latest`, `macos-latest`,
  `windows-latest` (`. .\setup.ps1` + both checkers).
- `check_codex_setup.py` requires the `.ps1` twin of every module and
  the `windows-x86_64` package in `codex-pin`, `bun`, and `node`.
- Two module implementations per change (`.sh` + `.ps1`); the module
  ids, actions, and pin reads are shared so the fork is mechanical.
- Windows arm64 is fail-closed with a pointer to WSL2.
