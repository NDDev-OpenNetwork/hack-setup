#!/usr/bin/env python3
"""Validate Codex 0.155.1 project artifacts. Python 3.11+. No third-party deps."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN_PATH = ROOT / "build" / "codex-pin.json"
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
ROOT_PLUGIN_KEYS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}
SKILL_NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)
SKILL_DESC_RE = re.compile(r"^description:\s*.+\s*$", re.MULTILINE)


class CheckError(Exception):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON {path.relative_to(ROOT)}: {exc}") from exc


def load_toml(path: Path) -> dict[str, object]:
    try:
        return tomllib.loads(read_text(path))
    except tomllib.TOMLDecodeError as exc:
        raise CheckError(f"invalid TOML {path.relative_to(ROOT)}: {exc}") from exc


def skill_name(path: Path) -> str:
    text = read_text(path)
    if not text.startswith("---"):
        raise CheckError(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
    name_match = SKILL_NAME_RE.search(text)
    if name_match is None:
        raise CheckError(f"{path.relative_to(ROOT)}: missing frontmatter name")
    if SKILL_DESC_RE.search(text) is None:
        raise CheckError(f"{path.relative_to(ROOT)}: missing frontmatter description")
    name = name_match.group(1)
    if len(name) > 64:
        raise CheckError(f"{path.relative_to(ROOT)}: name longer than 64 characters")
    return name


def collect_skill_names(root: Path) -> dict[str, Path]:
    names: dict[str, Path] = {}
    if not root.is_dir():
        return names
    for skill_md in sorted(root.glob("*/SKILL.md")):
        name = skill_name(skill_md)
        if name in names:
            raise CheckError(f"duplicate skill name {name}: {names[name]} and {skill_md}")
        names[name] = skill_md
    return names


def check_pin() -> str:
    pin = load_json(PIN_PATH)
    if not isinstance(pin, dict):
        raise CheckError("build/codex-pin.json must be an object")
    version = pin.get("codex_cli")
    if version != "0.155.1":
        raise CheckError(f"codex_cli pin must be 0.155.1, got {version!r}")
    if pin.get("release_tag") != "rust-v0.155.1":
        raise CheckError("release_tag must be rust-v0.155.1")
    return version


def check_agents_md() -> None:
    text = read_text(ROOT / "AGENTS.md")
    if not text.strip():
        raise CheckError("AGENTS.md is empty")
    size = len(text.encode("utf-8"))
    if size > 32768:
        raise CheckError(f"AGENTS.md is {size} bytes; Codex default cap is 32 KiB")
    if "0.155.1" not in text:
        raise CheckError("AGENTS.md must name the 0.155.1 pin")


def check_config() -> None:
    config = load_toml(ROOT / ".codex" / "config.toml")
    if config.get("approval_policy") == "untrusted":
        raise CheckError("approval_policy=untrusted is retired")
    if "default_permissions" in config and "sandbox_mode" in config:
        raise CheckError("do not mix default_permissions with sandbox_mode")
    features = config.get("features")
    if isinstance(features, dict):
        for key in features:
            if str(key).startswith("web_search"):
                raise CheckError("use top-level web_search, not features.web_search*")
    plugins = config.get("plugins")
    if not isinstance(plugins, dict) or "saint-tibo@saint-tibo" not in plugins:
        raise CheckError('.codex/config.toml must enable plugins."saint-tibo@saint-tibo"')


def check_custom_agents() -> None:
    required = {"name", "description", "developer_instructions"}
    expected = {
        "mapper.toml": "mapper",
        "reviewer.toml": "reviewer",
        "implementer.toml": "implementer",
    }
    agents_dir = ROOT / ".codex" / "agents"
    for filename, agent_name in expected.items():
        data = load_toml(agents_dir / filename)
        missing = required.difference(data)
        if missing:
            raise CheckError(f"{filename} missing {sorted(missing)}")
        if data.get("name") != agent_name:
            raise CheckError(f"{filename} name must be {agent_name}")


def check_plugin_and_marketplace() -> None:
    plugin = load_json(ROOT / "plugins" / "saint-tibo" / "plugin.json")
    if not isinstance(plugin, dict):
        raise CheckError("plugin.json must be an object")
    if plugin.get("$schema") != PLUGIN_SCHEMA:
        raise CheckError("plugin.json must declare Agent Plugins 1.0.0 $schema")
    if plugin.get("name") != "saint-tibo":
        raise CheckError("plugin.json name must be saint-tibo")
    extra = set(plugin).difference(ROOT_PLUGIN_KEYS)
    if extra:
        raise CheckError(f"plugin.json has non-portable root keys: {sorted(extra)}")
    for forbidden in ("skills", "interface", "mcpServers", "apps", "hooks"):
        if forbidden in plugin:
            raise CheckError(f"plugin.json must not set root {forbidden}")

    marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    if not isinstance(marketplace, dict):
        raise CheckError("marketplace.json must be an object")
    if marketplace.get("name") != "saint-tibo":
        raise CheckError("marketplace name must be saint-tibo")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise CheckError("marketplace.plugins must be a non-empty list")
    entry = plugins[0]
    if not isinstance(entry, dict):
        raise CheckError("marketplace plugin entry must be an object")
    if entry.get("name") != "saint-tibo":
        raise CheckError("marketplace plugin name must be saint-tibo")
    source = entry.get("source")
    if not isinstance(source, dict):
        raise CheckError("marketplace source must be an object")
    path = source.get("path")
    if not isinstance(path, str) or not path.startswith("./"):
        raise CheckError("marketplace source.path must start with ./")
    plugin_dir = (ROOT / path).resolve()
    if plugin_dir != (ROOT / "plugins" / "saint-tibo").resolve():
        raise CheckError(f"marketplace source.path does not resolve to plugins/saint-tibo: {path}")
    policy = entry.get("policy")
    if not isinstance(policy, dict):
        raise CheckError("marketplace policy must be an object")
    if "installation" not in policy or "authentication" not in policy:
        raise CheckError("marketplace policy needs installation and authentication")
    if "category" not in entry:
        raise CheckError("marketplace entry needs category")


def check_skills() -> None:
    repo_skills = collect_skill_names(ROOT / ".agents" / "skills")
    plugin_skills = collect_skill_names(ROOT / "plugins" / "saint-tibo" / "skills")
    expected_repo = {"repo-orientation", "quality-gate", "one-repo-workflow"}
    if set(repo_skills) != expected_repo:
        raise CheckError(f"repo skills must be {sorted(expected_repo)}, got {sorted(repo_skills)}")
    if set(plugin_skills) != {"saint-tibo"}:
        raise CheckError(f"plugin skills must be {{saint-tibo}}, got {sorted(plugin_skills)}")
    overlap = set(repo_skills).intersection(plugin_skills)
    if overlap:
        raise CheckError(f"skill name collision between repo and plugin: {sorted(overlap)}")


def main() -> int:
    checks = (
        check_pin,
        check_agents_md,
        check_config,
        check_custom_agents,
        check_plugin_and_marketplace,
        check_skills,
    )
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except CheckError as exc:
            errors.append(str(exc))
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print("PASS Codex 0.155.1 project artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
