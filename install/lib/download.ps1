# Download and SHA-256 helpers. PowerShell twin of lib/download.sh.

function Save-HackFile([string]$Url, [string]$Dest) {
    $parent = Split-Path -Parent $Dest
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    # Retry transient TLS/network flakes (schannel CRYPT_E_REVOCATION_OFFLINE
    # et al. hit CI runners); real failures still die after the last try.
    $attempts = 3
    for ($i = 1; $i -le $attempts; $i++) {
        if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
            & curl.exe -fsSL --proto '=https' --tlsv1.2 --max-redirs 5 $Url -o $Dest
            if ($LASTEXITCODE -eq 0) { return }
        } else {
            try { Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing; return }
            catch { if ($i -eq $attempts) { throw } }
        }
        if ($i -lt $attempts) {
            Write-Host "download attempt $i failed for $Url - retrying"
            Start-Sleep -Seconds (3 * $i)
            Remove-Item -LiteralPath $Dest -Force -ErrorAction SilentlyContinue
        }
    }
    Die "download failed: $Url"
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
