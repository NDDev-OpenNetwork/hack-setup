#!/bin/sh
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"
# shellcheck source=../../lib/download.sh
. "$HACK_LIB/download.sh"

PIN_PATH="$HACK_REPO_ROOT/build/codex-pin.json"
STACK_PIN_PATH="$HACK_REPO_ROOT/build/stack-pin.json"

pin_field() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["installer"][sys.argv[2]])' "$PIN_PATH" "$1"
}

pkg_field() {
  python3 -c 'import json,sys
pin=json.load(open(sys.argv[1]))
for pkg in pin.get("packages",{}).values():
    if pkg.get("triple")==sys.argv[2]:
        print(pkg[sys.argv[3]])
        break' "$PIN_PATH" "$HACK_TRIPLE" "$1"
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

ensure_sol_profile() {
  # Codex >=0.134: `--profile sol` overlays ~/.codex/sol.config.toml on top
  # of the user config. Project-local [profiles] are ignored, and a legacy
  # [profiles.sol] table in the user config.toml makes `--profile sol` fail.
  secondary="$(hack_pin_get "$STACK_PIN_PATH" models.secondary)"
  effort="$(hack_pin_get "$STACK_PIN_PATH" models.reasoning_effort)"
  ctx="$(hack_pin_get "$STACK_PIN_PATH" models.requested_context_window)"
  compact="$(hack_pin_get "$STACK_PIN_PATH" models.requested_auto_compact)"
  mkdir -p "${HOME}/.codex"
  cat > "${HOME}/.codex/sol.config.toml" <<EOF
# hack-setup managed: secondary model profile for \`codex --profile sol\`.
# Values come from build/stack-pin.json models.* — edit the pin, not this file.
model = "$secondary"
model_reasoning_effort = "$effort"
review_model = "$secondary"
model_context_window = $ctx
model_auto_compact_token_limit = $compact
EOF
  python3 - "${HOME}/.codex/config.toml" <<'PY'
import pathlib, re, sys
p = pathlib.Path(sys.argv[1])
if not p.exists():
    sys.exit(0)
src = p.read_text()
lines = src.splitlines(keepends=True)
out, i, n = [], 0, len(lines)
while i < n:
    line = lines[i]
    if line.lstrip().startswith("# hack-setup:"):
        while i < n and lines[i].lstrip().startswith("#"):
            i += 1
        continue
    if "# hack-setup" in line and "=" in line:
        i += 1
        continue
    if re.fullmatch(r"\[profiles\.sol\]", line.strip()):
        i += 1
        while i < n and not lines[i].strip().startswith("["):
            i += 1
        continue
    out.append(line)
    i += 1
res = "".join(out)
if res != src:
    p.write_text(res)
PY
  log "installed user profile ~/.codex/sol.config.toml ($secondary)"
}

ensure_notify() {
  # `notify` is a ROOT key in ~/.codex/config.toml and a foreign value
  # must never be duplicated — the TOML-aware writer lives in
  # repair_setup.py (single writer for installer + repair, HS-01/HS-03).
  # Without python3 this is a no-op; module 40 re-runs full repair after
  # runtimes land.
  command -v python3 >/dev/null 2>&1 || return 0
  python3 "${HACK_REPO_ROOT}/scripts/repair_setup.py" --only notify-block \
    >/dev/null 2>&1 || true
}

ensure_hook_trust() {
  # Non-managed hooks run only when a trusted_hash recorded in the USER
  # config layer matches the hook definition hash; project layers cannot
  # self-trust (codex-rs config_rules.rs). repair_setup.py writes the
  # managed [hooks.state.*] block — refresh it at install so hooks are
  # live from the first session without a manual `/hooks` review.
  command -v python3 >/dev/null 2>&1 || return 0
  python3 "${HACK_REPO_ROOT}/scripts/repair_setup.py" --only hook-trust \
    >/dev/null 2>&1 || true
}

run_install() {
  wanted="$(cli_version)"
  ensure_sol_profile
  ensure_notify
  ensure_hook_trust
  if found="$(already_pinned)"; then
    link_repo_bin "$found"
    log "Codex CLI $wanted already present; linked $HACK_LOCAL_BIN/codex"
    return 0
  fi

  mkdir -p "$HACK_CACHE"
  user_bin="${HOME}/.local/bin"
  mkdir -p "$user_bin"

  pkg_url="$(pkg_field url || true)"
  if [ -n "$pkg_url" ]; then
    pkg_sha="$(pkg_field sha256)"
    pkg_name="$(pkg_field name)"
    tarball="$HACK_CACHE/$pkg_name"
    log "downloading pinned package $pkg_name for $wanted"
    hack_download "$pkg_url" "$tarball"
    hack_verify_sha256 "$tarball" "$pkg_sha"
    standalone="${HOME}/.codex/packages/standalone"
    release_dir="$standalone/releases/${wanted}-${HACK_TRIPLE}"
    stage_dir="${release_dir}.tmp.$$"
    rm -rf "$stage_dir"
    mkdir -p "$stage_dir"
    tar -xzf "$tarball" -C "$stage_dir"
    [ -x "$stage_dir/bin/codex" ] || die "no bin/codex inside $pkg_name"
    ln -sfn bin/codex "$stage_dir/codex"
    rm -rf "$release_dir"
    mv "$stage_dir" "$release_dir"
    ln -sfn "$release_dir" "$standalone/current"
    ln -sfn "$standalone/current/bin/codex" "$user_bin/codex"
    if [ -x "$release_dir/bin/codex-code-mode-host" ]; then
      ln -sfn "$standalone/current/bin/codex-code-mode-host" \
        "$user_bin/codex-code-mode-host"
    fi
  else
    installer_url="$(pin_field url)"
    installer_sha="$(pin_field sha256)"
    installer_path="$HACK_CACHE/codex-official-install.sh"
    log "no pinned package for $HACK_TRIPLE; downloading official install.sh"
    hack_download "$installer_url" "$installer_path"
    hack_verify_sha256 "$installer_path" "$installer_sha"
    log "running official installer (CODEX_RELEASE=$wanted)"
    CODEX_RELEASE="$wanted" \
      CODEX_NON_INTERACTIVE=1 \
      CODEX_INSTALLER_USE_RELEASES_OPENAI_COM=false \
      CODEX_INSTALL_DIR="$user_bin" \
      sh "$installer_path"
  fi

  got="$(binary_version "$user_bin/codex" || true)"
  [ "$got" = "$wanted" ] || die "installed Codex reported $got, expected $wanted"
  link_repo_bin "$user_bin/codex"
  log "Codex CLI $wanted installed"
}

run_dry_run() {
  wanted="$(cli_version)"
  pkg_url="$(pkg_field url || true)"
  if [ -n "$pkg_url" ]; then
    log "would verify $pkg_url"
    log "would require sha256 $(pkg_field sha256)"
    log "would extract the pinned binary into ~/.local/bin on $HACK_PLATFORM"
  else
    url="$(pin_field url)"
    sha="$(pin_field sha256)"
    log "would verify $url"
    log "would require sha256 $sha"
    log "would run official installer with CODEX_RELEASE=$wanted on $HACK_PLATFORM"
  fi
}

case "${1:-status}" in
  install) run_install ;;
  status) run_status ;;
  dry-run) run_dry_run ;;
  *) die "unknown action: $1" ;;
esac
