#!/bin/sh
# deploy-watch — server-side pull watcher. No GitHub admin rights needed:
# the server polls its configured branch and redeploys when it moves.
# Config via environment (systemd EnvironmentFile or .env):
#   HACK_DEPLOY_DIR     repo checkout on the server        (required)
#   HACK_DEPLOY_BRANCH  branch to follow, e.g. dev|main    (required)
#   HACK_DEPLOY_CMD     deploy command                     (default: docker compose up -d --build)
#   HACK_DEPLOY_HEALTH  URL to curl after deploy           (optional)
#   HACK_DEPLOY_HEALTH_TRIES  readiness attempts ×5s       (default: 12)
#   HACK_DEPLOY_LOG     log file                           (default: stderr/journald)
#
# State: $HACK_DEPLOY_DIR/.deployed-sha records the SHA whose deploy
# SUCCEEDED. It always holds the real deployed HEAD — never the desired
# remote SHA — so a local-ahead or diverged checkout can never masquerade
# as a clean deploy (issue #6).
set -eu

# >> /dev/stderr fails under systemd (append on a journald socket gets
# ENXIO) — write to the fd itself when no log file is configured.
log() {
  if [ -n "${HACK_DEPLOY_LOG:-}" ]; then
    printf '%s deploy-watch: %s\n' "$(date -u +%H:%M:%S)" "$*" >> "$HACK_DEPLOY_LOG"
  else
    printf '%s deploy-watch: %s\n' "$(date -u +%H:%M:%S)" "$*" >&2
  fi
}
die() { log "FAIL $*"; exit 1; }

[ -n "${HACK_DEPLOY_DIR:-}" ] || die "HACK_DEPLOY_DIR unset"
[ -n "${HACK_DEPLOY_BRANCH:-}" ] || die "HACK_DEPLOY_BRANCH unset"
cd "$HACK_DEPLOY_DIR" || die "cannot cd $HACK_DEPLOY_DIR"

# Config gate: never deploy before the app has its .env — but once a
# deploy has succeeded the watcher keeps working even if .env is later
# removed (an intentional cleanup shouldn't stall redeploys). This lets
# the systemd timer run unconditionally; provisioning needs no manual
# start step (issue #7).
if [ ! -f .env ] && [ ! -f .deployed-sha ]; then
  log "no .env and never deployed — waiting for app config"
  exit 0
fi

# Server never owns local commits: ff-only. A dirty tree pauses the watch.
if ! git diff --quiet || ! git diff --cached --quiet; then
  log "dirty tree on server, skipping tick"
  exit 0
fi

git fetch --quiet origin "$HACK_DEPLOY_BRANCH" || die "git fetch failed"
remote=$(git rev-parse "origin/$HACK_DEPLOY_BRANCH")
deployed=$(cat .deployed-sha 2>/dev/null || echo none)
[ "$remote" = "$deployed" ] && exit 0

local=$(git rev-parse HEAD)
if [ "$remote" != "$local" ]; then
  if git merge-base --is-ancestor "$local" "$remote"; then
    log "checkout $local -> $remote ($HACK_DEPLOY_BRANCH)"
    git merge --ff-only "$remote" || die "ff-only pull failed; reset manually"
  else
    # HEAD is ahead of or has diverged from origin — merging would be a
    # no-op and .deployed-sha would lie about what is deployed (#6).
    # Refuse: a human must reconcile (review, then
    # `git reset --hard origin/$HACK_DEPLOY_BRANCH`).
    die "server HEAD $local is not an ancestor of origin/$HACK_DEPLOY_BRANCH $remote — local commits or diverged; refusing to deploy"
  fi
fi

log "deploying $remote ($HACK_DEPLOY_BRANCH)"
if [ -n "${HACK_DEPLOY_LOG:-}" ]; then
  ${HACK_DEPLOY_CMD:-docker compose up -d --build} >> "$HACK_DEPLOY_LOG" 2>&1 \
    || die "deploy command failed for $remote — will retry next tick"
else
  ${HACK_DEPLOY_CMD:-docker compose up -d --build} \
    || die "deploy command failed for $remote — will retry next tick"
fi

if [ -n "${HACK_DEPLOY_HEALTH:-}" ]; then
  tries=${HACK_DEPLOY_HEALTH_TRIES:-12}
  i=0
  until curl -fsS --max-time 10 -o /dev/null "$HACK_DEPLOY_HEALTH"; do
    i=$((i + 1))
    [ "$i" -ge "$tries" ] && die "health check failed for $remote after ${tries} tries — will retry next tick"
    sleep 5
  done
  log "healthy at $HACK_DEPLOY_HEALTH"
fi

# Record what is ACTUALLY checked out — enforced equal to remote above.
git rev-parse HEAD > .deployed-sha
log "deployed $remote"
