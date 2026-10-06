[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$RunDirectory,
    [Parameter(Mandatory)][int]$ExpectedProcessId,
    [Parameter(Mandatory)][string]$ExpectedStartTimeUtc,
    [ValidateRange(5,600)][int]$Seconds = 300
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'OfficialObservation.psm1') -Force
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
$collectorPath = Join-Path $PSScriptRoot 'official_session_metadata.py'
$runPath = [IO.Path]::GetFullPath($RunDirectory)
$privatePrefix = (Join-Path $workspaceRoot 'private\official-sessions') + [IO.Path]::DirectorySeparatorChar
if (-not $runPath.StartsWith($privatePrefix,[StringComparison]::OrdinalIgnoreCase)) { throw 'Private official-session run required.' }
$expectedStart = [datetimeoffset]::Parse($ExpectedStartTimeUtc).UtcDateTime
if ($ExpectedProcessId -le 0 -or $ExpectedStartTimeUtc -notmatch 'Z$') { throw 'Recorded owned process and UTC start required.' }
$sampleArguments = @('-B',$collectorPath,'sample','--run',$runPath)
$processFilter = 'ProcessId = {0}' -f $ExpectedProcessId
$initialMetadata = @(Get-CimInstance -ClassName Win32_Process -Filter $processFilter -Property ProcessId,Name,CreationDate -ErrorAction Stop)
if ($initialMetadata.Count -ne 1 -or -not (Test-OfficialPublicProcessCorrelation -Metadata $initialMetadata[0] -ExpectedProcessId $ExpectedProcessId -ExpectedStartUtc $expectedStart)) {
    throw 'Public owned-session correlation unavailable; protected image path is not retried.'
}
# The parser revalidates private paths, an open run and source-file identity.
& $pythonExecutable @sampleArguments | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Existing private log observation run unavailable.' }
$ownerPath = Join-Path $runPath 'log-only-resource-ownership.json'
if (Test-Path -LiteralPath $ownerPath) { throw 'Refusing another collector ownership file.' }
$collectorProcess = Get-Process -Id $PID
$ownership = [ordered]@{ schema=1; collector_process_id=$PID;
    collector_start_utc=$collectorProcess.StartTime.ToUniversalTime().ToString('o');
    owned_game_process_id=$ExpectedProcessId; owned_game_start_utc=$ExpectedStartTimeUtc;
    scope='ordinary_own_local_game_log_suffix_only';
    attribution='user_confirmed_normal_steam_session_plus_public_process_name_pid_creation_time';
    protected_executable_path='unavailable_not_retried'; installed_build_not_live_image_proof=$true;
    socket_metadata_collected=$false; raw_log_lines_collected=$false; process_memory_read=$false;
    collection_started_utc=[datetime]::UtcNow.ToString('o'); duration_seconds=$Seconds;
    collector_closed=$false; sample_count=0; end_reason='not_ended'; client_termination_performed=$false }
$ownership | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ownerPath -Encoding utf8
$stopwatch = [Diagnostics.Stopwatch]::StartNew()
try {
    while ($stopwatch.Elapsed.TotalSeconds -lt $Seconds) {
        if (Test-Path -LiteralPath (Join-Path $runPath 'stop.request')) { $ownership.end_reason='owned_stop_request'; break }
        $processFilter = 'ProcessId = {0}' -f $ExpectedProcessId
        $publicMetadata = @(Get-CimInstance -ClassName Win32_Process -Filter $processFilter -Property ProcessId,Name,CreationDate -ErrorAction Stop)
        if ($publicMetadata.Count -ne 1) { $ownership.end_reason='owned_client_exited'; break }
        if (-not (Test-OfficialPublicProcessCorrelation -Metadata $publicMetadata[0] -ExpectedProcessId $ExpectedProcessId -ExpectedStartUtc $expectedStart)) {
            $ownership.end_reason='public_process_identity_changed'; break
        }
        & $pythonExecutable @sampleArguments | Out-Null
        if ($LASTEXITCODE -ne 0) { $ownership.end_reason='metadata_parser_refused'; break }
        $ownership.sample_count++
        Start-Sleep -Milliseconds 1000
    }
    if ($ownership.end_reason -eq 'not_ended') { $ownership.end_reason='bounded_duration_elapsed' }
} finally {
    $stopwatch.Stop()
    $ownership.collector_closed=$true
    $ownership.ended_utc=[datetime]::UtcNow.ToString('o')
    $ownership.elapsed_ticks=$stopwatch.ElapsedTicks
    $ownership.monotonic_frequency=[Diagnostics.Stopwatch]::Frequency
    $ownership | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ownerPath -Encoding utf8
}
Write-Output 'OWNED_LOG_SUFFIX_COLLECTOR_CLOSED: protected path not retried; no game process stopped.'
