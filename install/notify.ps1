# codex notify hook — Windows twin of notify.sh. User-level
# ~/.codex/config.toml: notify = ["powershell","-NoProfile","-File","<this>"]
# Receives one JSON arg; silent no-op on any failure.
param([string]$Payload = '{}')
$ErrorActionPreference = 'SilentlyContinue'
if ($Payload -notmatch 'agent-turn-complete') { exit 0 }
try {
    $d = $Payload | ConvertFrom-Json
    $body = [string]$d.'last-assistant-message'
    if (-not $body) { $body = 'turn complete' }
    if ($body.Length -gt 120) { $body = $body.Substring(0, 120) }
    # Toast via the always-present balloon tip; BurntToast if installed.
    if (Get-Module -ListAvailable -Name BurntToast) {
        New-BurntToastNotification -Text 'Codex', $body
    } else {
        Add-Type -AssemblyName System.Windows.Forms
        $n = New-Object System.Windows.Forms.NotifyIcon
        $n.Icon = [System.Drawing.SystemIcons]::Information
        $n.Visible = $true
        $n.ShowBalloonTip(3000, 'Codex', $body, 'Info')
        Start-Sleep -Milliseconds 500
        $n.Dispose()
    }
} catch {}
exit 0
