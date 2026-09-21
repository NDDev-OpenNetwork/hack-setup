#!/bin/sh
# Pin Node LTS, bun, uv, and CPython from stack-pin.json into ~/.local and $REPO/.local/bin.
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"
# shellcheck source=../../lib/download.sh
. "$HACK_LIB/download.sh"

PIN_PATH="$HACK_REPO_ROOT/build/stack-pin.json"
HACK_RUNTIME_ROOT="${HACK_RUNTIME_ROOT:-$HOME/.local/share/hack-setup}"

pin_get() {
  python3 -c 'import json,sys; from functools import reduce; print(reduce(lambda a,b: a[b], sys.argv[2].split("."), json.load(open(sys.argv[1]))))' "$PIN_PATH" "$1"
}

bin_version() {
  path="$1"
  [ -x "$path" ] || return 1
  shift
  "$path" "$@" 2>/dev/null | awk '{ if (NF >= 2) print $2; else print $1; exit }' | tr -d 'v,'
}

link_bin() {
  source_bin="$1"
  dest="$HACK_LOCAL_BIN/$(basename "$source_bin")"
  mkdir -p "$HACK_LOCAL_BIN"
  if [ "$source_bin" = "$dest" ]; then
    return 0
  fi
  ln -sfn "$source_bin" "$dest"
}

extract_zip() {
  archive="$1"
  dest="$2"
  python3 -c 'import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' "$archive" "$dest"
}

install_uv() {
  wanted="$(pin_get runtimes.uv.version)"
  if [ "$(bin_version "$HACK_LOCAL_BIN/uv" --version || true)" = "$wanted" ]; then
    log "uv $wanted already at $HACK_LOCAL_BIN/uv"
  elif [ "$(bin_version "${HOME}/.local/bin/uv" --version || true)" = "$wanted" ]; then
    link_bin "${HOME}/.local/bin/uv"
    log "uv $wanted linked from ~/.local/bin"
  else
    mkdir -p "$HACK_CACHE"
    url="$(pin_get runtimes.uv.installer.url)"
    sha="$(pin_get runtimes.uv.installer.sha256)"
    installer="$HACK_CACHE/uv-installer.sh"
    log "downloading official uv $wanted installer"
    hack_download "$url" "$installer"
    hack_verify_sha256 "$installer" "$sha"
    mkdir -p "${HOME}/.local/bin"
    UV_INSTALL_DIR="${HOME}/.local/bin" UV_NO_MODIFY_PATH=1 sh "$installer"
    got="$(bin_version "${HOME}/.local/bin/uv" --version || true)"
    [ "$got" = "$wanted" ] || die "uv reported $got, expected $wanted"
    link_bin "${HOME}/.local/bin/uv"
    log "uv $wanted installed"
  fi
  [ -x "${HOME}/.local/bin/uvx" ] && link_bin "${HOME}/.local/bin/uvx"
}

link_python() {
  py="$1"
  wanted="$2"
  py_mm="${wanted%.*}"
  mkdir -p "$HACK_LOCAL_BIN"
  ln -sfn "$py" "$HACK_LOCAL_BIN/python3"
  ln -sfn "$py" "$HACK_LOCAL_BIN/python"
  ln -sfn "$py" "$HACK_LOCAL_BIN/python${py_mm}"
}

install_python() {
  wanted="$(pin_get runtimes.python.version)"
  if [ "$(bin_version "$HACK_LOCAL_BIN/python3" --version || true)" = "$wanted" ]; then
    py_mm="${wanted%.*}"
    ln -sfn "$HACK_LOCAL_BIN/python3" "$HACK_LOCAL_BIN/python${py_mm}"
    log "python $wanted already at $HACK_LOCAL_BIN/python3"
    return 0
  fi
  uv_bin="$HACK_LOCAL_BIN/uv"
  [ -x "$uv_bin" ] || uv_bin="${HOME}/.local/bin/uv"
  [ -x "$uv_bin" ] || die "uv is required before python $wanted"
  log "uv python install $wanted"
  "$uv_bin" python install "$wanted"
  py="$("$uv_bin" python find "$wanted")"
  [ -x "$py" ] || die "uv python find $wanted failed"
  link_python "$py" "$wanted"
  log "python $wanted linked"
}

install_bun() {
  wanted="$(pin_get runtimes.bun.version)"
  if [ "$(bin_version "$HACK_LOCAL_BIN/bun" --version || true)" = "$wanted" ]; then
    ln -sfn "$HACK_LOCAL_BIN/bun" "$HACK_LOCAL_BIN/bunx"
    log "bun $wanted already at $HACK_LOCAL_BIN/bun"
    return 0
  fi
  mkdir -p "$HACK_CACHE" "$HACK_RUNTIME_ROOT/bun"
  url="$(pin_get "runtimes.bun.packages.${HACK_PLATFORM}.url")"
  sha="$(pin_get "runtimes.bun.packages.${HACK_PLATFORM}.sha256")"
  name="$(pin_get "runtimes.bun.packages.${HACK_PLATFORM}.name")"
  archive="$HACK_CACHE/$name"
  log "downloading $name"
  hack_download "$url" "$archive"
  hack_verify_sha256 "$archive" "$sha"
  extract_dir="$HACK_RUNTIME_ROOT/bun/$wanted"
  rm -rf "$extract_dir"
  mkdir -p "$extract_dir"
  extract_zip "$archive" "$extract_dir"
  bun_bin="$(python3 -c 'import pathlib,sys; print(next(pathlib.Path(sys.argv[1]).rglob("bun")))' "$extract_dir")"
  [ -f "$bun_bin" ] || die "bun binary missing from $name"
  chmod +x "$bun_bin"
  got="$("$bun_bin" --version | tr -d 'v')"
  [ "$got" = "$wanted" ] || die "bun reported $got, expected $wanted"
  link_bin "$bun_bin"
  # bunx is the same binary dispatched on argv[0] basename (official installs
  # ship a bunx symlink; the bare zip does not).
  ln -sfn "$bun_bin" "$HACK_LOCAL_BIN/bunx"
  log "bun $wanted installed"
}

install_just() {
  # The documented command runner (`just gate` etc.) — must be installed,
  # not assumed on the host (#9).
  wanted="$(pin_get quality.just.version)"
  if [ "$(bin_version "$HACK_LOCAL_BIN/just" --version || true)" = "$wanted" ]; then
    log "just $wanted already at $HACK_LOCAL_BIN/just"
    return 0
  fi
  mkdir -p "$HACK_CACHE" "$HACK_RUNTIME_ROOT/just"
  url="$(pin_get "quality.just.packages.${HACK_PLATFORM}.url")"
  sha="$(pin_get "quality.just.packages.${HACK_PLATFORM}.sha256")"
  name="$(pin_get "quality.just.packages.${HACK_PLATFORM}.name")"
  archive="$HACK_CACHE/$name"
  log "downloading $name"
  hack_download "$url" "$archive"
  hack_verify_sha256 "$archive" "$sha"
  extract_dir="$HACK_RUNTIME_ROOT/just/$wanted"
  rm -rf "$extract_dir"
  mkdir -p "$extract_dir"
  case "$name" in
    *.zip) extract_zip "$archive" "$extract_dir" ;;
    *) tar -xzf "$archive" -C "$extract_dir" ;;
  esac
  just_bin="$(python3 -c 'import pathlib,sys; print(next(pathlib.Path(sys.argv[1]).rglob("just")))' "$extract_dir")"
  [ -f "$just_bin" ] || die "just binary missing from $name"
  chmod +x "$just_bin"
  got="$(bin_version "$just_bin" --version || true)"
  [ "$got" = "$wanted" ] || die "just reported $got, expected $wanted"
  link_bin "$just_bin"
  log "just $wanted installed"
}

warm_mcp_servers() {
  serena_v="$(pin_get mcp.serena.version)"
  shadcn_v="$(pin_get frontend.shadcn.version)"
  uvx_bin="$HACK_LOCAL_BIN/uvx"
  [ -x "$uvx_bin" ] || uvx_bin="${HOME}/.local/bin/uvx"
  [ -x "$uvx_bin" ] || die "uvx is required to warm the serena MCP cache"
  log "warming serena-agent $serena_v (uvx cache)"
  "$uvx_bin" --from "serena-agent==$serena_v" serena --version >/dev/null \
    || die "serena-agent $serena_v failed to resolve via uvx"
  bunx_bin="$HACK_LOCAL_BIN/bunx"
  [ -x "$bunx_bin" ] || die "bunx is required to warm the shadcn MCP cache"
  log "warming shadcn $shadcn_v (bunx cache)"
  "$bunx_bin" "shadcn@$shadcn_v" --version >/dev/null \
    || die "shadcn $shadcn_v failed to resolve via bunx"
}

install_node() {
  wanted="$(pin_get runtimes.node.version)"
  if [ "$(bin_version "$HACK_LOCAL_BIN/node" --version || true)" = "$wanted" ]; then
    log "node $wanted already at $HACK_LOCAL_BIN/node"
    return 0
  fi
  mkdir -p "$HACK_CACHE"
  url="$(pin_get "runtimes.node.packages.${HACK_PLATFORM}.url")"
  sha="$(pin_get "runtimes.node.packages.${HACK_PLATFORM}.sha256")"
  name="$(pin_get "runtimes.node.packages.${HACK_PLATFORM}.name")"
  archive="$HACK_CACHE/$name"
  log "downloading $name"
  hack_download "$url" "$archive"
  hack_verify_sha256 "$archive" "$sha"
  extract_root="$HACK_RUNTIME_ROOT/node"
  mkdir -p "$extract_root"
  tar -xzf "$archive" -C "$extract_root"
  prefix="$extract_root/${name%.tar.gz}"
  [ -x "$prefix/bin/node" ] || die "node binary missing from $name"
  got="$(bin_version "$prefix/bin/node" --version || true)"
  [ "$got" = "$wanted" ] || die "node reported $got, expected $wanted"
  link_bin "$prefix/bin/node"
  [ -x "$prefix/bin/npm" ] && link_bin "$prefix/bin/npm"
  [ -x "$prefix/bin/npx" ] && link_bin "$prefix/bin/npx"
  log "node $wanted installed"
}

run_install() {
  install_uv
  install_python
  install_bun
  install_node
  install_just
  warm_mcp_servers
}

run_status() {
  node_v="$(pin_get runtimes.node.version)"
  bun_v="$(pin_get runtimes.bun.version)"
  uv_v="$(pin_get runtimes.uv.version)"
  py_v="$(pin_get runtimes.python.version)"
  just_v="$(pin_get quality.just.version)"
  [ "$(bin_version "$HACK_LOCAL_BIN/uv" --version || true)" = "$uv_v" ] || die "uv $uv_v missing; run ./setup"
  [ "$(bin_version "$HACK_LOCAL_BIN/python3" --version || true)" = "$py_v" ] || die "python $py_v missing; run ./setup"
  [ "$(bin_version "$HACK_LOCAL_BIN/bun" --version || true)" = "$bun_v" ] || die "bun $bun_v missing; run ./setup"
  [ "$(bin_version "$HACK_LOCAL_BIN/node" --version || true)" = "$node_v" ] || die "node $node_v missing; run ./setup"
  [ "$(bin_version "$HACK_LOCAL_BIN/just" --version || true)" = "$just_v" ] || die "just $just_v missing; run ./setup"
  log "runtimes ok (node $node_v, bun $bun_v, python $py_v, uv $uv_v, just $just_v)"
}

run_dry_run() {
  log "would install uv $(pin_get runtimes.uv.version)"
  log "would uv python install $(pin_get runtimes.python.version)"
  log "would install bun $(pin_get runtimes.bun.version) ($HACK_PLATFORM)"
  log "would install node $(pin_get runtimes.node.version) ($HACK_PLATFORM)"
  log "would install just $(pin_get quality.just.version) ($HACK_PLATFORM)"
  log "would warm MCP caches: serena-agent $(pin_get mcp.serena.version), shadcn $(pin_get frontend.shadcn.version)"
}

case "${1:-status}" in
  install) run_install ;;
  status) run_status ;;
  dry-run) run_dry_run ;;
  *) die "unknown action: $1" ;;
esac
