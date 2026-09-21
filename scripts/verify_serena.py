#!/usr/bin/env python3
"""Live/capability proof for the Serena MCP (issue #2) — not artifact
level. Starts the pinned server over stdio JSON-RPC and proves the
chain Codex actually uses: handshake -> activate_project -> list tools
-> find_symbol on a real file (requires the python_ty analyzer to be
up, pinned via ls_specific_settings.python_ty.ty_version) ->
list_memories / read+write+delete a probe memory.

Usage: python3 scripts/verify_serena.py   (network + uvx required)
Exit 0 = PASS [live]; nonzero = FAIL with the failing step.
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / "build" / "stack-pin.json").read_text())
SERENA = PIN["mcp"]["serena"]["version"]

CMD = [
    "uvx", "--from", f"serena-agent=={SERENA}",
    "serena", "start-mcp-server",
    "--context", "codex",
    "--open-web-dashboard", "false",
]

TIMEOUT = 240  # uvx resolve + LS startup can be slow on a cold cache


class Mcp:
    """Minimal stdio JSON-RPC client: newline-delimited messages."""

    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, cwd=ROOT,
        )
        self._id = 0
        self._responses: dict[int, dict] = {}
        self._lock = threading.Condition()
        self._reader = threading.Thread(target=self._read, daemon=True)
        self._reader.start()

    def _read(self) -> None:
        assert self.proc.stdout
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "id" in msg and ("result" in msg or "error" in msg):
                with self._lock:
                    self._responses[msg["id"]] = msg
                    self._lock.notify_all()

    def call(self, method: str, params: dict | None = None,
             timeout: float = TIMEOUT) -> dict:
        self._id += 1
        rid = self._id
        req = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            req["params"] = params
        assert self.proc.stdin
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        deadline = time.time() + timeout
        with self._lock:
            while rid not in self._responses:
                left = deadline - time.time()
                if left <= 0:
                    raise TimeoutError(f"{method}: no response in {timeout}s")
                self._lock.wait(left)
        msg = self._responses.pop(rid)
        if "error" in msg:
            raise RuntimeError(f"{method}: {msg['error']}")
        result = msg["result"]
        # MCP tool errors arrive as a 200 result with isError — a failed
        # tools/call must not look like a pass.
        if method == "tools/call" and result.get("isError"):
            raise RuntimeError(f"tool isError: {tool_text(result)[:300]}")
        return result

    def notify(self, method: str) -> None:
        assert self.proc.stdin
        self.proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": method}) + "\n"
        )
        self.proc.stdin.flush()

    def close(self) -> None:
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()


def tool_text(result: dict) -> str:
    parts = result.get("content") or []
    return "\n".join(str(p.get("text", "")) for p in parts if isinstance(p, dict))


def main() -> int:
    print(f"verify-serena: serena-agent=={SERENA} over stdio MCP")
    mcp = Mcp()
    try:
        res = mcp.call("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "hack-setup-verify", "version": "0"},
        })
        server = (res.get("serverInfo") or {}).get("name", "?")
        print(f"  handshake OK — server={server}")

        mcp.notify("notifications/initialized")

        tools = mcp.call("tools/list")
        names = {t.get("name") for t in tools.get("tools", [])}
        need = {"activate_project", "find_symbol", "list_memories",
                "read_memory", "write_memory", "delete_memory"}
        missing = need - names
        if missing:
            raise RuntimeError(f"missing tools: {sorted(missing)}")
        print(f"  tools/list OK — {len(names)} tools, required present")

        res = mcp.call("tools/call", {
            "name": "activate_project",
            "arguments": {"project": str(ROOT)},
        })
        print("  activate_project OK")

        # Capability proof: symbol resolution through python_ty — an
        # LS-backed op, not a file read.
        res = mcp.call("tools/call", {
            "name": "find_symbol",
            "arguments": {
                "name_path": "pinned_version",
                "relative_path": "scripts/repair_setup.py",
            },
        })
        text = tool_text(res)
        if "pinned_version" not in text:
            raise RuntimeError(f"find_symbol returned no symbol: {text[:200]}")
        print("  find_symbol OK — python_ty resolved pinned_version()")

        res = mcp.call("tools/call", {"name": "list_memories", "arguments": {}})
        print(f"  list_memories OK — {tool_text(res)[:80].strip()}")

        mcp.call("tools/call", {"name": "write_memory", "arguments": {
            "memory_name": "_verify_probe",
            "content": "capability probe — safe to delete"}})
        read = mcp.call("tools/call", {"name": "read_memory", "arguments": {
            "memory_name": "_verify_probe"}})
        if "capability probe" not in tool_text(read):
            raise RuntimeError(f"read_memory mismatch: {tool_text(read)[:200]}")
        mcp.call("tools/call", {"name": "delete_memory", "arguments": {
            "memory_name": "_verify_probe"}})
        probe = ROOT / ".serena" / "memories" / "_verify_probe.md"
        if probe.exists():
            raise RuntimeError("delete_memory left _verify_probe.md behind")
        print("  memory write/read/delete OK")

        print("PASS [live] serena MCP handshake + activation + symbol + memory")
        return 0
    except Exception as exc:
        print(f"FAIL [live] verify_serena: {exc}", file=sys.stderr)
        return 1
    finally:
        mcp.close()


if __name__ == "__main__":
    sys.exit(main())
