#!/bin/sh
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"

install_plugins() {
  devin_bin="$HACK_LOCAL_BIN/devin"
  [ -x "$devin_bin" ] || devin_bin="${HOME}/.local/bin/devin"
  [ -x "$devin_bin" ] || devin_bin="$(command -v devin || true)"
  [ -n "$devin_bin" ] || die "devin is required before plugins; run module 20"
  # devin-pin plugins[] is the SoT — local install links the repo tree,
  # so skills/rules track the checkout (no cloud sync).
  python3 -c 'import json,sys
for p in json.load(open(sys.argv[1]))["plugins"]:
    print(p["dir"])' "$HACK_REPO_ROOT/build/devin-pin.json" \
    | while IFS= read -r dir; do
        "$devin_bin" plugins install --local "$HACK_REPO_ROOT/$dir" -y >/dev/null 2>&1 \
          || "$devin_bin" plugin install --local "$HACK_REPO_ROOT/$dir" -y >/dev/null
      done
  log "plugins installed (local) and synced with the repo"
}

run_verify() {
  require_cmd python3
  install_plugins
  # Single writer convergence: full repair AFTER runtimes land; module
  # 20 may have skipped user-config on a cold host without python3.
  python3 "$HACK_REPO_ROOT/scripts/repair_devin_setup.py"
  python3 "$HACK_REPO_ROOT/scripts/check_devin_setup.py"
}

case "${1:-status}" in
  install) run_verify ;;
  status)
    require_cmd python3
    python3 "$HACK_REPO_ROOT/scripts/check_devin_setup.py"
    ;;
  dry-run)
    log "would install plugins via devin plugins install --local and run check_devin_setup.py"
    ;;
  *)
    die "unknown action: $1"
    ;;
esac
