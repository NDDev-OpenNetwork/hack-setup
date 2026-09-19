import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_stack  # noqa: E402


def test_extract_version_common_tools() -> None:
    assert check_stack.extract_version("v24.21.0\n", r"v?([0-9]+(?:\.[0-9]+)*)") == "24.21.0"
    assert check_stack.extract_version("1.4.2\n", r"([0-9]+(?:\.[0-9]+)*)") == "1.4.2"
    assert (
        check_stack.extract_version("Python 3.14.7\n", r"Python\s+([0-9]+(?:\.[0-9]+)*)")
        == "3.14.7"
    )
    assert (
        check_stack.extract_version(
            "uv 0.12.17 (635500036 2026-09-18 aarch64-apple-darwin)\n",
            r"uv\s+([0-9]+(?:\.[0-9]+)*)",
        )
        == "0.12.17"
    )
    assert (
        check_stack.extract_version("codex-cli 0.155.1\n", r"codex-cli\s+([0-9]+(?:\.[0-9]+)*)")
        == "0.155.1"
    )
    assert check_stack.extract_version("nope", r"v?([0-9]+(?:\.[0-9]+)*)") is None


def test_standard_lists_core_pins() -> None:
    stack = check_stack.load_json(check_stack.STACK_PIN_PATH)
    codex = check_stack.load_json(check_stack.CODEX_PIN_PATH)
    probes = check_stack.load_probes(stack, codex)
    text = check_stack.render_standard(stack, probes)
    for needle in (
        "`runtimes.node`",
        "`24.21.0`",
        "`frontend.react`",
        "`frontend.vite`",
        "`backend.fastapi`",
        "`ai.openai`",
        "`2.9.0`",
        "`clients.flutter`",
        "`3.47.5`",
        "telegram",
        "7.4.1",
    ):
        assert needle in text, needle


def test_check_stack_doctor_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_stack.py")],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "PASS required host tools match the pin" in result.stdout
    assert "node" in result.stdout
    assert "24.21.0" in result.stdout


def _probe(kind: str, probe_id: str, status: str, expected: str = "1.0.0") -> check_stack.ProbeResult:
    probe = check_stack.Probe(kind, probe_id, "stack-pin.json", "x", probe_id, ("--version",), "x", expected)
    return check_stack.ProbeResult(probe, status, "0.9.0" if status == "DRIFT" else expected, "/bin/" + probe_id)


def test_doctor_decision_required_and_strict() -> None:
    required_ok = _probe("required", "node", "OK", "24.21.0")
    declared_drift = _probe("declared", "rustc", "DRIFT", "1.98.1")
    declared_missing = _probe("declared", "docker", "MISSING", "29.8.1")
    code, messages = check_stack.doctor_decision([required_ok, declared_drift], strict=False)
    assert code == 0
    assert any("PASS required" in item for item in messages)
    code, messages = check_stack.doctor_decision([required_ok, declared_drift], strict=True)
    assert code == 1
    assert any("FAIL --strict" in item for item in messages)
    code, _ = check_stack.doctor_decision([required_ok, declared_missing], strict=True)
    assert code == 1
    required_bad = _probe("required", "node", "DRIFT", "24.21.0")
    code, messages = check_stack.doctor_decision([required_bad], strict=False)
    assert code == 1
    assert any("FAIL required" in item for item in messages)
