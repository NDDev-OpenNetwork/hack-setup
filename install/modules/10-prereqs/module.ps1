# Prereqs, native Windows. Twin of module.sh — no host python needed:
# pin reads use ConvertFrom-Json, hashing uses Get-FileHash, tar.exe ships
# with Windows 10+ and Expand-Archive handles zips.
$ErrorActionPreference = 'Stop'
. (Join-Path $env:HACK_LIB 'common.ps1')

function Run-Status {
    Require-Cmd tar
    Require-Cmd git
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Die "gh (GitHub CLI) is required for the github-first workflow; winget install GitHub.cli then gh auth login"
    }
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Die "PowerShell 5.1+ is required (found $($PSVersionTable.PSVersion))"
    }
    Log "prereqs ok (powershell $($PSVersionTable.PSVersion))"
}

$Action = if ($args.Count -gt 0) { $args[0] } else { 'status' }
switch ($Action) {
    { $_ -in 'install', 'status' } { Run-Status }
    'dry-run' { Log "would require tar, git, gh; powershell 5.1+" }
    default { Die "unknown action: $Action" }
}
