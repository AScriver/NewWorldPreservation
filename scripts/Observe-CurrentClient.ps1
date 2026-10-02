[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ClientExecutable,
    [Parameter(Mandatory)][string]$LogPath,
    [ValidateRange(1,600)][int]$Seconds = 60
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$executablePath = (Resolve-Path -LiteralPath $ClientExecutable -ErrorAction Stop).Path
if ([IO.Path]::GetFileName($executablePath) -ine 'NewWorld.exe') { throw 'Expected NewWorld.exe.' }
$eventPath = [IO.Path]::GetFullPath($LogPath)
$privatePrefix = (Join-Path $workspaceRoot 'private') + [IO.Path]::DirectorySeparatorChar
$scratchPrefix = (Join-Path $workspaceRoot '.scratch') + [IO.Path]::DirectorySeparatorChar
if (-not ($eventPath.StartsWith($privatePrefix, [StringComparison]::OrdinalIgnoreCase) -or $eventPath.StartsWith($scratchPrefix, [StringComparison]::OrdinalIgnoreCase))) {
    throw 'Observation logs must stay in the workspace ignored private/ or .scratch/ directory.'
}
if (Test-Path -LiteralPath $eventPath) { throw 'Refusing to overwrite an earlier observation.' }
$null = New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($eventPath)) -Force
$eventStream = [IO.StreamWriter]::new([IO.FileStream]::new($eventPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::Read))
$observationRunId = [guid]::NewGuid().ToString()
$clientSha256 = (Get-FileHash -LiteralPath $executablePath -Algorithm SHA256).Hash.ToLowerInvariant()
$observedProcesses = [Collections.Generic.HashSet[string]]::new()
$observedConnections = [Collections.Generic.HashSet[string]]::new()
function Write-ClientObservation {
    param([string]$State, [hashtable]$Metadata)
    $clientEvent = [ordered]@{
        schema = 1
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        run_id = $observationRunId
        state = $State
        evidence_source = 'windows_process_tcp_table'
        client_sha256 = $clientSha256
        metadata = $Metadata
    }
    $eventStream.WriteLine(($clientEvent | ConvertTo-Json -Depth 5 -Compress))
    $eventStream.Flush()
}
try {
    Write-ClientObservation -State 'CLIENT_OBSERVER_STARTED' -Metadata @{ seconds = $Seconds; launches_client = $false; reads_credentials_or_game_logs = $false; polling_ms = 500 }
    $observationDeadline = [DateTime]::UtcNow.AddSeconds($Seconds)
    while ([DateTime]::UtcNow -lt $observationDeadline) {
        $matchingClients = @(Get-Process -Name 'NewWorld' -ErrorAction SilentlyContinue)
        foreach ($clientProcess in $matchingClients) {
            if (-not $clientProcess.Path -or $clientProcess.Path -ine $executablePath) { continue }
            $processIdentity = "$($clientProcess.Id):$($clientProcess.StartTime.ToUniversalTime().Ticks)"
            if ($observedProcesses.Add($processIdentity)) {
                Write-ClientObservation -State 'CLIENT_START' -Metadata @{ process_id = $clientProcess.Id; actual_process_start_utc = $clientProcess.StartTime.ToUniversalTime().ToString('o'); observation = 'matching_executable_process_seen_not_launched_by_observer' }
            }
            $tcpConnections = @(Get-NetTCPConnection -OwningProcess $clientProcess.Id -ErrorAction SilentlyContinue)
            foreach ($tcpConnection in $tcpConnections) {
                $connectionIdentity = "$processIdentity/$($tcpConnection.LocalAddress):$($tcpConnection.LocalPort)/$($tcpConnection.RemoteAddress):$($tcpConnection.RemotePort)/$($tcpConnection.State)"
                if (-not $observedConnections.Add($connectionIdentity)) { continue }
                Write-ClientObservation -State 'CONNECTION_ATTEMPT' -Metadata @{
                    process_id = $clientProcess.Id
                    local_address = $tcpConnection.LocalAddress
                    local_port = $tcpConnection.LocalPort
                    remote_address = $tcpConnection.RemoteAddress
                    remote_port = $tcpConnection.RemotePort
                    tcp_state = [string]$tcpConnection.State
                    observation = 'sampled_owned_tcp_socket_not_tls_or_authentication_proof'
                }
            }
        }
        Start-Sleep -Milliseconds 500
    }
    Write-ClientObservation -State 'CLIENT_OBSERVER_STOPPED' -Metadata @{ observed_process_count = $observedProcesses.Count; distinct_connection_state_count = $observedConnections.Count; dns_resolution_observed = $false; game_transport_observed = $false }
} finally {
    $eventStream.Dispose()
}
