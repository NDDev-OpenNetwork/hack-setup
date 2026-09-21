#!/bin/sh
# codex notify hook — turn-complete ping. Invoked by user-level
# ~/.codex/config.toml `notify = ["<repo>/install/notify.sh"]` with one
# JSON arg. Silent no-op on any failure.
set -eu
payload=${1:-"{}"}
case "$payload" in *agent-turn-complete*) ;; *) exit 0 ;; esac
title="Codex"

# Payload is data, never shell/script: one sanitizer bounds the text and
# strips characters that could break the osascript double-quoted string
# or the PowerShell single-quoted string downstream (issue #13).
body=$(python3 -c '
import json, sys
try:
    d = json.loads(sys.argv[1])
    m = d.get("last-assistant-message") or "turn complete"
except Exception:
    m = "turn complete"
m = str(m)[:120]
sys.stdout.write(m.replace(chr(34), " ").replace("\\", " ")
                 .replace("\n", " ").replace("\r", " "))
' "$payload" 2>/dev/null || true)
[ -n "${body:-}" ] || body="turn complete"

if command -v osascript >/dev/null 2>&1; then
  osascript -e "display notification \"$body\" with title \"$title\"" 2>/dev/null || true
elif command -v notify-send >/dev/null 2>&1; then
  notify-send "$title" "$body" 2>/dev/null || true
elif command -v powershell.exe >/dev/null 2>&1; then
  # PowerShell single-quoted strings escape ' as '' — escaping, not
  # interpolation, keeps model text inert.
  body_ps=$(printf '%s' "$body" | sed "s/'/''/g")
  powershell.exe -NoProfile -Command \
    "New-BurntToastNotification -Text '$title','$body_ps'" 2>/dev/null || true
fi
exit 0
