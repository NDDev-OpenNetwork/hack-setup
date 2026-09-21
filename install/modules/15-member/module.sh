#!/bin/sh
# Member identity + shared git defaults. One module, three declared
# member profiles in the pin — the member is data, not a code fork.
# Identity is derived from `gh api user` (name + email/noreply) so no
# personal mail lands in this public repo; the gh login MUST equal
# team.members.<member>.github or the install stops — that is the
# conflict-free guarantee (wrong-lane commits can't happen silently).
set -eu

# shellcheck source=../../lib/common.sh
. "$HACK_LIB/common.sh"

STACK_PIN="$HACK_REPO_ROOT/build/stack-pin.json"
MARKER="$HACK_REPO_ROOT/.agent/member"

member_list() {
  python3 -c 'import json,sys; print(" ".join(json.load(open(sys.argv[1]))["team"]["members"]))' "$STACK_PIN"
}

member_github() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["team"]["members"][sys.argv[2]]["github"])' "$STACK_PIN" "$1"
}

git_defaults() {
  python3 -c 'import json,sys
pin = json.load(open(sys.argv[1]))["team"]
for k, v in pin["git_defaults"].items():
    print(f"{k}\t{v}")' "$STACK_PIN"
}

resolve_member() {
  # --member flag / HACK_MEMBER env wins; else the checkout marker.
  if [ -n "${HACK_MEMBER:-}" ]; then
    printf '%s' "$HACK_MEMBER"
  elif [ -f "$MARKER" ]; then
    cat "$MARKER"
  fi
}

require_known_member() {
  member="$1"
  case " $(member_list) " in
    *" $member "*) ;;
    *) die "unknown member '$member' — expected one of: $(member_list)" ;;
  esac
}

gh_identity() {
  # Prints login<TAB>name<TAB>email for the authenticated gh user.
  gh api user 2>/dev/null | python3 -c 'import json,sys
u = json.load(sys.stdin)
login = u.get("login") or ""
name = u.get("name") or login
uid = u.get("id")
email = u.get("email") or ("%s+%s@users.noreply.github.com" % (uid, login))
print(f"{login}\t{name}\t{email}")'
}

apply_git_defaults() {
  git_defaults | while IFS="$(printf '\t')" read -r key val; do
    git config --global "$key" "$val"
  done
}

check_ssh() {
  # GitHub answers `ssh -T` with exit 1 + a greeting even on success.
  out="$(ssh -T -o BatchMode=yes -o ConnectTimeout=5 git@github.com 2>&1 || true)"
  case "$out" in
    *"successfully authenticated"*) log "ssh: github.com key ok" ;;
    *) log "WARN: no github.com SSH key — needed for the vibestrap submodule; ssh-keygen + add to GitHub" ;;
  esac
}

run_install() {
  member="$(resolve_member || true)"
  apply_git_defaults
  log "git defaults applied (ff-only, prune, rerere, zdiff3, lf)"

  if [ -z "$member" ]; then
    log "WARN: no --member flag — git identity untouched; rerun ./setup --member <$(member_list | tr ' ' '|')>"
    return 0
  fi
  require_known_member "$member"
  expected="$(member_github "$member")"

  command -v gh >/dev/null 2>&1 || die "gh is required for member identity; module 10 should have caught this"
  row="$(gh_identity || true)"
  if [ -z "$row" ]; then
    die "gh not authenticated — run: gh auth login  (member $member expects @$expected)"
  fi
  login="$(printf '%s' "$row" | cut -f1)"
  name="$(printf '%s' "$row" | cut -f2)"
  email="$(printf '%s' "$row" | cut -f3)"
  [ "$login" = "$expected" ] \
    || die "gh is authenticated as @$login but member '$member' is @$expected — run gh auth switch/login first"
  git config --global user.name "$name"
  git config --global user.email "$email"
  log "git identity: $name <$email>"

  gh auth setup-git 2>/dev/null || log "WARN: gh auth setup-git failed (https pushes may need manual creds)"
  check_ssh
  mkdir -p "$HACK_REPO_ROOT/.agent"
  printf '%s\n' "$member" > "$MARKER"
  log "member: $member (@$login) — marker at .agent/member"
}

run_status() {
  member="$(resolve_member || true)"
  if [ -z "$member" ]; then
    log "no member configured — run ./setup --member <$(member_list | tr ' ' '|')>"
    return 0
  fi
  require_known_member "$member"
  expected="$(member_github "$member")"
  row="$(gh_identity || true)"
  [ -n "$row" ] || die "gh not authenticated; member $member expects @$expected"
  login="$(printf '%s' "$row" | cut -f1)"
  [ "$login" = "$expected" ] \
    || die "gh login @$login does not match member $member (@$expected)"
  name="$(git config --global user.name || true)"
  email="$(git config --global user.email || true)"
  [ -n "$name" ] && [ -n "$email" ] \
    || die "git identity unset — run ./setup --member $member"
  log "member $member ok: $name <$email>, gh @$login"
}

run_dry_run() {
  member="$(resolve_member || true)"
  if [ -n "$member" ]; then
    require_known_member "$member"
    log "member $member → expects gh login @$(member_github "$member")"
    log "would set git user.name/user.email from gh api user (profile name + email/noreply)"
  else
    log "no member selected (./setup --member <$(member_list | tr ' ' '|')>) — would apply shared git defaults only"
  fi
  git_defaults | while IFS="$(printf '\t')" read -r key val; do
    log "would git config --global $key $val"
  done
  log "would verify ssh -T git@github.com and run gh auth setup-git"
}

case "${1:-status}" in
  install) run_install ;;
  status) run_status ;;
  dry-run) run_dry_run ;;
  *) die "unknown action: $1" ;;
esac
