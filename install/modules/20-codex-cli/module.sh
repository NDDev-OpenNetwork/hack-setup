#!/bin/sh
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"
# shellcheck source=../../lib/download.sh
. "$HACK_LIB/download.sh"

PIN_PATH="$HACK_REPO_ROOT/build/codex-pin.json"

pin_field() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["installer"][sys.argv[2]])' "$PIN_PATH" "$1"
}

cli_version() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["codex_cli"])' "$PIN_PATH"
}

binary_version() {
  path="$1"
  [ -x "$path" ] || return 1
  "$path" --version 2>/dev/null | awk '{ if (NF >= 2) print $2; else print $1; exit }'
}

already_pinned() {
  wanted="$(cli_version)"
  for candidate in "$HACK_LOCAL_BIN/codex" "${HOME}/.local/bin/codex"; do
    got="$(binary_version "$candidate" || true)"
    if [ "$got" = "$wanted" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

link_repo_bin() {
  source_bin="$1"
  dest="$HACK_LOCAL_BIN/codex"
  mkdir -p "$HACK_LOCAL_BIN"
  if [ "$source_bin" = "$dest" ]; then
    return 0
  fi
  ln -sfn "$source_bin" "$dest"
}

run_status() {
  wanted="$(cli_version)"
  if found="$(already_pinned)"; then
    log "Codex CLI $wanted already at $found"
    return 0
  fi
  die "Codex CLI $wanted is not installed; run ./setup"
}

run_install() {
  wanted="$(cli_version)"
  if found="$(already_pinned)"; then
    link_repo_bin "$found"
    log "Codex CLI $wanted already present; linked $HACK_LOCAL_BIN/codex"
    return 0
  fi

  mkdir -p "$HACK_CACHE"
  installer_url="$(pin_field url)"
  installer_sha="$(pin_field sha256)"
  installer_path="$HACK_CACHE/codex-official-install.sh"

  log "downloading official install.sh for $wanted"
  hack_download "$installer_url" "$installer_path"
  hack_verify_sha256 "$installer_path" "$installer_sha"

  user_bin="${HOME}/.local/bin"
  mkdir -p "$user_bin"
  log "running official installer (CODEX_RELEASE=$wanted)"
  CODEX_RELEASE="$wanted" \
    CODEX_NON_INTERACTIVE=1 \
    CODEX_INSTALLER_USE_RELEASES_OPENAI_COM=false \
    CODEX_INSTALL_DIR="$user_bin" \
    sh "$installer_path"

  got="$(binary_version "$user_bin/codex" || true)"
  [ "$got" = "$wanted" ] || die "installed Codex reported $got, expected $wanted"
  link_repo_bin "$user_bin/codex"
  log "Codex CLI $wanted installed"
}

run_dry_run() {
  wanted="$(cli_version)"
  url="$(pin_field url)"
  sha="$(pin_field sha256)"
  log "would verify $url"
  log "would require sha256 $sha"
  log "would run official installer with CODEX_RELEASE=$wanted on $HACK_PLATFORM"
}

case "${1:-status}" in
  install) run_install ;;
  status) run_status ;;
  dry-run) run_dry_run ;;
  *) die "unknown action: $1" ;;
esac
