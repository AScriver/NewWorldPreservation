[CmdletBinding()]
param(
    [ValidateSet('workspace','fixtures-static','protocol-loopback','windows-native','tooling','powershell','rep-readonly','frida-trial','upstream','all')]
    [Alias('Profile')]
    [string]$OfflineProfile = 'workspace',
    [switch]$ListProfiles
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) {
    throw 'Initialize the workspace development environment first.'
}
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$argumentList = @('-B', (Join-Path $PSScriptRoot 'validate_offline.py'))
if ($ListProfiles) { $argumentList += '--list-profiles' }
else { $argumentList += @('--profile', $OfflineProfile) }
& $pythonExecutable @argumentList
if ($LASTEXITCODE -ne 0) {
    throw "Offline validation failed for profile $OfflineProfile; inspect the reported ignored run receipt."
}
