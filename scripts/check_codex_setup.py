#!/usr/bin/env python3
"""Validate Codex 0.155.1 project artifacts. Python 3.11+. No third-party deps."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
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
    "windows-x86_64",
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


def marketplace_names() -> list[str]:
    """Plugin names from .agents/plugins/marketplace.json — the plugin SoT.

    Adding a plugin needs no checker edits: the marketplace entry drives
    the registered.<suffix>_plugin law key, config enablement, cache
    parity, and the <suffix>_plugin_skills pin set.
    """
    marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    plugins = marketplace.get("plugins") if isinstance(marketplace, dict) else None
    if not isinstance(plugins, list) or not plugins:
        raise CheckError("marketplace.plugins must be a non-empty list")
    names: list[str] = []
    for entry in plugins:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            raise CheckError("marketplace entries need a string name")
        names.append(entry["name"])
    if names[0] != "saint-tibo":
        raise CheckError("marketplace.plugins must start with saint-tibo")
    if len(names) != len(set(names)):
        raise CheckError("marketplace plugin names must be unique")
    return names


def plugin_key(name: str) -> str:
    """Marketplace name -> registered.<key>_plugin pin suffix.

    saint-tibo uses the bare `plugin`/`plugin_skills` keys; every other
    plugin must be hack-agent-<suffix> and maps to <suffix>_plugin /
    <suffix>_plugin_skills.
    """
    if name == "saint-tibo":
        return ""
    prefix = "hack-agent-"
    if not name.startswith(prefix):
        raise CheckError(
            f"marketplace plugin {name} must be saint-tibo or hack-agent-*"
        )
    return name[len(prefix) :]


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


def lookup_version(data: object, dotted: str) -> str:
    cur: object = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise CheckError(f"missing {dotted}")
        cur = cur[part]
    if isinstance(cur, dict):
        version = cur.get("version")
        if isinstance(version, str) and version:
            return version
        version_from = cur.get("version_from")
        if isinstance(version_from, str) and version_from:
            return lookup_version(data, version_from)
    raise CheckError(f"{dotted} has no version")


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
    desc_match = re.search(r"^description:\s*(.+?)\s*$", text, re.MULTILINE)
    if desc_match is None:
        raise CheckError(f"{path.relative_to(ROOT)}: missing frontmatter description")
    description = desc_match.group(1).strip()
    if not description:
        raise CheckError(f"{path.relative_to(ROOT)}: empty frontmatter description")
    if len(description) > 1024:
        raise CheckError(
            f"{path.relative_to(ROOT)}: description longer than 1024 characters"
        )
    return name


def collect_skill_names(root: Path) -> dict[str, Path]:
    names: dict[str, Path] = {}
    if not root.is_dir():
        return names
    for skill_md in sorted(root.glob("*/SKILL.md")):
        name = skill_name(skill_md)
        if skill_md.parent.name != name:
            raise CheckError(
                f"{skill_md.relative_to(ROOT)} name {name} must match "
                f"directory {skill_md.parent.name}"
            )
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
    installer_ps1 = pin.get("installer_ps1")
    if not isinstance(installer_ps1, dict):
        raise CheckError("pin installer_ps1 must be an object")
    ps1_url = installer_ps1.get("url")
    if not isinstance(ps1_url, str) or "rust-v0.155.1/install.ps1" not in ps1_url:
        raise CheckError("pin installer_ps1.url must be the rust-v0.155.1 install.ps1")
    require_sha256("pin installer_ps1.sha256", installer_ps1.get("sha256"))
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
    control = pin.get("control")
    if not isinstance(control, dict):
        raise CheckError("stack-pin.control must be an object")
    law = control.get("law")
    if law != ["build/codex-pin.json", "build/stack-pin.json"]:
        raise CheckError("stack-pin.control.law must be the two pin files")
    for key, expected in (
        ("runtime", ".codex/config.toml"),
        ("generated", "build/stack-standard.md"),
        ("router", "AGENTS.md"),
        ("rules", "plugins/hack-agent-standards/standards/INDEX.md"),
        ("proof", "just check"),
        ("gate", "just gate"),
    ):
        if control.get(key) != expected:
            raise CheckError(f"stack-pin.control.{key} must be {expected}")
    for rel in (
        "build/codex-pin.json",
        "build/stack-pin.json",
        ".codex/config.toml",
        "build/stack-standard.md",
        "AGENTS.md",
        "plugins/hack-agent-standards/standards/INDEX.md",
        "justfile",
    ):
        if not (ROOT / rel).is_file():
            raise CheckError(f"control path missing: {rel}")
    justfile = read_text(ROOT / "justfile")
    if not re.search(r"^check:", justfile, re.M):
        raise CheckError("justfile must define the proof recipe `check:`")
    if not re.search(r"^gate:", justfile, re.M):
        raise CheckError("justfile must define the gate recipe `gate:`")
    registered = pin.get("registered")
    if not isinstance(registered, dict):
        raise CheckError("stack-pin.registered must be an object")
    for name in marketplace_names():
        key = plugin_key(name)
        entry = registered.get(f"{key}_plugin" if key else "plugin")
        if not isinstance(entry, dict) or entry.get("id") != f"{name}@saint-tibo":
            raise CheckError(
                f"stack-pin must register {name} as registered.{key}_plugin"
                if key
                else "stack-pin must register plugin id saint-tibo@saint-tibo"
            )
        if entry.get("path") != f"plugins/{name}/plugin.json":
            raise CheckError(
                f"registered.{key}_plugin.path must be plugins/{name}/plugin.json"
                if key
                else "plugin.path must be plugins/saint-tibo/plugin.json"
            )
    standards_plugin = registered.get("standards_plugin", {})
    if standards_plugin.get("standards") != "plugins/hack-agent-standards/standards/INDEX.md":
        raise CheckError(
            "standards_plugin.standards must be plugins/hack-agent-standards/standards/INDEX.md"
        )
    if registered.get("agents_enabled") is not False:
        raise CheckError("stack-pin.registered.agents_enabled must be false")
    if registered.get("agents") != []:
        raise CheckError("stack-pin.registered.agents must be an empty list")
    session = registered.get("session")
    if not isinstance(session, dict):
        raise CheckError("stack-pin.registered.session must be an object")
    if session.get("approval_policy") != "never":
        raise CheckError('stack-pin.registered.session.approval_policy must be "never"')
    if session.get("sandbox_mode") != "danger-full-access":
        raise CheckError(
            'stack-pin.registered.session.sandbox_mode must be "danger-full-access"'
        )
    if session.get("allow_login_shell") is not True:
        raise CheckError("stack-pin.registered.session.allow_login_shell must be true")
    if session.get("web_search") != "live":
        raise CheckError('stack-pin.registered.session.web_search must be "live"')
    if session.get("permission_system") != "sandbox_mode":
        raise CheckError(
            'stack-pin.registered.session.permission_system must be "sandbox_mode"'
        )
    if "agents_inherit_parent_sandbox" in session:
        raise CheckError(
            "registered.session.agents_inherit_parent_sandbox is leftover; "
            "project agents are off"
        )
    if session.get("project_execpolicy_rules") is not False:
        raise CheckError(
            "stack-pin.registered.session.project_execpolicy_rules must be false"
        )
    if session.get("ignore_rules_is_config_key") is not False:
        raise CheckError(
            "stack-pin.registered.session.ignore_rules_is_config_key must be false"
        )
    features = registered.get("features")
    if not isinstance(features, dict) or features.get("web_search") != "live":
        raise CheckError('stack-pin.registered.features.web_search must be "live"')
    if features.get("multi_agent") is not False:
        raise CheckError("stack-pin.registered.features.multi_agent must be false")
    if features.get("multi_agent_v2") is not False:
        raise CheckError("stack-pin.registered.features.multi_agent_v2 must be false")
    if features.get("hooks") is not True:
        raise CheckError("stack-pin.registered.features.hooks must be true")
    if features.get("memories") is not False:
        raise CheckError("stack-pin.registered.features.memories must be false")
    mcp_servers = registered.get("mcp_servers")
    if not isinstance(mcp_servers, dict):
        raise CheckError("stack-pin.registered.mcp_servers must be an object")
    required_servers = {"serena", "shadcn", "context7", "grep", "deepwiki", "keenable"}
    missing_servers = required_servers.difference(mcp_servers)
    if missing_servers:
        raise CheckError(
            f"registered.mcp_servers missing servers: {sorted(missing_servers)}"
        )
    for name, spec in mcp_servers.items():
        if name == "rule":
            continue
        if not isinstance(spec, dict):
            raise CheckError(f"registered.mcp_servers.{name} must be an object")
        has_stdio = isinstance(spec.get("command"), str)
        has_remote = isinstance(spec.get("url"), str)
        if has_stdio == has_remote:
            raise CheckError(
                f"registered.mcp_servers.{name} needs exactly one of command/url"
            )
        for literal in ("bearer_token", "http_headers", "headers"):
            if literal in spec:
                raise CheckError(
                    f"registered.mcp_servers.{name}.{literal} is a literal secret "
                    "surface; use *_env_var references only"
                )
        token_var = spec.get("bearer_token_env_var")
        if token_var is not None and not re.fullmatch(r"[A-Z][A-Z0-9_]*", str(token_var)):
            raise CheckError(
                f"registered.mcp_servers.{name}.bearer_token_env_var must name an env var"
            )
        env_headers = spec.get("env_http_headers")
        if env_headers is not None and (
            not isinstance(env_headers, dict)
            or not all(
                re.fullmatch(r"[A-Z][A-Z0-9_]*", str(v))
                for v in env_headers.values()
            )
        ):
            raise CheckError(
                f"registered.mcp_servers.{name}.env_http_headers values must be env var names"
            )
    mcp_block = pin.get("mcp")
    if not isinstance(mcp_block, dict) or not isinstance(mcp_block.get("serena"), dict):
        raise CheckError("stack-pin.mcp.serena must be an object")
    serena_version = mcp_block["serena"].get("version")
    serena_args = mcp_servers.get("serena", {}).get("args", [])
    if f"serena-agent=={serena_version}" not in serena_args:
        raise CheckError(
            "registered.mcp_servers.serena.args must carry "
            f"serena-agent=={serena_version} (mcp.serena.version)"
        )
    shadcn_version = lookup_version(pin, "frontend.shadcn")
    shadcn_args = mcp_servers.get("shadcn", {}).get("args", [])
    if f"shadcn@{shadcn_version}" not in shadcn_args:
        raise CheckError(
            f"registered.mcp_servers.shadcn.args must carry shadcn@{shadcn_version}"
        )
    remote_urls = mcp_block.get("remote", {})
    if isinstance(remote_urls, dict):
        for name, url in remote_urls.items():
            if mcp_servers.get(name, {}).get("url") != url:
                raise CheckError(
                    f"registered.mcp_servers.{name}.url must match mcp.remote.{name}"
                )
    models = pin.get("models")
    if not isinstance(models, dict):
        raise CheckError("stack-pin.models must be an object")
    if models.get("primary") != "gpt-6-astra":
        raise CheckError('stack-pin.models.primary must be "gpt-6-astra"')
    if models.get("secondary") != "gpt-5.6-sol":
        raise CheckError('stack-pin.models.secondary must be "gpt-5.6-sol"')
    if models.get("secondary_profile") != "sol":
        raise CheckError('stack-pin.models.secondary_profile must be "sol"')
    if models.get("review_model") != "gpt-5.6-sol":
        raise CheckError('stack-pin.models.review_model must be "gpt-5.6-sol"')
    if models.get("reasoning_effort") != "xhigh":
        raise CheckError('stack-pin.models.reasoning_effort must be "xhigh"')
    if models.get("requested_context_window") != 872_000:
        raise CheckError("stack-pin.models.requested_context_window must be 872000")
    if models.get("requested_auto_compact") != 700_000:
        raise CheckError("stack-pin.models.requested_auto_compact must be 700000")
    if models.get("catalog_max_context_window") != 872_000:
        raise CheckError("stack-pin.models.catalog_max_context_window must be 872000")
    if models.get("catalog_auto_compact_cap") != 784_800:
        raise CheckError("stack-pin.models.catalog_auto_compact_cap must be 784800")
    if models.get("effective_context_window") != 872_000:
        raise CheckError("stack-pin.models.effective_context_window must be 872000")
    if models.get("usable_context_window") != 828_400:
        raise CheckError("stack-pin.models.usable_context_window must be 828400")
    if models.get("effective_auto_compact") != 700_000:
        raise CheckError("stack-pin.models.effective_auto_compact must be 700000")
    catalog_max = models.get("catalog_max_context_window")
    if not isinstance(catalog_max, int):
        raise CheckError("stack-pin.models.catalog_max_context_window must be an int")
    if models.get("requested_context_window") != catalog_max:
        raise CheckError("requested_context_window must equal catalog_max_context_window")
    if models.get("effective_context_window") != catalog_max:
        raise CheckError("effective_context_window must equal catalog_max_context_window")
    if models.get("usable_context_window") != catalog_max * 95 // 100:
        raise CheckError("usable_context_window must be catalog_max * 95 / 100")
    if models.get("catalog_auto_compact_cap") != catalog_max * 9 // 10:
        raise CheckError("catalog_auto_compact_cap must be catalog_max * 90%")
    compact = models.get("requested_auto_compact")
    if not isinstance(compact, int):
        raise CheckError("requested_auto_compact must be an int")
    if compact > models.get("catalog_auto_compact_cap"):
        raise CheckError("requested_auto_compact must be <= catalog 90% cap")
    if compact >= models.get("usable_context_window"):
        raise CheckError("requested_auto_compact must be below usable /status")
    if models.get("effective_auto_compact") != compact:
        raise CheckError("effective_auto_compact must equal requested_auto_compact")
    reject = models.get("reject")
    if not isinstance(reject, list) or not {
        "gpt-5.6-luna",
        "gpt-5.6-terra",
        "gpt-5.6",
    }.issubset(reject):
        raise CheckError("stack-pin.models.reject must include gpt-5.6-luna, gpt-5.6-terra, gpt-5.6")
    if pin.get("package_manager") != "bun":
        raise CheckError("stack-pin.package_manager must be bun")
    if "pnpm" in pin.get("runtimes", {}):
        raise CheckError("stack-pin must not include pnpm")
    runtimes = pin.get("runtimes")
    if not isinstance(runtimes, dict):
        raise CheckError("stack-pin.runtimes must be an object")
    for key in ("node", "bun", "uv", "typescript", "rust", "go"):
        require_versioned_package(runtimes.get(key), f"stack-pin.runtimes.{key}")
    for key in ("node", "bun"):
        packages = runtimes[key].get("packages")
        if not isinstance(packages, dict):
            raise CheckError(f"stack-pin.runtimes.{key}.packages must be an object")
        missing = [name for name in PINNED_PLATFORMS if name not in packages]
        if missing:
            raise CheckError(f"stack-pin.runtimes.{key}.packages missing {missing}")
        for name in PINNED_PLATFORMS:
            package = packages[name]
            if not isinstance(package, dict):
                raise CheckError(f"stack-pin.runtimes.{key}.packages.{name} must be an object")
            for field in ("name", "url", "sha256"):
                if field not in package:
                    raise CheckError(f"stack-pin.runtimes.{key}.packages.{name} missing {field}")
            require_sha256(f"stack-pin.runtimes.{key}.packages.{name}.sha256", package["sha256"])
    uv = runtimes["uv"]
    for installer_key in ("installer", "installer_ps1"):
        installer = uv.get(installer_key)
        if not isinstance(installer, dict):
            raise CheckError(f"stack-pin.runtimes.uv.{installer_key} must be an object")
        require_sha256(f"stack-pin.runtimes.uv.{installer_key}.sha256", installer.get("sha256"))
    typescript = runtimes.get("typescript")
    if isinstance(typescript, dict):
        if typescript.get("version") != "7.0.2":
            raise CheckError("stack-pin.runtimes.typescript.version must be 7.0.2")
        if "compat_package" in typescript:
            raise CheckError("web typescript must not declare compat_package")
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
    mise_path = ROOT / "mise.toml"
    if mise_path.is_file():
        mise = load_toml(mise_path)
        tools = mise.get("tools")
        if not isinstance(tools, dict):
            raise CheckError("mise.toml [tools] must be a table")
        expected_tools = {
            "node": runtimes["node"]["version"],
            "python": python["version"],
            "bun": runtimes["bun"]["version"],
            "uv": runtimes["uv"]["version"],
        }
        for key, version in expected_tools.items():
            if tools.get(key) != version:
                raise CheckError(f"mise.toml tools.{key} must be {version}")
    frontend = pin.get("frontend")
    if not isinstance(frontend, dict):
        raise CheckError("stack-pin.frontend must be an object")
    if "next" in frontend:
        raise CheckError("stack-pin.frontend must not include Next.js")
    for key in ("react", "vite", "tailwindcss", "shadcn", "zod"):
        require_versioned_package(frontend.get(key), f"stack-pin.frontend.{key}")
    api_client = frontend.get("api_client")
    if not isinstance(api_client, dict):
        raise CheckError("stack-pin.frontend.api_client must be an object")
    if api_client.get("package") != "@hey-api/openapi-ts":
        raise CheckError("api_client.package must be @hey-api/openapi-ts")
    if api_client.get("version") != "0.99.0":
        raise CheckError("api_client.version must be 0.99.0")
    if api_client.get("workspace") != "not-web":
        raise CheckError("api_client.workspace must be not-web")
    shadcn = frontend.get("shadcn")
    if isinstance(shadcn, dict) and shadcn.get("install") != "cli-only; do not bun add shadcn":
        raise CheckError("shadcn.install must be cli-only; do not bun add shadcn")
    types_node = frontend.get("types_node")
    if isinstance(types_node, dict) and types_node.get("version") != "24.13.6":
        raise CheckError("types_node.version must be 24.13.6")
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
    for key in ("biome", "vitest", "playwright", "ruff", "just"):
        require_versioned_package(quality.get(key), f"stack-pin.quality.{key}")
    just = quality.get("just")
    if isinstance(just, dict) and just.get("version") != "1.58.0":
        raise CheckError("stack-pin.quality.just.version must be 1.58.0")
    banned = pin.get("do_not_use")
    if not isinstance(banned, list) or "Next.js" not in banned or "pnpm" not in banned:
        raise CheckError("stack-pin.do_not_use must include Next.js and pnpm")
    if not any(isinstance(item, str) and "asyncpg" in item for item in banned):
        raise CheckError("stack-pin.do_not_use must include asyncpg")
    for needed in (
        "typescript@6 or @typescript/typescript6 in the web workspace",
        "typescript-eslint in the web workspace",
        "@hey-api/openapi-ts@next",
        "bun add shadcn (nests zod 3); use bunx shadcn@4.21.0",
        "@types/node 26.x until Node 26 is LTS",
        "unconstrained rapidocr / opencv-python; pin is opencv-python-headless 5.0.0.93",
        "httpx 1.x; FastAPI extras require httpx<1",
        "GNU make / Makefile as the project command runner",
        "gpt-5.6-luna",
        "gpt-5.6-terra",
        "Codex subagents / features.multi_agent / features.multi_agent_v2",
    ):
        if needed not in banned:
            raise CheckError(f"stack-pin.do_not_use must include {needed}")
    if any(isinstance(item, str) and "gpt-6-astra until" in item for item in banned):
        raise CheckError("do_not_use must not ban gpt-6-astra; it is the primary model")
    lsp = pin.get("lsp")
    if not isinstance(lsp, dict):
        raise CheckError("stack-pin.lsp must be an object")
    for key, entry in lsp.items():
        if not isinstance(entry, dict):
            continue
        install = entry.get("install")
        if isinstance(install, str) and (
            "npm " in install or "pip " in install or "pnpm" in install
        ):
            raise CheckError(
                f"stack-pin.lsp.{key}.install must not use npm/pip/pnpm: {install}"
            )
    conflicts = pin.get("conflicts")
    if not isinstance(conflicts, list):
        raise CheckError("stack-pin.conflicts must be a list")
    conflict_ids = {
        item.get("id") for item in conflicts if isinstance(item, dict) and item.get("id")
    }
    for needed in (
        "openai-sdk-major",
        "hey-api-ts7-runtime",
        "bifrost-gateway-not-sdk",
        "bifrost-otel",
        "aiogram-redis-vs-taskiq",
        "docling-opencv-cv2",
        "shadcn-cli-not-dep",
        "httpx-fastapi-lt-1",
    ):
        if needed not in conflict_ids:
            raise CheckError(f"stack-pin.conflicts must include {needed}")
    check_verify_block(pin)
    check_generated_standard()


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
    if required_ids != ["codex", "node", "bun", "python", "uv", "just"]:
        raise CheckError("verify.required ids must be codex, node, bun, python, uv, just")
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


def check_generated_standard() -> None:
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import check_stack

    stack = check_stack.load_json(check_stack.STACK_PIN_PATH)
    codex = check_stack.load_json(check_stack.CODEX_PIN_PATH)
    try:
        check_stack.check_standard_fresh(stack, check_stack.load_probes(stack, codex))
    except check_stack.CheckError as exc:
        raise CheckError(str(exc)) from exc


def check_bootstrap() -> None:
    if (ROOT / "install").is_file():
        raise CheckError("root file named install cannot coexist with install/")
    setup = ROOT / "setup"
    if not setup.is_file():
        raise CheckError("missing ./setup entry")
    if "install/bootstrap.sh" not in read_text(setup):
        raise CheckError("./setup must exec install/bootstrap.sh")
    if not (ROOT / "setup.ps1").is_file():
        raise CheckError("missing ./setup.ps1 entry")
    if "install/bootstrap.ps1" not in read_text(ROOT / "setup.ps1"):
        raise CheckError("./setup.ps1 must call install/bootstrap.ps1")
    if not (ROOT / "install" / "bootstrap.sh").is_file():
        raise CheckError("missing install/bootstrap.sh")
    if not (ROOT / "install" / "bootstrap.ps1").is_file():
        raise CheckError("missing install/bootstrap.ps1")
    if not (ROOT / "install" / "env.sh").is_file():
        raise CheckError("missing install/env.sh")
    if not (ROOT / "install" / "env.ps1").is_file():
        raise CheckError("missing install/env.ps1")
    catalog = load_toml(CATALOG_PATH)
    if catalog.get("schema_version") != 1:
        raise CheckError("install/catalog.toml schema_version must be 1")
    if catalog.get("entry") != "./setup":
        raise CheckError("install/catalog.toml entry must be ./setup")
    if catalog.get("entry_windows") != "./setup.ps1":
        raise CheckError("install/catalog.toml entry_windows must be ./setup.ps1")
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
        module_ps1 = ROOT / "install" / relative / "module.ps1"
        if not module_ps1.is_file():
            raise CheckError(f"missing {module_ps1.relative_to(ROOT)}")
    modules_root = ROOT / "install" / "modules"
    found = sorted(
        path.name
        for path in modules_root.iterdir()
        if path.is_dir() and re.fullmatch(r"[0-9]{2}-.+", path.name)
    )
    expected = [Path(relative).name for _, relative in CATALOG_MODULES]
    if found != expected:
        raise CheckError(
            "install/modules/<nn>-* must match catalog.toml exactly; "
            f"found {found}, expected {expected}"
        )
    env_sh = read_text(ROOT / "install" / "env.sh")
    if "BASH_SOURCE" not in env_sh:
        raise CheckError("install/env.sh must resolve the sourced file via BASH_SOURCE")
    justfile = ROOT / "justfile"
    if not justfile.is_file():
        raise CheckError("missing justfile; just is the project command runner")
    just_text = read_text(justfile)
    for recipe in ("gate:", "check:", "setup:", "test:"):
        if recipe not in just_text:
            raise CheckError(f"justfile must define recipe {recipe.rstrip(':')}")
    for name in ("Makefile", "makefile", "GNUmakefile"):
        if (ROOT / name).exists():
            raise CheckError(f"{name} must not exist; use justfile")


def check_agents_md() -> None:
    text = read_text(ROOT / "AGENTS.md")
    if not text.strip():
        raise CheckError("AGENTS.md is empty")
    size = len(text.encode("utf-8"))
    if size > 32768:
        raise CheckError(f"AGENTS.md is {size} bytes; Codex default cap is 32 KiB")
    if "0.155.1" not in text:
        raise CheckError("AGENTS.md must name the 0.155.1 pin")
    if "gpt-6-astra" not in text or "gpt-5.6-sol" not in text:
        raise CheckError("AGENTS.md must name gpt-6-astra and gpt-5.6-sol")
    if "Do not spawn Codex subagents" not in text:
        raise CheckError("AGENTS.md must forbid Codex subagents")
    if "872_000" not in text or "700_000" not in text:
        raise CheckError("AGENTS.md must name context 872_000 and compact 700_000")
    if "## Mechanism" not in text or "just check" not in text:
        raise CheckError("AGENTS.md must describe the pin → config → just check loop")
    if "docs/rules" in text:
        raise CheckError("AGENTS.md must not route to stale docs/rules/")
    if "plugins/hack-agent-standards/standards" not in text:
        raise CheckError("AGENTS.md must route to plugins/hack-agent-standards/standards")
    if "## Motion" not in text:
        raise CheckError("AGENTS.md must include the Motion kernel")
    if "$hack-agent-standards:" not in text:
        raise CheckError(
            "AGENTS.md must invoke plugin skills as $hack-agent-standards:<name>"
        )
    if "plugins/hack-agent-standards/nested" not in text:
        raise CheckError("AGENTS.md must point at nested AGENTS templates")
    index = ROOT / "plugins" / "hack-agent-standards" / "standards" / "INDEX.md"
    if not index.is_file():
        raise CheckError("standards INDEX.md is missing")
    linked_names = set(re.findall(r"\]\(([A-Za-z0-9_.-]+\.md)\)", read_text(index)))
    for linked in linked_names:
        if not (index.parent / linked).is_file():
            raise CheckError(f"standards/INDEX.md links to missing {linked}")
    for orphan in sorted(
        path.name for path in index.parent.glob("*.md") if path.name not in linked_names
    ):
        raise CheckError(f"standards/{orphan} is not linked from INDEX.md")
    if (ROOT / "docs" / "rules").exists():
        raise CheckError("docs/rules/ is stale; frames live in the standards plugin")
    if (ROOT / "docs" / "agent-standards").exists():
        raise CheckError("docs/agent-standards/ is stale; frames live in the standards plugin")


def check_config() -> None:
    pin = load_json(STACK_PIN_PATH)
    session = {}
    if isinstance(pin, dict):
        registered = pin.get("registered")
        if isinstance(registered, dict) and isinstance(registered.get("session"), dict):
            session = registered["session"]
    config = load_toml(ROOT / ".codex" / "config.toml")
    if config.get("approval_policy") == "untrusted":
        raise CheckError("approval_policy=untrusted is retired")
    if config.get("approval_policy") != session.get("approval_policy", "never"):
        raise CheckError(
            'approval_policy must match stack-pin.registered.session ("never")'
        )
    if config.get("sandbox_mode") != session.get("sandbox_mode", "danger-full-access"):
        raise CheckError(
            'sandbox_mode must match stack-pin.registered.session ("danger-full-access")'
        )
    if config.get("allow_login_shell") is not True:
        raise CheckError("allow_login_shell must be true")
    if config.get("web_search") != session.get("web_search", "live"):
        raise CheckError('web_search must match stack-pin.registered.session ("live")')
    if config.get("check_for_update_on_startup") is not False:
        raise CheckError(
            "check_for_update_on_startup must be false; the CLI is pinned"
        )
    for key in ("developer_instructions", "compact_prompt"):
        want_markers = session.get(f"{key}_markers")
        if not want_markers:
            continue
        value = config.get(key)
        if not isinstance(value, str):
            raise CheckError(f"{key} must be a string (law: registered.session)")
        missing = [m for m in want_markers if m not in value]
        if missing:
            raise CheckError(f"{key} is missing pinned markers: {missing}")
    models = {}
    if isinstance(pin, dict) and isinstance(pin.get("models"), dict):
        models = pin["models"]
    if config.get("model") != models.get("primary", "gpt-6-astra"):
        raise CheckError('model must be "gpt-6-astra"')
    if config.get("review_model") != models.get("review_model", "gpt-5.6-sol"):
        raise CheckError('review_model must be "gpt-5.6-sol"')
    if config.get("model_reasoning_effort") != models.get("reasoning_effort", "xhigh"):
        raise CheckError('model_reasoning_effort must be "xhigh"')
    if config.get("model_context_window") != models.get("requested_context_window", 872_000):
        raise CheckError("model_context_window must be 872000")
    if config.get("model_auto_compact_token_limit") != models.get(
        "requested_auto_compact", 700_000
    ):
        raise CheckError("model_auto_compact_token_limit must be 700000")
    agents = config.get("agents")
    if not isinstance(agents, dict) or agents.get("enabled") is not False:
        raise CheckError("[agents].enabled must be false")
    if "max_concurrent_threads_per_session" in agents:
        raise CheckError("do not set max_concurrent_threads_per_session while agents are off")
    if "profiles" in config:
        raise CheckError(
            "project config must not define [profiles]; Codex 0.155.1 "
            "ignores project-local profiles. The sol profile is installed "
            "into the user config by install/modules/20-codex-cli"
        )
    codex_bin = Path.home() / ".local" / "bin" / "codex"
    user_cfg_path = Path.home() / ".codex" / "config.toml"
    sol_path = Path.home() / ".codex" / "sol.config.toml"
    if codex_bin.exists():
        if user_cfg_path.exists() and "sol" in load_toml(user_cfg_path).get(
            "profiles", {}
        ):
            raise CheckError(
                "legacy [profiles.sol] in ~/.codex/config.toml blocks --profile sol; run ./setup"
            )
        if not sol_path.exists():
            raise CheckError(
                "~/.codex/sol.config.toml missing; run ./setup"
            )
        sol = load_toml(sol_path)
        if sol.get("model") != models.get("secondary", "gpt-5.6-sol"):
            raise CheckError("sol.config.toml model must match models.secondary")
        if sol.get("model_reasoning_effort") != models.get("reasoning_effort", "xhigh"):
            raise CheckError("sol.config.toml model_reasoning_effort must match models.reasoning_effort")
        if sol.get("review_model") != models.get("review_model", "gpt-5.6-sol"):
            raise CheckError("sol.config.toml review_model must match models.review_model")
        if sol.get("model_context_window") != models.get("requested_context_window", 872_000):
            raise CheckError("sol.config.toml model_context_window must match models.requested_context_window")
        if sol.get("model_auto_compact_token_limit") != models.get(
            "requested_auto_compact", 700_000
        ):
            raise CheckError("sol.config.toml model_auto_compact_token_limit must match models.requested_auto_compact")
    if "default_permissions" in config:
        raise CheckError(
            "do not set default_permissions; session law is sandbox_mode "
            "danger-full-access"
        )
    if "sandbox_workspace_write" in config:
        raise CheckError("sandbox_workspace_write is unused under danger-full-access")
    if "ignore_user_and_project_exec_policy_rules" in config:
        raise CheckError(
            "ignore_user_and_project_exec_policy_rules is a CLI loader override, "
            "not a config.toml key; use codex exec --ignore-rules"
        )
    features = config.get("features")
    if not isinstance(features, dict):
        raise CheckError(".codex/config.toml [features] is required")
    for key in features:
        if str(key).startswith("web_search"):
            raise CheckError("use top-level web_search, not features.web_search*")
    network_proxy = features.get("network_proxy")
    if network_proxy is True or (
        isinstance(network_proxy, dict) and network_proxy.get("enabled") is True
    ):
        raise CheckError("features.network_proxy restricts YOLO; leave it off")
    if features.get("multi_agent") is not False:
        raise CheckError("features.multi_agent must be false")
    if features.get("multi_agent_v2") is not False:
        raise CheckError("features.multi_agent_v2 must be false")
    pin_features = {}
    if isinstance(pin, dict):
        registered = pin.get("registered")
        if isinstance(registered, dict) and isinstance(registered.get("features"), dict):
            pin_features = registered["features"]
    if features.get("hooks") is not pin_features.get("hooks", True):
        raise CheckError("features.hooks must match stack-pin.registered.features.hooks")
    if features.get("memories") is not pin_features.get("memories", False):
        raise CheckError("features.memories must match stack-pin.registered.features.memories")
    if "model_catalog_json" in config:
        raise CheckError("do not set model_catalog_json; remote catalog stays authoritative")
    plugins = config.get("plugins")
    if not isinstance(plugins, dict):
        raise CheckError(".codex/config.toml [plugins] is required")
    for plugin_id in (f"{name}@saint-tibo" for name in marketplace_names()):
        entry = plugins.get(plugin_id)
        if not isinstance(entry, dict) or entry.get("enabled") is not True:
            raise CheckError(f'.codex/config.toml must enable plugins."{plugin_id}"')
    mcp_spec: dict[str, object] = {}
    if isinstance(pin, dict):
        reg = pin.get("registered")
        if isinstance(reg, dict) and isinstance(reg.get("mcp_servers"), dict):
            mcp_spec = reg["mcp_servers"]
    expected_servers = {k for k in mcp_spec if k != "rule"}
    servers = config.get("mcp_servers")
    if not isinstance(servers, dict):
        raise CheckError(".codex/config.toml [mcp_servers] is required")
    if set(servers) != expected_servers:
        raise CheckError(
            f"mcp_servers must be exactly {sorted(expected_servers)} "
            f"(registered.mcp_servers), got {sorted(servers)}"
        )
    for name in expected_servers:
        spec = mcp_spec[name]
        want = {k: v for k, v in spec.items() if k != "note"} if isinstance(spec, dict) else {}
        got = servers.get(name)
        if got != want:
            raise CheckError(
                f'mcp_servers."{name}" must match registered.mcp_servers.{name} '
                "(minus the note field)"
            )
    rules_dir = ROOT / ".codex" / "rules"
    if rules_dir.is_dir():
        leftover = sorted(
            path.name
            for path in rules_dir.iterdir()
            if path.is_file() and path.suffix == ".rules"
        )
        if leftover:
            raise CheckError(
                "project .codex/rules/*.rules is execpolicy, not session law; "
                f"remove {', '.join(leftover)}"
            )


def check_custom_agents() -> None:
    agents_dir = ROOT / ".codex" / "agents"
    if not agents_dir.exists():
        return
    leftover = sorted(
        path.name for path in agents_dir.glob("*.toml") if path.is_file()
    )
    if leftover:
        raise CheckError(
            "do not add project .codex/agents/*.toml; spawn tools are off; "
            f"remove {', '.join(leftover)}"
        )


def check_portable_plugin(rel: str, expected_name: str) -> None:
    plugin = load_json(ROOT / rel)
    if not isinstance(plugin, dict):
        raise CheckError(f"{rel} must be an object")
    if plugin.get("$schema") != PLUGIN_SCHEMA:
        raise CheckError(f"{rel} must declare Agent Plugins 1.0.0 $schema")
    if plugin.get("name") != expected_name:
        raise CheckError(f"{rel} name must be {expected_name}")
    extra = set(plugin).difference(ROOT_PLUGIN_KEYS)
    if extra:
        raise CheckError(f"{rel} has non-portable root keys: {sorted(extra)}")
    for forbidden in ("skills", "interface", "mcpServers", "apps", "hooks"):
        if forbidden in plugin:
            raise CheckError(f"{rel} must not set root {forbidden}")


def check_marketplace_entry(entry: object, expected_name: str, dest: str) -> None:
    if not isinstance(entry, dict):
        raise CheckError("marketplace plugin entry must be an object")
    if entry.get("name") != expected_name:
        raise CheckError(f"marketplace plugin name must be {expected_name}")
    source = entry.get("source")
    if not isinstance(source, dict):
        raise CheckError("marketplace source must be an object")
    path = source.get("path")
    if not isinstance(path, str) or not path.startswith("./"):
        raise CheckError("marketplace source.path must start with ./")
    plugin_dir = (ROOT / path).resolve()
    if plugin_dir != (ROOT / dest).resolve():
        raise CheckError(f"marketplace source.path does not resolve to {dest}: {path}")
    policy = entry.get("policy")
    if not isinstance(policy, dict):
        raise CheckError("marketplace policy must be an object")
    if "installation" not in policy or "authentication" not in policy:
        raise CheckError("marketplace policy needs installation and authentication")
    if "category" not in entry:
        raise CheckError("marketplace entry needs category")


def check_plugin_cache_sync() -> None:
    codex_bin = Path.home() / ".local" / "bin" / "codex"
    if not codex_bin.exists():
        return
    cache_root = Path.home() / ".codex" / "plugins" / "cache" / "saint-tibo"
    for name in marketplace_names():
        repo_dir = ROOT / "plugins" / name
        version = load_json(repo_dir / "plugin.json").get("version", "")
        cache_dir = cache_root / name / str(version)
        if not cache_dir.is_dir():
            raise CheckError(
                f"plugin {name}@{version} not installed; run "
                f"codex plugin add {name}@saint-tibo"
            )
        repo_files = {
            p.relative_to(repo_dir): p
            for p in repo_dir.rglob("*")
            if p.is_file()
        }
        cache_files = {
            p.relative_to(cache_dir) for p in cache_dir.rglob("*") if p.is_file()
        }
        if set(repo_files) != cache_files:
            raise CheckError(
                f"plugin cache {name}@{version} file set differs from the repo; "
                f"re-run codex plugin add {name}@saint-tibo"
            )
        for rel, src in repo_files.items():
            cached = cache_dir / rel
            if hashlib.sha256(src.read_bytes()).digest() != hashlib.sha256(
                cached.read_bytes()
            ).digest():
                raise CheckError(
                    f"plugin cache {name}@{version} is stale at {rel}; "
                    f"re-run codex plugin add {name}@saint-tibo"
                )


def check_plugin_and_marketplace() -> None:
    names = marketplace_names()
    marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    if marketplace.get("name") != "saint-tibo":
        raise CheckError("marketplace name must be saint-tibo")
    for entry, name in zip(marketplace["plugins"], names, strict=True):
        check_marketplace_entry(entry, name, f"plugins/{name}")
        check_portable_plugin(f"plugins/{name}/plugin.json", name)


NESTED_AGENTS_TEMPLATES = frozenset(
    {
        "README.md",
        "web.md",
        "api.md",
        "mobile.md",
        "desktop.md",
        "telegram.md",
        "infra.md",
    }
)


def check_nested_templates() -> None:
    nested = ROOT / "plugins" / "hack-agent-standards" / "nested"
    if not nested.is_dir():
        raise CheckError("plugins/hack-agent-standards/nested/ is missing")
    got = {path.name for path in nested.iterdir() if path.is_file()}
    if got != NESTED_AGENTS_TEMPLATES:
        raise CheckError(
            "nested AGENTS templates must be "
            f"{sorted(NESTED_AGENTS_TEMPLATES)}, got {sorted(got)}"
        )


def check_skills() -> None:
    repo_skills = collect_skill_names(ROOT / ".agents" / "skills")
    expected_repo = {
        "repo-orientation",
        "quality-gate",
        "one-repo-workflow",
        "apply-stack-rule",
    }
    if set(repo_skills) != expected_repo:
        raise CheckError(f"repo skills must be {sorted(expected_repo)}, got {sorted(repo_skills)}")
    pin = load_json(STACK_PIN_PATH)
    if not isinstance(pin, dict):
        raise CheckError("build/stack-pin.json must be an object")
    registered = pin.get("registered")
    if not isinstance(registered, dict):
        raise CheckError("stack-pin.registered must be an object")
    listed = registered.get("repo_skills")
    if not isinstance(listed, list) or set(listed) != expected_repo:
        raise CheckError(
            "stack-pin.registered.repo_skills must match the repo skill set"
        )
    groups: dict[str, dict[str, Path]] = {".agents/skills": repo_skills}
    listed_all: list[str] = []
    for plugin_name in marketplace_names():
        key = plugin_key(plugin_name)
        skills_key = f"{key}_plugin_skills" if key else "plugin_skills"
        disk = collect_skill_names(ROOT / "plugins" / plugin_name / "skills")
        listed_plugin = registered.get(skills_key)
        if not isinstance(listed_plugin, list) or not listed_plugin:
            raise CheckError(
                f"stack-pin.registered.{skills_key} must be a non-empty list"
            )
        if any(not isinstance(name, str) or not name for name in listed_plugin):
            raise CheckError(f"{skills_key} must be non-empty strings")
        if len(listed_plugin) != len(set(listed_plugin)):
            raise CheckError(f"{skills_key} must be unique")
        if set(disk) != set(listed_plugin):
            raise CheckError(
                f"{plugin_name} plugin skills must match "
                f"stack-pin.registered.{skills_key}: "
                f"expected {sorted(listed_plugin)}, got {sorted(disk)}"
            )
        groups[f"plugins/{plugin_name}"] = disk
        listed_all.extend(listed_plugin)
    listed_standards = registered.get("standards_plugin_skills")
    if isinstance(listed_standards, list) and "apply-agent-standard" not in listed_standards:
        raise CheckError("standards_plugin_skills must include apply-agent-standard")
    seen: dict[str, Path] = {}
    for group in groups.values():
        for name, path in group.items():
            if name in seen:
                raise CheckError(
                    f"skill name collision {name}: {seen[name]} and {path}"
                )
            seen[name] = path
    agents = read_text(ROOT / "AGENTS.md")
    missing = [name for name in listed_all if name not in agents]
    if missing:
        raise CheckError(f"AGENTS.md must name plugin skills {missing}")


def check_hooks() -> None:
    pin = load_json(STACK_PIN_PATH)
    hooks_spec = pin.get("registered", {}).get("hooks")
    if not isinstance(hooks_spec, dict):
        raise CheckError("stack-pin.registered.hooks must be an object")
    hooks_path = ROOT / str(hooks_spec.get("file", ".codex/hooks.json"))
    if not hooks_path.is_file():
        raise CheckError(f"{hooks_spec.get('file')} is missing")
    try:
        hooks_doc = json.loads(hooks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckError(f"{hooks_path.relative_to(ROOT)} must parse: {exc}") from exc
    events = hooks_doc.get("hooks")
    if not isinstance(events, dict):
        raise CheckError(".codex/hooks.json must carry a hooks object")
    expected_events = set(hooks_spec.get("events", []))
    if set(events) != expected_events:
        raise CheckError(
            f".codex/hooks.json events must be {sorted(expected_events)}, "
            f"got {sorted(events)}"
        )
    scripts = {str(s) for s in hooks_spec.get("scripts", [])}
    seen_scripts: set[str] = set()
    for event, groups in events.items():
        if not isinstance(groups, list) or not groups:
            raise CheckError(f"hooks.{event} must be a non-empty list")
        for group in groups:
            for hook in (group or {}).get("hooks", []):
                command = str(hook.get("command", ""))
                match = re.search(r"(\.codex/hooks/[^\"'\s)]+)", command)
                if not match:
                    raise CheckError(
                        f"hooks.{event} command must reference .codex/hooks/: {command}"
                    )
                script = match.group(1)
                if script not in scripts:
                    raise CheckError(f"hook script {script} not in registered.hooks.scripts")
                seen_scripts.add(script)
                script_path = ROOT / script
                if not script_path.is_file():
                    raise CheckError(f"hook script {script} is missing")
                py_compile(str(script_path))
    if seen_scripts != scripts:
        raise CheckError(
            f"registered.hooks.scripts unused: {sorted(scripts - seen_scripts)}"
        )
    # 0.155.1 names the exec tool `exec_command` for PreToolUse (tool_input
    # carries `cmd`); `Bash` is only the PostToolUse normalization. A matcher
    # without `exec_command` never fires on shell calls — dead guard.
    for tool_event in ("PreToolUse", "PostToolUse"):
        matchers = [
            str(group.get("matcher") or "") for group in events.get(tool_event, [])
        ]
        if not any(
            "exec_command" in m.split("|") or m in ("", "*") for m in matchers
        ):
            raise CheckError(
                f"hooks.{tool_event} matcher must cover exec_command "
                f"(0.155.1 exec tool name); got {matchers}"
            )
    if "SubagentStart" in events or "SubagentStop" in events:
        raise CheckError(
            "subagent hooks are banned: agents are disabled and lazy-mode "
            "injection biases reviewer subagents (openai/codex-style #502)"
        )
    repair = pin.get("registered", {}).get("repair")
    if not isinstance(repair, dict):
        raise CheckError("stack-pin.registered.repair must be an object")
    repair_script = ROOT / str(repair.get("script", "scripts/repair_setup.py"))
    if not repair_script.is_file():
        raise CheckError(f"repair script missing: {repair.get('script')}")
    py_compile(str(repair_script))
    recipe = str(repair.get("justfile_recipe", "repair"))
    if not re.search(rf"(?m)^{re.escape(recipe)}:\s*$", read_text(ROOT / "justfile")):
        raise CheckError(f"justfile must carry a `{recipe}:` recipe")
    deploy = pin.get("registered", {}).get("deploy")
    if not isinstance(deploy, dict):
        raise CheckError("stack-pin.registered.deploy must be an object")
    for rel in deploy.get("kit", []):
        kit_path = ROOT / str(rel)
        if not kit_path.is_file():
            raise CheckError(f"deploy kit missing: {rel}")
        if str(rel).endswith(".sh"):
            result = subprocess.run(
                ["sh", "-n", str(kit_path)], capture_output=True, text=True
            )
            if result.returncode != 0:
                raise CheckError(f"{rel} fails sh -n: {result.stderr.strip()}")


def py_compile(script_path: str) -> None:
    import py_compile as _py_compile

    try:
        _py_compile.compile(script_path, doraise=True)
    except _py_compile.PyCompileError as exc:
        raise CheckError(f"{script_path} must compile: {exc}") from exc


def main() -> int:
    checks = (
        check_pin,
        check_stack_pin,
        check_bootstrap,
        check_agents_md,
        check_config,
        check_custom_agents,
        check_plugin_and_marketplace,
        check_plugin_cache_sync,
        check_skills,
        check_nested_templates,
        check_hooks,
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
    # Proof level 1 (artifact): pin == config == docs == generated files.
    # Installed proof is `./setup --status`; live/capability proof needs a
    # real Codex session (trust, hooks, MCP) — this check cannot claim it.
    print("PASS [artifact] Codex 0.155.1 project artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
