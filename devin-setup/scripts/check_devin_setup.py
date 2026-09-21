#!/usr/bin/env python3
"""Saint Tibo Devin setup artifact checker.

Twin of ../scripts/check_codex_setup.py for the devin-setup tree.
Proves: build/devin-pin.json law == .devin/ projection == plugin ==
catalog/bootstrap twins, and that shared files copied from ../install
have not drifted. Host/installation checks live in repair_devin_setup.py.
"""

from __future__ import annotations

import os
import py_compile
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARENT = ROOT.parent
PIN_PATH = ROOT / "build" / "devin-pin.json"
STACK_PIN_PATH = ROOT / "build" / "stack-pin.json"
PARENT_STACK_PIN = PARENT / "build" / "stack-pin.json"

ERRORS: list[str] = []


def fail(msg: str) -> None:
    ERRORS.append(msg)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _strip_jsonc(text: str) -> str:
    out = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    lines = []
    for line in out.splitlines():
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


def load_json(path: Path, jsonc: bool = False):
    import json
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(_strip_jsonc(text) if jsonc else text)
    except Exception as exc:
        fail(f"{path.relative_to(PARENT)} unreadable: {exc}")
        return {}


VALID_EVENTS = {
    "SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse",
    "PermissionRequest", "Stop", "SessionEnd", "PostCompaction",
}


def check_devin_pin() -> None:
    pin = load_json(PIN_PATH)
    if not pin:
        return
    cli = pin.get("devin_cli", {})
    version = cli.get("version")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(version or "")):
        fail("devin-pin: devin_cli.version must be semver")
    for key in ("install_sh", "install_ps1"):
        url = str(cli.get(key, ""))
        if f"/cli/{version}/" not in url:
            fail(f"devin-pin: {key} must be the versioned URL for {version}")
    herdr = pin.get("herdr", {})
    pkgs = herdr.get("packages", {})
    for plat in ("darwin-arm64", "darwin-x86_64", "linux-x86_64",
                 "linux-arm64", "windows-x86_64"):
        pkg = pkgs.get(plat)
        if not pkg:
            fail(f"devin-pin: herdr.packages missing {plat}")
            continue
        if not re.fullmatch(r"[0-9a-f]{64}", str(pkg.get("sha256", ""))):
            fail(f"devin-pin: herdr {plat} sha256 malformed")
    session = pin.get("session", {})
    if session.get("permission_mode") != "bypass":
        fail("devin-pin: session.permission_mode must be bypass")
    if session.get("permission_mode_env") != "DEVIN_PERMISSION_MODE":
        fail("devin-pin: permission_mode_env must be DEVIN_PERMISSION_MODE")
    if session.get("subagents_enabled") is not False:
        fail("devin-pin: subagents_enabled must be pinned false")
    if session.get("auto_update") is not False:
        fail("devin-pin: auto_update must be pinned false")
    rcf = session.get("read_config_from", {})
    for key in ("claude", "cursor", "windsurf", "copilot", "opencode"):
        if rcf.get(key) is not False:
            fail(f"devin-pin: read_config_from.{key} must be pinned false")
    if not pin.get("models", {}).get("primary"):
        fail("devin-pin: models.primary required")
    hooks = pin.get("hooks", {})
    events = set(hooks.get("events", []))
    if not events <= VALID_EVENTS:
        fail(f"devin-pin: hooks.events has unknown events {sorted(events - VALID_EVENTS)}")
    wired = set(hooks.get("wired", {}))
    if not wired <= events:
        fail("devin-pin: hooks.wired references events not in hooks.events")
    for plugin in pin.get("plugins", []):
        if not (ROOT / plugin.get("dir", "") / ".devin-plugin" / "plugin.json").is_file():
            fail(f"devin-pin: plugin dir missing for {plugin.get('name')}")


def check_stack_pin_sync() -> None:
    if not STACK_PIN_PATH.is_file():
        fail("build/stack-pin.json missing; run scripts/sync_stack_pin.py")
        return
    if not PARENT_STACK_PIN.is_file():
        fail("root build/stack-pin.json missing — shared law source gone")
        return
    if STACK_PIN_PATH.read_bytes() != PARENT_STACK_PIN.read_bytes():
        fail("build/stack-pin.json drifted from root pin; run scripts/sync_stack_pin.py")


def check_devin_config() -> None:
    pin = load_json(PIN_PATH)
    cfg = load_json(ROOT / ".devin" / "config.json", jsonc=True)
    if not cfg:
        return
    want_rcf = pin.get("session", {}).get("read_config_from", {})
    if cfg.get("read_config_from") != want_rcf:
        fail(".devin/config.json read_config_from != pin")
    perms = cfg.get("permissions", {})
    deny = set(perms.get("deny", []))
    for required in ("Exec(sudo)", "Exec(doas)", "Write(.env*)"):
        if required not in deny:
            fail(f".devin/config.json permissions.deny missing {required}")
    allow = perms.get("allow", [])
    if not any(str(a).startswith("Read(") for a in allow):
        fail(".devin/config.json permissions.allow missing Read")


def check_mcp_config() -> None:
    pin = load_json(PIN_PATH)
    cfg = load_json(ROOT / ".devin" / "mcp_config.json", jsonc=True)
    if not cfg:
        return
    want = pin.get("mcp_servers", {})
    servers = cfg.get("mcpServers", {})
    if set(servers) != set(want):
        fail(f".devin/mcp_config.json servers {sorted(servers)} != pin {sorted(want)}")
        return
    for name, spec in want.items():
        got = servers[name]
        if "command" in spec:
            if got.get("command") != spec["command"] or got.get("args") != spec["args"]:
                fail(f"mcp {name}: command/args drift")
        else:
            if got.get("url") != spec.get("url"):
                fail(f"mcp {name}: url drift")
            if got.get("headers", {}) != spec.get("headers", {}):
                fail(f"mcp {name}: headers drift")
        blob = repr(got)
        if re.search(r"(api[_-]?key|token|secret)['\"]?\s*[:=]\s*['\"][^$][^\"]{8,}", blob, re.I):
            fail(f"mcp {name}: possible literal secret; use ${{VAR}} references")


def check_hooks() -> None:
    pin = load_json(PIN_PATH)
    doc = load_json(ROOT / ".devin" / "hooks.v1.json")
    if not doc:
        return
    events = set(pin.get("hooks", {}).get("events", []))
    wired = set(pin.get("hooks", {}).get("wired", {}))
    for event in doc:
        if event not in VALID_EVENTS:
            fail(f"hooks.v1.json: unknown event {event}")
    for event in wired:
        if event not in doc:
            fail(f"hooks.v1.json: wired event {event} missing")
    for event, groups in doc.items():
        for group in groups:
            matcher = group.get("matcher")
            if event in ("PreToolUse", "PostToolUse") and matcher != "exec":
                fail(f"hooks.v1.json {event}: matcher must be exec")
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                if "devin_mode.py" not in cmd or "DEVIN_PROJECT_DIR" not in cmd:
                    fail(f"hooks.v1.json {event}: command must run devin_mode.py via $DEVIN_PROJECT_DIR")
    script = ROOT / ".devin" / "hooks" / "devin_mode.py"
    if not script.is_file():
        fail(".devin/hooks/devin_mode.py missing")
        return
    try:
        py_compile.compile(str(script), doraise=True)
    except py_compile.PyCompileError as exc:
        fail(f"devin_mode.py does not compile: {exc}")
    body = read_text(script)
    for anchor in ("DEVIN_PROJECT_DIR", "hookSpecificOutput",
                   '"decision": "block"', "lanes.json", "PostCompaction",
                   "session-log.ndjson"):
        if anchor not in body:
            fail(f"devin_mode.py missing anchor {anchor}")


def check_plugin() -> None:
    pin = load_json(PIN_PATH)
    for plugin in pin.get("plugins", []):
        pdir = ROOT / plugin.get("dir", "")
        manifest = load_json(pdir / ".devin-plugin" / "plugin.json")
        if not manifest:
            continue
        if manifest.get("name") != plugin.get("name"):
            fail(f"plugin manifest name != pin ({plugin.get('name')})")
        for key in ("version", "description"):
            if not manifest.get(key):
                fail(f"plugin manifest missing {key}")
        if not (pdir / "AGENTS.md").is_file():
            fail(f"plugin {plugin.get('name')} missing AGENTS.md")
        skill_dirs = sorted(
            p.name for p in (pdir / "skills").iterdir() if p.is_dir()
        ) if (pdir / "skills").is_dir() else []
        want = sorted(plugin.get("skills", []))
        if skill_dirs != want:
            fail(f"plugin skills {skill_dirs} != pin {want}")
            continue
        for name in skill_dirs:
            skill_md = pdir / "skills" / name / "SKILL.md"
            head = read_text(skill_md)[:400]
            if not re.search(rf"^name:\s*{re.escape(name)}\s*$", head, re.M):
                fail(f"skill {name}/SKILL.md frontmatter name mismatch")


def check_catalog() -> None:
    catalog = ROOT / "install" / "catalog.toml"
    try:
        doc = tomllib.loads(read_text(catalog))
    except Exception as exc:
        fail(f"catalog.toml unreadable: {exc}")
        return
    modules = doc.get("modules", [])
    names = [str(m.get("dir", "")).removeprefix("modules/") for m in modules]
    want = ["10-prereqs", "15-member", "20-devin-cli", "30-runtimes", "40-devin-verify"]
    if names != want:
        fail(f"catalog modules {names} != {want}")
    for name in names:
        mdir = ROOT / "install" / "modules" / name
        for twin in ("module.sh", "module.ps1"):
            if not (mdir / twin).is_file():
                fail(f"module {name} missing {twin}")


SHARED_FILES = (
    ["lib/common.sh", "lib/common.ps1", "lib/download.sh", "lib/download.ps1",
     "lib/os.sh", "lib/os.ps1"]
    + [f"modules/{m}/module.{ext}" for m in ("10-prereqs", "15-member", "30-runtimes")
       for ext in ("sh", "ps1")]
)


def check_shared_sync() -> None:
    """Shared twins must stay byte-identical to ../install — devin-setup
    reuses the same mechanism, and silent drift forks the law."""
    for rel in SHARED_FILES:
        mine = ROOT / "install" / rel
        theirs = PARENT / "install" / rel
        if not mine.is_file():
            fail(f"install/{rel} missing")
            continue
        if not theirs.is_file() or mine.read_bytes() != theirs.read_bytes():
            fail(f"install/{rel} drifted from ../install/{rel}")


def check_bootstrap() -> None:
    setup = read_text(ROOT / "setup")
    if "install/bootstrap.sh" not in setup or not setup.startswith("#!"):
        fail("setup entry must exec install/bootstrap.sh")
    sh = read_text(ROOT / "install" / "bootstrap.sh")
    ps1 = read_text(ROOT / "install" / "bootstrap.ps1")
    for token in ("--member", "--os", "--dry-run", "--status"):
        if token not in sh:
            fail(f"bootstrap.sh lost {token}")
    for token in ("--?member", "--?os", "--?status", "--?dry-run"):
        if token not in ps1:
            fail(f"bootstrap.ps1 lost {token}")
    for env_file in ("env.sh", "env.ps1"):
        if "DEVIN_PERMISSION_MODE" not in read_text(ROOT / "install" / env_file):
            fail(f"install/{env_file} lost DEVIN_PERMISSION_MODE")
    just = read_text(ROOT / "justfile")
    for recipe in ("setup", "check", "gate", "dry-run", "status", "sync-pin"):
        if not re.search(rf"^{recipe}[ :]?", just, re.M):
            fail(f"justfile lost {recipe} recipe")


def check_ps1_ascii() -> None:
    """Windows PowerShell 5.1 reads BOM-less .ps1 as ANSI; non-ASCII in
    executable lines mangles into smart quotes and breaks parsing.
    Comments are exempt."""
    for path in ROOT.rglob("*.ps1"):
        if ".git" in path.parts:
            continue
        for n, line in enumerate(read_text(path).splitlines(), 1):
            code = line.split("#", 1)[0]
            if any(ord(c) > 127 for c in code):
                fail(f"{path.relative_to(ROOT)}:{n} non-ASCII outside a comment")


def check_devin_mode_smoke() -> None:
    """Run the hook's dry paths hermetically — no stdin, no network."""
    import subprocess
    script = ROOT / ".devin" / "hooks" / "devin_mode.py"
    if not script.is_file():
        return
    # Keep the host env (Windows needs SystemRoot/USERPROFILE for Python
    # and Path.home()) but neuter PATH so git/gh calls inside the hook
    # fail fast — the run stays offline-hermetic.
    env = dict(os.environ)
    env["PATH"] = str(ROOT / "tests")
    env["DEVIN_PROJECT_DIR"] = str(ROOT)
    for event in ("session", "prompt", "compact"):
        proc = subprocess.run(
            [sys.executable, str(script), event],
            capture_output=True, text=True, timeout=10,
            env=env,
            input="",
        )
        if proc.returncode != 0:
            fail(f"devin_mode.py {event} exited {proc.returncode}: {proc.stderr.strip()[:120]}")


def main() -> int:
    checks = [
        check_devin_pin,
        check_stack_pin_sync,
        check_devin_config,
        check_mcp_config,
        check_hooks,
        check_plugin,
        check_catalog,
        check_shared_sync,
        check_bootstrap,
        check_ps1_ascii,
        check_devin_mode_smoke,
    ]
    for check in checks:
        try:
            check()
        except Exception as exc:
            fail(f"{check.__name__} crashed: {exc}")
    for error in ERRORS:
        print(f"FAIL {error}", file=sys.stderr)
    if ERRORS:
        print(f"{len(ERRORS)} artifact errors", file=sys.stderr)
        return 1
    print("PASS [artifact] devin-setup projections (pin == config == plugin == shared twins)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
