#!/bin/sh
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"

run_verify() {
  require_cmd python3
  python3 "$HACK_REPO_ROOT/scripts/check_codex_setup.py"
  python3 "$HACK_REPO_ROOT/scripts/check_stack.py"
}

case "${1:-status}" in
  install | status)
    run_verify
    ;;
  dry-run)
    log "would run python3 scripts/check_codex_setup.py and python3 scripts/check_stack.py"
    ;;
  *)
    die "unknown action: $1"
    ;;
esac
