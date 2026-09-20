# Native Windows entry point. Mirrors ./setup; runs install/bootstrap.ps1.
# Usage:  powershell -ExecutionPolicy Bypass -File .\setup.ps1 [--dry-run|--status|--print-env]
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'install\bootstrap.ps1') @args
