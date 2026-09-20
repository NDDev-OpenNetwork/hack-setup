# Dot-source after .\setup.ps1:  . .\install\env.ps1
# Puts repo-local and user-local pinned bins ahead of system PATH.
$HACK_ENV_ROOT = Split-Path -Parent $PSScriptRoot
$env:PATH = "$HACK_ENV_ROOT\.local\bin;$HOME\.local\bin;$HOME\.bun\bin;$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin;$env:PATH"
Remove-Variable HACK_ENV_ROOT
