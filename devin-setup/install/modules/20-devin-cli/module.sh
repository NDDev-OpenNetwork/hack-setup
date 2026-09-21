#!/bin/sh
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"
# shellcheck source=../../lib/download.sh
. "$HACK_LIB/download.sh"

PIN_PATH="$HACK_REPO_ROOT/build/devin-pin.json"

pin_field() {
  hack_pin_get "$PIN_PATH" "$1"
}

devin_version() { pin_field devin_cli.version; }
herdr_version() { pin_field herdr.version; }

herdr_pkg_field() {
  python3 -c 'import json,sys
pin=json.load(open(sys.argv[1]))
print(pin["herdr"]["packages"][sys.argv[2]][sys.argv[3]])' \
    "$PIN_PATH" "$HACK_PLATFORM" "$1"
}

binary_version() {
  path="$1"
  [ -x "$path" ] || return 1
  "$path" --version 2>/dev/null | awk '{ if (NF >= 2) print $2; else print $1; exit }'
}

devin_ok() {
  wanted="$(devin_version)"
  for candidate in "$HACK_LOCAL_BIN/devin" "${HOME}/.local/bin/devin"; do
    [ "$(binary_version "$candidate" || true)" = "$wanted" ] && {
      printf '%s\n' "$candidate"; return 0; }
  done
  return 1
}

herdr_ok() {
  wanted="$(herdr_version)"
  for candidate in "$HACK_LOCAL_BIN/herdr" "${HOME}/.local/bin/herdr"; do
    [ "$(binary_version "$candidate" || true)" = "$wanted" ] && {
      printf '%s\n' "$candidate"; return 0; }
  done
  return 1
}

link_repo_bin() {
  source_bin="$1"
  dest="$HACK_LOCAL_BIN/$(basename "$source_bin")"
  mkdir -p "$HACK_LOCAL_BIN"
  [ "$source_bin" = "$dest" ] || ln -sfn "$source_bin" "$dest"
}

ensure_user_config() {
  # Managed block in ~/.config/devin/config.json: agent.model,
  # subagents_enabled=false, auto_update=false, read_config_from off.
  # repair_devin_setup.py is the single writer (same pattern as codex).
  command -v python3 >/dev/null 2>&1 || return 0
  python3 "${HACK_REPO_ROOT}/scripts/repair_devin_setup.py" --only user-config \
    || log "WARN: user-config repair failed"
}

ensure_devin() {
  wanted="$(devin_version)"
  if found="$(devin_ok)"; then
    link_repo_bin "$found"
    log "Devin CLI $wanted already present"
    return 0
  fi
  url="$(pin_field devin_cli.install_sh)"
  installer="$HACK_CACHE/devin-setup-$wanted.sh"
  mkdir -p "$HACK_CACHE" "${HOME}/.local/bin"
  # The setup script is versioned by URL (static.devin.ai/cli/<ver>/) —
  # no published sha; the installer itself fetches the versioned binary.
  log "downloading pinned Devin installer for $wanted"
  hack_download "$url" "$installer"
  # bash, not sh: the script starts with `set -o pipefail` (dash dies).
  # Its last line launches `devin setup` — the interactive login wizard.
  # Auth is a per-member step and CI has no TTY, so strip the tail;
  # the version check below is the install proof.
  grep -vF '"$VERSION_DIR/bin/$COMPILED_BIN_NAME" setup' "$installer" \
    > "$installer.run"
  bash "$installer.run" </dev/null \
    || log "installer tail nonzero (interactive setup skipped); verifying binary"
  got="$(binary_version "${HOME}/.local/bin/devin" || true)"
  [ "$got" = "$wanted" ] || die "installed Devin reported $got, expected $wanted"
  link_repo_bin "${HOME}/.local/bin/devin"
  log "Devin CLI $wanted installed"
}

ensure_herdr() {
  wanted="$(herdr_version)"
  if found="$(herdr_ok)"; then
    link_repo_bin "$found"
    log "herdr $wanted already present"
    return 0
  fi
  asset="$(herdr_pkg_field asset)"
  sha="$(herdr_pkg_field sha256)"
  tag="$(pin_field herdr.tag)"
  repo="$(pin_field herdr.repo)"
  url="https://github.com/$repo/releases/download/$tag/$asset"
  archive="$HACK_CACHE/$asset"
  mkdir -p "$HACK_CACHE" "${HOME}/.local/bin"
  log "downloading herdr $asset ($wanted)"
  hack_download "$url" "$archive"
  hack_verify_sha256 "$archive" "$sha"
  case "$asset" in
    *.zip)
      unzip -o -q "$archive" -d "$HACK_CACHE/herdr-$wanted"
      cp "$HACK_CACHE/herdr-$wanted/herdr" "${HOME}/.local/bin/herdr"
      ;;
    *)
      cp "$archive" "${HOME}/.local/bin/herdr"
      ;;
  esac
  chmod +x "${HOME}/.local/bin/herdr"
  got="$(binary_version "${HOME}/.local/bin/herdr" || true)"
  [ "$got" = "$wanted" ] || die "installed herdr reported $got, expected $wanted"
  link_repo_bin "${HOME}/.local/bin/herdr"
  log "herdr $wanted installed"
}

ensure_integration() {
  # `herdr integration install devin` writes herdr-agent-state.sh and
  # adds hook entries to the devin USER config. It needs the devin
  # config dir to exist — ensure_user_config creates it. Idempotent.
  herdr integration install devin >/dev/null 2>&1 \
    || log "WARN: herdr integration install devin failed; run it manually"
}

run_status() {
  devin_ok >/dev/null || die "Devin CLI $(devin_version) is not installed; run ./setup"
  herdr_ok >/dev/null || die "herdr $(herdr_version) is not installed; run ./setup"
  log "Devin CLI $(devin_version) + herdr $(herdr_version) OK"
}

run_install() {
  ensure_user_config
  ensure_devin
  ensure_herdr
  ensure_integration
}

run_dry_run() {
  log "would write managed block to ~/.config/devin/config.json (model $(pin_field models.primary), subagents_enabled=false, auto_update=false)"
  log "would run $(pin_field devin_cli.install_sh) to install Devin CLI $(devin_version)"
  log "would verify $(herdr_pkg_field asset) sha256 $(herdr_pkg_field sha256) and install herdr $(herdr_version) for $HACK_PLATFORM"
  log "would run: herdr integration install devin"
}

case "${1:-status}" in
  install) run_install ;;
  status) run_status ;;
  dry-run) run_dry_run ;;
  *) die "unknown action: $1" ;;
esac
