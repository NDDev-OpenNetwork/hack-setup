# ADR 0012: Windows hosts enter through WSL2

Date: 2026-09-20. Status: accepted.

## Context

Team hosts are Ubuntu desktop (x86_64), Windows (x86_64), and macOS
(arm64). Codex `0.155.1` does ship native Windows builds
(`codex-package-x86_64-pc-windows-msvc.tar.gz`, `install.ps1`, win_amd64
wheels), but every other moving part of this setup is POSIX: the
numbered `install/modules/*/module.sh`, `install/env.sh` (bash/zsh
only), `just`, the sha256 download path, and the bun/uv/node tarball
layout. A native Windows port would fork every module into PowerShell.

## Decision

Windows support means **WSL2 Ubuntu**, full stop:

```powershell
wsl --install -d Ubuntu
```

Inside WSL the host is `linux-x86_64`: `./setup`, `env.sh`, plugins,
`just`, and both checkers run unchanged. `install/lib/os.sh` detects
WSL (`uname -r` matches `microsoft`/`WSL`), logs it, and stays on the
linux path. Native Windows remains fail-closed with a message pointing
to WSL. `.gitattributes` forces `eol=lf` so a Windows-side checkout
cannot inject CRLF into shell scripts.

WSL notes for the team:

- Clone the repo inside the WSL filesystem (`$HOME`), not under
  `/mnt/c` — NTFS mounts are slow and chmod is unreliable.
- Docker: install Docker Desktop on Windows with the WSL2 backend, or
  `docker.io` inside Ubuntu — either satisfies the `docker` declared
  tool.
- `gh` inside WSL: `apt install gh` (Ubuntu 24.04 universe) or the
  GitHub CLI apt repo; then `gh auth login`.
- Codex authentication is per-WSL-home (`~/.codex`), independent of
  the Windows-side login.

## Consequences

- One code path serves Ubuntu and Windows; CI covers it with a
  `windows-latest` job that runs `./setup` inside WSL Ubuntu.
- Anyone needing native-Windows codex can still run the official
  `install.ps1`, but the project setup, plugins, and gates are WSL-only.
