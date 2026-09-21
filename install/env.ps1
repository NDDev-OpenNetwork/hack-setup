# Dot-source after .\setup.ps1:  . .\install\env.ps1
# Puts repo-local and user-local pinned bins ahead of system PATH.
$HACK_ENV_ROOT = Split-Path -Parent $PSScriptRoot
# HACK_USER_BIN mirrors module 30's override - default ~/.local/bin.
$HACK_USER_BIN = if ($env:HACK_USER_BIN) { $env:HACK_USER_BIN } else { Join-Path $HOME '.local\bin' }
$env:PATH = "$HACK_ENV_ROOT\.local\bin;$HACK_USER_BIN;$HOME\.bun\bin;$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin;$env:PATH"
Remove-Variable HACK_ENV_ROOT, HACK_USER_BIN
