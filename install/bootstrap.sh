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
HACK_MEMBER="${HACK_MEMBER:-}"
HACK_TARGET_OS="${HACK_TARGET_OS:-}"

# shellcheck source=lib/common.sh
. "$HACK_LIB/common.sh"
# shellcheck source=lib/os.sh
. "$HACK_LIB/os.sh"
# shellcheck source=lib/download.sh
. "$HACK_LIB/download.sh"

usage() {
  cat <<EOF
Usage: ./setup [--dry-run] [--status] [--print-env]
              [--member <danil|ivan|artem>] [--os <macos|ubuntu|windows>]

Clone the repo, then run ./setup. Modules live under install/modules/.
--member sets git identity + team defaults for that member (bare
--danil/--ivan/--artem works too). --os declares the install target:
it must match this host, except under --dry-run where it previews the
plan for that OS (windows installs run .\setup.ps1 on the Windows host).
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) HACK_DRY_RUN=1 ;;
    --status) HACK_ACTION="status" ;;
    --member)
      [ "$#" -ge 2 ] || die "--member needs a name (danil|ivan|artem)"
      HACK_MEMBER="$2"
      shift
      ;;
    --member=*) HACK_MEMBER="${1#--member=}" ;;
    --danil | --ivan | --artem) HACK_MEMBER="${1#--}" ;;
    --os)
      [ "$#" -ge 2 ] || die "--os needs a value (macos|ubuntu|windows)"
      HACK_TARGET_OS="$2"
      shift
      ;;
    --os=*) HACK_TARGET_OS="${1#--os=}" ;;
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

export HACK_INSTALL_HOME HACK_REPO_ROOT HACK_LIB HACK_CACHE HACK_LOCAL_BIN HACK_DRY_RUN HACK_ACTION HACK_MEMBER HACK_TARGET_OS
# Modules install into repo/.local/bin, ~/.local/bin, ~/.bun/bin — put them
# on PATH *before* the module loop so module 30/40 see what earlier
# modules installed (fresh-host order; HS-04).
export PATH="$HACK_LOCAL_BIN:${HOME}/.local/bin:${HOME}/.bun/bin:$PATH"

hack_detect_os

# --os declares the install target. POSIX bootstrap covers darwin/linux
# only: a windows target belongs to .\setup.ps1 on the Windows host.
# Under --dry-run the flag instead previews that platform's plan.
case "$HACK_TARGET_OS" in
  "") ;;
  macos | mac | darwin)
    HACK_TARGET_FAMILY="darwin"
    HACK_TARGET_PLATFORM="darwin-arm64"
    HACK_TARGET_TRIPLE="aarch64-apple-darwin"
    ;;
  ubuntu | linux)
    HACK_TARGET_FAMILY="linux"
    HACK_TARGET_PLATFORM="linux-x86_64"
    HACK_TARGET_TRIPLE="x86_64-unknown-linux-musl"
    ;;
  windows | win)
    HACK_TARGET_FAMILY="windows"
    HACK_TARGET_PLATFORM="windows-x86_64"
    HACK_TARGET_TRIPLE="x86_64-pc-windows-msvc"
    ;;
  *) die "unknown --os $HACK_TARGET_OS (expected macos|ubuntu|windows)" ;;
esac
if [ -n "$HACK_TARGET_OS" ]; then
  if [ "$HACK_TARGET_FAMILY" != "$HACK_OS" ]; then
    # Family mismatch: a POSIX bootstrap cannot install another family.
    if [ "$HACK_DRY_RUN" != "1" ]; then
      case "$HACK_TARGET_FAMILY" in
        windows) die "--os windows is native: run powershell -File .\setup.ps1 on the Windows host (WSL2 users run ./setup inside Ubuntu)" ;;
        *) die "--os $HACK_TARGET_OS targets $HACK_TARGET_FAMILY; this host is $HACK_OS — run ./setup on that host" ;;
      esac
    fi
    HACK_PLATFORM="$HACK_TARGET_PLATFORM"
    HACK_TRIPLE="$HACK_TARGET_TRIPLE"
    log "dry-run preview for $HACK_TARGET_PLATFORM (this host is $HACK_OS)"
  fi
fi

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
