[CmdletBinding()]
param([string]$PythonExecutable)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$uvExecutable = (Get-Command uv -ErrorAction Stop).Source
if (-not $PythonExecutable) {
    $pythonLauncher = (Get-Command py -ErrorAction Stop).Source
    $launcherArguments = @('-3.11', '-c', 'import sys; print(sys.executable)')
    $PythonExecutable = & $pythonLauncher @launcherArguments
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 is required; pass -PythonExecutable for a supported interpreter.' }
}
$versionArguments = @('-c', 'import sys; print("%s.%s" % sys.version_info[:2])')
$pythonVersion = & $PythonExecutable @versionArguments
if ($LASTEXITCODE -ne 0 -or $pythonVersion -notin @('3.11', '3.12')) { throw 'Use Python 3.11 or 3.12, matching upstream CI.' }
$environmentRoot = Join-Path $workspaceRoot '.venv'
$environmentPython = Join-Path $environmentRoot 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $environmentRoot)) {
    $venvArguments = @('venv', '--python', $PythonExecutable, $environmentRoot)
    & $uvExecutable @venvArguments
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
} elseif (-not (Test-Path -LiteralPath $environmentPython)) {
    throw 'Existing .venv is not a usable Windows environment; it was left unchanged.'
}
$environmentVersion = & $environmentPython @versionArguments
if ($LASTEXITCODE -ne 0 -or $environmentVersion -ne $pythonVersion) { throw 'Existing .venv Python version differs; it was left unchanged.' }
$syncArguments = @('pip', 'sync', '--python', $environmentPython, '--require-hashes', (Join-Path $workspaceRoot 'requirements-dev.lock'))
& $uvExecutable @syncArguments
if ($LASTEXITCODE -ne 0) { throw 'Hash-pinned dependency sync failed.' }
$checkArguments = @('pip', 'check', '--python', $environmentPython)
& $uvExecutable @checkArguments
if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency check failed.' }
[pscustomobject]@{ State = 'ENVIRONMENT_READY'; Python = $environmentVersion; Environment = $environmentRoot; GlobalPackagesChanged = $false }
