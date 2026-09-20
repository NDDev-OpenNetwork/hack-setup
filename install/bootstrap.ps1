# Native Windows bootstrap. Mirrors install/bootstrap.sh:
# discovers install/modules/<nn>-* in order and runs each module.ps1.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$HACK_INSTALL_HOME = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:HACK_REPO_ROOT = Split-Path -Parent $HACK_INSTALL_HOME
$env:HACK_LIB = Join-Path $HACK_INSTALL_HOME 'lib'
$env:HACK_CACHE = if ($env:HACK_CACHE) { $env:HACK_CACHE } else { Join-Path $env:HACK_REPO_ROOT '.cache\install' }
$env:HACK_LOCAL_BIN = if ($env:HACK_LOCAL_BIN) { $env:HACK_LOCAL_BIN } else { Join-Path $env:HACK_REPO_ROOT '.local\bin' }
$env:HACK_DRY_RUN = if ($env:HACK_DRY_RUN) { $env:HACK_DRY_RUN } else { '0' }
$env:HACK_ACTION = 'install'

. (Join-Path $env:HACK_LIB 'common.ps1')
. (Join-Path $env:HACK_LIB 'os.ps1')
. (Join-Path $env:HACK_LIB 'download.ps1')

foreach ($arg in $args) {
    switch ($arg) {
        '--dry-run'   { $env:HACK_DRY_RUN = '1' }
        '--status'    { $env:HACK_ACTION = 'status' }
        '--print-env' {
            Write-Host "`$env:PATH = `"$env:HACK_LOCAL_BIN;$HOME\.local\bin;`$env:PATH`""
            return
        }
        { $_ -in '--help', '-h' } {
            Write-Host "Usage: .\setup.ps1 [--dry-run] [--status] [--print-env]"
            Write-Host "Clone the repo, then run .\setup.ps1. Modules live under install/modules/."
            return
        }
        default { Die "unknown argument: $arg" }
    }
}

Hack-DetectOs
Log "platform $env:HACK_PLATFORM ($env:HACK_TRIPLE)"
Log "repo $env:HACK_REPO_ROOT"
if ($env:HACK_DRY_RUN -eq '1') { Log "dry-run; no downloads" }

# Same PATH the modules install into; env.ps1 mirrors this for the user shell.
$codexBinDir = Join-Path $env:LOCALAPPDATA 'Programs\OpenAI\Codex\bin'
$env:PATH = "$env:HACK_LOCAL_BIN;$HOME\.local\bin;$HOME\.bun\bin;$codexBinDir;$env:PATH"

$modulesRoot = Join-Path $HACK_INSTALL_HOME 'modules'
$moduleDirs = Get-ChildItem -LiteralPath $modulesRoot -Directory |
    Where-Object { $_.Name -match '^\d\d-' } | Sort-Object Name
if (-not $moduleDirs) { Die "no install/modules/<nn>-* directories found" }

foreach ($moduleDir in $moduleDirs) {
    if (Test-Path (Join-Path $moduleDir.FullName 'disabled')) { continue }
    $modulePs1 = Join-Path $moduleDir.FullName 'module.ps1'
    if (-not (Test-Path $modulePs1)) { Die "missing $modulePs1" }
    $action = $env:HACK_ACTION
    if ($env:HACK_DRY_RUN -eq '1' -and $env:HACK_ACTION -eq 'install') { $action = 'dry-run' }
    Log "module $($moduleDir.Name) ($action)"
    & $modulePs1 $action
}

if ($env:HACK_ACTION -eq 'install' -and $env:HACK_DRY_RUN -ne '1') {
    Log "done. load PATH: . $(Join-Path $HACK_INSTALL_HOME 'env.ps1')"
}
