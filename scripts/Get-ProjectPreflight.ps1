[CmdletBinding()]
param(
    [ValidateSet('Text', 'Json')][string]$OutputFormat = 'Text',
    [string]$Receipt
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
$pythonArguments = @('-B')
if (-not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) {
    $pythonExecutable = (Get-Command py -ErrorAction Stop).Source
    $pythonArguments = @('-3.11', '-B')
}
$analyzerModule = Get-Module -ListAvailable -Name PSScriptAnalyzer | Sort-Object Version -Descending | Select-Object -First 1
$pythonArguments += @((Join-Path $PSScriptRoot 'project_preflight.py'), '--format', $OutputFormat.ToLowerInvariant(), '--powershell-version', $PSVersionTable.PSVersion.ToString())
if ($null -ne $analyzerModule) { $pythonArguments += @('--analyzer-version', $analyzerModule.Version.ToString()) }
if ($Receipt) { $pythonArguments += @('--receipt', $Receipt) }
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
& $pythonExecutable @pythonArguments
if ($LASTEXITCODE -ne 0) { throw 'Project preflight found missing or mismatched workspace requirements; review the report.' }
