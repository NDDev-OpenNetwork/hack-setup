# Native Windows platform detection. The POSIX twin is lib/os.sh.

function Hack-DetectOs {
    $onWindows = ($env:OS -eq 'Windows_NT')
    if (-not $onWindows -and $PSVersionTable.PSVersion.Major -ge 6) {
        $onWindows = [bool]$IsWindows
    }
    if (-not $onWindows) {
        Die "install/bootstrap.ps1 is Windows-native; run ./setup on macOS/Linux/WSL"
    }
    if (-not $env:LOCALAPPDATA) {
        $env:LOCALAPPDATA = Join-Path $HOME 'AppData\Local'
    }
    $arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
    switch ("$arch") {
        'X64' {
            $env:HACK_PLATFORM = 'windows-x86_64'
            $env:HACK_TRIPLE = 'x86_64-pc-windows-msvc'
        }
        'Arm64' {
            Die "Windows arm64 has no pinned packages; supported native target is windows-x86_64 (WSL2 Ubuntu works on arm64 too)"
        }
        default { Die "unsupported Windows architecture: $arch" }
    }
}
