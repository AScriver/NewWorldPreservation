[CmdletBinding()]
param([switch]$PreflightOnly)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExecutable)) { throw 'Initialize the isolated development environment first.' }
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
Push-Location -LiteralPath $workspaceRoot
try {
    $unitArguments = @('-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'tests\test_validation_gate.py')
    & $pythonExecutable @unitArguments
    if ($LASTEXITCODE -ne 0) { throw 'Original validation-gate tests failed.' }
    $validationArguments = @('scripts\validate_first_light.py')
    if ($PreflightOnly) { $validationArguments += '--preflight-only' }
    & $pythonExecutable @validationArguments
    if ($LASTEXITCODE -ne 0) { throw 'Offline First Light validation failed; inspect the private scratch diagnostics.' }
} finally {
    Pop-Location
}
