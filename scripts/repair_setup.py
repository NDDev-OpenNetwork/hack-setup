#!/usr/bin/env python3
"""Repair the Saint Tibo setup: diagnose, fix what is safe, report the rest.

`just repair` runs this. FIX lines mutate state; FAIL lines need a human
(or `./setup`). Exits non-zero while any FAIL remains.

Law: build/stack-pin.json `registered.repair`.
"""

from __future__ import annotations

import hashlib
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
from pathlib import Path

def _arg_value(flag: str) -> str | None:
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


ROOT = Path(_arg_value("--root") or Path(__file__).resolve().parent.parent).resolve()
PIN_PATH = ROOT / "build" / "codex-pin.json"
STACK_PIN_PATH = ROOT / "build" / "stack-pin.json"
DRY_RUN = "--dry-run" in sys.argv

RESULTS: list[tuple[str, str, str]] = []  # (status, name, detail)


def report(status: str, name: str, detail: str = "") -> None:
    RESULTS.append((status, name, detail))
    line = f"{status:<5} {name}"
    print(f"{line} — {detail}" if detail else line)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def pinned_version() -> str:
    return str(load_json(PIN_PATH).get("version", "0.155.1"))


def marketplace_names() -> list[str]:
    doc = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    return [str(p.get("name")) for p in doc.get("plugins", []) if p.get("name")]


def codex_bin() -> str | None:
    local = Path.home() / ".local" / "bin" / ("codex.exe" if os.name == "nt" else "codex")
    if local.exists():
        return str(local)
    return shutil.which("codex")


def run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


# --- FIX items ---------------------------------------------------------------

def fix_plugin_cache() -> None:
    """Reinstall marketplace plugins whose cache under
    ~/.codex/plugins/cache/saint-tibo/ drifts from the repo (same parity
    rules as check_codex_setup.check_plugin_cache_sync)."""
    bin_path = codex_bin()
    if not bin_path:
        report("WARN", "plugin-cache", "codex not on PATH; skipped")
        return
    cache_root = Path.home() / ".codex" / "plugins" / "cache" / "saint-tibo"
    fixed = []
    for name in marketplace_names():
        repo_dir = ROOT / "plugins" / name
        if not repo_dir.is_dir():
            continue
        version = str(load_json(repo_dir / "plugin.json").get("version", ""))
        cache_dir = cache_root / name / version
        stale = not cache_dir.is_dir()
        if not stale:
            repo_files = {
                p.relative_to(repo_dir): p for p in repo_dir.rglob("*") if p.is_file()
            }
            cache_files = {
                p.relative_to(cache_dir) for p in cache_dir.rglob("*") if p.is_file()
            }
            if set(repo_files) != cache_files:
                stale = True
            else:
                stale = any(
                    hashlib.sha256(src.read_bytes()).digest()
                    != hashlib.sha256((cache_dir / rel).read_bytes()).digest()
                    for rel, src in repo_files.items()
                )
        if stale:
            if not DRY_RUN:
                res = run([bin_path, "plugin", "add", f"{name}@saint-tibo"], 120)
                if res.returncode != 0:
                    report("FAIL", "plugin-cache", f"{name}@{version} reinstall failed: {res.stderr.strip()[:120]}")
                    return
            fixed.append(name)
    if fixed:
        report("FIX", "plugin-cache", f"reinstalled: {', '.join(fixed)}")
    else:
        report("OK", "plugin-cache")


def fix_notify_block() -> None:
    """Ensure the managed '# hack-setup: notify' block exists in
    ~/.codex/config.toml. Never clobber a foreign `notify` key — a duplicate
    top-level key would make the whole user config invalid TOML."""
    cfg = Path.home() / ".codex" / "config.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    src = cfg.read_text(encoding="utf-8") if cfg.is_file() else ""
    if "hack-setup: notify" in src:
        report("OK", "notify-block")
        return
    if re.search(r"(?m)^\s*notify\s*=", src):
        report(
            "WARN", "notify-block",
            "foreign `notify` already set in ~/.codex/config.toml — "
            "merge install/notify.sh manually (duplicate key = invalid TOML)",
        )
        return
    if os.name == "nt":
        script = str(ROOT / "install" / "notify.ps1")
        entry = f"notify = ['powershell', '-NoProfile', '-File', '{script}']  # hack-setup"
    else:
        script = str(ROOT / "install" / "notify.sh")
        entry = f'notify = ["{script}"]  # hack-setup'
    block = f"\n# hack-setup: notify\n{entry}\n"
    if not DRY_RUN:
        with cfg.open("a", encoding="utf-8") as fh:
            fh.write(block)
    report("FIX", "notify-block", f"{'would append' if DRY_RUN else 'appended'} managed block to {cfg}")


def fix_sol_profile() -> None:
    """Rewrite ~/.codex/sol.config.toml from stack-pin models.* — the file is
    fully managed, so regeneration is always safe."""
    pin = load_json(STACK_PIN_PATH)
    models = pin.get("models") or {}
    secondary = models.get("secondary", "gpt-5.6-sol")
    effort = models.get("reasoning_effort", "xhigh")
    ctx = models.get("requested_context_window", 872000)
    compact = models.get("requested_auto_compact", 700000)
    target = Path.home() / ".codex" / "sol.config.toml"
    body = (
        "# hack-setup managed: secondary model profile for `codex --profile sol`.\n"
        "# Values come from build/stack-pin.json models.* — edit the pin, not this file.\n"
        f'model = "{secondary}"\n'
        f'model_reasoning_effort = "{effort}"\n'
        f'review_model = "{secondary}"\n'
        f"model_context_window = {ctx}\n"
        f"model_auto_compact_token_limit = {compact}\n"
    )
    if target.is_file() and target.read_text(encoding="utf-8") == body:
        report("OK", "sol-profile")
        return
    if not DRY_RUN:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    report("FIX", "sol-profile", f"{'would rewrite' if DRY_RUN else 'rewrote'} {target} from the pin")


def fix_agent_dirs() -> None:
    """`.agent/` (session log, briefs, orchestrator marker) is created lazily
    by the hook — create it so first-run logging never depends on timing."""
    target = ROOT / ".agent" / "briefs"
    if target.is_dir():
        report("OK", "agent-dirs")
        return
    if not DRY_RUN:
        target.mkdir(parents=True, exist_ok=True)
    report("FIX", "agent-dirs", f"{'would create' if DRY_RUN else 'created'} {target.relative_to(ROOT)}")


def fix_hook_bytecode() -> None:
    """Stale __pycache__ under .codex/hooks can outlive hook edits."""
    cache = ROOT / ".codex" / "hooks" / "__pycache__"
    if not cache.exists():
        report("OK", "hook-bytecode")
        return
    if not DRY_RUN:
        shutil.rmtree(cache, ignore_errors=True)
    report("FIX", "hook-bytecode", "removed stale __pycache__")


HOOK_EVENT_LABELS = {
    "PreToolUse": "pre_tool_use",
    "PermissionRequest": "permission_request",
    "PostToolUse": "post_tool_use",
    "PreCompact": "pre_compact",
    "PostCompact": "post_compact",
    "SessionStart": "session_start",
    "SessionEnd": "session_end",
    "UserPromptSubmit": "user_prompt_submit",
    "SubagentStart": "subagent_start",
    "SubagentStop": "subagent_stop",
    "Stop": "stop",
    "Interrupt": "interrupt",
}


def _hook_hash(event_label: str, matcher: str | None, handler: dict) -> str:
    """Port of codex-rs hooks::engine::discovery::hook_hash +
    config::fingerprint::version_for_toml (0.155.1, be2951ea):
    sha256 over the canonical JSON of the normalized TOML identity."""
    h: dict = {"type": handler.get("type", "command"), "async": bool(handler.get("async", False))}
    for key in ("command", "commandWindows"):
        if handler.get(key):
            h[key] = handler[key]
    if handler.get("timeout") is not None:
        h["timeout"] = int(handler["timeout"])
    if handler.get("statusMessage"):
        h["statusMessage"] = handler["statusMessage"]
    if handler.get("additionalContextLimit") is not None:
        h["additionalContextLimit"] = int(handler["additionalContextLimit"])
    ident: dict = {"event_name": event_label, "hooks": [h]}
    if matcher:
        ident["matcher"] = matcher
    blob = json.dumps(ident, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def fix_hook_trust() -> None:
    """Non-managed hooks only run when their trusted_hash matches the
    current definition; trust state is honored only from the USER config
    layer (codex-rs config_rules.rs). Write a managed
    [hooks.state."<key>"] block into ~/.codex/config.toml so our pinned
    hooks stay trusted across edits and fresh installs.
    Missing hooks.json (product repos without the file yet) is OK."""
    hooks_path = (ROOT / ".codex" / "hooks.json").resolve()
    if not hooks_path.is_file():
        report("OK", "hook-trust", "no hooks.json — nothing to trust")
        return
    doc = load_json(hooks_path)
    events = doc.get("hooks") or {}
    entries: list[tuple[str, str]] = []
    for event, groups in events.items():
        label = HOOK_EVENT_LABELS.get(event)
        if not label:
            continue
        for gi, group in enumerate(groups or []):
            for hi, handler in enumerate((group or {}).get("hooks") or []):
                key = f"{hooks_path}:{label}:{gi}:{hi}"
                entries.append((key, _hook_hash(label, group.get("matcher"), handler)))
    if not entries:
        report("WARN", "hook-trust", "no hook handlers parsed")
        return
    cfg = Path.home() / ".codex" / "config.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    src = cfg.read_text(encoding="utf-8") if cfg.is_file() else ""
    prefix = str(hooks_path)
    # Drop stale managed state tables for THIS hooks.json only.
    out: list[str] = []
    skip = False
    for line in src.splitlines():
        m = re.match(r'\[hooks\.state\."((?:[^"\\]|\\.)*)"\]', line.strip())
        if m:
            key = m.group(1).encode().decode("unicode_escape")
            skip = key.startswith(prefix)
        elif line.strip().startswith("[") and not line.strip().startswith("[["):
            skip = False
        if skip:
            continue
        out.append(line)
    src = "\n".join(out).rstrip() + "\n"
    block_lines = ["", "# hack-setup: hook trust"]
    for key, digest in entries:
        esc_key = key.replace("\\", "\\\\").replace('"', '\\"')
        block_lines.append(f'[hooks.state."{esc_key}"]  # hack-setup')
        block_lines.append(f'trusted_hash = "{digest}"  # hack-setup')
    new_src = src + "\n".join(block_lines) + "\n"
    if new_src == (cfg.read_text(encoding="utf-8") if cfg.is_file() else ""):
        report("OK", "hook-trust", f"{len(entries)} handlers trusted")
        return
    if not DRY_RUN:
        cfg.write_text(new_src, encoding="utf-8")
    report("FIX", "hook-trust", f"{'would write' if DRY_RUN else 'wrote'} {len(entries)} trusted_hash entries to {cfg}")


def fix_state_files() -> None:
    """Corrupt per-repo hook state (~/.codex/hack-mode-*.json,
    hack-issues-*.json) self-heals on next hook run — drop broken files."""
    codex_home = Path.home() / ".codex"
    removed = []
    for pattern in ("hack-mode-*.json", "hack-issues-*.json"):
        for path in codex_home.glob(pattern):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                if not DRY_RUN:
                    path.unlink(missing_ok=True)
                removed.append(path.name)
    if removed:
        report("FIX", "state-files", f"dropped corrupt: {', '.join(removed)}")
    else:
        report("OK", "state-files")


# --- CHECK items -------------------------------------------------------------

def check_codex_version() -> None:
    wanted = pinned_version()
    try:
        res = run(["codex", "--version"])
    except (OSError, subprocess.SubprocessError):
        report("FAIL", "codex-version", f"codex not runnable; expected codex-cli {wanted} — run ./setup")
        return
    got = res.stdout.strip()
    if f"codex-cli {wanted}" in got:
        report("OK", "codex-version", got)
    else:
        report("FAIL", "codex-version", f"got '{got}', expected codex-cli {wanted} — run ./setup")


def check_python3() -> None:
    """hooks.json invokes `python3`; on Windows only `python` may exist."""
    if shutil.which("python3"):
        report("OK", "python3-on-path")
    elif os.name == "nt" and shutil.which("python"):
        report("WARN", "python3-on-path", "only `python` resolves; hooks call `python3` — install the python3 alias or uv python")
    else:
        report("FAIL", "python3-on-path", "python3 not on PATH; hooks will not run")


def check_hook_smoke() -> None:
    script = ROOT / ".codex" / "hooks" / "hack_mode.py"
    if not script.is_file():
        report("FAIL", "hook-smoke", "hack_mode.py missing")
        return
    try:
        py_compile.compile(str(script), doraise=True)
    except py_compile.PyCompileError as exc:
        report("FAIL", "hook-smoke", f"does not compile: {exc}")
        return
    payload = json.dumps(
        {"hook_event_name": "UserPromptSubmit", "prompt": "repair smoke", "cwd": str(ROOT)}
    )
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "prompt"],
            input=payload, capture_output=True, text=True, timeout=15,
        )
        out = proc.stdout.strip()
        doc = json.loads(out) if out else {}
        ctx = (doc.get("hookSpecificOutput") or {}).get("additionalContext", "")
        if proc.returncode == 0 and ("STATUS" in ctx or "hack" in ctx.lower()):
            report("OK", "hook-smoke", "UserPromptSubmit emits context")
        else:
            report("FAIL", "hook-smoke", f"unexpected output: {out[:120]}")
    except Exception as exc:
        report("FAIL", "hook-smoke", f"hook crashed: {exc}")


def check_env_sh() -> None:
    if os.name == "nt":
        report("OK", "env-sh", "skipped on Windows")
        return
    path = ROOT / "install" / "env.sh"
    if path.is_file():
        report("OK", "env-sh")
    else:
        report("FAIL", "env-sh", "install/env.sh missing — run ./setup")


def check_git_sync() -> None:
    try:
        main = run(["git", "rev-parse", "main"]).stdout.strip()
        dev = run(["git", "rev-parse", "dev"], ).stdout.strip()
    except subprocess.SubprocessError:
        report("WARN", "git-sync", "git refs unreadable")
        return
    dirty = len(run(["git", "status", "--porcelain"]).stdout.splitlines())
    if main == dev:
        report("OK", "git-sync", f"main==dev, dirty={dirty}")
    else:
        report("WARN", "git-sync", f"local main={main[:7]} dev={dev[:7]} diverged, dirty={dirty}")


def check_serena() -> None:
    yml = ROOT / ".serena" / "project.yml"
    if yml.is_file() and yml.read_text(encoding="utf-8").strip():
        report("OK", "serena-project")
    else:
        report("WARN", "serena-project", ".serena/project.yml missing or empty")


def verify_gate() -> None:
    """Final proof: the real checkers."""
    fails = []
    for script in ("check_codex_setup.py", "check_stack.py"):
        res = run([sys.executable, str(ROOT / "scripts" / script)], timeout=180)
        if res.returncode != 0:
            last = [l for l in res.stdout.splitlines() if l.startswith("FAIL")][:3]
            fails.append(f"{script}: {'; '.join(last) or res.stdout.strip()[-120:]}")
    if fails:
        report("FAIL", "verify-gate", " | ".join(fails))
    else:
        report("OK", "verify-gate", "check_codex_setup + check_stack PASS")


ONLY = None
for i, arg in enumerate(sys.argv):
    if arg == "--only" and i + 1 < len(sys.argv):
        ONLY = sys.argv[i + 1].split(",")


def main() -> int:
    print(f"repair {ROOT.name}" + (" (dry-run)" if DRY_RUN else ""))
    if ONLY:
        for name in ONLY:
            fn = globals().get(f"fix_{name.replace('-', '_')}") or globals().get(
                f"check_{name.replace('-', '_')}"
            )
            if fn:
                fn()
            else:
                report("FAIL", name, "unknown repair item")
        return 1 if any(s == "FAIL" for s, _, _ in RESULTS) else 0
    fix_plugin_cache()
    fix_notify_block()
    fix_sol_profile()
    fix_agent_dirs()
    fix_hook_bytecode()
    fix_hook_trust()
    fix_state_files()
    check_codex_version()
    check_python3()
    check_hook_smoke()
    check_env_sh()
    check_git_sync()
    check_serena()
    verify_gate()
    fails = sum(1 for s, _, _ in RESULTS if s == "FAIL")
    warns = sum(1 for s, _, _ in RESULTS if s == "WARN")
    fixes = sum(1 for s, _, _ in RESULTS if s == "FIX")
    print(f"repair: {fixes} fixed, {warns} warnings, {fails} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
