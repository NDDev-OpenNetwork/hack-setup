#!/bin/sh
# provision-server — one-shot server setup for the pull-watcher deploy
# model. Run from a workstation; the only manual input is SSH access.
#
#   provision-server.sh <host> <branch> <repo-url> [app-dir]
#
# Example:
#   provision-server.sh dev.example.com dev git@github.com:ORG/repo.git /opt/app
#
# Does: install git + docker, clone the repo (deploy key / https token
# must already grant read access), write /etc/default/hack-deploy,
# install + enable the deploy-watch systemd timer.
set -eu

host=${1:?usage: provision-server.sh <host> <branch> <repo-url> [app-dir]}
branch=${2:?branch required}
repo=${3:?repo-url required}
dir=${4:-/opt/app}

ssh "root@$host" sh -s <<EOF
set -eu
export DEBIAN_FRONTEND=noninteractive
if ! command -v git >/dev/null || ! command -v docker >/dev/null; then
  apt-get update -qq
  command -v git >/dev/null || apt-get install -y -qq git
  command -v docker >/dev/null || apt-get install -y -qq docker.io docker-compose-v2
fi
if [ ! -d "$dir/.git" ]; then git clone "$repo" "$dir"; fi
cd "$dir" && git fetch origin && git checkout "$branch" && git reset --hard "origin/$branch"
EOF

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
scp "$script_dir/deploy-watch.sh" "root@$host:/usr/local/bin/deploy-watch.sh"
scp "$script_dir/deploy-watch.service" "$script_dir/deploy-watch.timer" \
  "root@$host:/etc/systemd/system/"

ssh "root@$host" sh -s <<EOF
set -eu
chmod +x /usr/local/bin/deploy-watch.sh
cat > /etc/default/hack-deploy <<'ENV'
HACK_DEPLOY_DIR=$dir
HACK_DEPLOY_BRANCH=$branch
# HACK_DEPLOY_CMD=docker compose up -d --build
# HACK_DEPLOY_HEALTH=http://localhost:3000
# HACK_DEPLOY_LOG=/var/log/deploy-watch.log
ENV
systemctl daemon-reload
systemctl enable --now deploy-watch.timer
systemctl status deploy-watch.timer --no-pager | head -5
EOF

echo "provisioned $host: watches $branch in $dir every 30s"
echo "next: put the app .env in $dir on the server and confirm"
echo "  ssh root@$host journalctl -u deploy-watch.service -f"
