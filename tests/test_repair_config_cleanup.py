"""fix_config_cleanup regression (issue #1): legacy managed lines are
stripped while per-checkout [hooks.state] tables — ours AND foreign —
and sibling-writer entries (notify, hook-trust header) are preserved, so
the repair pipeline converges instead of ping-ponging."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "repair_setup", ROOT / "scripts" / "repair_setup.py"
)
repair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repair)

OWN_HOOKS = str((ROOT / ".codex" / "hooks.json").resolve())
FOREIGN = "/Users/other/dev/vibestrap/.codex/hooks.json"

CONFIG = f"""\
# hack-setup: notify
notify = ["{ROOT}/install/notify.sh"]  # hack-setup
approval_policy = "never"
trusted_hash = "sha256:orphan"  # hack-setup

# hack-setup: stale legacy header
# hack-setup: hook trust
[hooks.state."{OWN_HOOKS}:session_start:0:0"]  # hack-setup
trusted_hash = "sha256:aaa"  # hack-setup

[hooks.state."{FOREIGN}:session_start:0:0"]
trusted_hash = "sha256:fff"  # hack-setup

[[servers.extra]]
name = "kept"  # array-of-tables after a managed block must survive

[profiles.sol]
model = "old"

[mcp_servers.serena]
command = "uvx"
"""


def _run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    home = tmp_path / ".codex"
    home.mkdir()
    cfg = home / "config.toml"
    cfg.write_text(CONFIG)
    monkeypatch.setenv("CODEX_HOME", str(home))
    repair.fix_config_cleanup()
    return cfg.read_text()


def test_foreign_hook_table_survives(tmp_path, monkeypatch):
    out = _run(tmp_path, monkeypatch)
    assert f'[hooks.state."{FOREIGN}:session_start:0:0"]' in out
    assert 'trusted_hash = "sha256:fff"  # hack-setup' in out


def test_own_hook_table_preserved_for_hook_trust(tmp_path, monkeypatch):
    out = _run(tmp_path, monkeypatch)
    assert f'[hooks.state."{OWN_HOOKS}:session_start:0:0"]' in out
    assert 'trusted_hash = "sha256:aaa"' in out
    assert "# hack-setup: hook trust" in out


def test_array_of_tables_and_foreign_keys_survive(tmp_path, monkeypatch):
    out = _run(tmp_path, monkeypatch)
    assert '[[servers.extra]]' in out
    assert 'name = "kept"' in out
    assert '[mcp_servers.serena]' in out
    assert 'approval_policy = "never"' in out


def test_only_orphans_and_legacy_removed(tmp_path, monkeypatch):
    out = _run(tmp_path, monkeypatch)
    assert "[profiles.sol]" not in out
    assert "# hack-setup: stale legacy header" not in out
    assert "sha256:orphan" not in out
    # managed notify entry + its header belong to fix_notify_block
    assert "# hack-setup: notify" in out
    assert "notify =" in out


def test_idempotent(tmp_path, monkeypatch):
    _run(tmp_path, monkeypatch)
    cfg = tmp_path / ".codex" / "config.toml"
    first = cfg.read_text()
    repair.RESULTS.clear()
    repair.fix_config_cleanup()
    assert cfg.read_text() == first
