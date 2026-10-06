[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ArchiveRoot,
    [string]$ClientRoot = 'C:\Program Files (x86)\Steam\steamapps\common\New World',
    [string]$SteamRoot = 'C:\Program Files (x86)\Steam'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
$clientExecutable = Join-Path $ClientRoot 'Bin64\NewWorld.exe'
if (@(Get-Process -Name NewWorld -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Archive requires no running NewWorld process; leave unrelated processes alone.'
}
$clientVersion = (Get-Item -LiteralPath $clientExecutable).VersionInfo.FileVersion
$argumentList = @('-B', (Join-Path $PSScriptRoot 'preserve_owned_client.py'),
    '--client-root', $ClientRoot, '--archive-root', $ArchiveRoot,
    '--steam-manifest', (Join-Path $SteamRoot 'steamapps\appmanifest_1063730.acf'),
    '--version', $clientVersion)
$steamExecutable = Join-Path $SteamRoot 'steam.exe'
$argumentList += @('--dependency', $steamExecutable)
$commonRedist = Join-Path $SteamRoot 'steamapps\common\Steamworks Shared\_CommonRedist'
if (Test-Path -LiteralPath $commonRedist -PathType Container) {
    $argumentList += @('--dependency', $commonRedist)
}
& $pythonExecutable @argumentList
if ($LASTEXITCODE -ne 0) { throw 'Private static archive did not verify; retain partial output as unverified.' }
