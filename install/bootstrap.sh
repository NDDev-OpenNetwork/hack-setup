#!/bin/sh
# One-command macOS/Linux bootstrap. Discovers install/modules/<nn>-* in order.

set -eu

HACK_INSTALL_HOME="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
HACK_REPO_ROOT="$(CDPATH= cd -- "$HACK_INSTALL_HOME/.." && pwd)"
HACK_LIB="$HACK_INSTALL_HOME/lib"
HACK_CACHE="${HACK_CACHE:-$HACK_REPO_ROOT/.cache/install}"
HACK_LOCAL_BIN="${HACK_LOCAL_BIN:-$HACK_REPO_ROOT/.local/bin}"
HACK_DRY_RUN="${HACK_DRY_RUN:-0}"
HACK_ACTION="install"

# shellcheck source=lib/common.sh
. "$HACK_LIB/common.sh"
# shellcheck source=lib/os.sh
. "$HACK_LIB/os.sh"
# shellcheck source=lib/download.sh
. "$HACK_LIB/download.sh"

usage() {
  cat <<EOF
Usage: ./setup [--dry-run] [--status] [--print-env]

Clone the repo, then run ./setup. Modules live under install/modules/.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) HACK_DRY_RUN=1 ;;
    --status) HACK_ACTION="status" ;;
    --print-env)
      printf 'export PATH="%s:%s:${PATH}"\n' "$HACK_LOCAL_BIN" "${HOME}/.local/bin"
      exit 0
      ;;
    --help | -h)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
  shift
done

export HACK_INSTALL_HOME HACK_REPO_ROOT HACK_LIB HACK_CACHE HACK_LOCAL_BIN HACK_DRY_RUN HACK_ACTION
# Modules install into repo/.local/bin, ~/.local/bin, ~/.bun/bin — put them
# on PATH *before* the module loop so module 30/40 see what earlier
# modules installed (fresh-host order; HS-04).
export PATH="$HACK_LOCAL_BIN:${HOME}/.local/bin:${HOME}/.bun/bin:$PATH"

hack_detect_os
log "platform $HACK_PLATFORM ($HACK_TRIPLE)"
log "repo $HACK_REPO_ROOT"

if [ "$HACK_DRY_RUN" = "1" ]; then
  log "dry-run; no downloads"
fi

set -- "$HACK_INSTALL_HOME/modules"/[0-9][0-9]-*
if [ ! -d "$1" ]; then
  die "no install/modules/<nn>-* directories found"
fi

for module_dir in "$@"; do
  [ -d "$module_dir" ] || continue
  [ -f "$module_dir/disabled" ] && continue
  [ -f "$module_dir/module.sh" ] || die "missing $module_dir/module.sh"
  module_id="$(basename "$module_dir")"
  log "module $module_id ($HACK_ACTION)"
  if [ "$HACK_DRY_RUN" = "1" ] && [ "$HACK_ACTION" = "install" ]; then
    sh "$module_dir/module.sh" dry-run
  else
    sh "$module_dir/module.sh" "$HACK_ACTION"
  fi
done

if [ "$HACK_ACTION" = "install" ] && [ "$HACK_DRY_RUN" != "1" ]; then
  log "done. load PATH: . $HACK_INSTALL_HOME/env.sh"
fi
