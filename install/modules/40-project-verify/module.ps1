# Plugin install + checkers, native Windows. Twin of module.sh.
$ErrorActionPreference = 'Stop'
. (Join-Path $env:HACK_LIB 'common.ps1')

function Find-Codex {
    $localAppData = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path $HOME 'AppData\Local' }
    $candidates = @(
        (Join-Path $env:HACK_LOCAL_BIN 'codex.exe'),
        (Join-Path $localAppData 'Programs\OpenAI\Codex\bin\codex.exe')
    )
    $cmd = Get-Command codex -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    foreach ($c in $candidates) {
        if (Test-Path -LiteralPath $c -PathType Leaf) { return $c }
    }
    Die "codex is required before plugins; run module 20"
}

function Find-Python {
    foreach ($name in 'python', 'python3') {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    Die "python is required for the checkers; run .\setup.ps1"
}

function Install-Plugins([string]$CodexBin) {
    & $CodexBin plugin marketplace add $env:HACK_REPO_ROOT | Out-Null
    # Marketplace is the plugin SoT - install whatever it lists.
    $marketplace = Get-Content -Raw -LiteralPath (Join-Path $env:HACK_REPO_ROOT '.agents\plugins\marketplace.json') | ConvertFrom-Json
    foreach ($plugin in $marketplace.plugins) {
        & $CodexBin plugin add "$($plugin.name)@saint-tibo" | Out-Null
    }
    Log "plugins installed and synced with the repo"
}

function Run-Checkers {
    $python = Find-Python
    & $python (Join-Path $env:HACK_REPO_ROOT 'scripts\check_codex_setup.py')
    if ($LASTEXITCODE -ne 0) { Die "check_codex_setup.py failed" }
    & $python (Join-Path $env:HACK_REPO_ROOT 'scripts\check_stack.py')
    if ($LASTEXITCODE -ne 0) { Die "check_stack.py failed" }
}

$Action = if ($args.Count -gt 0) { $args[0] } else { 'status' }
switch ($Action) {
    'install' { Install-Plugins (Find-Codex); Run-Checkers }
    { $_ -in 'status' } { Run-Checkers }
    'dry-run' { Log "would install marketplace plugins and run the checkers" }
    default { Die "unknown action: $Action" }
}
