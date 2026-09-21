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
import tomllib
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


def load_json(path: Path, required: bool = False) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        if required:
            raise SystemExit(f"{path} unreadable ({exc}) — pin is law, no fallback")
        return {}


def pinned_version() -> str:
    version = load_json(PIN_PATH, required=True).get("codex_cli")
    if not version:
        raise SystemExit(f"{PIN_PATH} missing codex_cli — pin is law, no fallback")
    return str(version)


def marketplace_names() -> list[str]:
    doc = load_json(ROOT / ".agents" / "plugins" / "marketplace.json", required=True)
    return [str(p.get("name")) for p in doc.get("plugins", []) if p.get("name")]


def codex_home() -> Path:
    """One resolver for the Codex user home: CODEX_HOME wins, else ~/.codex.
    Used by every writer below so custom homes stay coherent (#11)."""
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def codex_bin() -> str | None:
    """Repo-local install wins (setup installs into $REPO/.local/bin),
    then the user bin, then PATH."""
    exe = "codex.exe" if os.name == "nt" else "codex"
    for base in (ROOT / ".local" / "bin", Path.home() / ".local" / "bin"):
        candidate = base / exe
        if candidate.exists():
            return str(candidate)
    return shutil.which("codex")


def atomic_write(path: Path, text: str) -> None:
    """Sibling temp + os.replace — a crashed write never leaves a torn
    config file for readers."""
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def run(cmd: list[str], timeout: int = 30,
        cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, cwd=cwd)


# --- FIX items ---------------------------------------------------------------

def fix_plugin_cache() -> None:
    """Reinstall marketplace plugins whose cache under
    ~/.codex/plugins/cache/saint-tibo/ drifts from the repo (same parity
    rules as check_codex_setup.check_plugin_cache_sync)."""
    bin_path = codex_bin()
    if not bin_path:
        report("WARN", "plugin-cache", "codex not on PATH; skipped")
        return
    cache_root = codex_home() / "plugins" / "cache" / "saint-tibo"
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
        # Prune non-selected cached versions — a stale sibling dir is
        # drift the resolver could pick up (#14). Only cache dirs under
        # the plugin name; the selected version is never touched.
        plugin_cache = cache_root / name
        if plugin_cache.is_dir():
            for old in plugin_cache.iterdir():
                if old.is_dir() and old.name != version:
                    if not DRY_RUN:
                        shutil.rmtree(old, ignore_errors=True)
                    fixed.append(f"{name}@{old.name} pruned")
    if fixed:
        report("FIX", "plugin-cache", f"reinstalled: {', '.join(fixed)}")
    else:
        report("OK", "plugin-cache")


def fix_notify_block() -> None:
    """Ensure the managed '# hack-setup: notify' block exists in
    ~/.codex/config.toml. `notify` is a ROOT key — it must be written
    before the first table header, not appended at EOF (appending lands
    it inside the last table). A foreign root-level `notify` is reported,
    never clobbered: a duplicate key would invalidate the whole config."""
    cfg = codex_home() / "config.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    src = cfg.read_text(encoding="utf-8") if cfg.is_file() else ""
    lines = src.splitlines(keepends=True)
    # Root keyspace ends at the first table header.
    root_end = next(
        (i for i, l in enumerate(lines) if l.lstrip().startswith("[")),
        len(lines),
    )
    if os.name == "nt":
        script = str(ROOT / "install" / "notify.ps1")
    else:
        script = str(ROOT / "install" / "notify.sh")
    root_lines = lines[:root_end]
    entry_idx = next(
        (i for i, l in enumerate(root_lines)
         if re.match(r"\s*notify\s*=", l)),
        None,
    )
    if entry_idx is not None:
        line = root_lines[entry_idx]
        if script in line:
            report("OK", "notify-block")
            return
        if "# hack-setup" in line:
            # Our own entry at a stale path — rewrite in place, not foreign.
            lines[entry_idx] = None  # marker for rewrite below
            root_lines[entry_idx] = None
        else:
            report(
                "WARN", "notify-block",
                "foreign `notify` already set at root of "
                "~/.codex/config.toml — merge install/notify.sh manually "
                "(duplicate key = invalid TOML)",
            )
            return
    # Stale managed marker comments/entries in the root region are ours —
    # remove them so the rewrite below stays the single managed block.
    kept = [
        l for l in lines[:root_end]
        if l is not None
        and l.strip() != "# hack-setup: notify"
        and not (l.lstrip().startswith("notify") and "# hack-setup" in l)
    ]
    lines = kept + lines[root_end:]
    root_end = len(kept)
    if os.name == "nt":
        entry = f"notify = ['powershell', '-NoProfile', '-File', '{script}']  # hack-setup"
    else:
        entry = f'notify = ["{script}"]  # hack-setup'
    block = f"# hack-setup: notify\n{entry}\n"
    new_src = "".join(lines[:root_end]) + block + "".join(lines[root_end:])
    try:
        tomllib.loads(new_src)
    except Exception as exc:
        report("FAIL", "notify-block", f"would produce invalid TOML: {exc}")
        return
    if not DRY_RUN:
        atomic_write(cfg, new_src)
    report("FIX", "notify-block", f"{'would insert' if DRY_RUN else 'inserted'} managed root block in {cfg}")


def fix_sol_profile() -> None:
    """Rewrite ~/.codex/sol.config.toml from stack-pin models.* — the file is
    fully managed, so regeneration is always safe."""
    pin = load_json(STACK_PIN_PATH, required=True)
    models = pin.get("models") or {}
    secondary = models.get("secondary", "gpt-5.6-sol")
    effort = models.get("reasoning_effort", "xhigh")
    ctx = models.get("requested_context_window", 872000)
    compact = models.get("requested_auto_compact", 700000)
    target = codex_home() / "sol.config.toml"
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
        atomic_write(target, body)
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
    sha256 over the canonical JSON of the NORMALIZED identity —
    platform-resolved command (commandWindows never reaches the hash),
    normalized timeout (SessionEnd/Interrupt: default 1s, clamp 1-3;
    others: default 600, min 1), additionalContextLimit dropped when
    it equals the 2500 default."""
    command = handler.get("command")
    if os.name == "nt" and handler.get("commandWindows"):
        command = handler["commandWindows"]
    timeout = handler.get("timeout")
    if event_label in ("session_end", "interrupt"):
        timeout = min(max(int(timeout), 1), 3) if timeout is not None else 1
    else:
        timeout = max(int(timeout), 1) if timeout is not None else 600
    h: dict = {
        "type": handler.get("type", "command"),
        "async": bool(handler.get("async", False)),
        "command": command,
        "timeout": timeout,
    }
    if handler.get("statusMessage"):
        h["statusMessage"] = handler["statusMessage"]
    acl = handler.get("additionalContextLimit")
    if acl is not None and int(acl) != 2500:
        h["additionalContextLimit"] = int(acl)
    ident: dict = {"event_name": event_label, "hooks": [h]}
    if matcher:
        ident["matcher"] = matcher
    blob = json.dumps(
        ident, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
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
    cfg = codex_home() / "config.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    src = cfg.read_text(encoding="utf-8") if cfg.is_file() else ""
    prefix = str(hooks_path)
    # Drop stale managed state tables for THIS hooks.json only.
    out: list[str] = []
    skip = False
    for line in src.splitlines():
        m = re.match(r'\[hooks\.state\."((?:[^"\\]|\\.)*)"\]', line.strip())
        if m:
            # TOML basic-string unescape: our writer emits only \\ and \".
            # (unicode_escape would mangle non-ASCII paths — HS-02.)
            key = m.group(1).replace('\\"', '"').replace("\\\\", "\\")
            skip = key.startswith(prefix)
        elif line.strip().startswith("["):
            # Any table header ends the skipped block — including
            # [[array-of-tables]] (previously eaten, #1).
            skip = False
        if skip or line.strip() == "# hack-setup: hook trust":
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
    try:
        tomllib.loads(new_src)
    except Exception as exc:
        report("FAIL", "hook-trust", f"would produce invalid TOML: {exc}")
        return
    if not DRY_RUN:
        atomic_write(cfg, new_src)
    report("FIX", "hook-trust", f"{'would write' if DRY_RUN else 'wrote'} {len(entries)} trusted_hash entries to {cfg}")


def fix_config_cleanup() -> None:
    """Strip legacy managed lines from the USER config.toml without
    touching per-checkout state (#1): `# hack-setup:` comment blocks,
    stale `key = v # hack-setup` entries, and the removed [profiles.sol].
    [hooks.state.*] tables — ours AND foreign — are preserved verbatim;
    fix_hook_trust owns them (it rewrites this checkout's entries itself).
    Removing them here would fight that writer every run."""
    cfg = codex_home() / "config.toml"
    if not cfg.is_file():
        report("OK", "config-cleanup", "no user config.toml")
        return
    src = cfg.read_text(encoding="utf-8")
    lines = src.splitlines(keepends=True)
    # Comment headers + entries OWNED by sibling writers — stripping them
    # would ping-pong with fix_notify_block / fix_hook_trust every run.
    owned_comments = {"# hack-setup: notify", "# hack-setup: hook trust"}
    out: list[str] = []
    i, n = 0, len(lines)
    in_hooks_state = False
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if re.match(r'\[hooks\.state\."', stripped):
            in_hooks_state = True
            out.append(line)
            i += 1
            continue
        if in_hooks_state:
            out.append(line)
            i += 1
            if stripped.startswith("["):
                in_hooks_state = False
            continue
        if line.lstrip().startswith("# hack-setup:"):
            if stripped in owned_comments:
                out.append(line)
                i += 1
            else:
                # eat the stale comment block but stop at owned headers
                while (
                    i < n
                    and lines[i].lstrip().startswith("#")
                    and lines[i].strip() not in owned_comments
                ):
                    i += 1
            continue
        if "# hack-setup" in line and "=" in line and not line.lstrip().startswith("notify"):
            i += 1
            continue
        if re.fullmatch(r"\[profiles\.sol\]", stripped):
            i += 1
            while i < n and not lines[i].strip().startswith("["):
                i += 1
            continue
        out.append(line)
        i += 1
    res = "".join(out)
    if res != src:
        if not DRY_RUN:
            atomic_write(cfg, res)
        report("FIX", "config-cleanup",
               f"{'would strip' if DRY_RUN else 'stripped'} legacy managed entries")
    else:
        report("OK", "config-cleanup")


def fix_state_files() -> None:
    """Corrupt per-repo hook state (~/.codex/hack-mode-*.json,
    hack-issues-*.json) self-heals on next hook run — drop broken files."""
    home = codex_home()
    removed = []
    for pattern in ("hack-mode-*.json", "hack-issues-*.json"):
        for path in home.glob(pattern):
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
    bin_path = codex_bin()
    if not bin_path:
        report("FAIL", "codex-version", f"codex not found; expected codex-cli {wanted} — run ./setup")
        return
    try:
        res = run([bin_path, "--version"])
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
    # `session` always emits (systemMessage when mode is off,
    # additionalContext when on) and never mutates state — deterministic
    # regardless of the persisted mode (#12). Proof level: script runs +
    # emits valid hook JSON; discovery/trust is fix_hook_trust's proof.
    payload = json.dumps(
        {"hook_event_name": "SessionStart", "source": "startup", "cwd": str(ROOT)}
    )
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "session"],
            input=payload, capture_output=True, text=True, timeout=15,
        )
        out = proc.stdout.strip()
        doc = json.loads(out) if out else {}
        ctx = (doc.get("hookSpecificOutput") or {}).get("additionalContext", "")
        msg = doc.get("systemMessage", "")
        if proc.returncode == 0 and (ctx or "HACK-MODE" in msg):
            report("OK", "hook-smoke", "SessionStart emits hook JSON")
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
    # -C ROOT so --root from another cwd inspects the requested checkout,
    # not whatever repository the caller happens to sit in (#11).
    try:
        main = run(["git", "-C", str(ROOT), "rev-parse", "main"]).stdout.strip()
        dev = run(["git", "-C", str(ROOT), "rev-parse", "dev"]).stdout.strip()
    except subprocess.SubprocessError:
        report("WARN", "git-sync", "git refs unreadable")
        return
    dirty = len(run(["git", "-C", str(ROOT), "status", "--porcelain"]).stdout.splitlines())
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
    fix_config_cleanup()
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
