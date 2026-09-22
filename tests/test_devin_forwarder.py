"""Devin sessions opened in devin-setup/ get DEVIN_PROJECT_DIR = this repo
root (nearest .git), so the hook command lands on the root forwarder
.devin/hooks/devin_mode.py — it must reach the real hook and exit 0
(exit 2 = Devin blocks the prompt).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORWARDER = ROOT / ".devin" / "hooks" / "devin_mode.py"


def test_forwarder_reaches_devin_hook(tmp_path: Path) -> None:
    env = dict(os.environ)
    env["DEVIN_PROJECT_DIR"] = str(ROOT)
    # Hermetic: no git/gh on PATH, hook state under a temp config home.
    env["PATH"] = str(tmp_path)
    env["XDG_CONFIG_HOME"] = str(tmp_path)
    env["APPDATA"] = str(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(FORWARDER), "session"],
        capture_output=True, text=True, timeout=10, env=env, input="",
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
