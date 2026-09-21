# Plugin install + checkers, native Windows. Twin of module.sh:
# devin plugins install --local for each devin-pin plugin, full repair,
# then check_devin_setup.py.
$ErrorActionPreference = 'Stop'
. (Join-Path $env:HACK_LIB 'common.ps1')

function Find-Devin {
    $candidates = @(
        (Join-Path $env:HACK_LOCAL_BIN 'devin.exe'),
        (Join-Path $HOME '.local\bin\devin.exe')
    )
    $cmd = Get-Command devin -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    foreach ($c in $candidates) {
        if (Test-Path -LiteralPath $c -PathType Leaf) { return $c }
    }
    Die 'devin is required before plugins; run module 20'
}

function Find-Python {
    foreach ($name in 'python', 'python3') {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    Die 'python is required for the checkers; run .\setup.ps1'
}

function Install-Plugins([string]$DevinBin) {
    # devin-pin plugins[] is the SoT - local install links the repo tree.
    $pin = Get-Content -Raw -LiteralPath (Join-Path $env:HACK_REPO_ROOT 'build\devin-pin.json') | ConvertFrom-Json
    $ok = $true
    foreach ($plugin in $pin.plugins) {
        $dir = Join-Path $env:HACK_REPO_ROOT ($plugin.dir -replace '/', '\')
        $err = (& $DevinBin plugins install --local $dir -y 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0) {
            Write-Host $err
            $ok = $false
        }
    }
    if (-not $ok) {
        # Auth-gated on a fresh host; the checker still proves the repo side.
        Log 'WARN: devin plugins install --local failed (needs devin auth); run again on a logged-in host'
    } else {
        Log 'plugins installed (local) and synced with the repo'
    }
}

function Run-Repair {
    $python = Find-Python
    & $python (Join-Path $env:HACK_REPO_ROOT 'scripts\repair_devin_setup.py')
    if ($LASTEXITCODE -ne 0) { Die 'repair_devin_setup.py failed' }
}

function Run-Checkers {
    $python = Find-Python
    & $python (Join-Path $env:HACK_REPO_ROOT 'scripts\check_devin_setup.py')
    if ($LASTEXITCODE -ne 0) { Die 'check_devin_setup.py failed' }
}

switch ($args[0]) {
    'install' { Install-Plugins (Find-Devin); Run-Repair; Run-Checkers }
    'status' { Run-Checkers }
    'dry-run' { Log 'would install plugins via devin plugins install --local and run check_devin_setup.py' }
    default { if (-not $args[0]) { Run-Checkers } else { Die "unknown action: $($args[0])" } }
}
