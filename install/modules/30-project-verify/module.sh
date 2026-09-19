#!/bin/sh
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"

run_verify() {
  require_cmd python3
  python3 "$HACK_REPO_ROOT/scripts/check_codex_setup.py"
  if [ -x "$HACK_LOCAL_BIN/codex" ]; then
    "$HACK_LOCAL_BIN/codex" --version
  elif command -v codex >/dev/null 2>&1; then
    codex --version
  else
    die "codex is not on PATH; source install/env.sh after ./setup"
  fi
}

case "${1:-status}" in
  install | status)
    run_verify
    ;;
  dry-run)
    log "would run python3 scripts/check_codex_setup.py and codex --version"
    ;;
  *)
    die "unknown action: $1"
    ;;
esac
