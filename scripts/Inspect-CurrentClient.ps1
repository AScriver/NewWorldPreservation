[CmdletBinding()]
param([string]$ClientExecutable)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$steamRoots = @('C:\Program Files (x86)\Steam', 'C:\Program Files\Steam', 'D:\Steam', 'D:\SteamLibrary')
$steamRegistry = Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam' -Name SteamPath -ErrorAction SilentlyContinue
if ($null -ne $steamRegistry) { $steamRoots += $steamRegistry.SteamPath }
$libraryRoots = @()
foreach ($steamRoot in ($steamRoots | Select-Object -Unique)) {
    if (-not (Test-Path -LiteralPath $steamRoot -PathType Container)) { continue }
    $libraryRoots += $steamRoot
    $libraryFile = Join-Path $steamRoot 'steamapps\libraryfolders.vdf'
    if (Test-Path -LiteralPath $libraryFile -PathType Leaf) {
        $libraryText = Get-Content -LiteralPath $libraryFile -Raw
        foreach ($libraryMatch in [regex]::Matches($libraryText, '"path"\s+"([^"]+)"')) {
            $libraryRoots += $libraryMatch.Groups[1].Value.Replace('\\', '\')
        }
    }
}
$manifestChecks = @()
$clientCandidates = @()
foreach ($libraryRoot in ($libraryRoots | Select-Object -Unique)) {
    $manifestFile = Join-Path $libraryRoot 'steamapps\appmanifest_1063730.acf'
    $manifestPresent = Test-Path -LiteralPath $manifestFile -PathType Leaf
    $manifestChecks += [ordered]@{ library = $libraryRoot; manifestPresent = $manifestPresent }
    if (-not $manifestPresent) { continue }
    $manifestText = Get-Content -LiteralPath $manifestFile -Raw
    $installMatch = [regex]::Match($manifestText, '"installdir"\s+"([^"]+)"')
    $buildMatch = [regex]::Match($manifestText, '"buildid"\s+"([0-9]+)"')
    if ($installMatch.Success) {
        $installRoot = Join-Path $libraryRoot ('steamapps\common\' + $installMatch.Groups[1].Value)
        $clientCandidates += [ordered]@{ path = (Join-Path $installRoot 'Bin64\NewWorld.exe'); steamBuildId = $buildMatch.Groups[1].Value; source = 'Steam manifest' }
    }
}
if ($ClientExecutable) {
    if (-not (Test-Path -LiteralPath $ClientExecutable -PathType Leaf)) { throw 'Supplied client executable does not exist.' }
    $clientCandidates += [ordered]@{ path = (Resolve-Path -LiteralPath $ClientExecutable).Path; steamBuildId = $null; source = 'explicit path' }
}
$clientInstalls = @()
foreach ($clientCandidate in $clientCandidates) {
    if (-not (Test-Path -LiteralPath $clientCandidate.path -PathType Leaf)) { continue }
    $clientFile = Get-Item -LiteralPath $clientCandidate.path
    if ($clientFile.Name -ine 'NewWorld.exe') { throw 'Expected NewWorld.exe; refusing an unrelated binary.' }
    $clientInstalls += [ordered]@{
        executable = $clientFile.FullName
        source = $clientCandidate.source
        steamBuildId = $clientCandidate.steamBuildId
        fileVersion = $clientFile.VersionInfo.FileVersion
        productVersion = $clientFile.VersionInfo.ProductVersion
        bytes = $clientFile.Length
        sha256 = (Get-FileHash -LiteralPath $clientFile.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$configLocations = @()
foreach ($configRelativePath in @('AGS\New World', 'AGS\NewWorld', 'New World', 'NewWorld')) {
    foreach ($configBase in @($env:LOCALAPPDATA, $env:APPDATA)) {
        $configPath = Join-Path $configBase $configRelativePath
        $configLocations += [ordered]@{ path = $configPath; exists = (Test-Path -LiteralPath $configPath -PathType Container) }
    }
}
$clientProcesses = @(Get-Process -Name 'NewWorld' -ErrorAction SilentlyContinue | Select-Object -Property Id,Path)
$receipt = [ordered]@{
    observedAtUtc = [DateTime]::UtcNow.ToString('o')
    operation = 'Read-only Steam manifest, executable identity, config-directory existence and process metadata. No game files/logs/credentials copied; no client started.'
    scope = 'Registered Steam libraries, existing conventional C/D Steam roots, optional explicit executable. Not an exhaustive disk search.'
    manifestChecks = $manifestChecks
    installs = $clientInstalls
    configLocations = $configLocations
    runningClientProcesses = $clientProcesses
    clientTested = $false
}
$receiptPath = Join-Path $workspaceRoot 'research\evidence\current-client-discovery.json'
$receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receiptPath -Encoding utf8
$receipt | ConvertTo-Json -Depth 6
