# Shared helpers for install/bootstrap.sh and modules. POSIX sh.

die() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

log() {
  printf '==> %s\n' "$1"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required"
}

abs_path() {
  CDPATH= cd -- "$1" && pwd
}
