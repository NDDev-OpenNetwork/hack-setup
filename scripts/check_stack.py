#!/usr/bin/env python3
"""Doctor for the frozen product stack. Python 3.11+. No third-party deps.

Pin is the source of truth. build/stack-standard.md is generated from it.
Required host tools must match. Declared host tools are reported; --strict
fails on declared MISSING/DRIFT.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _json_atom(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


STACK_PIN_PATH = ROOT / "build" / "stack-pin.json"
CODEX_PIN_PATH = ROOT / "build" / "codex-pin.json"
STANDARD_PATH = ROOT / "build" / "stack-standard.md"
SKIP_WALK = {
    "verify",
    "do_not_use",
    "conflicts",
    "registered",
    "models",
    "locales",
    "policy",
    "schema_version",
    "verified_on",
    "reverify_on_hackathon",
    "package_manager",
    "codex_pin",
    "control",
}
SECTION_ORDER = (
    "runtimes",
    "frontend",
    "backend",
    "data",
    "clients",
    "auth",
    "ai",
    "media",
    "education",
    "deploy",
    "quality",
    "lsp",
)
REQUIRED_PROBE_IDS = ("codex", "node", "bun", "python", "uv")
DEFAULT_TIMEOUT = 8.0


class CheckError(Exception):
    pass


@dataclass(frozen=True)
class Probe:
    kind: str
    probe_id: str
    source: str
    path: str
    bin: str
    argv: tuple[str, ...]
    pattern: str
    expected: str


@dataclass(frozen=True)
class ProbeResult:
    probe: Probe
    status: str
    got: str
    binary: str
    detail: str = ""


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"{path.relative_to(ROOT)} must be an object")
    return payload


def lookup(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            raise CheckError(f"missing {dotted}")
        current = current[part]
    return current


def extract_version(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text)
    if match is None:
        return None
    return match.group(1)


def prepend_pin_path() -> None:
    local = str(ROOT / ".local" / "bin")
    home = str(Path.home() / ".local" / "bin")
    os.environ["PATH"] = os.pathsep.join([local, home, os.environ.get("PATH", "")])


def collect_version_rows(pin: dict[str, Any]) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []

    def resolve(path: str) -> str:
        cur: Any = pin
        for part in path.split("."):
            if not isinstance(cur, dict):
                return ""
            if part.isdigit() and isinstance(cur, list):
                cur = cur[int(part)]
            else:
                cur = cur.get(part)
        if isinstance(cur, dict):
            value = cur.get("version")
            return value if isinstance(value, str) else ""
        return ""

    def walk(node: Any, prefix: str) -> None:
        if not isinstance(node, dict):
            return
        version = node.get("version")
        version_from = node.get("version_from")
        if isinstance(version, str) and version.strip():
            package = node.get("package")
            package_name = package if isinstance(package, str) else ""
            rows.append((prefix, version, package_name))
        elif isinstance(version_from, str) and version_from.strip():
            resolved = resolve(version_from)
            package = node.get("server")
            package_name = package if isinstance(package, str) else ""
            rows.append((prefix, f"{resolved} (via {version_from})", package_name))
        for key, value in node.items():
            if key in SKIP_WALK or key == "version":
                continue
            path = f"{prefix}.{key}" if prefix else key
            walk(value, path)

    for section in SECTION_ORDER:
        block = pin.get(section)
        if isinstance(block, dict):
            walk(block, section)
    return rows


def load_probes(stack: dict[str, Any], codex: dict[str, Any]) -> list[Probe]:
    verify = stack.get("verify")
    if not isinstance(verify, dict):
        raise CheckError("stack-pin.verify must be an object")
    probes: list[Probe] = []
    for kind in ("required", "declared"):
        entries = verify.get(kind)
        if not isinstance(entries, list) or not entries:
            raise CheckError(f"stack-pin.verify.{kind} must be a non-empty list")
        for raw in entries:
            probes.append(parse_probe(kind, raw, stack, codex))
    return probes


def parse_probe(kind: str, raw: object, stack: dict[str, Any], codex: dict[str, Any]) -> Probe:
    if not isinstance(raw, dict):
        raise CheckError(f"verify.{kind} entry must be an object")
    probe_id = raw.get("id")
    path = raw.get("path")
    bin_name = raw.get("bin")
    argv = raw.get("argv")
    pattern = raw.get("pattern")
    source_name = raw.get("source", "stack-pin.json")
    if not isinstance(probe_id, str) or not probe_id:
        raise CheckError(f"verify.{kind} entry missing id")
    if not isinstance(path, str) or not path:
        raise CheckError(f"verify.{kind}.{probe_id} missing path")
    if not isinstance(bin_name, str) or not bin_name:
        raise CheckError(f"verify.{kind}.{probe_id} missing bin")
    if not isinstance(pattern, str) or not pattern:
        raise CheckError(f"verify.{kind}.{probe_id} missing pattern")
    if not isinstance(argv, list) or not all(isinstance(item, str) for item in argv):
        raise CheckError(f"verify.{kind}.{probe_id}.argv must be a string list")
    try:
        re.compile(pattern)
    except re.error as exc:
        raise CheckError(f"verify.{kind}.{probe_id}.pattern is invalid: {exc}") from exc
    if source_name == "codex-pin.json":
        expected = lookup(codex, path)
    elif source_name == "stack-pin.json":
        expected = lookup(stack, path)
    else:
        raise CheckError(f"verify.{kind}.{probe_id}.source must be stack-pin.json or codex-pin.json")
    if not isinstance(expected, str) or not expected.strip():
        raise CheckError(f"verify.{kind}.{probe_id} path {path} is not a version string")
    return Probe(kind, probe_id, source_name, path, bin_name, tuple(argv), pattern, expected)


def run_probe(probe: Probe) -> ProbeResult:
    binary = shutil.which(probe.bin)
    if binary is None:
        return ProbeResult(probe, "MISSING", "-", "-", "not on PATH")
    timeout = DEFAULT_TIMEOUT
    try:
        completed = subprocess.run(
            [binary, *probe.argv],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return ProbeResult(probe, "TIMEOUT", "-", binary, f">{timeout:.0f}s")
    text = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    got = extract_version(text, probe.pattern)
    if got is None:
        snippet = " ".join(text.split())[:80] or f"exit {completed.returncode}"
        return ProbeResult(probe, "UNPARSED", "-", binary, snippet)
    if got == probe.expected:
        return ProbeResult(probe, "OK", got, binary)
    return ProbeResult(probe, "DRIFT", got, binary)


def render_standard(stack: dict[str, Any], probes: list[Probe]) -> str:
    rows = collect_version_rows(stack)
    lines = [
        "# Stack standard",
        "",
        "Generated from `build/stack-pin.json`. Do not edit by hand.",
        "Refresh with `python3 scripts/check_stack.py --write`.",
        "",
        f"- verified_on: `{stack.get('verified_on')}`",
        f"- schema_version: `{stack.get('schema_version')}`",
        f"- package_manager: `{stack.get('package_manager')}`",
        f"- locales: `{', '.join(stack.get('locales', []))}`",
    ]
    control = stack.get("control")
    if isinstance(control, dict):
        law = control.get("law")
        if isinstance(law, list):
            law_txt = ", ".join(f"`{item}`" for item in law)
        else:
            law_txt = f"`{law}`"
        lines.extend(
            [
                "",
                "## Control",
                "",
                f"- law: {law_txt}",
                f"- runtime: `{control.get('runtime')}`",
                f"- generated: `{control.get('generated')}`",
                f"- router: `{control.get('router')}`",
                f"- rules: `{control.get('rules')}`",
                f"- proof: `{control.get('proof')}`",
                f"- gate: `{control.get('gate')}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Versioned pins",
            "",
            "| Path | Version | Package |",
            "| --- | --- | --- |",
        ]
    )
    for path, version, package in rows:
        package_cell = f"`{package}`" if package else ""
        lines.append(f"| `{path}` | `{version}` | {package_cell} |")

    environments = stack.get("environments")
    if isinstance(environments, dict):
        lines.extend(["", "## Environments", "", "| Env | redis-py | Notes |", "| --- | --- | --- |"])
        for name, block in environments.items():
            if not isinstance(block, dict):
                continue
            redis_py = block.get("redis_py", "")
            notes = block.get("reason") or block.get("shares") or block.get("isolates") or ""
            if isinstance(notes, list):
                notes = ", ".join(str(item) for item in notes)
            lines.append(f"| `{name}` | `{redis_py}` | {notes} |")

    lines.extend(["", "## Host probes", "", "| Class | Id | Bin | Pin path | Want |", "| --- | --- | --- | --- | --- |"])
    for probe in probes:
        lines.append(
            f"| {probe.kind} | `{probe.probe_id}` | `{probe.bin}` | `{probe.path}` | `{probe.expected}` |"
        )

    banned = stack.get("do_not_use")
    models = stack.get("models")
    if isinstance(models, dict):
        lines.extend(
            [
                "",
                "## Codex models",
                "",
                f"- primary: `{models.get('primary')}`",
                f"- secondary: `{models.get('secondary')}` (`--profile {models.get('secondary_profile')}`)",
                f"- review_model: `{models.get('review_model')}`",
                f"- reasoning_effort: `{models.get('reasoning_effort')}`",
                f"- requested window / compact: `{models.get('requested_context_window')}` / `{models.get('requested_auto_compact')}`",
                f"- API window / max input: `{models.get('api_context_window')}` / `{models.get('api_max_input')}`",
                f"- Codex catalog max / effective: `{models.get('catalog_max_context_window')}` / `{models.get('effective_context_window')}`",
                f"- usable /status: `{models.get('usable_context_window')}`",
                f"- 90% compact cap: `{models.get('catalog_auto_compact_cap')}`",
                f"- effective auto-compact: `{models.get('effective_auto_compact')}`",
            ]
        )

    registered = stack.get("registered")
    if isinstance(registered, dict):
        if registered.get("agents_enabled") is False:
            if isinstance(stack.get("models"), dict):
                # models section already exists; session block added below
                pass
        session = registered.get("session")
        if isinstance(session, dict):
            lines.extend(
                [
                    "",
                    "## Codex session",
                    "",
                    f"- approval_policy: `{session.get('approval_policy')}`",
                    f"- sandbox_mode: `{session.get('sandbox_mode')}`",
                    f"- allow_login_shell: `{_json_atom(session.get('allow_login_shell'))}`",
                    f"- web_search: `{session.get('web_search')}`",
                    f"- permission_system: `{session.get('permission_system')}`",
                    f"- CLI: `{session.get('cli_equivalent')}` (`{session.get('cli_alias')}`)",
                    f"- not YOLO: `{session.get('not_yolo')}`",
                    f"- project agents: `{_json_atom(registered.get('agents_enabled'))}`",
                    f"- project execpolicy `.rules`: `{_json_atom(session.get('project_execpolicy_rules'))}`",
                    f"- ignore-rules config key: `{_json_atom(session.get('ignore_rules_is_config_key'))}`",
                    f"- ignore-rules CLI: `{session.get('ignore_rules_cli')}`",
                ]
            )
        plugin = registered.get("plugin")
        standards_plugin = registered.get("standards_plugin")
        if isinstance(plugin, dict) or isinstance(standards_plugin, dict):
            lines.extend(["", "## Plugins", ""])
            if isinstance(plugin, dict):
                lines.append(f"- team: `{plugin.get('id')}`")
            if isinstance(standards_plugin, dict):
                lines.append(f"- standards: `{standards_plugin.get('id')}`")
                lines.append(f"- frames: `{standards_plugin.get('standards')}`")
            skills = registered.get("standards_plugin_skills")
            if isinstance(skills, list) and skills:
                listed = ", ".join(f"`{name}`" for name in skills if isinstance(name, str))
                if listed:
                    lines.append(f"- standards skills: {listed}")

    if isinstance(banned, list) and banned:
        lines.extend(["", "## Do not use", ""])
        lines.extend(f"- {item}" for item in banned)

    conflicts = stack.get("conflicts")
    if isinstance(conflicts, list) and conflicts:
        lines.extend(["", "## Conflicts", "", "| Id | Decision |", "| --- | --- |"])
        for item in conflicts:
            if isinstance(item, dict):
                lines.append(f"| `{item.get('id', '')}` | {item.get('decision', '')} |")

    lines.append("")
    return "\n".join(lines)


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    fmt = "  ".join(f"{{:{width}}}" for width in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * width for width in widths)))
    for row in rows:
        print(fmt.format(*row))


def cmd_list(stack: dict[str, Any], probes: list[Probe]) -> int:
    sys.stdout.write(render_standard(stack, probes))
    return 0


def cmd_write(stack: dict[str, Any], probes: list[Probe]) -> int:
    STANDARD_PATH.write_text(render_standard(stack, probes), encoding="utf-8")
    print(f"wrote {STANDARD_PATH.relative_to(ROOT)}")
    return 0


def check_standard_fresh(stack: dict[str, Any], probes: list[Probe]) -> None:
    expected = render_standard(stack, probes)
    if not STANDARD_PATH.is_file():
        raise CheckError("build/stack-standard.md missing; run python3 scripts/check_stack.py --write")
    actual = STANDARD_PATH.read_text(encoding="utf-8")
    if actual != expected:
        raise CheckError("build/stack-standard.md is stale; run python3 scripts/check_stack.py --write")


def doctor_decision(results: list[ProbeResult], *, strict: bool) -> tuple[int, list[str]]:
    failed = [result for result in results if result.probe.kind == "required" and result.status != "OK"]
    declared_bad = [
        result
        for result in results
        if result.probe.kind == "declared" and result.status not in {"OK", "MISSING"}
    ]
    missing_declared = [
        result for result in results if result.probe.kind == "declared" and result.status == "MISSING"
    ]
    messages: list[str] = []
    if declared_bad:
        messages.append(
            "declared drift/unparsed: " + ", ".join(item.probe.probe_id for item in declared_bad)
        )
    if missing_declared:
        messages.append(
            "declared missing (ok until installer exists): "
            + ", ".join(item.probe.probe_id for item in missing_declared)
        )
    if failed:
        messages.append(
            "FAIL required: " + ", ".join(item.probe.probe_id + "=" + item.status for item in failed)
        )
        return 1, messages
    if strict and (declared_bad or missing_declared):
        messages.append("FAIL --strict: declared host tools must match the pin")
        return 1, messages
    messages.append("PASS required host tools match the pin")
    return 0, messages


def cmd_doctor(probes: list[Probe], *, strict: bool) -> int:
    results = [run_probe(probe) for probe in probes]
    rows = [
        [
            result.probe.kind,
            result.probe.probe_id,
            result.probe.expected,
            result.got,
            result.status,
            result.binary if result.binary != "-" else result.detail,
        ]
        for result in results
    ]
    print_table(["class", "id", "want", "got", "status", "bin"], rows)
    code, messages = doctor_decision(results, strict=strict)
    for message in messages:
        print(message)
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List and verify the frozen stack pin")
    parser.add_argument("--list", action="store_true", help="print the generated standard")
    parser.add_argument("--write", action="store_true", help="write build/stack-standard.md")
    parser.add_argument("--strict", action="store_true", help="fail on declared MISSING/DRIFT")
    args = parser.parse_args(argv)
    prepend_pin_path()
    stack = load_json(STACK_PIN_PATH)
    codex = load_json(CODEX_PIN_PATH)
    probes = load_probes(stack, codex)
    required_ids = tuple(probe.probe_id for probe in probes if probe.kind == "required")
    if required_ids != REQUIRED_PROBE_IDS:
        raise CheckError(f"verify.required ids must be {REQUIRED_PROBE_IDS}, got {required_ids}")
    if args.write:
        return cmd_write(stack, probes)
    if args.list:
        return cmd_list(stack, probes)
    check_standard_fresh(stack, probes)
    return cmd_doctor(probes, strict=args.strict)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        sys.exit(1)
