"""env.ps1 twin of test_env_sh.py — PATH order on native Windows:
repo .local/bin first, then the user bin (HACK_USER_BIN-aware)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="env.ps1 is the Windows surface"
)

REPO = Path(__file__).resolve().parents[1]
ENV_PS1 = REPO / "install" / "env.ps1"
PIN_BIN = REPO / ".local" / "bin"
HOME_BIN = Path.home() / ".local" / "bin"


def _path_heads(extra_env: dict | None = None) -> list[str]:
    env = os.environ.copy()
    env.update(extra_env or {})
    script = (
        f'. "{ENV_PS1}"; '
        "$p = $env:PATH -split ';'; Write-Output $p[0]; Write-Output $p[1]"
    )
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell, "need pwsh or powershell"
    result = subprocess.run(
        [shell, "-NoProfile", "-Command", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) >= 2, result.stdout
    return lines[:2]


def test_env_ps1_path_order() -> None:
    heads = _path_heads()
    assert Path(heads[0]) == PIN_BIN
    assert Path(heads[1]) == HOME_BIN


def test_env_ps1_honors_hack_user_bin(tmp_path: Path) -> None:
    heads = _path_heads({"HACK_USER_BIN": str(tmp_path)})
    assert Path(heads[0]) == PIN_BIN
    assert Path(heads[1]) == tmp_path
