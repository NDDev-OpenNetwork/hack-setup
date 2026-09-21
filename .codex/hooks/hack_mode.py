#!/usr/bin/env python3
"""hack-mode lifecycle hook for Codex (project layer, .codex/hooks.json).

session: inject the hack-mode ruleset (SKILL.md body) as SessionStart
additionalContext. prompt: track standalone mode commands on
UserPromptSubmit and emit a one-line reminder every prompt while the
mode is on. Never blocks the session: stdin is read on a thread with a
timeout (upstream issue #443 — PowerShell can swallow EOF), every
failure path exits silently.
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = Path.home() / ".codex" / f"hack-mode-{ROOT.name}.json"


def _skill_path() -> Path:
    # Repo checkout first; a projected product repo resolves the same
    # skill from the installed plugin cache instead.
    local = (
        ROOT / "plugins" / "hack-agent-workflow"
        / "skills" / "hack-mode" / "SKILL.md"
    )
    if local.is_file():
        return local
    cache = Path.home() / ".codex" / "plugins" / "cache"
    try:
        for hit in sorted(
            cache.glob("*/hack-agent-workflow/*/skills/hack-mode/SKILL.md")
        ):
            return hit
    except Exception:
        pass
    return local


SKILL = _skill_path()

REMINDER = (
    "HACK-MODE ACTIVE: laziest working solution (YAGNI ladder), "
    "no review round, no test suite — done means verified live on the "
    "server; `hack:` comment on every deliberately cut corner."
)

OFF_COMMANDS = {"normal mode", "stop hack mode", "stop hack-mode", "hack off"}
ON_COMMANDS = {"hack mode", "hack-mode", "hack on", "hack full"}
ULTRA_COMMANDS = {"hack ultra", "hack-mode ultra"}

GH_CACHE = Path.home() / ".codex" / f"hack-issues-{ROOT.name}.json"
GH_TTL = 60


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True, text=True, timeout=2,
        ).stdout.strip()
    except Exception:
        return ""


def _refresh_issues() -> None:
    try:
        proc = subprocess.run(
            ["gh", "issue", "list", "--assignee", "@me", "--state", "open",
             "--json", "number,title", "--limit", "10"],
            capture_output=True, text=True, timeout=8, cwd=ROOT,
        )
        if proc.returncode == 0:
            tmp = GH_CACHE.with_suffix(".tmp")
            tmp.write_text(json.dumps(
                {"ts": time.time(), "root": str(ROOT),
                 "issues": json.loads(proc.stdout)}))
            os.replace(tmp, GH_CACHE)
    except Exception:
        pass


def issues_status() -> str:
    try:
        cache = json.loads(GH_CACHE.read_text())
    except Exception:
        cache = {}
    fresh = (
        cache.get("root") == str(ROOT)
        and time.time() - float(cache.get("ts", 0)) < GH_TTL
    )
    if not fresh:
        try:
            subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "_refresh-issues"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL, start_new_session=True,
            )
        except Exception:
            pass
    issues = cache.get("issues") or []
    if not issues:
        return "issues:@me=none"
    return "issues:@me=" + ",".join(f"#{i['number']}" for i in issues)


def status_line() -> str:
    branch = _git("branch", "--show-current") or "?"
    dirty = _git("status", "--porcelain")
    n_dirty = len([l for l in dirty.splitlines() if l.strip()])
    last = _git("log", "-1", "--format=%h %s")[:60]
    return (
        f"STATUS repo={ROOT.name} branch={branch} dirty={n_dirty} "
        f"last={last!r} {issues_status()}"
    )


def read_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def write_state(state: dict) -> None:
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(state))
    except Exception:
        pass


def mode() -> str:
    return read_state().get(str(ROOT), "full")


def set_mode(value: str) -> None:
    state = read_state()
    if value == "full":
        state.pop(str(ROOT), None)
    else:
        state[str(ROOT)] = value
    write_state(state)


def ruleset(level: str) -> str:
    try:
        body = SKILL.read_text().split("---", 2)[2].strip()
    except Exception:
        body = REMINDER
    if level == "ultra":
        body += (
            "\n\nULTRA: challenge the requirement itself before building; "
            "deletion before addition; ship the one-liner."
        )
    return f"HACK-MODE ACTIVE — level: {level}\n\n{body}"


def emit(context: str = "", message: str = "", event: str = "") -> None:
    out = {}
    if message:
        out["systemMessage"] = message
    if context:
        out["hookSpecificOutput"] = {
            "hookEventName": event
            or (
                "SessionStart"
                if (sys.argv[1] if len(sys.argv) > 1 else "") == "session"
                else "UserPromptSubmit"
            ),
            "additionalContext": context,
        }
    if out:
        sys.stdout.write(json.dumps(out))


def session() -> None:
    level = mode()
    if level == "off":
        emit(message="HACK-MODE:OFF")
        return
    emit(ruleset(level), f"HACK-MODE:{level.upper()}")


def prompt(payload: dict) -> None:
    # Whole-message match only (upstream #161): an ordinary prompt that
    # happens to contain the phrase must not silently toggle the mode.
    text = str(payload.get("prompt") or "").strip().lower()
    if text in OFF_COMMANDS:
        set_mode("off")
        emit(message="HACK-MODE:OFF", context="HACK-MODE OFF for this project.")
        return
    if text in ULTRA_COMMANDS:
        set_mode("ultra")
        emit(message="HACK-MODE:ULTRA", context=ruleset("ultra"))
        return
    if text in ON_COMMANDS:
        set_mode("full")
        emit(message="HACK-MODE:FULL", context=ruleset("full"))
        return
    if mode() != "off":
        emit(context=f"{REMINDER}\n{status_line()}")


LANES_FILE = ".codex/lanes.json"
ORCH_MARKER = ".agent/orchestrator"


def _tool_command(payload: dict) -> str:
    """Exec surface arg shapes in 0.155.1 (be2951ea): exec_command sends
    `cmd` (string), write_stdin sends `chars` (string), legacy/permission
    payloads send `command` (string or argv list)."""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    for key in ("cmd", "command", "chars", "input"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, list):
            return " ".join(str(part) for part in value)
    return ""


_GIT_FLAGS = (
    r"(?:-[cC]\s+\S+|-[cC]\S+|-P|--no-pager|--literal-pathspecs"
    r"|--no-optional-locks|--(?:git-dir|work-tree|exec-path)"
    r"(?:=|\s+)\S+)\s+"
)


def _push_to(
    command: str, guard: str, root: Path | None, protected: list[str]
) -> bool:
    # `git <global-flags> push <tail>` inside one |;& segment. Guard rail,
    # not a security boundary: aliases/wrappers are out of scope, workers
    # are our own agents.
    for match in re.finditer(
        rf"\bgit\s+(?:{_GIT_FLAGS})*push\b([^|;&]*)", command
    ):
        tail = match.group(1)
        if re.search(rf"\b({guard})\b", tail):
            return True
        if re.search(r"--all\b|--mirror\b", tail):
            return True
        words = [w for w in tail.split() if not w.startswith("-")]
        refspecs = words[1:] if words else []
        if not refspecs or all(w == "HEAD" for w in refspecs):
            # `git push`, `git push origin`, `git push origin HEAD` — target
            # is upstream of HEAD: deny only when HEAD itself is protected.
            if root is not None and _current_branch(root) in protected:
                return True
    return bool(
        re.search(r"\bgh\s+pr\s+merge\b", command)
        or re.search(
            r"\bgh\s+api\b[^|;&]*(?:/merges\b|/merge\b|merge-upstream)",
            command,
        )
    )


def _current_branch(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"],
            capture_output=True, text=True, timeout=2,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def _repo_root(cwd: str) -> Path | None:
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=2,
        )
        return Path(out.stdout.strip()) if out.returncode == 0 else None
    except Exception:
        return None


def _protected_branches(root: Path) -> list[str]:
    """Lane law applies only where the tracked `.codex/lanes.json` exists —
    this setup repo pushes main/dev freely; the product repo declares lanes."""
    try:
        data = json.loads((root / LANES_FILE).read_text())
        branches = data.get("protected_branches")
        if isinstance(branches, list) and branches:
            return [str(b) for b in branches]
    except Exception:
        pass
    return []


def pretooluse(payload: dict) -> None:
    """Lane enforcement: in a repo that declares `.agent/lanes.json`, only
    the orchestrator checkout (untracked `.agent/orchestrator` marker —
    worker worktrees never have it) may push protected branches or merge
    PRs."""
    command = _tool_command(payload)
    if not command:
        return
    root = _repo_root(str(payload.get("cwd") or "."))
    if not root:
        return
    protected = _protected_branches(root)
    if not protected or (root / ORCH_MARKER).is_file():
        return
    guard = "|".join(re.escape(b) for b in protected)
    if not _push_to(command, guard, root, protected):
        return
    emit_pre(
        {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"lane law: workers push only their personal lane "
                f"(feat/<issue> -> <user>). {guard} pushes and PR merges "
                f"run from the orchestrator checkout "
                f"(mkdir -p .agent && touch .agent/orchestrator there)."
            ),
        }
    )


def emit_pre(out: dict) -> None:
    sys.stdout.write(json.dumps({"hookSpecificOutput": out}))


def posttooluse(payload: dict) -> None:
    command = _tool_command(payload)
    if not re.search(r"\bgit\b[^|;&]*\bpush\b", command):
        return
    emit(
        context=(
            "Push landed. If it carried a feature/lane: verify live on the "
            "server before calling it done — ship-verify, done means live."
        ),
        event="PostToolUse",
    )


def sessionend(payload: dict) -> None:
    root = _repo_root(str(payload.get("cwd") or "."))
    if not root:
        return
    try:
        log_dir = root / ".agent"
        log_dir.mkdir(exist_ok=True)
        with (log_dir / "session-log.ndjson").open("a") as fh:
            fh.write(json.dumps({
                "ts": int(time.time()),
                "repo": root.name,
                "branch": _git("branch", "--show-current"),
                "reason": payload.get("reason"),
                "session": payload.get("session_id"),
            }) + "\n")
    except Exception:
        pass


def read_stdin(timeout: float = 1.5) -> str:
    buf = []

    def _read() -> None:
        try:
            buf.append(sys.stdin.read())
        except Exception:
            pass

    t = threading.Thread(target=_read, daemon=True)
    t.start()
    t.join(timeout)
    return buf[0] if buf else ""


def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else "session"
    if event == "_refresh-issues":
        _refresh_issues()
        return
    if event == "session":
        session()
        return
    raw = read_stdin()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}
    if event == "pretooluse":
        pretooluse(payload)
        return
    if event == "posttooluse":
        posttooluse(payload)
        return
    if event == "sessionend":
        sessionend(payload)
        return
    if event == "interrupt":
        payload.setdefault("reason", "interrupt")
        sessionend(payload)
        return
    prompt(payload)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
