# Codex CLI, native Windows. Twin of module.sh: same pinned version, same
# sol profile file. Package-first like POSIX — the pinned release archive
# is sha256-verified and deterministic; official install.ps1 is only the
# fallback for triples without a package (#11).
$ErrorActionPreference = 'Stop'
. (Join-Path $env:HACK_LIB 'common.ps1')
. (Join-Path $env:HACK_LIB 'download.ps1')

$PinPath = Join-Path $env:HACK_REPO_ROOT 'build\codex-pin.json'
$StackPinPath = Join-Path $env:HACK_REPO_ROOT 'build\stack-pin.json'
$LocalAppData = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path $HOME 'AppData\Local' }
$CodexBinDir = Join-Path $LocalAppData 'Programs\OpenAI\Codex\bin'

function Get-CliVersion { return Get-HackPin $PinPath 'codex_cli' }

function Get-BinaryVersion([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $line = (& $Path --version 2>$null | Select-Object -First 1)
    if (-not $line) { return $null }
    $parts = @("$line" -split '\s+')
    if ($parts.Count -ge 2) { return $parts[1] }
    return $parts[0]
}

function Find-PinnedCodex {
    $wanted = Get-CliVersion
    $candidates = @(
        (Join-Path $env:HACK_LOCAL_BIN 'codex.exe'),
        (Join-Path $CodexBinDir 'codex.exe')
    )
    $cmd = Get-Command codex -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    foreach ($candidate in $candidates) {
        if ((Get-BinaryVersion $candidate) -eq $wanted) { return $candidate }
    }
    return $null
}

function Ensure-SolProfile {
    # Twin of the POSIX heredoc block: write ~/.codex/sol.config.toml from the
    # pin and strip legacy [profiles.sol] + '# hack-setup:' comment blocks from
    # the user config.toml.
    $secondary = Get-HackPin $StackPinPath 'models.secondary'
    $effort = Get-HackPin $StackPinPath 'models.reasoning_effort'
    $ctx = Get-HackPin $StackPinPath 'models.requested_context_window'
    $compact = Get-HackPin $StackPinPath 'models.requested_auto_compact'
    # CODEX_HOME wins, same resolver as the checkers (#11).
    $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
    New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
    $lines = @(
        '# hack-setup managed: secondary model profile for `codex --profile sol`.',
        '# Values come from build/stack-pin.json models.* - edit the pin, not this file.',
        "model = `"$secondary`"",
        "model_reasoning_effort = `"$effort`"",
        "review_model = `"$secondary`"",
        "model_context_window = $ctx",
        "model_auto_compact_token_limit = $compact"
    )
    [System.IO.File]::WriteAllText((Join-Path $codexHome 'sol.config.toml'), ($lines -join "`n") + "`n")

    # Legacy managed-line cleanup (foreign [hooks.state] tables are
    # preserved — issue #1) lives in repair_setup.py as the single writer.
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
    if ($py) {
        & $py.Source (Join-Path $env:HACK_REPO_ROOT 'scripts\repair_setup.py') --only config-cleanup | Out-Null
        if ($LASTEXITCODE -ne 0) { Log "WARN: config-cleanup repair failed (exit $LASTEXITCODE)" }
    }
    Log "installed user profile $codexHome\sol.config.toml ($secondary)"
}

function Ensure-Notify {
    # Twin of the POSIX ensure_notify: `notify` is a ROOT key — the
    # TOML-aware writer lives in repair_setup.py (single writer for
    # installer + repair). Without python this is a no-op; module 40
    # re-runs full repair after runtimes land (HS-01/HS-03/HS-05).
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
    if (-not $py) { return }
    & $py.Source (Join-Path $env:HACK_REPO_ROOT 'scripts\repair_setup.py') --only notify-block | Out-Null
    if ($LASTEXITCODE -ne 0) { Log "WARN: notify-block repair failed (exit $LASTEXITCODE)" }
}

function Run-Status {
    $wanted = Get-CliVersion
    $found = Find-PinnedCodex
    if ($found) { Log "Codex CLI $wanted already at $found"; return }
    Die "Codex CLI $wanted is not installed; run .\setup.ps1"
}

function Ensure-HookTrust {
    # Twin of POSIX ensure_hook_trust: refresh managed [hooks.state.*]
    # trusted_hash entries via the shared repair script when Python is
    # available (uv-managed or system).
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
    if (-not $py) { return }
    & $py.Source (Join-Path $env:HACK_REPO_ROOT 'scripts\repair_setup.py') --only hook-trust | Out-Null
    if ($LASTEXITCODE -ne 0) { Log "WARN: hook-trust repair failed (exit $LASTEXITCODE)" }
}

function Run-Install {
    $wanted = Get-CliVersion
    Ensure-SolProfile
    Ensure-Notify
    Ensure-HookTrust
    $found = Find-PinnedCodex
    if ($found) {
        Link-Bin $found $env:HACK_LOCAL_BIN | Out-Null
        Log "Codex CLI $wanted already present; linked $env:HACK_LOCAL_BIN\codex.exe"
        return
    }
    New-Item -ItemType Directory -Force -Path $env:HACK_CACHE | Out-Null
    # Package-first, same contract as module.sh: the pinned release
    # archive is sha256-verified and deterministic; install.ps1 is the
    # fallback when no package exists for this triple (#11 — the
    # official installer can exit 0 without producing a binary).
    $pkg = Get-CodexPackage $PinPath $env:HACK_TRIPLE
    if ($pkg) {
        Install-FromPackage $wanted $pkg
        return
    }
    $installer = Join-Path $env:HACK_CACHE 'codex-official-install.ps1'
    Log "no pinned package for $env:HACK_TRIPLE; downloading official install.ps1"
    Save-HackFile (Get-HackPin $PinPath 'installer_ps1.url') $installer
    Assert-HackSha256 $installer (Get-HackPin $PinPath 'installer_ps1.sha256')
    Log "running official installer (CODEX_RELEASE=$wanted)"
    $env:CODEX_RELEASE = $wanted
    $env:CODEX_NON_INTERACTIVE = '1'
    $env:CODEX_INSTALLER_USE_RELEASES_OPENAI_COM = 'false'
    $env:CODEX_INSTALL_DIR = $CodexBinDir
    # pwsh first — the installer targets modern PowerShell; Windows
    # PowerShell 5.1 is the fallback, not the default.
    $psHost = Get-Command pwsh -ErrorAction SilentlyContinue
    if (-not $psHost) { $psHost = Get-Command powershell -ErrorAction SilentlyContinue }
    if (-not $psHost) { Die "no pwsh/powershell for install.ps1 and no pinned package for $env:HACK_TRIPLE" }
    & $psHost.Source -NoProfile -ExecutionPolicy Bypass -File $installer
    $installed = Join-Path $CodexBinDir 'codex.exe'
    if ((Get-BinaryVersion $installed) -ne $wanted) {
        Die "official install.ps1 left no working codex.exe at $CodexBinDir (exit $LASTEXITCODE)"
    }
    Link-Bin $installed $env:HACK_LOCAL_BIN | Out-Null
    Log "Codex CLI $wanted installed"
}

function Install-FromPackage {
    # Pinned per-platform release package, sha256-verified — same
    # contract as module.sh (#11).
    param([string]$Wanted, $Pkg)
    $name = $Pkg.name
    $archive = Join-Path $env:HACK_CACHE $name
    Log "downloading pinned package $name"
    Save-HackFile $Pkg.url $archive
    Assert-HackSha256 $archive $Pkg.sha256
    $extract = Join-Path $env:HACK_CACHE "codex-pkg-$Wanted"
    if (Test-Path $extract) { Remove-Item -Recurse -Force $extract }
    New-Item -ItemType Directory -Force -Path $extract | Out-Null
    tar -xzf $archive -C $extract
    if ($LASTEXITCODE -ne 0) { Die "could not extract $name (tar exit $LASTEXITCODE)" }
    $exe = Get-ChildItem -Recurse -Filter 'codex.exe' $extract | Select-Object -First 1
    if (-not $exe) { Die "codex.exe missing from $name" }
    New-Item -ItemType Directory -Force -Path $CodexBinDir | Out-Null
    $installed = Join-Path $CodexBinDir 'codex.exe'
    Copy-Item $exe.FullName $installed -Force
    if ((Get-BinaryVersion $installed) -ne $Wanted) {
        Die "package Codex reported $(Get-BinaryVersion $installed), expected $Wanted"
    }
    Link-Bin $installed $env:HACK_LOCAL_BIN | Out-Null
    Log "Codex CLI $Wanted installed from pinned package"
}

function Run-DryRun {
    $wanted = Get-CliVersion
    $pkg = Get-CodexPackage $PinPath $env:HACK_TRIPLE
    if ($pkg) {
        Log "would verify $($pkg.url)"
        Log "would require sha256 $($pkg.sha256)"
        Log "would extract the pinned package into $CodexBinDir on $env:HACK_PLATFORM"
    } else {
        Log "would verify $(Get-HackPin $PinPath 'installer_ps1.url')"
        Log "would require sha256 $(Get-HackPin $PinPath 'installer_ps1.sha256')"
        Log "would run official install.ps1 with CODEX_RELEASE=$wanted on $env:HACK_PLATFORM"
    }
}

$Action = if ($args.Count -gt 0) { $args[0] } else { 'status' }
switch ($Action) {
    'install' { Run-Install }
    { $_ -in 'status' } { Run-Status }
    'dry-run' { Run-DryRun }
    default { Die "unknown action: $Action" }
}
