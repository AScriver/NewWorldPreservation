[CmdletBinding()]
param(
    [ValidateSet('staged','committed')][string]$Mode = 'staged'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) {
    throw 'Initialize the workspace development environment first.'
}
$argumentList = @('-B',(Join-Path $PSScriptRoot 'publish_hygiene.py'),'--repo',$workspaceRoot,'--mode',$Mode)
& $pythonExecutable @argumentList
if ($LASTEXITCODE -ne 0) { throw 'Publication hygiene rejected the candidate or could not finish; review the rule IDs above.' }
