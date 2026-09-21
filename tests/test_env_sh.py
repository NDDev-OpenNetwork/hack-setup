import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="env.sh is the POSIX surface; Windows uses env.ps1 (test_env_ps1.py)",
)

REPO = Path(__file__).resolve().parents[1]
ENV_SH = REPO / "install" / "env.sh"
PIN_BIN = REPO / ".local" / "bin"
HOME_BIN = Path.home() / ".local" / "bin"


def _path_heads(shell: list[str], source: Path, cwd: Path) -> list[str]:
    script = (
        f'. "{source}" && {sys.executable} -c '
        '"import os; p=os.environ[\\"PATH\\"].split(\\":\\"); print(p[0]); print(p[1])"'
    )
    result = subprocess.run(
        [*shell, "-c", script],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=os.environ.copy(),
    )
    assert result.returncode == 0, result.stderr or result.stdout
    lines = [line for line in result.stdout.splitlines() if line]
    assert len(lines) >= 2, result.stdout
    return lines[:2]


def _assert_pin_path(heads: list[str]) -> None:
    assert heads[0] == str(PIN_BIN), heads
    assert heads[1] == str(HOME_BIN), heads


def test_env_sh_path_bash_and_zsh() -> None:
    cases = []
    if shutil.which("bash"):
        cases.append(["bash", "--norc", "--noprofile"])
    if shutil.which("zsh"):
        cases.append(["zsh", "--no-rcs"])
    assert cases, "need bash or zsh"

    for shell in cases:
        _assert_pin_path(_path_heads(shell, ENV_SH, REPO))
        _assert_pin_path(_path_heads(shell, Path("install/env.sh"), REPO))
        _assert_pin_path(_path_heads(shell, ENV_SH, Path("/tmp")))
