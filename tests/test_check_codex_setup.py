import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WIN32 = sys.platform == "win32"


def test_check_codex_setup_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "check_codex_setup.py")],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS [artifact] Codex 0.155.1 project artifacts" in result.stdout


def test_setup_dry_run_passes() -> None:
    # Extensionless POSIX entry cannot spawn on native Windows — the ps1
    # twin prints the same dry-run lines (issue #24).
    if WIN32:
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(REPO / "setup.ps1"), "--dry-run",
        ]
    else:
        cmd = [str(REPO / "setup"), "--dry-run"]
    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "dry-run; no downloads" in result.stdout
    assert "would verify https://github.com/openai/codex/releases/" in result.stdout
    assert "would require sha256" in result.stdout
