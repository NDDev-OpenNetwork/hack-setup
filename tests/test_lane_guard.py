"""Lane-guard regression tests for .codex/hooks/hack_mode.py PreToolUse
(issue #5): quoted refspecs, `git -C` path resolution, per-target lane
authority, orchestrator marker, feature-branch allowance.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".codex" / "hooks" / "hack_mode.py"
LANES = json.dumps({"protected_branches": ["dev", "main"]})


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True,
    )


def _mk_repo(path: Path, *, lanes: bool, orchestrator: bool,
             branch: str = "feat/1-x") -> Path:
    path.mkdir(parents=True)
    _git(path, "init", "-q", "-b", branch)
    _git(path, "commit", "-q", "--allow-empty", "-m", "init")
    if lanes:
        (path / ".codex").mkdir()
        (path / ".codex" / "lanes.json").write_text(LANES)
    if orchestrator:
        (path / ".agent").mkdir(exist_ok=True)
        (path / ".agent" / "orchestrator").touch()
    return path


def _pretool(cmd: str, cwd: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(HOOK), "pretooluse"],
        input=json.dumps({"tool_input": {"cmd": cmd}, "cwd": str(cwd)}),
        capture_output=True, text=True, timeout=15,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.strip()
    return json.loads(out) if out else {}


def _denied(cmd: str, cwd: Path) -> bool:
    doc = _pretool(cmd, cwd)
    out = doc.get("hookSpecificOutput") or {}
    return out.get("permissionDecision") == "deny"


import pytest


@pytest.fixture()
def repos(tmp_path: Path):
    worker = _mk_repo(tmp_path / "worker", lanes=True, orchestrator=False)
    orch = _mk_repo(tmp_path / "orch", lanes=True, orchestrator=True)
    free = _mk_repo(tmp_path / "free", lanes=False, orchestrator=False)
    spaced = _mk_repo(tmp_path / "repo with space", lanes=True,
                      orchestrator=False)
    dev_head = _mk_repo(tmp_path / "devhead", lanes=True,
                        orchestrator=False, branch="dev")
    return worker, orch, free, spaced, dev_head


def test_quoted_protected_refs_denied(repos):
    worker, *_ = repos
    for cmd in (
        'git push origin "dev"',
        "git push origin 'dev'",
        'git push origin "HEAD:main"',
        'git push origin "+feat/x:refs/heads/main"',
    ):
        assert _denied(cmd, worker), cmd


def test_plain_and_special_pushes_denied(repos):
    worker, *_ = repos
    for cmd in (
        "git push origin dev",
        "git push origin HEAD:main",
        "git push --all origin",
        "git push --mirror",
        "git push origin -d dev",
        "git push --delete origin main",
        "gh pr merge 12 --squash",
        "gh api repos/o/r/pulls/3/merge -X PUT",
    ):
        assert _denied(cmd, worker), cmd


def test_git_c_target_authority(repos):
    worker, orch, free, spaced, _ = repos
    # -C into a laned repo denies even when cwd has no lanes / is not a repo
    assert _denied(f"git -C {worker} push origin dev", free)
    assert _denied(f'git -C "{spaced}" push origin dev', free)
    assert _denied(f"git -C {worker} push origin dev", Path("/tmp"))
    # -C into a lane-free or orchestrator repo does not deny
    assert not _denied(f"git -C {free} push origin main", worker)
    assert not _denied(f"git -C {orch} push origin dev", worker)


def test_implicit_push_denied_on_protected_head(repos):
    *_, dev_head = repos
    assert _denied("git push", dev_head)
    assert _denied("git push origin", dev_head)
    assert _denied("git push origin HEAD", dev_head)


def test_feature_and_personal_lanes_allowed(repos):
    worker, orch, free, _, _ = repos
    for cmd in (
        "git push origin feat/12-main-fix",
        "git push origin danil",
        "git push -u origin feat/3-x",
        "git push origin feat/x:dev-notes",  # dest not protected
        "git status",
        "git fetch origin dev",
        "git commit -m 'push dev'",  # word inside message
    ):
        assert not _denied(cmd, worker), cmd
    # implicit push on a feature branch is fine
    assert not _denied("git push", worker)
    # orchestrator checkout may push protected branches and merge PRs
    assert not _denied("git push origin dev", orch)
    assert not _denied("gh pr merge 12", orch)
    # repo without lanes.json is unrestricted
    assert not _denied("git push origin main", free)
