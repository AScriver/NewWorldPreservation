[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$RunDirectory,
    [ValidateRange(5,900)][int]$Seconds = 600,
    [switch]$LaunchThroughSteam,
    [string]$ClientRoot = 'C:\Program Files (x86)\Steam\steamapps\common\New World',
    [string]$SteamRoot = 'C:\Program Files (x86)\Steam'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'OfficialObservation.psm1') -Force
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
$collectorPath = Join-Path $PSScriptRoot 'official_session_metadata.py'
$clientExecutable = Join-Path $ClientRoot 'Bin64\NewWorld.exe'
$targetDigest = (Get-FileHash -LiteralPath $clientExecutable -Algorithm SHA256).Hash.ToLowerInvariant()
if ($targetDigest -ne '8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e') { throw 'Owned archived-build hash mismatch.' }
if (@(Get-Process -Name NewWorld -ErrorAction SilentlyContinue).Count -gt 0) { throw 'Cold observation needs the game closed normally first.' }
$environmentReceipt = Test-OfficialObservationEnvironment
if (-not $environmentReceipt.ready) { throw 'Routing/environment preflight refused; no system settings changed.' }
$clientVersion = (Get-Item -LiteralPath $clientExecutable).VersionInfo.FileVersion
$armArguments = @('-B', $collectorPath, 'arm', '--run', $RunDirectory,
    '--log', (Join-Path $env:LOCALAPPDATA 'AGS\New World\Game.log'),
    '--steam-manifest', (Join-Path $SteamRoot 'steamapps\appmanifest_1063730.acf'),
    '--executable', $clientExecutable, '--version', $clientVersion)
& $pythonExecutable @armArguments
if ($LASTEXITCODE -ne 0) { throw 'Official metadata arm failed.' }
$runPath = [IO.Path]::GetFullPath($RunDirectory)
$ownershipPath = Join-Path $runPath 'resource-ownership.json'
$transportPath = Join-Path $runPath 'transport.jsonl'
if ((Test-Path -LiteralPath $ownershipPath) -or (Test-Path -LiteralPath $transportPath)) { throw 'Resource output already exists.' }
$collectorProcess = Get-Process -Id $PID
$notBeforeUtc = [datetime]::UtcNow
$ownership = [ordered]@{ schema = 1; collector_process_id = $PID;
    collector_start_utc = $collectorProcess.StartTime.ToUniversalTime().ToString('o');
    armed_utc = $notBeforeUtc.ToString('o'); duration_seconds = $Seconds;
    environment = $environmentReceipt; installed_image_sha256 = $targetDigest;
    launch_mode = $(if ($LaunchThroughSteam) { 'ordinary_steam_applaunch' } else { 'user_manual_steam_launch' });
    client_identity = $null; client_termination_performed = $false; raw_packets_or_process_memory_read = $false;
    collector_closed = $false; end_reason = 'not_ended' }
$ownership | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ownershipPath -Encoding utf8
$transportStream = [IO.StreamWriter]::new([IO.FileStream]::new($transportPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read))
$stopwatch = [Diagnostics.Stopwatch]::StartNew()
$selectedIdentity = $null
$sampleCount = 0
try {
    if ($LaunchThroughSteam) {
        $steamExecutable = Join-Path $SteamRoot 'steam.exe'
        $steamArguments = @('-applaunch','1063730')
        $null = Start-Process -FilePath $steamExecutable -ArgumentList $steamArguments -WindowStyle Hidden
    }
    Write-Output 'OFFICIAL_OBSERVER_READY: log categories and owned socket tables only; login and recordings are manual.'
    while ($stopwatch.Elapsed.TotalSeconds -lt $Seconds) {
        if (Test-Path -LiteralPath (Join-Path $runPath 'stop.request')) { $ownership.end_reason = 'owned_stop_request'; break }
        $candidates = @(Get-Process -Name NewWorld -ErrorAction SilentlyContinue)
        if ($candidates.Count -gt 1) { $ownership.end_reason = 'ambiguous_game_processes'; break }
        if ($candidates.Count -eq 1) {
            $candidateIdentity = Get-OfficialProcessIdentity -Process $candidates[0] -ExpectedPath $clientExecutable -NotBeforeUtc $notBeforeUtc
            if ($candidateIdentity.state -ne 'matched') { $ownership.end_reason = $candidateIdentity.state; break }
            if ($null -eq $selectedIdentity) {
                $selectedIdentity = $candidateIdentity
                $ownership.client_identity = $candidateIdentity
                $ownership | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ownershipPath -Encoding utf8
            } elseif ($candidateIdentity.process_id -ne $selectedIdentity.process_id -or $candidateIdentity.start_ticks -ne $selectedIdentity.start_ticks) {
                $ownership.end_reason = 'game_process_identity_changed'; break
            }
            try {
                $ownedTcp = @(Get-NetTCPConnection -OwningProcess $selectedIdentity.process_id -ErrorAction Stop)
            } catch [Microsoft.PowerShell.Cmdletization.Cim.CimJobException] {
                if ($_.Exception.Message -match 'No MSFT_NetTCPConnection objects') { $ownedTcp = @() } else { $ownership.end_reason = 'tcp_metadata_unavailable'; break }
            }
            try { $ownedUdp = @(Get-NetUDPEndpoint -OwningProcess $selectedIdentity.process_id -ErrorAction Stop) }
            catch [Microsoft.PowerShell.Cmdletization.Cim.CimJobException] {
                if ($_.Exception.Message -match 'No MSFT_NetUDPEndpoint objects') { $ownedUdp = @() } else { $ownership.end_reason = 'udp_metadata_unavailable'; break }
            }
            $postQueryProcesses = @(Get-Process -Id $selectedIdentity.process_id -ErrorAction SilentlyContinue)
            if ($postQueryProcesses.Count -ne 1) { $ownership.end_reason = 'owned_client_exited_during_sample'; break }
            $postQueryIdentity = Get-OfficialProcessIdentity -Process $postQueryProcesses[0] -ExpectedPath $clientExecutable -NotBeforeUtc $notBeforeUtc
            if ($postQueryIdentity.state -ne 'matched' -or $postQueryIdentity.start_ticks -ne $selectedIdentity.start_ticks) {
                $ownership.end_reason = 'sample_ownership_changed'; break
            }
            $sampleRecord = [ordered]@{ schema = 1; timestamp_utc = [datetime]::UtcNow.ToString('o');
                collector_elapsed_ticks = $stopwatch.ElapsedTicks; monotonic_frequency = [Diagnostics.Stopwatch]::Frequency;
                process_id = $selectedIdentity.process_id; process_start_utc = $selectedIdentity.start_utc;
                tcp_udp_socket_metadata = @(ConvertTo-OfficialSocketMetadata -Tcp $ownedTcp -Udp $ownedUdp);
                packet_payloads_collected = $false; decoded_schema_observed = $false }
            $transportStream.WriteLine(($sampleRecord | ConvertTo-Json -Depth 8 -Compress))
            $transportStream.Flush()
            $sampleArguments = @('-B',$collectorPath,'sample','--run',$runPath)
            & $pythonExecutable @sampleArguments | Out-Null
            if ($LASTEXITCODE -ne 0) { $ownership.end_reason = 'log_metadata_failed'; break }
            $sampleCount++
        } elseif ($null -ne $selectedIdentity) { $ownership.end_reason = 'owned_client_exited'; break }
        Start-Sleep -Milliseconds 1000
    }
    if ($ownership.end_reason -eq 'not_ended') { $ownership.end_reason = 'bounded_duration_elapsed' }
} finally {
    $transportStream.Dispose()
    $stopwatch.Stop()
    $ownership.collector_closed = $true
    $ownership.sample_count = $sampleCount
    $ownership.ended_utc = [datetime]::UtcNow.ToString('o')
    $ownership | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ownershipPath -Encoding utf8
    # Leave the scenario open for explicit user observation marks/recording review.
    Write-Output 'OFFICIAL_OBSERVER_CLOSED: no client or unrelated process was stopped; finalize metadata after observation marks.'
}
