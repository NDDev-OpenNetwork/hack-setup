#!/bin/sh
# codex notify hook — turn-complete ping. Invoked by user-level
# ~/.codex/config.toml `notify = ["<repo>/install/notify.sh"]` with one
# JSON arg. Silent no-op on any failure.
set -eu
payload=${1:-"{}"}
case "$payload" in *agent-turn-complete*) ;; *) exit 0 ;; esac
title="Codex"
body=$(printf '%s' "$payload" | python3 -c 'import json,sys; d=json.load(sys.stdin); print((d.get("last-assistant-message") or "turn complete")[:120])' 2>/dev/null | tr '"\\' '  ' || echo "turn complete")
if command -v osascript >/dev/null 2>&1; then
  osascript -e "display notification \"$body\" with title \"$title\"" 2>/dev/null || true
elif command -v notify-send >/dev/null 2>&1; then
  notify-send "$title" "$body" 2>/dev/null || true
elif command -v powershell.exe >/dev/null 2>&1; then
  powershell.exe -NoProfile -Command "New-BurntToastNotification -Text '$title','$body'" 2>/dev/null || true
fi
exit 0
