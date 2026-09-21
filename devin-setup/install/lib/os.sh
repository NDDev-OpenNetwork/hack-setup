# Detect macOS/Linux and a Codex package triple. POSIX sh.

hack_detect_os() {
  HACK_WSL=0
  case "$(uname -s)" in
    Darwin) HACK_OS="darwin" ;;
    Linux)
      HACK_OS="linux"
      case "$(uname -r)" in
        *microsoft*|*WSL*) HACK_WSL=1 ;;
      esac
      ;;
    *)
      die "unsupported OS $(uname -s); supported: macOS, Ubuntu/Linux, native Windows via .\\setup.ps1, or WSL2 Ubuntu"
      ;;
  esac

  case "$(uname -m)" in
    x86_64 | amd64) HACK_ARCH="x86_64" ;;
    arm64 | aarch64) HACK_ARCH="arm64" ;;
    *) die "unsupported architecture $(uname -m)" ;;
  esac

  if [ "$HACK_OS" = "darwin" ] && [ "$HACK_ARCH" = "x86_64" ]; then
    if [ "$(sysctl -n sysctl.proc_translated 2>/dev/null || true)" = "1" ]; then
      HACK_ARCH="arm64"
    fi
  fi

  case "$HACK_OS-$HACK_ARCH" in
    darwin-arm64)
      HACK_PLATFORM="darwin-arm64"
      HACK_TRIPLE="aarch64-apple-darwin"
      ;;
    darwin-x86_64)
      HACK_PLATFORM="darwin-x86_64"
      HACK_TRIPLE="x86_64-apple-darwin"
      ;;
    linux-arm64)
      HACK_PLATFORM="linux-arm64"
      HACK_TRIPLE="aarch64-unknown-linux-musl"
      ;;
    linux-x86_64)
      HACK_PLATFORM="linux-x86_64"
      HACK_TRIPLE="x86_64-unknown-linux-musl"
      ;;
    *)
      die "no pinned Codex package for $HACK_OS/$HACK_ARCH"
      ;;
  esac

  if [ "$HACK_WSL" = "1" ]; then
    log "detected WSL (Windows) — running the linux-x86_64 path"
  fi
  export HACK_OS HACK_ARCH HACK_PLATFORM HACK_TRIPLE HACK_WSL
}
