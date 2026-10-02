[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) { throw 'Initialize the workspace development environment first.' }
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$validationArguments = @((Join-Path $PSScriptRoot 'validate_connectivity.py'))
& $pythonExecutable @validationArguments
if ($LASTEXITCODE -ne 0) { throw 'Connectivity control tests failed; see ignored scratch diagnostics.' }
$cliArguments = @((Join-Path $PSScriptRoot 'verify_probe_cli.py'))
& $pythonExecutable @cliArguments
if ($LASTEXITCODE -ne 0) { throw 'Probe CLI lifecycle control failed; see ignored scratch diagnostics.' }
$instrumentationArguments = @((Join-Path $PSScriptRoot 'validate_connectivity.py'), '--profile', 'instrumentation')
& $pythonExecutable @instrumentationArguments
if ($LASTEXITCODE -ne 0) { throw 'Connectivity instrumentation tests failed; see ignored scratch diagnostics.' }
$observerTestPath = Join-Path $workspaceRoot 'tests\test_observe_current_client.ps1'
& 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1' -Path $observerTestPath -Execute
