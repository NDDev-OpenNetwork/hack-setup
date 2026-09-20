#!/bin/sh
# deploy-watch — server-side pull watcher. No GitHub admin rights needed:
# the server polls its configured branch and redeploys when it moves.
# Config via environment (systemd EnvironmentFile or .env):
#   HACK_DEPLOY_DIR     repo checkout on the server        (required)
#   HACK_DEPLOY_BRANCH  branch to follow, e.g. dev|main    (required)
#   HACK_DEPLOY_CMD     deploy command                     (default: docker compose up -d --build)
#   HACK_DEPLOY_HEALTH  URL to curl after deploy           (optional)
#   HACK_DEPLOY_LOG     log file                           (default: stderr/journald)
set -eu

log() { printf '%s deploy-watch: %s\n' "$(date -u +%H:%M:%S)" "$*" >> "${HACK_DEPLOY_LOG:-/dev/stderr}"; }
die() { log "FAIL $*"; exit 1; }

[ -n "${HACK_DEPLOY_DIR:-}" ] || die "HACK_DEPLOY_DIR unset"
[ -n "${HACK_DEPLOY_BRANCH:-}" ] || die "HACK_DEPLOY_BRANCH unset"
cd "$HACK_DEPLOY_DIR" || die "cannot cd $HACK_DEPLOY_DIR"

# Server never owns local commits: ff-only. A dirty tree pauses the watch.
if ! git diff --quiet || ! git diff --cached --quiet; then
  log "dirty tree on server, skipping tick"
  exit 0
fi

git fetch --quiet origin "$HACK_DEPLOY_BRANCH" || die "git fetch failed"
remote=$(git rev-parse "origin/$HACK_DEPLOY_BRANCH")
local=$(git rev-parse HEAD)
[ "$remote" = "$local" ] && exit 0

log "deploying $local -> $remote ($HACK_DEPLOY_BRANCH)"
git merge --ff-only "$remote" || die "ff-only pull failed; reset manually"

${HACK_DEPLOY_CMD:-docker compose up -d --build} >> "${HACK_DEPLOY_LOG:-/dev/stderr}" 2>&1 \
  || die "deploy command failed"

if [ -n "${HACK_DEPLOY_HEALTH:-}" ]; then
  sleep "${HACK_DEPLOY_HEALTH_DELAY:-5}"
  curl -fsS --max-time 10 -o /dev/null "$HACK_DEPLOY_HEALTH" \
    && log "healthy at $HACK_DEPLOY_HEALTH" \
    || log "WARN health check failed: $HACK_DEPLOY_HEALTH"
fi
