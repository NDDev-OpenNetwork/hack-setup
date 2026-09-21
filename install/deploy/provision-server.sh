#!/bin/sh
# provision-server — repeatable, non-destructive server setup for the
# pull-watcher deploy model. Run from a workstation; the only manual
# input is SSH access.
#
#   provision-server.sh <host> <branch> <repo-url> [app-dir]
#
# Example:
#   provision-server.sh dev.example.com dev git@github.com:ORG/repo.git /opt/app
#
# Does: verify git + docker + compose + curl, clone the repo if absent
# (deploy key / https token must already grant read access), fast-forward
# the configured branch — NEVER reset --hard, a diverged/dirty checkout
# stops the run (issue #7), write /etc/default/hack-deploy only when
# missing (existing env is preserved), install the deploy-watch systemd
# units, and start the timer unconditionally — the watcher self-gates on
# $dir/.env, so deploys begin on the next tick after config lands.
set -eu

host=${1:?usage: provision-server.sh <host> <branch> <repo-url> [app-dir]}
# <host> may carry a user (deploy@1.2.3.4); default to root.
target=$host
case "$host" in *@*) ;; *) target="root@$host" ;; esac
branch=${2:?branch required}
repo=${3:?repo-url required}
dir=${4:-/opt/app}

# Single-quote a value for safe interpolation into the remote command
# line (host/branch/repo/dir are data, never shell — issue #7).
sq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

remote_env="HACK_DIR=$(sq "$dir") HACK_BRANCH=$(sq "$branch") HACK_REPO=$(sq "$repo")"

# --- Phase 1: prerequisites + repo checkout -------------------------------
ssh "$target" "$remote_env sh -s" <<'EOF'
set -eu
export DEBIAN_FRONTEND=noninteractive
if ! command -v git >/dev/null || ! command -v docker >/dev/null; then
  apt-get update -qq
  command -v git >/dev/null || apt-get install -y -qq git
  command -v docker >/dev/null || apt-get install -y -qq docker.io docker-compose-v2
fi
command -v curl >/dev/null || { apt-get update -qq && apt-get install -y -qq curl; }
docker compose version >/dev/null 2>&1 \
  || { echo "FAIL: docker compose plugin missing"; exit 1; }
command -v systemctl >/dev/null \
  || { echo "FAIL: systemd required for deploy-watch.timer"; exit 1; }

if [ -d "$HACK_DIR/.git" ]; then
  cd "$HACK_DIR"
  git fetch origin "$HACK_BRANCH"
  current=$(git branch --show-current)
  [ "$current" = "$HACK_BRANCH" ] || git checkout "$HACK_BRANCH"
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "FAIL: $HACK_DIR has uncommitted changes — reconcile manually"
    exit 1
  fi
  if ! git merge-base --is-ancestor HEAD "origin/$HACK_BRANCH"; then
    echo "FAIL: $HACK_DIR HEAD diverged/ahead of origin/$HACK_BRANCH — reconcile manually"
    exit 1
  fi
  git merge --ff-only "origin/$HACK_BRANCH"
elif [ -e "$HACK_DIR" ]; then
  echo "FAIL: $HACK_DIR exists but is not a git checkout"
  exit 1
else
  git clone --branch "$HACK_BRANCH" "$HACK_REPO" "$HACK_DIR"
fi
EOF

# --- Phase 2: watcher install ---------------------------------------------
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
scp "$script_dir/deploy-watch.sh" "$target:/usr/local/bin/deploy-watch.sh"
scp "$script_dir/deploy-watch.service" "$script_dir/deploy-watch.timer" \
  "$target:/etc/systemd/system/"

# Render the env file locally; scp only when absent (existing HACK_DEPLOY_*
# config — health URL, custom cmd, log path — is preserved, issue #7).
tmp_env=$(mktemp)
trap 'rm -f "$tmp_env"' EXIT
{
  printf 'HACK_DEPLOY_DIR=%s\n' "$dir"
  printf 'HACK_DEPLOY_BRANCH=%s\n' "$branch"
  printf '# HACK_DEPLOY_CMD=docker compose up -d --build\n'
  printf '# HACK_DEPLOY_HEALTH=http://localhost:3000\n'
  printf '# HACK_DEPLOY_LOG=/var/log/deploy-watch.log\n'
} > "$tmp_env"

ssh "$target" "$remote_env sh -s" <<'EOF'
set -eu
chmod +x /usr/local/bin/deploy-watch.sh
if [ -f /etc/default/hack-deploy ]; then
  echo "existing /etc/default/hack-deploy preserved — review it matches this run"
fi
EOF
# Write the rendered env only when absent; stdin carries the file.
ssh "$target" "test -f /etc/default/hack-deploy || { cat > /etc/default/hack-deploy.new && chmod 0644 /etc/default/hack-deploy.new && mv /etc/default/hack-deploy.new /etc/default/hack-deploy; }" < "$tmp_env"

# --- Phase 3: enable + start — the watcher self-gates on $dir/.env -----
# deploy-watch.sh exits 0 without deploying until the app .env exists
# (and a first deploy has happened), so the timer is always safe to run;
# dropping .env later is picked up on the next tick (issue #7).
ssh "$target" <<'EOF'
set -eu
systemctl daemon-reload
systemctl enable --now deploy-watch.timer
systemctl status deploy-watch.timer --no-pager | head -5
EOF
echo "provisioned $host: watches $branch in $dir every 30s (timer running; deploys start once $dir/.env exists)"
