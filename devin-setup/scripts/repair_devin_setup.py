#!/usr/bin/env python3
"""Repair the Saint Tibo Devin setup: diagnose, fix what is safe, report the rest.

Twin of ../scripts/repair_setup.py for the devin-setup tree. FIX lines
mutate state; FAIL lines need a human (or `./setup`). Exits non-zero
while any FAIL remains.

Law: devin-setup/build/devin-pin.json `session` — the managed block in
the Devin USER config (~/.config/devin/config.json) is written only
here: model, subagents_enabled, auto_update, read_config_from. Other
keys are preserved; a one-time backup lands at config.json.hack-bak.
"""

from __future__ import annotations

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
PIN_PATH = ROOT / "build" / "devin-pin.json"
STACK_PIN_PATH = ROOT / "build" / "stack-pin.json"
DRY_RUN = "--dry-run" in sys.argv

RESULTS: list[tuple[str, str, str]] = []


def report(status: str, name: str, detail: str = "") -> None:
    RESULTS.append((status, name, detail))
    line = f"{status:<5} {name}"
    print(f"{line} — {detail}" if detail else line)


def load_json(path: Path, required: bool = False) -> dict:
    try:
        return json.loads(_strip_jsonc(path.read_text(encoding="utf-8")))
    except Exception as exc:
        if required:
            raise SystemExit(f"{path} unreadable ({exc}) — pin is law, no fallback")
        return {}


def _strip_jsonc(text: str) -> str:
    """Devin config files allow // and /* */ comments. Strip them without
    touching string contents."""
    out = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    lines = []
    for line in out.splitlines():
        # cut // only outside string literals
        in_str = False
        esc = False
        cut = len(line)
        for i, ch in enumerate(line):
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = not in_str
            elif ch == "/" and not in_str and line[i:i + 2] == "//":
                cut = i
                break
        lines.append(line[:cut])
    return "\n".join(lines)


def pin() -> dict:
    return load_json(PIN_PATH, required=True)


def devin_home() -> Path:
    """One resolver for the Devin user home: %APPDATA%/devin on Windows,
    else XDG_CONFIG_HOME/devin or ~/.config/devin."""
    if os.name == "nt":
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData/Roaming") / "devin"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return (Path(xdg) if xdg else Path.home() / ".config") / "devin"


def devin_bin() -> str | None:
    exe = "devin.exe" if os.name == "nt" else "devin"
    for base in (ROOT / ".local" / "bin", Path.home() / ".local" / "bin"):
        candidate = base / exe
        if candidate.exists():
            return str(candidate)
    return shutil.which("devin")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def run(cmd: list[str], timeout: int = 30, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kw)


MANAGED_TOP = ("subagents_enabled", "auto_update", "read_config_from")


def fix_user_config() -> None:
    """Single writer for the managed block in the Devin user config.
    Law keys come from devin-pin.json session+models; foreign keys
    (theme_mode, org, telemetry, ...) are preserved byte-value."""
    cfg_path = devin_home() / "config.json"
    law = pin()
    session = law["session"]
    model = law["models"]["primary"]
    want: dict = {
        "agent": {"model": model},
        "subagents_enabled": session["subagents_enabled"],
        "auto_update": session["auto_update"],
        "read_config_from": session["read_config_from"],
    }
    existing = load_json(cfg_path) if cfg_path.is_file() else {}
    if not isinstance(existing, dict):
        report("FAIL", "user-config", f"{cfg_path} is not a JSON object")
        return

    def managed_ok() -> bool:
        return (
            existing.get("agent", {}).get("model") == model
            and all(existing.get(k) == want[k] for k in ("subagents_enabled", "auto_update"))
            and existing.get("read_config_from") == want["read_config_from"]
        )

    if managed_ok():
        report("PASS", "user-config", f"{cfg_path} managed block matches the pin")
        return
    if DRY_RUN:
        report("FAIL", "user-config", f"{cfg_path} managed block drifts from the pin")
        return
    merged = dict(existing)
    agent = dict(existing.get("agent") or {})
    agent["model"] = model
    merged["agent"] = agent
    for key in MANAGED_TOP:
        merged[key] = want[key]
    if cfg_path.is_file() and not cfg_path.with_suffix(".json.hack-bak").exists():
        shutil.copyfile(cfg_path, cfg_path.with_suffix(".json.hack-bak"))
    atomic_write(cfg_path, json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    report("FIX", "user-config", f"{cfg_path} managed block set (model={model}, subagents off, auto_update off, imports off)")


def fix_agent_dirs() -> None:
    for rel in (".agent", ".agent/briefs"):
        target = ROOT / rel
        if not target.is_dir() and not DRY_RUN:
            target.mkdir(parents=True, exist_ok=True)
    report("PASS", "agent-dirs", ".agent/ present")


def fix_hook_bytecode() -> None:
    script = ROOT / ".devin" / "hooks" / "devin_mode.py"
    try:
        py_compile.compile(str(script), doraise=True)
        report("PASS", "hook-compile", script.name)
    except py_compile.PyCompileError as exc:
        report("FAIL", "hook-compile", str(exc).splitlines()[0])
    for cache in (ROOT / ".devin" / "hooks" / "__pycache__",):
        if cache.is_dir() and not DRY_RUN:
            shutil.rmtree(cache, ignore_errors=True)


def _bin_version(binary: str) -> str | None:
    try:
        out = run([binary, "--version"], timeout=10)
        line = (out.stdout or out.stderr).strip().splitlines()[0]
        parts = line.split()
        return parts[1] if len(parts) >= 2 else parts[0]
    except Exception:
        return None


def check_devin_version() -> None:
    want = str(pin()["devin_cli"]["version"])
    binary = devin_bin()
    if not binary:
        report("FAIL", "devin-version", f"devin not found; expected {want} (run ./setup)")
        return
    got = _bin_version(binary)
    if got == want:
        report("PASS", "devin-version", f"devin {got}")
    else:
        report("FAIL", "devin-version", f"{binary} reports {got}, expected {want}")


def check_herdr_version() -> None:
    want = str(pin()["herdr"]["version"])
    exe = "herdr.exe" if os.name == "nt" else "herdr"
    binary = None
    for base in (ROOT / ".local" / "bin", Path.home() / ".local" / "bin"):
        if (base / exe).exists():
            binary = str(base / exe)
            break
    binary = binary or shutil.which("herdr")
    if not binary:
        report("FAIL", "herdr-version", f"herdr not found; expected {want} (run ./setup)")
        return
    got = _bin_version(binary)
    if got == want:
        report("PASS", "herdr-version", f"herdr {got}")
    else:
        report("FAIL", "herdr-version", f"{binary} reports {got}, expected {want}")


def check_stack_pin_sync() -> None:
    source = ROOT.parent / "build" / "stack-pin.json"
    target = STACK_PIN_PATH
    if not target.is_file():
        report("FAIL", "stack-pin-sync", "run python3 scripts/sync_stack_pin.py")
        return
    if source.is_file() and source.read_bytes() == target.read_bytes():
        report("PASS", "stack-pin-sync", "build/stack-pin.json matches root pin")
    else:
        report("FAIL", "stack-pin-sync", "generated copy drifted; run python3 scripts/sync_stack_pin.py")


def check_env_sh() -> None:
    env_sh = ROOT / "install" / "env.sh"
    if "DEVIN_PERMISSION_MODE" not in env_sh.read_text():
        report("FAIL", "env-bypass", "install/env.sh lost DEVIN_PERMISSION_MODE")
    else:
        report("PASS", "env-bypass", "session law projected (DEVIN_PERMISSION_MODE)")


def check_git_sync() -> None:
    inside = run(["git", "-C", str(ROOT), "rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        report("FAIL", "git", "not inside a git work tree")
        return
    report("PASS", "git", "work tree")


def check_serena() -> None:
    if (ROOT / ".serena" / "project.yml").is_file() or (ROOT.parent / ".serena" / "project.yml").is_file():
        report("PASS", "serena", "project memory present")
    else:
        report("FAIL", "serena", "no .serena/project.yml — run session-boot")


def verify_gate() -> None:
    checker = ROOT / "scripts" / "check_devin_setup.py"
    if not checker.is_file():
        report("FAIL", "verify-gate", "check_devin_setup.py missing")
        return
    if DRY_RUN:
        report("PASS", "verify-gate", "skipped in dry-run")
        return
    proc = run([sys.executable, str(checker)], timeout=120, cwd=ROOT)
    if proc.returncode == 0:
        report("PASS", "verify-gate", "check_devin_setup.py green")
    else:
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
        report("FAIL", "verify-gate", "; ".join(tail))


FIXES = {
    "user-config": fix_user_config,
    "agent-dirs": fix_agent_dirs,
    "hook-bytecode": fix_hook_bytecode,
}
CHECKS = {
    "devin-version": check_devin_version,
    "herdr-version": check_herdr_version,
    "stack-pin-sync": check_stack_pin_sync,
    "env-bypass": check_env_sh,
    "git": check_git_sync,
    "serena": check_serena,
    "verify-gate": verify_gate,
}


def main() -> int:
    only = _arg_value("--only")
    if only:
        fn = FIXES.get(only) or CHECKS.get(only)
        if not fn:
            print(f"unknown --only target {only}", file=sys.stderr)
            return 2
        fn()
    else:
        for fn in FIXES.values():
            fn()
        for fn in CHECKS.values():
            fn()
    fails = [r for r in RESULTS if r[0] == "FAIL"]
    print(f"\n{len(RESULTS) - len(fails)} ok, {len(fails)} fail")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
