# Shared helpers for install/bootstrap.ps1 and modules. PowerShell 5.1+ safe.

function Log([string]$Message) {
    Write-Host "==> $Message"
}

function Die([string]$Message) {
    # throw (not exit) so an interactive .\setup.ps1 does not close the shell;
    # under powershell -File an unhandled throw still yields exit code 1.
    throw "ERROR: $Message"
}

function Require-Cmd([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Die "$Name is required"
    }
}

function Get-HackPin([string]$Path, [string]$DotPath) {
    $obj = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    foreach ($part in $DotPath.Split('.')) {
        if ($null -eq $obj -or -not ($obj.PSObject.Properties.Name -contains $part)) {
            Die "pin path $DotPath missing in $Path"
        }
        $obj = $obj.$part
    }
    return $obj
}

function Get-CodexPackage([string]$PinPath, [string]$Triple) {
    $pkgs = (Get-Content -Raw -LiteralPath $PinPath | ConvertFrom-Json).packages
    foreach ($prop in $pkgs.PSObject.Properties) {
        if ($prop.Value.triple -eq $Triple) { return $prop.Value }
    }
    return $null
}

function Link-Bin([string]$Source, [string]$DestDir) {
    # POSIX uses symlinks; on Windows use a hardlink, fall back to a copy
    # (hardlinks need same-volume source and dest).
    New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
    $dest = Join-Path $DestDir (Split-Path -Leaf $Source)
    if ($Source -eq $dest) { return $dest }
    Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
    try {
        New-Item -ItemType HardLink -Path $dest -Target $Source | Out-Null
    } catch {
        Copy-Item -LiteralPath $Source -Destination $dest -Force
    }
    return $dest
}
