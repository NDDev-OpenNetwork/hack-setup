# Server deploy — pull watcher

No GitHub admin rights needed. Each server polls its branch and
redeploys when it moves. Dev server watches `dev`, prod watches `main`.

## Provision (once per server)

```sh
install/deploy/provision-server.sh <host> <branch> <repo-url> [dir]

# dev server:  provision-server.sh dev.example.com  dev   git@github.com:ORG/repo.git
# prod server: provision-server.sh prod.example.com main  git@github.com:ORG/repo.git
```

Prereqs: root ssh to an Ubuntu/Debian host; the repo must be readable
from the server (deploy key or HTTPS token in the URL / credential
helper). `doctl compute droplet create` day-before is the expected
source of hosts.

## What it installs

- `/usr/local/bin/deploy-watch.sh` — fetch → ff-only pull →
  `HACK_DEPLOY_CMD` (default `docker compose up -d --build`) → optional
  health curl. A dirty tree pauses the watcher instead of clobbering it.
- `deploy-watch.{service,timer}` — systemd, every 30 s.
- `/etc/default/hack-deploy` — env config (dir, branch, deploy cmd,
  health URL, log file).

## Operate

```sh
journalctl -u deploy-watch.service -f     # live deploy log
systemctl stop deploy-watch.timer         # freeze deploys
```

The app `.env` lives on the server only — never committed. Put it in
the app dir before the first deploy tick or the health check will fail.

## Repo-side contract

`dev` and `main` must always be deployable: the watcher pulls whatever
the branch tip is. The merge gate in `$hack-agent-workflow:github-flow`
is what keeps bad code off those branches.
