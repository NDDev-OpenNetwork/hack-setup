import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
WIN32 = sys.platform == "win32"


def _setup(*args: str) -> subprocess.CompletedProcess:
    # Native Windows cannot CreateProcess an extensionless POSIX script —
    # route through setup.ps1 (same flag surface, single-dash tolerant).
    if WIN32:
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(REPO / "setup.ps1"), *args,
        ]
    else:
        cmd = [str(REPO / "setup"), *args]
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )


def test_member_dry_run_shows_identity_source() -> None:
    result = _setup("--dry-run", "--member", "ivan")
    assert result.returncode == 0, result.stderr
    assert "member ivan" in result.stdout
    assert "@r3flector" in result.stdout
    assert "gh api user" in result.stdout


def test_member_shorthand_flag() -> None:
    result = _setup("--dry-run", "--artem")
    assert result.returncode == 0, result.stderr
    assert "member artem" in result.stdout
    assert "@letya999" in result.stdout


def test_member_dry_run_lists_git_defaults() -> None:
    result = _setup("--dry-run", "--danil")
    assert result.returncode == 0, result.stderr
    assert "pull.ff only" in result.stdout
    assert "merge.ff false" in result.stdout
    assert "merge.conflictStyle zdiff3" in result.stdout
    assert "rerere.enabled true" in result.stdout


def test_unknown_member_fails() -> None:
    result = _setup("--dry-run", "--member", "nobody")
    assert result.returncode != 0
    assert "unknown member" in result.stderr


def test_empty_member_value_fails() -> None:
    result = _setup("--member=", "--dry-run")
    assert result.returncode != 0
    assert "needs a name" in result.stderr


@pytest.mark.skipif(WIN32, reason="on Windows --os windows is a real install")
def test_os_windows_real_install_redirects_to_ps1() -> None:
    result = _setup("--os", "windows")
    assert result.returncode != 0
    assert "setup.ps1" in result.stderr


@pytest.mark.skipif(not WIN32, reason="POSIX targets die only on Windows")
def test_os_posix_real_install_redirects_to_setup() -> None:
    result = _setup("--os", "ubuntu")
    assert result.returncode != 0
    assert "POSIX" in result.stderr


def test_os_dry_run_previews_target_platform() -> None:
    result = _setup("--dry-run", "--os", "windows")
    assert result.returncode == 0, result.stderr
    assert "windows-x86_64" in result.stdout

    result = _setup("--dry-run", "--os", "ubuntu")
    assert result.returncode == 0, result.stderr
    assert "linux-x86_64" in result.stdout


def test_unknown_os_fails() -> None:
    result = _setup("--dry-run", "--os", "beos")
    assert result.returncode != 0
    assert "unknown --os" in result.stderr
