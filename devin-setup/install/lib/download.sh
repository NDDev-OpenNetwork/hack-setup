# Download and SHA-256 helpers. POSIX sh.

hack_sha256() {
  path="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$path" | awk '{print $1}'
    return
  fi
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$path" | awk '{print $1}'
    return
  fi
  die "sha256sum or shasum is required"
}

hack_verify_sha256() {
  path="$1"
  expected="$2"
  actual="$(hack_sha256 "$path")"
  if [ "$actual" != "$expected" ]; then
    rm -f "$path"
    die "checksum mismatch for $path (expected $expected, got $actual); file removed"
  fi
}

hack_download() {
  url="$1"
  dest="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --proto '=https' --tlsv1.2 --max-redirs 5 "$url" -o "$dest"
    return
  fi
  if command -v wget >/dev/null 2>&1; then
    wget -q -O "$dest" "$url"
    return
  fi
  die "curl or wget is required"
}
