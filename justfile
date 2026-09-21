set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# List recipes
default:
    @just --list

# Install numbered modules (args pass through: just setup --member ivan)
[unix]
setup *args:
    ./setup {{args}}

[windows]
setup *args:
    powershell -NoProfile -ExecutionPolicy Bypass -File ./setup.ps1 {{args}}

# Planned work, no downloads
[unix]
dry-run:
    ./setup --dry-run

[windows]
dry-run:
    powershell -NoProfile -ExecutionPolicy Bypass -File ./setup.ps1 --dry-run

# Check without installing
[unix]
status:
    ./setup --status

[windows]
status:
    powershell -NoProfile -ExecutionPolicy Bypass -File ./setup.ps1 --status

# Proof: pin == config == AGENTS == generated standard
[unix]
check:
    python3 scripts/check_codex_setup.py
    python3 scripts/check_stack.py

[windows]
check:
    python scripts/check_codex_setup.py
    python scripts/check_stack.py

alias doctor := check

# Diagnose the setup, auto-fix safe drift (plugin cache, notify, state files)
[unix]
repair:
    python3 scripts/repair_setup.py

[windows]
repair:
    python scripts/repair_setup.py

# AGENTS four-command ready gate
[unix]
gate:
    ./setup --status
    python3 scripts/check_codex_setup.py
    python3 scripts/check_stack.py
    codex --version

[windows]
gate:
    powershell -NoProfile -ExecutionPolicy Bypass -File ./setup.ps1 --status
    python scripts/check_codex_setup.py
    python scripts/check_stack.py
    codex --version

# Print generated stack standard
stack:
    python3 scripts/check_stack.py --list

# Hackathon-day live pin drift (network)
reverify:
    python3 scripts/reverify_stack_pin.py

# Live proof: real Serena MCP handshake + activation + symbol + memory.
# Needs uvx + network; slower than check — not part of `gate`.
live:
    python3 scripts/verify_serena.py

# Repo tests
test:
    pytest -q
