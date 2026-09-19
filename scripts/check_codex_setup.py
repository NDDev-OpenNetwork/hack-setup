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
STACK_PIN_PATH = ROOT / "build" / "stack-pin.json"
CATALOG_PATH = ROOT / "install" / "catalog.toml"
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PINNED_PLATFORMS = (
    "darwin-arm64",
    "darwin-x86_64",
    "linux-arm64",
    "linux-x86_64",
)
CATALOG_MODULES = (
    ("prereqs", "modules/10-prereqs"),
    ("codex-cli", "modules/20-codex-cli"),
    ("runtimes", "modules/30-runtimes"),
    ("project-verify", "modules/40-project-verify"),
)
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


def require_sha256(label: str, value: object) -> None:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise CheckError(f"{label} must be a 64-char lowercase sha256")


def check_pin() -> str:
    pin = load_json(PIN_PATH)
    if not isinstance(pin, dict):
        raise CheckError("build/codex-pin.json must be an object")
    version = pin.get("codex_cli")
    if version != "0.155.1":
        raise CheckError(f"codex_cli pin must be 0.155.1, got {version!r}")
    if pin.get("release_tag") != "rust-v0.155.1":
        raise CheckError("release_tag must be rust-v0.155.1")
    installer = pin.get("installer")
    if not isinstance(installer, dict):
        raise CheckError("pin installer must be an object")
    url = installer.get("url")
    if not isinstance(url, str) or "rust-v0.155.1/install.sh" not in url:
        raise CheckError("pin installer.url must be the rust-v0.155.1 install.sh")
    require_sha256("pin installer.sha256", installer.get("sha256"))
    packages = pin.get("packages")
    if not isinstance(packages, dict):
        raise CheckError("pin packages must be an object")
    missing = [name for name in PINNED_PLATFORMS if name not in packages]
    if missing:
        raise CheckError(f"pin packages missing {missing}")
    for name in PINNED_PLATFORMS:
        package = packages[name]
        if not isinstance(package, dict):
            raise CheckError(f"pin packages.{name} must be an object")
        for key in ("name", "triple", "url", "sha256"):
            if key not in package:
                raise CheckError(f"pin packages.{name} missing {key}")
        require_sha256(f"pin packages.{name}.sha256", package["sha256"])
    return version


def require_versioned_package(block: object, label: str) -> None:
    if not isinstance(block, dict):
        raise CheckError(f"{label} must be an object")
    version = block.get("version")
    if not isinstance(version, str) or not version.strip():
        raise CheckError(f"{label}.version must be a non-empty string")


def check_stack_pin() -> None:
    pin = load_json(STACK_PIN_PATH)
    if not isinstance(pin, dict):
        raise CheckError("build/stack-pin.json must be an object")
    if pin.get("schema_version") != 2:
        raise CheckError("stack-pin schema_version must be 2")
    verified_on = pin.get("verified_on")
    if not isinstance(verified_on, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", verified_on) is None:
        raise CheckError("stack-pin.verified_on must be YYYY-MM-DD")
    if pin.get("codex_pin") != "build/codex-pin.json":
        raise CheckError("stack-pin.codex_pin must point at build/codex-pin.json")
    registered = pin.get("registered")
    if not isinstance(registered, dict):
        raise CheckError("stack-pin.registered must be an object")
    plugin = registered.get("plugin")
    if not isinstance(plugin, dict) or plugin.get("id") != "saint-tibo@saint-tibo":
        raise CheckError("stack-pin must register plugin id saint-tibo@saint-tibo")
    if registered.get("agents") != ["mapper", "reviewer", "implementer"]:
        raise CheckError("stack-pin agents must be mapper, reviewer, implementer")
    models = pin.get("models")
    if not isinstance(models, dict) or models.get("default") != "gpt-5.6":
        raise CheckError("stack-pin models.default must be gpt-5.6")
    if pin.get("package_manager") != "bun":
        raise CheckError("stack-pin.package_manager must be bun")
    if "pnpm" in pin.get("runtimes", {}):
        raise CheckError("stack-pin must not include pnpm")
    runtimes = pin.get("runtimes")
    if not isinstance(runtimes, dict):
        raise CheckError("stack-pin.runtimes must be an object")
    for key in ("node", "bun", "uv", "typescript", "rust", "go"):
        require_versioned_package(runtimes.get(key), f"stack-pin.runtimes.{key}")
    python = runtimes.get("python")
    if not isinstance(python, dict):
        raise CheckError("stack-pin.runtimes.python must be an object")
    require_versioned_package(python, "stack-pin.runtimes.python")
    node_file = read_text(ROOT / ".node-version").strip()
    if node_file != runtimes["node"]["version"]:
        raise CheckError(".node-version must match stack-pin runtimes.node.version")
    python_file = read_text(ROOT / ".python-version").strip()
    if python_file != python["version"]:
        raise CheckError(".python-version must match stack-pin runtimes.python.version")
    package = load_json(ROOT / "package.json")
    if not isinstance(package, dict):
        raise CheckError("package.json must be an object")
    expected_pm = f"bun@{runtimes['bun']['version']}"
    if package.get("packageManager") != expected_pm:
        raise CheckError(f"package.json packageManager must be {expected_pm}")
    frontend = pin.get("frontend")
    if not isinstance(frontend, dict):
        raise CheckError("stack-pin.frontend must be an object")
    if "next" in frontend:
        raise CheckError("stack-pin.frontend must not include Next.js")
    for key in ("react", "vite", "tailwindcss", "shadcn", "zod"):
        require_versioned_package(frontend.get(key), f"stack-pin.frontend.{key}")
    backend = pin.get("backend")
    if not isinstance(backend, dict):
        raise CheckError("stack-pin.backend must be an object")
    require_versioned_package(backend.get("fastapi"), "stack-pin.backend.fastapi")
    environments = pin.get("environments")
    if not isinstance(environments, dict):
        raise CheckError("stack-pin.environments must be an object")
    telegram = environments.get("telegram")
    if not isinstance(telegram, dict) or telegram.get("redis_py") != "7.4.1":
        raise CheckError("telegram env must pin redis_py 7.4.1")
    api_workers = environments.get("api_workers")
    if not isinstance(api_workers, dict) or api_workers.get("redis_py") != "8.1.0":
        raise CheckError("api_workers env must pin redis_py 8.1.0")
    quality = pin.get("quality")
    if not isinstance(quality, dict):
        raise CheckError("stack-pin.quality must be an object")
    for key in ("biome", "vitest", "playwright", "ruff"):
        require_versioned_package(quality.get(key), f"stack-pin.quality.{key}")
    banned = pin.get("do_not_use")
    if not isinstance(banned, list) or "Next.js" not in banned or "pnpm" not in banned:
        raise CheckError("stack-pin.do_not_use must include Next.js and pnpm")
    check_verify_block(pin)
    if not (ROOT / "build" / "stack-standard.md").is_file():
        raise CheckError("missing build/stack-standard.md; run python3 scripts/check_stack.py --write")


def check_verify_block(pin: dict[str, object]) -> None:
    verify = pin.get("verify")
    if not isinstance(verify, dict):
        raise CheckError("stack-pin.verify must be an object")
    required = verify.get("required")
    declared = verify.get("declared")
    if not isinstance(required, list) or not isinstance(declared, list):
        raise CheckError("stack-pin.verify.required and verify.declared must be lists")
    required_ids = []
    for index, entry in enumerate(required):
        probe_id = require_probe_entry(entry, f"verify.required[{index}]", pin)
        required_ids.append(probe_id)
    if required_ids != ["codex", "node", "bun", "python", "uv"]:
        raise CheckError("verify.required ids must be codex, node, bun, python, uv")
    seen = set(required_ids)
    for index, entry in enumerate(declared):
        probe_id = require_probe_entry(entry, f"verify.declared[{index}]", pin)
        if probe_id in seen:
            raise CheckError(f"duplicate verify probe id {probe_id}")
        seen.add(probe_id)


def require_probe_entry(entry: object, label: str, pin: dict[str, object]) -> str:
    if not isinstance(entry, dict):
        raise CheckError(f"{label} must be an object")
    probe_id = entry.get("id")
    path = entry.get("path")
    bin_name = entry.get("bin")
    argv = entry.get("argv")
    pattern = entry.get("pattern")
    source = entry.get("source", "stack-pin.json")
    if not isinstance(probe_id, str) or not probe_id:
        raise CheckError(f"{label}.id must be a non-empty string")
    if not isinstance(path, str) or not path:
        raise CheckError(f"{label}.path must be a non-empty string")
    if not isinstance(bin_name, str) or not bin_name:
        raise CheckError(f"{label}.bin must be a non-empty string")
    if not isinstance(argv, list) or not all(isinstance(item, str) for item in argv):
        raise CheckError(f"{label}.argv must be a list of strings")
    if not isinstance(pattern, str):
        raise CheckError(f"{label}.pattern must be a string")
    try:
        re.compile(pattern)
    except re.error as exc:
        raise CheckError(f"{label}.pattern is invalid: {exc}") from exc
    if source == "codex-pin.json":
        return probe_id
    if source != "stack-pin.json":
        raise CheckError(f"{label}.source must be stack-pin.json or codex-pin.json")
    current: object = pin
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise CheckError(f"{label}.path {path} does not resolve")
        current = current[part]
    if not isinstance(current, str) or not current.strip():
        raise CheckError(f"{label}.path {path} must resolve to a version string")
    return probe_id


def check_bootstrap() -> None:
    if (ROOT / "install").is_file():
        raise CheckError("root file named install cannot coexist with install/")
    setup = ROOT / "setup"
    if not setup.is_file():
        raise CheckError("missing ./setup entry")
    if "install/bootstrap.sh" not in read_text(setup):
        raise CheckError("./setup must exec install/bootstrap.sh")
    if not (ROOT / "install" / "bootstrap.sh").is_file():
        raise CheckError("missing install/bootstrap.sh")
    if not (ROOT / "install" / "env.sh").is_file():
        raise CheckError("missing install/env.sh")
    catalog = load_toml(CATALOG_PATH)
    if catalog.get("schema_version") != 1:
        raise CheckError("install/catalog.toml schema_version must be 1")
    if catalog.get("entry") != "./setup":
        raise CheckError("install/catalog.toml entry must be ./setup")
    modules = catalog.get("modules")
    if not isinstance(modules, list) or len(modules) != len(CATALOG_MODULES):
        raise CheckError("install/catalog.toml must list the four bootstrap modules")
    for expected, raw in zip(CATALOG_MODULES, modules, strict=True):
        if not isinstance(raw, dict):
            raise CheckError("catalog module must be a table")
        module_id, relative = expected
        if raw.get("id") != module_id:
            raise CheckError(f"catalog module id must be {module_id}")
        if raw.get("dir") != relative:
            raise CheckError(f"catalog {module_id} dir must be {relative}")
        if raw.get("enabled") is not True:
            raise CheckError(f"catalog {module_id} must be enabled")
        module_sh = ROOT / "install" / relative / "module.sh"
        if not module_sh.is_file():
            raise CheckError(f"missing {module_sh.relative_to(ROOT)}")


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
        check_stack_pin,
        check_bootstrap,
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
