[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$observerPath = Join-Path $workspaceRoot 'scripts/Observe-CurrentClient.ps1'
$testDirectory = Join-Path $workspaceRoot ('.scratch/observer-test-' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $testDirectory -Force
$targetPath = Join-Path $testDirectory 'NewWorld.exe'
[IO.File]::WriteAllText($targetPath, 'offline identity test target')
$testStart = [datetime]::Parse('2026-10-02T15:13:35.000197Z', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind)
$script:mockProcesses = @([pscustomobject]@{ Id = 30848; Path = $null; StartTime = $testStart })
$script:mockConnections = @(
    [pscustomobject]@{ LocalAddress = '0.0.0.0'; LocalPort = 5000; RemoteAddress = '0.0.0.0'; RemotePort = 0; State = 'Bound' },
    [pscustomobject]@{ LocalAddress = '0.0.0.0'; LocalPort = 5001; RemoteAddress = '0.0.0.0'; RemotePort = 0; State = 'Listen' },
    [pscustomobject]@{ LocalAddress = '10.0.0.2'; LocalPort = 5002; RemoteAddress = '203.0.113.1'; RemotePort = 443; State = 'SynSent' },
    [pscustomobject]@{ LocalAddress = '10.0.0.2'; LocalPort = 5003; RemoteAddress = '203.0.113.2'; RemotePort = 443; State = 'Established' }
)
function Get-Process { [CmdletBinding()] param([string]$Name) return $script:mockProcesses }
function Get-NetTCPConnection { [CmdletBinding()] param([int]$OwningProcess) if ($OwningProcess -ne 30848) { throw 'Unexpected PID.' }; return $script:mockConnections }
function Assert-Test { param([bool]$Condition, [string]$Description) if (-not $Condition) { throw $Description } }
try {
    $missingPairRejected = $false
    try { . $observerPath -ClientExecutable $targetPath -LogPath (Join-Path $testDirectory 'invalid.jsonl') -Seconds 1 -ProcessId 30848 } catch { $missingPairRejected = $true }
    Assert-Test $missingPairRejected 'PID without expected start time must be rejected.'
    $defaultLog = Join-Path $testDirectory 'default.jsonl'
    . $observerPath -ClientExecutable $targetPath -LogPath $defaultLog -Seconds 1
    $defaultEvents = @(Get-Content -LiteralPath $defaultLog | ConvertFrom-Json)
    Assert-Test (@($defaultEvents | Where-Object state -eq 'CLIENT_IDENTITY_UNAVAILABLE').Count -eq 1) 'Default run must report inaccessible path once.'
    Assert-Test (@($defaultEvents | Where-Object state -eq 'CLIENT_START').Count -eq 0) 'Default run must reject inaccessible path.'

    $correlatedLog = Join-Path $testDirectory 'correlated.jsonl'
    . $observerPath -ClientExecutable $targetPath -LogPath $correlatedLog -Seconds 1 -ProcessId 30848 -ExpectedStartTimeUtc '2026-10-02T15:13:35.000197Z'
    $correlatedEvents = @(Get-Content -LiteralPath $correlatedLog | ConvertFrom-Json)
    Assert-Test (@($correlatedEvents | Where-Object state -eq 'CLIENT_START').Count -eq 1) 'Correlated run must record client.'
    $startEvent = @($correlatedEvents | Where-Object state -eq 'CLIENT_START')[0]
    Assert-Test ($startEvent.metadata.identity_mode -eq 'launch_correlated_name_pid_start_time_executable_path_unverified') 'Correlated identity must disclose path uncertainty.'
    Assert-Test ($null -eq $startEvent.PSObject.Properties['client_sha256']) 'Installed target hash must not be labeled as live client hash.'
    Assert-Test ($null -ne $startEvent.installed_target_sha256) 'Installed target hash must be labeled.'
    $socketEvents = @($correlatedEvents | Where-Object state -eq 'CONNECTION_ATTEMPT')
    Assert-Test ($socketEvents.Count -eq 2) 'Only non-Bound/Listen TCP sockets should be recorded.'
    Assert-Test (@($socketEvents | ForEach-Object { $_.metadata.tcp_state } | Sort-Object) -join ',' -eq 'Established,SynSent') 'TCP states must retain distinct names.'

    $staleLog = Join-Path $testDirectory 'stale.jsonl'
    . $observerPath -ClientExecutable $targetPath -LogPath $staleLog -Seconds 1 -ProcessId 30848 -ExpectedStartTimeUtc '2026-10-02T15:13:34.000197Z'
    $staleEvents = @(Get-Content -LiteralPath $staleLog | ConvertFrom-Json)
    Assert-Test (@($staleEvents | Where-Object state -eq 'CLIENT_START').Count -eq 0) 'Changed start time must reject reused PID.'
    Assert-Test (@($staleEvents | Where-Object state -eq 'CONNECTION_ATTEMPT').Count -eq 0) 'Changed start time must reject sockets.'
    Write-Output 'Offline observer identity checks passed.'
} finally {
    Get-ChildItem -LiteralPath $testDirectory -File | Remove-Item -Force
    Remove-Item -LiteralPath $testDirectory
}
