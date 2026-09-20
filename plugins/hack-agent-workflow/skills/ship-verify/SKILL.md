---
name: ship-verify
description: The hackathon delivery loop — build and restart on the server, then verify the live result online before calling anything done. Use after every code change meant for the running deployment, when the user says "ship", "deploy", "check it live", "is it up", or when a fix needs confirmation on the server.
---

# Ship and verify live

Local green is not done. The hackathon proof is the running service.
Loop per change:

1. **Ship**: get the change onto the server — push and pull there, or
   rsync/deploy per `deploy.pipeline`. No deploy script yet? Build one
   lazily: one `ssh`/`git pull`/`docker compose up -d --build` line is
   enough; do not scaffold CI for a two-day event.
2. **Build/restart on the server**: run the pinned build
   (`bun run build`, `docker compose up -d --build`, or the service
   restart command). Capture the exit code — a failed build is the
   result, not a detail.
3. **Verify live**: open the real surface. UI change → load the page
   (cmux browser surface or a plain fetch; check for the new element,
   not just HTTP 200). API change → `curl` the endpoint and read the
   response body. Worker change → tail the log for the expected line.
4. **On failure**: read the server log first (`docker compose logs
   --tail=50 <svc>` or journalctl), fix the root cause, ship again.
   Do not patch locally and re-deploy blindly — reproduce against the
   live instance.
5. **Report**: one line — what is live, the URL or endpoint checked,
   and any `hack:` corners still standing.

## Rules

- Verify the thing that changed, not a proxy for it: a 200 on `/` does
  not prove the new button renders.
- Check logs even on success the first time — silent warnings on a fresh
  deploy become 3am pages at demo time.
- Migrations and destructive operations on the server still need the
  owner's explicit go — speed never waives that.
- If the live check is impossible (no deploy yet, DNS pending), say so
  and state exactly what is unverified. Never claim live-verified from
  a local screenshot.
