# Pin Node LTS, bun, uv, and CPython on native Windows. Twin of module.sh.
$ErrorActionPreference = 'Stop'
. (Join-Path $env:HACK_LIB 'common.ps1')
. (Join-Path $env:HACK_LIB 'download.ps1')

$PinPath = Join-Path $env:HACK_REPO_ROOT 'build\stack-pin.json'
$UserBin = Join-Path $HOME '.local\bin'
$RuntimeRoot = if ($env:HACK_RUNTIME_ROOT) { $env:HACK_RUNTIME_ROOT } else { Join-Path $HOME '.local\share\hack-setup' }

function Pin-Get([string]$Path) { return Get-HackPin $PinPath $Path }

function Get-BinVersion([string]$Path, [string[]]$Argv) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $line = (& $Path @Argv 2>$null | Select-Object -First 1)
    if (-not $line) { return $null }
    $parts = @("$line" -split '\s+' | Where-Object { $_ -ne '' })
    $tok = if ($parts.Count -ge 2) { $parts[1] } else { $parts[0] }
    return $tok.TrimStart('v').Trim(',')
}

function Write-CmdShim([string]$Dest, [string]$Target) {
    [System.IO.File]::WriteAllText($Dest, "@echo off`r`n`"$Target`" %*`r`n")
}

function Install-Uv {
    $wanted = Pin-Get 'runtimes.uv.version'
    $local = Join-Path $env:HACK_LOCAL_BIN 'uv.exe'
    $user = Join-Path $UserBin 'uv.exe'
    if ((Get-BinVersion $local '--version') -eq $wanted) {
        Log "uv $wanted already at $local"
    } elseif ((Get-BinVersion $user '--version') -eq $wanted) {
        Link-Bin $user $env:HACK_LOCAL_BIN | Out-Null
        Log "uv $wanted linked from ~/.local/bin"
    } else {
        New-Item -ItemType Directory -Force -Path $env:HACK_CACHE, $UserBin | Out-Null
        $installer = Join-Path $env:HACK_CACHE 'uv-installer.ps1'
        Log "downloading official uv $wanted installer"
        Save-HackFile (Pin-Get 'runtimes.uv.installer_ps1.url') $installer
        Assert-HackSha256 $installer (Pin-Get 'runtimes.uv.installer_ps1.sha256')
        $env:UV_INSTALL_DIR = $UserBin
        $env:UV_NO_MODIFY_PATH = '1'
        $env:UV_PYTHON_BIN_DIR = $UserBin
        $psHost = Get-Command powershell -ErrorAction SilentlyContinue
        if (-not $psHost) { $psHost = Get-Command pwsh -ErrorAction SilentlyContinue }
        if (-not $psHost) { Die "powershell/pwsh is required to run uv-installer.ps1" }
        & $psHost.Source -NoProfile -ExecutionPolicy Bypass -File $installer
        if ($LASTEXITCODE -ne 0) { Die "uv-installer.ps1 failed (exit $LASTEXITCODE)" }
        if ((Get-BinVersion $user '--version') -ne $wanted) {
            Die "uv reported $(Get-BinVersion $user '--version'), expected $wanted"
        }
        Link-Bin $user $env:HACK_LOCAL_BIN | Out-Null
        Log "uv $wanted installed"
    }
    $uvx = Join-Path $UserBin 'uvx.exe'
    if (Test-Path $uvx) { Link-Bin $uvx $env:HACK_LOCAL_BIN | Out-Null }
}

function Install-Python {
    $wanted = Pin-Get 'runtimes.python.version'
    $py3 = Join-Path $env:HACK_LOCAL_BIN 'python3.exe'
    $py3cmd = Join-Path $env:HACK_LOCAL_BIN 'python3.cmd'
    if ((Get-BinVersion $py3 '--version') -eq $wanted -or (Get-BinVersion $py3cmd '--version') -eq $wanted) {
        Log "python $wanted already at $env:HACK_LOCAL_BIN\python3"
        return
    }
    $uv = Join-Path $env:HACK_LOCAL_BIN 'uv.exe'
    if (-not (Test-Path $uv)) { $uv = Join-Path $UserBin 'uv.exe' }
    if (-not (Test-Path $uv)) { Die "uv is required before python $wanted" }
    Log "uv python install $wanted --default"
    $env:UV_PYTHON_BIN_DIR = $UserBin
    & $uv python install $wanted --default
    if ($LASTEXITCODE -ne 0) { Die "uv python install $wanted failed" }
    $py = (& $uv python find $wanted | Select-Object -First 1)
    if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { Die "uv python find $wanted failed" }
    # uv --default writes real python.exe/python3.exe/python3.x.exe launchers
    # into UV_PYTHON_BIN_DIR. Fall back to .cmd shims if they are missing.
    foreach ($name in @('python3', 'python', "python$($wanted -replace '^(\d+\.\d+).*','$1')")) {
        $exe = Join-Path $UserBin "$name.exe"
        if (-not (Test-Path $exe)) { Write-CmdShim (Join-Path $UserBin "$name.cmd") $py }
        if (-not (Test-Path (Join-Path $env:HACK_LOCAL_BIN "$name.exe"))) {
            Write-CmdShim (Join-Path $env:HACK_LOCAL_BIN "$name.cmd") $py
        } else {
            Link-Bin (Join-Path $UserBin "$name.exe") $env:HACK_LOCAL_BIN | Out-Null
        }
    }
    Log "python $wanted linked"
}

function Install-Bun {
    $wanted = Pin-Get 'runtimes.bun.version'
    $local = Join-Path $env:HACK_LOCAL_BIN 'bun.exe'
    $bunx = Join-Path $env:HACK_LOCAL_BIN 'bunx.exe'
    if ((Get-BinVersion $local '--version') -eq $wanted) {
        if (-not (Test-Path $bunx)) {
            try { New-Item -ItemType HardLink -Path $bunx -Target $local | Out-Null }
            catch { Copy-Item -LiteralPath $local -Destination $bunx -Force }
        }
        Log "bun $wanted already at $local"
        return
    }
    New-Item -ItemType Directory -Force -Path $env:HACK_CACHE, (Join-Path $RuntimeRoot 'bun') | Out-Null
    $name = Pin-Get "runtimes.bun.packages.$env:HACK_PLATFORM.name"
    $archive = Join-Path $env:HACK_CACHE $name
    Log "downloading $name"
    Save-HackFile (Pin-Get "runtimes.bun.packages.$env:HACK_PLATFORM.url") $archive
    Assert-HackSha256 $archive (Pin-Get "runtimes.bun.packages.$env:HACK_PLATFORM.sha256")
    $extractDir = Join-Path $RuntimeRoot "bun\$wanted"
    Remove-Item -LiteralPath $extractDir -Recurse -Force -ErrorAction SilentlyContinue
    Expand-Archive -LiteralPath $archive -DestinationPath $extractDir -Force
    $bunBin = Get-ChildItem -LiteralPath $extractDir -Recurse -Filter 'bun.exe' | Select-Object -First 1
    if (-not $bunBin) { Die "bun.exe missing from $name" }
    if ((Get-BinVersion $bunBin.FullName '--version') -ne $wanted) {
        Die "bun reported $(Get-BinVersion $bunBin.FullName '--version'), expected $wanted"
    }
    # bunx is the same binary dispatched on argv[0] basename (official Windows
    # zip ships bun.exe only).
    Link-Bin $bunBin.FullName $UserBin | Out-Null
    $bunx = Join-Path $UserBin 'bunx.exe'
    Remove-Item -LiteralPath $bunx -Force -ErrorAction SilentlyContinue
    try { New-Item -ItemType HardLink -Path $bunx -Target $bunBin.FullName | Out-Null }
    catch { Copy-Item -LiteralPath $bunBin.FullName -Destination $bunx -Force }
    Link-Bin $bunBin.FullName $env:HACK_LOCAL_BIN | Out-Null
    Link-Bin $bunx $env:HACK_LOCAL_BIN | Out-Null
    Log "bun $wanted installed"
}

function Install-Node {
    $wanted = Pin-Get 'runtimes.node.version'
    $local = Join-Path $env:HACK_LOCAL_BIN 'node.exe'
    if ((Get-BinVersion $local '--version') -eq $wanted) { Log "node $wanted already at $local"; return }
    New-Item -ItemType Directory -Force -Path $env:HACK_CACHE | Out-Null
    $name = Pin-Get "runtimes.node.packages.$env:HACK_PLATFORM.name"
    $archive = Join-Path $env:HACK_CACHE $name
    Log "downloading $name"
    Save-HackFile (Pin-Get "runtimes.node.packages.$env:HACK_PLATFORM.url") $archive
    Assert-HackSha256 $archive (Pin-Get "runtimes.node.packages.$env:HACK_PLATFORM.sha256")
    $extractRoot = Join-Path $RuntimeRoot 'node'
    New-Item -ItemType Directory -Force -Path $extractRoot | Out-Null
    Expand-Archive -LiteralPath $archive -DestinationPath $extractRoot -Force
    $prefix = Join-Path $extractRoot ($name -replace '\.zip$', '')
    $nodeExe = Join-Path $prefix 'node.exe'
    if (-not (Test-Path $nodeExe)) { Die "node.exe missing from $name" }
    if ((Get-BinVersion $nodeExe '--version') -ne $wanted) {
        Die "node reported $(Get-BinVersion $nodeExe '--version'), expected $wanted"
    }
    Link-Bin $nodeExe $UserBin | Out-Null
    Link-Bin $nodeExe $env:HACK_LOCAL_BIN | Out-Null
    # Parity with POSIX npm/npx symlinks: .cmd shims into the extracted dir.
    foreach ($tool in @('npm', 'npx')) {
        $real = Join-Path $prefix "$tool.cmd"
        if (Test-Path $real) {
            Write-CmdShim (Join-Path $UserBin "$tool.cmd") $real
            Write-CmdShim (Join-Path $env:HACK_LOCAL_BIN "$tool.cmd") $real
        }
    }
    Log "node $wanted installed"
}

function Invoke-McpWarm {
    $serenaV = Pin-Get 'mcp.serena.version'
    $shadcnV = Pin-Get 'frontend.shadcn.version'
    $uvx = Join-Path $env:HACK_LOCAL_BIN 'uvx.exe'
    if (-not (Test-Path $uvx)) { $uvx = Join-Path $UserBin 'uvx.exe' }
    if (-not (Test-Path $uvx)) { Die "uvx is required to warm the serena MCP cache" }
    Log "warming serena-agent $serenaV (uvx cache)"
    & $uvx --from "serena-agent==$serenaV" serena --version | Out-Null
    if ($LASTEXITCODE -ne 0) { Die "serena-agent $serenaV failed to resolve via uvx" }
    $bunx = Join-Path $env:HACK_LOCAL_BIN 'bunx.exe'
    if (-not (Test-Path $bunx)) { Die "bunx is required to warm the shadcn MCP cache" }
    Log "warming shadcn $shadcnV (bunx cache)"
    & $bunx "shadcn@$shadcnV" --version | Out-Null
    if ($LASTEXITCODE -ne 0) { Die "shadcn $shadcnV failed to resolve via bunx" }
}

function Run-Install {
    Install-Uv
    Install-Python
    Install-Bun
    Install-Node
    Invoke-McpWarm
}

function Run-Status {
    $nodeV = Pin-Get 'runtimes.node.version'
    $bunV = Pin-Get 'runtimes.bun.version'
    $uvV = Pin-Get 'runtimes.uv.version'
    $pyV = Pin-Get 'runtimes.python.version'
    if ((Get-BinVersion (Join-Path $env:HACK_LOCAL_BIN 'uv.exe') '--version') -ne $uvV) { Die "uv $uvV missing; run .\setup.ps1" }
    $pyOk = (Get-BinVersion (Join-Path $env:HACK_LOCAL_BIN 'python3.exe') '--version') -eq $pyV -or
            (Get-BinVersion (Join-Path $env:HACK_LOCAL_BIN 'python3.cmd') '--version') -eq $pyV
    if (-not $pyOk) { Die "python $pyV missing; run .\setup.ps1" }
    if ((Get-BinVersion (Join-Path $env:HACK_LOCAL_BIN 'bun.exe') '--version') -ne $bunV) { Die "bun $bunV missing; run .\setup.ps1" }
    if ((Get-BinVersion (Join-Path $env:HACK_LOCAL_BIN 'node.exe') '--version') -ne $nodeV) { Die "node $nodeV missing; run .\setup.ps1" }
    Log "runtimes ok (node $nodeV, bun $bunV, python $pyV, uv $uvV)"
}

function Run-DryRun {
    Log "would install uv $(Pin-Get 'runtimes.uv.version')"
    Log "would uv python install $(Pin-Get 'runtimes.python.version') --default"
    Log "would install bun $(Pin-Get 'runtimes.bun.version') ($env:HACK_PLATFORM)"
    Log "would install node $(Pin-Get 'runtimes.node.version') ($env:HACK_PLATFORM)"
    Log "would warm MCP caches: serena-agent $(Pin-Get 'mcp.serena.version'), shadcn $(Pin-Get 'frontend.shadcn.version')"
}

$Action = if ($args.Count -gt 0) { $args[0] } else { 'status' }
switch ($Action) {
    'install' { Run-Install }
    { $_ -in 'status' } { Run-Status }
    'dry-run' { Run-DryRun }
    default { Die "unknown action: $Action" }
}
