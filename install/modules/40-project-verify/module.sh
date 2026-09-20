#!/bin/sh
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"

install_plugins() {
  codex_bin="$HACK_LOCAL_BIN/codex"
  [ -x "$codex_bin" ] || codex_bin="${HOME}/.local/bin/codex"
  [ -x "$codex_bin" ] || codex_bin="$(command -v codex || true)"
  [ -n "$codex_bin" ] || die "codex is required before plugins; run module 20"
  "$codex_bin" plugin marketplace add "$HACK_REPO_ROOT" >/dev/null
  # Marketplace is the plugin SoT — install whatever it lists.
  python3 -c 'import json,sys; print("\n".join(p["name"] for p in json.load(open(sys.argv[1]))["plugins"]))' \
    "$HACK_REPO_ROOT/.agents/plugins/marketplace.json" \
    | while IFS= read -r name; do
        "$codex_bin" plugin add "$name@saint-tibo" >/dev/null
      done
  log "plugins installed and synced with the repo"
}

run_verify() {
  require_cmd python3
  install_plugins
  python3 "$HACK_REPO_ROOT/scripts/check_codex_setup.py"
  python3 "$HACK_REPO_ROOT/scripts/check_stack.py"
}

case "${1:-status}" in
  install) run_verify ;;
  status)
    require_cmd python3
    python3 "$HACK_REPO_ROOT/scripts/check_codex_setup.py"
    python3 "$HACK_REPO_ROOT/scripts/check_stack.py"
    ;;
  dry-run)
    log "would install marketplace plugins and run the checkers"
    ;;
  *)
    die "unknown action: $1"
    ;;
esac
