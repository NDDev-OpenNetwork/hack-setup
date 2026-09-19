import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_check_codex_setup_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "check_codex_setup.py")],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS Codex 0.155.1 project artifacts" in result.stdout
