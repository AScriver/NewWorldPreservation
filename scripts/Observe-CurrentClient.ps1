[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ClientExecutable,
    [Parameter(Mandatory)][string]$LogPath,
    [ValidateRange(1,600)][int]$Seconds = 60,
    [int]$ProcessId,
    [string]$ExpectedStartTimeUtc
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($PSBoundParameters.ContainsKey('ProcessId') -ne $PSBoundParameters.ContainsKey('ExpectedStartTimeUtc')) {
    throw 'ProcessId and ExpectedStartTimeUtc must be supplied together.'
}
$useLaunchCorrelation = $PSBoundParameters.ContainsKey('ProcessId')
if ($useLaunchCorrelation) {
    if ($ProcessId -le 0 -or $ExpectedStartTimeUtc -notmatch 'Z$') { throw 'Expected a positive ProcessId and UTC start time ending in Z.' }
    $expectedStart = [DateTimeOffset]::Parse($ExpectedStartTimeUtc, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind)
}
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
$installedTargetSha256 = (Get-FileHash -LiteralPath $executablePath -Algorithm SHA256).Hash.ToLowerInvariant()
$observedProcesses = [Collections.Generic.HashSet[string]]::new()
$inaccessiblePaths = [Collections.Generic.HashSet[int]]::new()
$observedConnections = [Collections.Generic.HashSet[string]]::new()
function Write-ClientObservation {
    param([string]$State, [hashtable]$Metadata)
    $clientEvent = [ordered]@{
        schema = 1
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        run_id = $observationRunId
        state = $State
        evidence_source = 'windows_process_tcp_table'
        installed_target_sha256 = $installedTargetSha256
        metadata = $Metadata
    }
    $eventStream.WriteLine(($clientEvent | ConvertTo-Json -Depth 5 -Compress))
    $eventStream.Flush()
}
try {
    Write-ClientObservation -State 'CLIENT_OBSERVER_STARTED' -Metadata @{ seconds = $Seconds; launches_client = $false; reads_credentials_or_game_logs = $false; polling_ms = 500; installed_target_path = $executablePath; identity_mode = $(if ($useLaunchCorrelation) { 'launch_correlated_name_pid_start_time_executable_path_unverified' } else { 'matching_executable_path' }) }
    $observationDeadline = [DateTime]::UtcNow.AddSeconds($Seconds)
    while ([DateTime]::UtcNow -lt $observationDeadline) {
        $matchingClients = @(Get-Process -Name 'NewWorld' -ErrorAction SilentlyContinue)
        foreach ($clientProcess in $matchingClients) {
            $clientPath = $null
            try { $clientPath = $clientProcess.Path } catch { }
            if (-not $clientPath -and $inaccessiblePaths.Add($clientProcess.Id)) {
                Write-ClientObservation -State 'CLIENT_IDENTITY_UNAVAILABLE' -Metadata @{ process_id = $clientProcess.Id; reason = 'executable_path_unavailable'; observation = 'same_name_process_path_could_not_be_verified' }
            }
            if ($useLaunchCorrelation) {
                if ($clientProcess.Id -ne $ProcessId) { continue }
            } elseif (-not $clientPath -or $clientPath -ine $executablePath) { continue }
            if ($clientPath -and $clientPath -ine $executablePath) { continue }
            try { $clientStart = $clientProcess.StartTime.ToUniversalTime() } catch { continue }
            if ($useLaunchCorrelation -and $clientStart.Ticks -ne $expectedStart.UtcDateTime.Ticks) { continue }
            $processIdentity = "$($clientProcess.Id):$($clientStart.Ticks)"
            $identityMode = if ($useLaunchCorrelation) { 'launch_correlated_name_pid_start_time_executable_path_unverified' } else { 'matching_executable_path' }
            if ($observedProcesses.Add($processIdentity)) {
                Write-ClientObservation -State 'CLIENT_START' -Metadata @{ process_id = $clientProcess.Id; actual_process_start_utc = $clientStart.ToString('o'); identity_mode = $identityMode; executable_path_observed = [bool]$clientPath; observation = 'matching_process_seen_not_launched_by_observer' }
            }
            $tcpConnections = @(Get-NetTCPConnection -OwningProcess $clientProcess.Id -ErrorAction SilentlyContinue)
            foreach ($tcpConnection in $tcpConnections) {
                $tcpState = [string]$tcpConnection.State
                if ($tcpState -in @('Bound', 'Listen')) { continue }
                $connectionIdentity = "$processIdentity/$($tcpConnection.LocalAddress):$($tcpConnection.LocalPort)/$($tcpConnection.RemoteAddress):$($tcpConnection.RemotePort)/$tcpState"
                if (-not $observedConnections.Add($connectionIdentity)) { continue }
                Write-ClientObservation -State 'CONNECTION_ATTEMPT' -Metadata @{
                    process_id = $clientProcess.Id
                    local_address = $tcpConnection.LocalAddress
                    local_port = $tcpConnection.LocalPort
                    remote_address = $tcpConnection.RemoteAddress
                    remote_port = $tcpConnection.RemotePort
                    tcp_state = $tcpState
                    identity_mode = $identityMode
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
