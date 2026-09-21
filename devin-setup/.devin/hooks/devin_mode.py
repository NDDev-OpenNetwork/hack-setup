#!/usr/bin/env python3
"""hack-mode lifecycle hook for Devin CLI (project layer, .devin/hooks.v1.json).

Twin of .codex/hooks/hack_mode.py, ported to the Devin hook protocol:
stdin JSON {hook_event_name, tool_name, tool_input, session_id,
prompt_id}; stdout {decision|reason} or {hookSpecificOutput:
{hookEventName, additionalContext}}; exit 2 also blocks. Repo root comes
from DEVIN_PROJECT_DIR (the hook script may run outside the checkout).
Lane authority: .devin/lanes.json OR .codex/lanes.json — a product repo
guarded for one agent is guarded for both.
"""
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(
    os.environ.get("DEVIN_PROJECT_DIR")
    or Path(__file__).resolve().parents[2]
)

# Devin config home — same resolver herdr uses: XDG_CONFIG_HOME wins,
# else ~/.config/devin (%APPDATA%\devin on Windows).
def _devin_home() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData/Roaming") / "devin"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return (Path(xdg) if xdg else Path.home() / ".config") / "devin"

_DEVIN_HOME = _devin_home()
STATE = _DEVIN_HOME / f"hack-devin-mode-{ROOT.name}.json"


def _semver_key(v: str) -> tuple:
    try:
        return tuple(int(p) for p in v.split("."))
    except ValueError:
        return (0,)


def _skill_path() -> Path:
    # Repo checkout first; --local plugin installs are linked to the
    # source tree, cloud installs are cached under the devin share dir.
    local = (
        ROOT / "plugins" / "hack-devin-workflow" / "skills"
        / "hack-mode" / "SKILL.md"
    )
    if local.is_file():
        return local
    hits = []
    for base in (
        Path.home() / ".local/share/devin",
        _DEVIN_HOME,
    ):
        try:
            hits.extend(base.glob("**/hack-devin-workflow/**/hack-mode/SKILL.md"))
        except Exception:
            pass
    if not hits:
        return local
    hits.sort(
        key=lambda p: _semver_key(p.parent.parent.parent.name),
        reverse=True,
    )
    return hits[0]


SKILL = _skill_path()

REMINDER = (
    "HACK-MODE ACTIVE: laziest working solution (YAGNI ladder), "
    "no review round, no test suite — done means verified live on the "
    "server; `hack:` comment on every deliberately cut corner."
)

OFF_COMMANDS = {"normal mode", "stop hack mode", "stop hack-mode", "hack off"}
ON_COMMANDS = {"hack mode", "hack-mode", "hack on", "hack full"}
ULTRA_COMMANDS = {"hack ultra", "hack-mode ultra"}

GH_CACHE = _DEVIN_HOME / (
    f"hack-issues-{ROOT.name}-"
    + hashlib.sha256(str(ROOT).encode()).hexdigest()[:6]
    + ".json"
)
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
    # Never claim a state we cannot prove: a missing/foreign-root cache is
    # `?`, not `none`.
    if cache.get("root") != str(ROOT):
        return "issues:@me=?"
    issues = cache.get("issues") or []
    if not issues:
        return "issues:@me=none"
    return "issues:@me=" + ",".join(f"#{i['number']}" for i in issues)


def status_line() -> str:
    branch = _git("branch", "--show-current") or "?"
    dirty = _git("status", "--porcelain")
    n_dirty = len([l for l in dirty.splitlines() if l.strip()])
    # SHA only — commit subjects are untrusted text injected into prompts.
    last = _git("log", "-1", "--format=%h")
    member = ""
    try:
        marker = ROOT / ".agent" / "member"
        if marker.is_file():
            member = f" member={marker.read_text().strip()}"
    except Exception:
        pass
    return (
        f"STATUS repo={ROOT.name}{member} branch={branch} dirty={n_dirty} "
        f"last={last} {issues_status()}"
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


def emit(context: str = "", event: str = "") -> None:
    """Devin output protocol — no systemMessage field; context lands via
    hookSpecificOutput.additionalContext on the named event."""
    if not context:
        return
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event or "UserPromptSubmit",
            "additionalContext": context,
        }
    }))


LANES_FILES = (".devin/lanes.json", ".codex/lanes.json")
ORCH_MARKER = ".agent/orchestrator"


def _protected_branches(root: Path) -> list[str]:
    """Lane law applies only where a tracked lanes file exists — this
    setup tree pushes freely; the product repo declares lanes. Both
    .devin/lanes.json and .codex/lanes.json count so a repo guarded for
    one agent is guarded for the other."""
    branches: list[str] = []
    for name in LANES_FILES:
        try:
            data = json.loads((root / name).read_text())
            for b in data.get("protected_branches") or []:
                if str(b) not in branches:
                    branches.append(str(b))
        except Exception:
            pass
    return branches


def _is_product_checkout() -> bool:
    """The full hack-mode ruleset (no tests, done=live) governs only
    lane-guarded product checkouts. The setup repo keeps its own proof
    contract (`just gate`) — the ruleset must not leak into harness work."""
    return bool(_protected_branches(ROOT))


SETUP_NOTE = (
    "SETUP CHECKOUT — this is the harness repo, not the product. Proof is "
    "`just gate` / `just check`; the hack-mode ruleset (no review round, "
    "done=live) applies only inside lane-guarded checkouts carrying a "
    "lanes.json."
)


def session() -> None:
    level = mode()
    if level == "off":
        return
    if not _is_product_checkout():
        emit(f"{SETUP_NOTE}\n{status_line()}", event="SessionStart")
        return
    emit(ruleset(level), event="SessionStart")


def prompt(payload: dict) -> None:
    # Whole-message match only: an ordinary prompt that happens to
    # contain the phrase must not silently toggle the mode.
    text = str(payload.get("prompt") or "").strip().lower()
    product = _is_product_checkout()
    if text in OFF_COMMANDS:
        set_mode("off")
        emit("HACK-MODE OFF for this project.")
        return
    if text in ULTRA_COMMANDS:
        set_mode("ultra")
        emit(ruleset("ultra") if product else SETUP_NOTE)
        return
    if text in ON_COMMANDS:
        set_mode("full")
        emit(ruleset("full") if product else SETUP_NOTE)
        return
    if mode() != "off":
        if product:
            emit(f"{REMINDER}\n{status_line()}")
        else:
            emit(status_line())


def _tool_command(payload: dict) -> str:
    """Devin exec tool sends tool_input.command (string); other arg
    shapes are accepted defensively (argv list, cmd, chars)."""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    for key in ("command", "cmd", "chars", "input"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, list):
            return " ".join(str(part) for part in value)
    return ""


# git global flags that consume the NEXT argv token as a value.
_GIT_VALUE_FLAGS = {"-C", "-c", "--config-env", "--git-dir", "--work-tree",
                    "--namespace"}
# push options that consume the next argv token when given without `=`.
_PUSH_VALUE_OPTS = {"-o", "--push-option", "--receive-pack", "--exec",
                    "--repo"}


def _protected_ref(token: str, protected: list[str]) -> bool:
    """A refspec token hits a protected branch when its destination side
    (after `:`) or the ref itself equals it — `feat/12-main-fix` does NOT
    match `main` (token-level compare, not substring)."""
    if "*" in token:
        return True  # wildcard refspec can fan out to protected branches
    dst = token.split(":")[-1].lstrip("+")
    return dst.removeprefix("refs/heads/") in protected


_POSIX_SHLEX = os.name != "nt"


def _split_tokens(segment: str) -> list[str]:
    """Shell-aware tokenize. POSIX mode strips quoting but treats `\\` as
    an escape — on Windows that eats `C:\\repo` into `C:repo`, so Windows
    uses posix=False and strips the outer quote pair manually instead."""
    try:
        words = shlex.split(segment, posix=_POSIX_SHLEX)
    except ValueError:
        return []
    if not _POSIX_SHLEX:
        words = [
            w[1:-1] if len(w) >= 2 and w[0] == w[-1] and w[0] in "\"'" else w
            for w in words
        ]
    return words


def _git_pushes(segment: str):
    """Yield (push_argv, -C_dir|None) for each `git … push` in one shell
    segment. `git` is the command only when every preceding word is
    transparent: a wrapper (sudo/doas/env/command/time/nice), a VAR=…
    assignment, a -flag, or a bare word that is a flag's argument."""
    words = _split_tokens(segment)
    if not words:
        return
    i = 0
    prev_was_flag = False
    while i < len(words):
        w = words[i]
        if w == "git":
            break
        if re.match(r"^\w+=", w) or w in (
            "env", "command", "time", "nice", "sudo", "doas"
        ) or w.startswith("-") or prev_was_flag:
            prev_was_flag = w.startswith("-")
            i += 1
            continue
        return
    if i >= len(words) or words[i] != "git":
        return
    j = i + 1
    cwd = None
    while j < len(words):
        w = words[j]
        if w == "-C" and j + 1 < len(words):
            cwd = words[j + 1]
            j += 2
            continue
        if w.startswith("-C") and len(w) > 2:
            cwd = w[2:]
            j += 1
            continue
        if w in _GIT_VALUE_FLAGS and j + 1 < len(words):
            j += 2
            continue
        if w.startswith(("--git-dir=", "--work-tree=", "--namespace=",
                         "--config-env=", "--exec-path=", "-c")):
            j += 1
            continue
        if w.startswith("-"):
            j += 1
            continue
        break
    if j < len(words) and words[j] == "push":
        yield words[j + 1 :], cwd


def _push_args_hit(
    args: list[str], target: Path, protected: list[str]
) -> bool:
    positional = []
    deleted = False
    i = 0
    while i < len(args):
        w = args[i]
        if w in ("--all", "--mirror"):
            return True
        if w in ("-d", "--delete"):
            deleted = True
        elif w in _PUSH_VALUE_OPTS and "=" not in w:
            i += 1  # skip the option's value token
        elif not w.startswith("-"):
            positional.append(w)
        i += 1
    refspecs = positional[1:]  # first positional is the remote
    if deleted:
        return any(_protected_ref(t, protected) for t in positional)
    if any(_protected_ref(t, protected) for t in refspecs):
        return True
    if not refspecs or all(r == "HEAD" for r in refspecs):
        return _current_branch(target) in protected
    return False


def _push_to(command: str, cwd_root: Path | None,
             caller_cwd: Path | None = None) -> bool:
    """True when any `git push` in the command hits a protected branch.
    Lane authority comes from the TARGET repo (`git -C <dir>` wins over
    the caller's cwd; a relative dir resolves against `caller_cwd`).
    Guard rail, not a security boundary: aliases/wrappers are out of
    scope."""
    for segment in re.split(r"[|;&\n\r`()]+", command):
        for args, git_cwd in _git_pushes(segment):
            if git_cwd:
                target = _repo_root(git_cwd, base=caller_cwd)
            else:
                target = cwd_root
            if target is None:
                continue
            protected = _protected_branches(target)
            if not protected or (target / ORCH_MARKER).is_file():
                continue
            if _push_args_hit(args, target, protected):
                return True
    return False


def _current_branch(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"],
            capture_output=True, text=True, timeout=2,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def _repo_root(cwd: str, base: Path | None = None) -> Path | None:
    """`git -C <cwd>` — `base` is the CALLER's cwd so a relative -C dir
    resolves against where the user typed, not the hook process."""
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=2,
            cwd=str(base) if base else None,
        )
        return Path(out.stdout.strip()) if out.returncode == 0 else None
    except Exception:
        return None


def pretooluse(payload: dict) -> None:
    """Lane enforcement: in a repo that declares a lanes file, only the
    orchestrator checkout (untracked `.agent/orchestrator` marker) may
    push protected branches or merge PRs."""
    command = _tool_command(payload)
    if not command:
        return
    caller_cwd = Path(str(payload.get("cwd") or ROOT))
    root = _repo_root(str(caller_cwd))
    hit = _push_to(command, root, caller_cwd)
    if not hit and root:
        protected = _protected_branches(root)
        if protected and not (root / ORCH_MARKER).is_file():
            hit = bool(
                re.search(r"\bgh\s+pr\s+merge\b", command)
                or re.search(
                    r"\bgh\s+api\b[^|;&]*(?:/merges\b|/merge\b|merge-upstream)",
                    command,
                )
            )
    if not hit:
        return
    # Devin deny protocol: top-level decision + reason (exit 2 also blocks).
    sys.stdout.write(json.dumps({
        "decision": "block",
        "reason": (
            "lane law: workers push only their personal lane "
            "(feat/<issue> -> <user>). dev|main pushes and PR merges "
            "run from the orchestrator checkout "
            "(mkdir -p .agent && touch .agent/orchestrator there)."
        ),
    }))


def posttooluse(payload: dict) -> None:
    command = _tool_command(payload)
    if not re.search(r"\bgit\b[^|;&]*\bpush\b", command):
        return
    emit(
        "Push landed. If it carried a feature/lane: verify live on the "
        "server before calling it done — ship-verify, done means live.",
        event="PostToolUse",
    )


def compact() -> None:
    """PostCompaction: Devin fires AFTER context compaction — the moment
    the ruleset most needs re-injection (codex needed the SessionStart
    compact matcher workaround; Devin's event is direct)."""
    if _is_product_checkout():
        emit(ruleset(mode()), event="PostCompaction")
    else:
        emit(f"{SETUP_NOTE}\n{status_line()}", event="PostCompaction")


def sessionend(payload: dict) -> None:
    caller_cwd = Path(str(payload.get("cwd") or ROOT))
    root = _repo_root(str(caller_cwd)) or ROOT
    try:
        log_dir = root / ".agent"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "session-log.ndjson"
        with log_file.open("a") as fh:
            fh.write(json.dumps({
                "ts": int(time.time()),
                "repo": root.name,
                "agent": "devin",
                "branch": _git("branch", "--show-current"),
                "reason": payload.get("reason"),
                "session": payload.get("session_id"),
            }) + "\n")
        if log_file.stat().st_size > 256 * 1024:
            lines = log_file.read_text().splitlines()[-200:]
            log_file.write_text("\n".join(lines) + "\n")
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
    if event == "compact":
        compact()
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
    prompt(payload)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Hooks must never break a session on our bugs.
        pass
