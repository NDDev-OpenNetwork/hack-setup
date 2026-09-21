# Devin CLI + herdr, native Windows. Twin of module.sh: pinned Devin
# via the versioned setup.ps1, herdr from the sha256-verified release
# asset, managed user-config block via repair_devin_setup.py, then
# `herdr integration install devin`.
$ErrorActionPreference = 'Stop'
# pwsh 7.5+ turns native stderr into NativeCommandError under EAP=Stop
# before $LASTEXITCODE is readable — native installers report by exit code.
$PSNativeCommandUseErrorActionPreference = $false
. (Join-Path $env:HACK_LIB 'common.ps1')
. (Join-Path $env:HACK_LIB 'download.ps1')

$PinPath = Join-Path $env:HACK_REPO_ROOT 'build\devin-pin.json'
$LocalAppData = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path $HOME 'AppData\Local' }
$HerdrDir = Join-Path $LocalAppData 'Programs\herdr'
# Windows installer layout: %LOCALAPPDATA%\devin\cli\bin\devin.exe
$DevinBinDir = Join-Path $LocalAppData 'devin\cli\bin'

function Get-DevinVersion { return Get-HackPin $PinPath 'devin_cli.version' }
function Get-HerdrVersion { return Get-HackPin $PinPath 'herdr.version' }

function Get-BinaryVersion([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $line = (& $Path --version 2>$null | Select-Object -First 1)
    if (-not $line) { return $null }
    $parts = @("$line" -split '\s+')
    if ($parts.Count -ge 2) { return $parts[1] }
    return $parts[0]
}

function Find-PinnedBinary([string]$Name, [string]$Wanted) {
    $candidates = @(
        (Join-Path $env:HACK_LOCAL_BIN "$Name.exe"),
        (Join-Path $HOME ".local\bin\$Name.exe")
    )
    if ($Name -eq 'herdr') { $candidates += (Join-Path $HerdrDir 'herdr.exe') }
    if ($Name -eq 'devin') { $candidates += (Join-Path $DevinBinDir 'devin.exe') }
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    foreach ($candidate in $candidates) {
        if ((Get-BinaryVersion $candidate) -eq $Wanted) { return $candidate }
    }
    return $null
}

function Ensure-UserConfig {
    # Single writer: repair_devin_setup.py --only user-config manages the
    # model/subagents/auto_update/read_config_from block in the user config.
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) { return }
    & python (Join-Path $env:HACK_REPO_ROOT 'scripts\repair_devin_setup.py') --only user-config
    if ($LASTEXITCODE -ne 0) { Log 'WARN: user-config repair failed' }
}

function Ensure-Python3Shim {
    # .devin/hooks.v1.json invokes `python3` like POSIX. Windows has only
    # python.exe - drop a cmd shim into the managed .local\bin so project
    # hooks run identically on all three OSes.
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) { return }
    $shim = Join-Path $env:HACK_LOCAL_BIN 'python3.cmd'
    New-Item -ItemType Directory -Force -Path $env:HACK_LOCAL_BIN | Out-Null
    [System.IO.File]::WriteAllText($shim, "@echo off`r`npython %*`r`n")
}

function Ensure-Devin {
    $wanted = Get-DevinVersion
    $found = Find-PinnedBinary 'devin' $wanted
    if ($found) {
        Link-Bin $found $env:HACK_LOCAL_BIN
        Log "Devin CLI $wanted already present"
        return
    }
    $url = Get-HackPin $PinPath 'devin_cli.install_ps1'
    $installer = Join-Path $env:HACK_CACHE "devin-setup-$wanted.ps1"
    New-Item -ItemType Directory -Force -Path $env:HACK_CACHE | Out-Null
    # The setup script is versioned by URL; it installs under
    # %USERPROFILE%\.local\share\devin\cli and shims ~/.local/bin.
    Log "downloading pinned Devin installer for $wanted"
    Save-HackFile $url $installer
    # The installer ends with `& $EntryExe setup` - the interactive login
    # wizard. Auth is a per-member step and CI has no TTY, so strip the
    # tail; the version check below is the install proof.
    $filtered = "$installer.run.ps1"  # -File requires the .ps1 extension
    [System.IO.File]::WriteAllLines($filtered, @(
        [System.IO.File]::ReadAllLines($installer) | Where-Object { $_ -notmatch 'EntryExe\s+setup\s*$' }
    ))
    & powershell -NoProfile -ExecutionPolicy Bypass -File $filtered
    if ($LASTEXITCODE -ne 0) { Die 'Devin installer failed' }
    $devinBin = Join-Path $DevinBinDir 'devin.exe'
    $got = Get-BinaryVersion $devinBin
    if ($got -ne $wanted) { Die "installed Devin reported $got, expected $wanted" }
    Link-Bin $devinBin $env:HACK_LOCAL_BIN
    Log "Devin CLI $wanted installed"
}

function Ensure-Herdr {
    $wanted = Get-HerdrVersion
    $found = Find-PinnedBinary 'herdr' $wanted
    if ($found) {
        Link-Bin $found $env:HACK_LOCAL_BIN
        Log "herdr $wanted already present"
        return
    }
    $pin = Get-Content -Raw $PinPath | ConvertFrom-Json
    $pkg = $pin.herdr.packages.'windows-x86_64'
    $tag = $pin.herdr.tag
    $repo = $pin.herdr.repo
    $url = "https://github.com/$repo/releases/download/$tag/$($pkg.asset)"
    $archive = Join-Path $env:HACK_CACHE $pkg.asset
    New-Item -ItemType Directory -Force -Path $env:HACK_CACHE | Out-Null
    Log "downloading herdr $($pkg.asset) ($wanted)"
    Save-HackFile $url $archive
    Assert-HackSha256 $archive $pkg.sha256
    # The zip carries herdr.exe plus its ConPTY runtime; keep them together
    # in %LOCALAPPDATA%\Programs\herdr and expose a cmd shim (Windows x86_64
    # is the only supported herdr build - ARM64 runs it under emulation).
    New-Item -ItemType Directory -Force -Path $HerdrDir | Out-Null
    Expand-Archive -Force -Path $archive -DestinationPath $HerdrDir
    $herdrBin = Join-Path $HerdrDir 'herdr.exe'
    $got = Get-BinaryVersion $herdrBin
    if ($got -ne $wanted) { Die "installed herdr reported $got, expected $wanted" }
    $shim = Join-Path $env:HACK_LOCAL_BIN 'herdr.cmd'
    [System.IO.File]::WriteAllText($shim, "@echo off`r`n`"$herdrBin`" %*`r`n")
    Log "herdr $wanted installed"
}

function Ensure-Integration {
    # `herdr integration install devin` writes herdr-agent-state.ps1 and
    # adds hook entries to the devin USER config. Needs the config dir to
    # exist (Ensure-UserConfig creates it). Idempotent.
    $herdr = Get-Command herdr -ErrorAction SilentlyContinue
    if (-not $herdr) { Log 'WARN: herdr not on PATH; run herdr integration install devin manually'; return }
    & herdr integration install devin *> $null
    if ($LASTEXITCODE -ne 0) { Log 'WARN: herdr integration install devin failed; run it manually' }
}

function Run-Status {
    if (-not (Find-PinnedBinary 'devin' (Get-DevinVersion))) {
        Die "Devin CLI $(Get-DevinVersion) is not installed; run .\setup.ps1"
    }
    if (-not (Find-PinnedBinary 'herdr' (Get-HerdrVersion))) {
        Die "herdr $(Get-HerdrVersion) is not installed; run .\setup.ps1"
    }
    Log "Devin CLI $(Get-DevinVersion) + herdr $(Get-HerdrVersion) OK"
}

function Run-Install {
    Ensure-UserConfig
    Ensure-Python3Shim
    Ensure-Devin
    Ensure-Herdr
    Ensure-Integration
}

function Run-DryRun {
    $pin = Get-Content -Raw $PinPath | ConvertFrom-Json
    Log "would write managed block to %APPDATA%\devin\config.json (model $($pin.models.primary), subagents_enabled=false, auto_update=false)"
    Log "would run $($pin.devin_cli.install_ps1) to install Devin CLI $($pin.devin_cli.version)"
    $pkg = $pin.herdr.packages.'windows-x86_64'
    Log "would verify $($pkg.asset) sha256 $($pkg.sha256) and install herdr $($pin.herdr.version) for windows-x86_64"
    Log 'would run: herdr integration install devin'
}

switch ($args[0]) {
    'install' { Run-Install }
    'status' { Run-Status }
    'dry-run' { Run-DryRun }
    default { if (-not $args[0]) { Run-Status } else { Die "unknown action: $($args[0])" } }
}
