"""Hermetic tests for the devin-setup tree — no network, no devin/herdr
binaries, no user config touched (DEVIN env + HOME redirected)."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".devin" / "hooks" / "devin_mode.py"


def run_hook(event: str, stdin: str = "", env_extra: dict | None = None,
             cwd: Path | None = None) -> subprocess.CompletedProcess:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(ROOT / ".agent" / "test-home"),
        "DEVIN_PROJECT_DIR": str(cwd or ROOT),
        **(env_extra or {}),
    }
    Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [sys.executable, str(HOOK), event],
        input=stdin, capture_output=True, text=True, timeout=15,
        env=env, cwd=str(cwd or ROOT),
    )


def test_checker_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_devin_setup.py")],
        capture_output=True, text=True, timeout=60, cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stderr


def test_stack_pin_is_generated_copy() -> None:
    assert (ROOT / "build" / "stack-pin.json").read_bytes() == (
        ROOT.parent / "build" / "stack-pin.json"
    ).read_bytes()


def test_shared_modules_byte_identical() -> None:
    for rel in ("lib/common.sh", "lib/os.ps1",
                "modules/15-member/module.sh", "modules/30-runtimes/module.ps1"):
        assert (ROOT / "install" / rel).read_bytes() == (
            ROOT.parent / "install" / rel
        ).read_bytes(), rel


def test_hook_session_emits_setup_note() -> None:
    proc = run_hook("session")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "SETUP CHECKOUT" in ctx and "STATUS" in ctx


def test_hook_prompt_emits_status() -> None:
    proc = run_hook("prompt", stdin=json.dumps({"prompt": "hello"}))
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert "STATUS" in payload["hookSpecificOutput"]["additionalContext"]


def test_hook_lane_guard_blocks_protected_push(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    (repo / ".devin").mkdir()
    (repo / ".devin" / "lanes.json").write_text(
        json.dumps({"protected_branches": ["dev", "main"]}))
    proc = run_hook(
        "pretooluse",
        stdin=json.dumps({
            "tool_input": {"command": "git push origin main"},
            "cwd": str(repo),
        }),
        cwd=repo,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["decision"] == "block"
    assert "lane law" in payload["reason"]


def test_hook_lane_guard_allows_feature_push(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    (repo / ".devin").mkdir()
    (repo / ".devin" / "lanes.json").write_text(
        json.dumps({"protected_branches": ["dev", "main"]}))
    proc = run_hook(
        "pretooluse",
        stdin=json.dumps({
            "tool_input": {"command": "git push origin feat/12-fix"},
            "cwd": str(repo),
        }),
        cwd=repo,
    )
    assert proc.returncode == 0
    assert not proc.stdout.strip()


def test_hook_orchestrator_marker_bypasses(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    (repo / ".devin").mkdir()
    (repo / ".devin" / "lanes.json").write_text(
        json.dumps({"protected_branches": ["main"]}))
    (repo / ".agent").mkdir()
    (repo / ".agent" / "orchestrator").write_text("")
    proc = run_hook(
        "pretooluse",
        stdin=json.dumps({
            "tool_input": {"command": "git push origin main"},
            "cwd": str(repo),
        }),
        cwd=repo,
    )
    assert proc.returncode == 0
    assert not proc.stdout.strip()


def test_hook_bad_input_never_crashes() -> None:
    for event in ("prompt", "pretooluse", "posttooluse", "sessionend"):
        proc = run_hook(event, stdin="{not json")
        assert proc.returncode == 0, (event, proc.stderr)


def test_bootstrap_member_flag_parsing() -> None:
    if sys.platform == "win32":
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(ROOT / "setup.ps1"), "--member=", "--dry-run"],
            capture_output=True, text=True, timeout=30, cwd=ROOT,
        )
        assert "needs a name" in proc.stderr
        return
    proc = subprocess.run(
        ["sh", "-c",
         f'cd "{ROOT}" && ./setup --member= --dry-run 2>&1 || true'],
        capture_output=True, text=True, timeout=30,
    )
    assert "needs a name" in proc.stdout
