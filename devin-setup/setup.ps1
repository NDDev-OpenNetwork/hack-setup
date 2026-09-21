# Native Windows entry point for the Devin CLI setup. Mirrors ./setup.
# Usage:  powershell -ExecutionPolicy Bypass -File .\setup.ps1 [--dry-run|--status|--print-env] [--member <danil|ivan|artem>] [--os windows]
#         (single-dash forms -Member/-Status/... work too)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'install\bootstrap.ps1') @args
