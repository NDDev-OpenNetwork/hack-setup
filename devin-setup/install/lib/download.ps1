# Download and SHA-256 helpers. PowerShell twin of lib/download.sh.

function Save-HackFile([string]$Url, [string]$Dest) {
    $parent = Split-Path -Parent $Dest
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
        & curl.exe -fsSL --proto '=https' --tlsv1.2 --max-redirs 5 $Url -o $Dest
        if ($LASTEXITCODE -ne 0) { Die "download failed: $Url" }
        return
    }
    Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing
}

function Get-HackSha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-HackSha256([string]$Path, [string]$Expected) {
    $actual = Get-HackSha256 $Path
    if ($actual -ne $Expected) {
        Remove-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
        Die "checksum mismatch for $Path (expected $Expected, got $actual); file removed"
    }
}
