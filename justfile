set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# List recipes
default:
    @just --list

# Install numbered modules
setup:
    ./setup

# Planned work, no downloads
dry-run:
    ./setup --dry-run

# Check without installing
status:
    ./setup --status

# Proof: pin == config == AGENTS == generated standard
check:
    python3 scripts/check_codex_setup.py
    python3 scripts/check_stack.py

alias doctor := check

# AGENTS four-command ready gate
gate:
    ./setup --status
    python3 scripts/check_codex_setup.py
    python3 scripts/check_stack.py
    codex --version

# Print generated stack standard
stack:
    python3 scripts/check_stack.py --list

# Hackathon-day live pin drift (network)
reverify:
    python3 scripts/reverify_stack_pin.py

# Repo tests
test:
    pytest -q
