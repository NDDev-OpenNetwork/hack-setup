#!/bin/sh
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"

check_python() {
  require_cmd python3
  python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' \
    || die "python3 3.11+ is required"
}

run_status() {
  require_cmd tar
  require_cmd git
  command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 \
    || die "curl or wget is required"
  command -v sha256sum >/dev/null 2>&1 || command -v shasum >/dev/null 2>&1 \
    || die "sha256sum or shasum is required"
  command -v gh >/dev/null 2>&1 \
    || die "gh (GitHub CLI) is required for the github-first workflow; install it and run gh auth login"
  check_python
  log "prereqs ok (python3 $(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'))"
}

case "${1:-status}" in
  install | status)
    run_status
    ;;
  dry-run)
    log "would require tar, git, gh, curl|wget, sha256sum|shasum, python3>=3.11"
    ;;
  *)
    die "unknown action: $1"
    ;;
esac
