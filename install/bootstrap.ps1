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
$env:HACK_MEMBER = if ($env:HACK_MEMBER) { $env:HACK_MEMBER } else { '' }
$env:HACK_TARGET_OS = if ($env:HACK_TARGET_OS) { $env:HACK_TARGET_OS } else { '' }

. (Join-Path $env:HACK_LIB 'common.ps1')
. (Join-Path $env:HACK_LIB 'os.ps1')
. (Join-Path $env:HACK_LIB 'download.ps1')

for ($i = 0; $i -lt $args.Count; $i++) {
    $arg = $args[$i]
    switch -Regex ($arg) {
        '^--?dry-run$'   { $env:HACK_DRY_RUN = '1' }
        '^--?status$'    { $env:HACK_ACTION = 'status' }
        '^--?member$'    {
            if ($i + 1 -ge $args.Count) { Die "--member needs a name (danil|ivan|artem)" }
            $env:HACK_MEMBER = $args[++$i]
        }
        '^--?member=(.+)$' { $env:HACK_MEMBER = $Matches[1] }
        '^--?member=$'   { Die "--member needs a name (danil|ivan|artem)" }
        { $_ -in '--danil', '--ivan', '--artem', '-danil', '-ivan', '-artem' } { $env:HACK_MEMBER = $_.TrimStart('-') }
        '^--?os$'        {
            if ($i + 1 -ge $args.Count) { Die "--os needs a value (macos|ubuntu|windows)" }
            $env:HACK_TARGET_OS = $args[++$i]
        }
        '^--?os=(.+)$'   { $env:HACK_TARGET_OS = $Matches[1] }
        '^--?os=$'       { Die "--os needs a value (macos|ubuntu|windows)" }
        '^--?print-env$' {
            $ub = if ($env:HACK_USER_BIN) { $env:HACK_USER_BIN } else { "$HOME\.local\bin" }
            Write-Host "`$env:PATH = `"$env:HACK_LOCAL_BIN;$ub;`$env:PATH`""
            return
        }
        { $_ -in '--help', '-h', '-help' } {
            Write-Host "Usage: .\setup.ps1 [--dry-run] [--status] [--print-env] [--member <danil|ivan|artem>] [--os <macos|ubuntu|windows>]"
            Write-Host "--member sets git identity + team defaults; --os must match this host (POSIX targets run ./setup inside WSL2 or on that host)."
            Write-Host "Single-dash PowerShell forms work too: -Member ivan, -Status, -Dry-Run (matching is case-insensitive)."
            return
        }
        default { Die "unknown argument: $arg" }
    }
}

Hack-DetectOs

# --os declares the install target; native Windows covers only windows.
# POSIX targets belong to ./setup inside WSL2 Ubuntu or on that host.
# Under --dry-run the flag instead previews that platform's plan.
$targetFamily = $null
switch -Regex ($env:HACK_TARGET_OS) {
    '^$'                    { }
    '^(macos|mac|darwin)$'  { $targetFamily = 'darwin' }
    '^(ubuntu|linux)$'      { $targetFamily = 'linux' }
    '^(windows|win)$'       { $targetFamily = 'windows' }
    default { Die "unknown --os $env:HACK_TARGET_OS (expected macos|ubuntu|windows)" }
}
if ($targetFamily -and $targetFamily -ne 'windows') {
    if ($env:HACK_DRY_RUN -ne '1') {
        Die "--os $env:HACK_TARGET_OS is POSIX: run ./setup inside WSL2 Ubuntu or on that host"
    }
    $preview = @{ darwin = 'darwin-arm64'; linux = 'linux-x86_64' }[$targetFamily]
    $env:HACK_PLATFORM = $preview
    $env:HACK_TRIPLE = @{ darwin = 'aarch64-apple-darwin'; linux = 'x86_64-unknown-linux-musl' }[$targetFamily]
    Log "dry-run preview for $preview (this host is windows)"
}

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
