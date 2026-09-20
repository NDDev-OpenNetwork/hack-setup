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
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "plugins" / "hack-agent-workflow" / "skills" / "hack-mode" / "SKILL.md"
STATE = Path.home() / ".codex" / "hack-setup-mode.json"

REMINDER = (
    "HACK-MODE ACTIVE: laziest working solution (YAGNI ladder), "
    "no review round, no test suite — done means verified live on the "
    "server; `hack:` comment on every deliberately cut corner."
)

OFF_COMMANDS = {"normal mode", "stop hack mode", "stop hack-mode", "hack off"}
ON_COMMANDS = {"hack mode", "hack-mode", "hack on", "hack full"}
ULTRA_COMMANDS = {"hack ultra", "hack-mode ultra"}

GH_CACHE = Path.home() / ".codex" / "hack-setup-issues.json"
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
            GH_CACHE.write_text(json.dumps(
                {"ts": time.time(), "root": str(ROOT),
                 "issues": json.loads(proc.stdout)}))
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


def emit(context: str = "", message: str = "") -> None:
    out = {}
    if message:
        out["systemMessage"] = message
    if context:
        out["hookSpecificOutput"] = {
            "hookEventName": "SessionStart"
            if (sys.argv[1] if len(sys.argv) > 1 else "") == "session"
            else "UserPromptSubmit",
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
    prompt(payload)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
