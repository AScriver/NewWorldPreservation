# IPv4/IPv6 ranges and program scope: Microsoft NetSecurity New-NetFirewallRule.
# https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule
# Own live trial only; never called by offline protocol validation.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$RunDirectory,
    [Parameter(Mandatory)][int]$IPv4ListenerProcessId,
    [Parameter(Mandatory)][int]$IPv6ListenerProcessId,
    [ValidateRange(1,600)][int]$Seconds = 300,
    [ValidateSet('TokenServices')][string]$EndpointProfile = 'TokenServices'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ownedLauncherObject = $null
$workspaceRoot = 'C:\Code\NewWorldPreservation'
$runPath = [IO.Path]::GetFullPath($RunDirectory)
$privatePrefix = (Join-Path $workspaceRoot 'private') + [IO.Path]::DirectorySeparatorChar
if (-not $runPath.StartsWith($privatePrefix, [StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $runPath -PathType Container)) { throw 'Existing ignored private run required.' }
$journalPath = Join-Path $runPath 'hosts-journal'
$eventsPath = Join-Path $runPath 'trial-window.jsonl'
$ownedClientPath = Join-Path $runPath 'owned-client.json'
$clientExecutable = 'C:\Program Files (x86)\Steam\steamapps\common\New World\Bin64\NewWorld.exe'
$expectedClientHash = '8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e'
$validatorPath = 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1'
$redirectScript = Join-Path $workspaceRoot 'scripts\Set-ConnectivityHosts.ps1'
$endpointNames = @('d2c74t4zimux3r.cloudfront.net')
if ($EndpointProfile -eq 'TokenServices') { $endpointNames += @('tokenservice.amazongames.com','prod.newworld.com') }
$activeTrial = Get-Content -LiteralPath (Join-Path $runPath 'run-manifest.json') -Raw | ConvertFrom-Json -DateKind String
$anchorJournal = $activeTrial.rep_anchor_candidate_journal
$anchorSetter = Join-Path $workspaceRoot 'scripts\Set-RepAnchorTrialImage.ps1'
& $validatorPath -Path $anchorSetter | Out-Null
$ruleName = 'NewWorldPreservation-Bootstrap-' + [guid]::NewGuid().ToString('N')
$ruleGroup = $ruleName
# Permit only 127.0.0.1 / ::1 for this executable. No other process is filtered.
$remoteAddresses = @('0.0.0.0-127.0.0.0','127.0.0.2-255.255.255.255','::2-ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
function Write-TrialWindowEvent {
    param([string]$State, [hashtable]$Details)
    $record = [ordered]@{ schema = 1; timestamp_utc = [DateTime]::UtcNow.ToString('o'); state = $State; metadata = $Details }
    [IO.File]::AppendAllText($eventsPath, ($record | ConvertTo-Json -Depth 6 -Compress) + "`n", [Text.UTF8Encoding]::new($false))
}
function Get-OwnedRule {
    param([string]$PolicyStore = 'PersistentStore')
    $rules = @(Get-NetFirewallRule -PolicyStore $PolicyStore -Name $ruleName -ErrorAction SilentlyContinue)
    if ($rules.Count -eq 0) { return $null }
    if ($rules.Count -ne 1 -or $rules[0].Group -cne $ruleGroup -or $rules[0].Description -cne $runPath) { throw 'Firewall rule ownership conflict; no removal.' }
    $applications = @($rules[0] | Get-NetFirewallApplicationFilter)
    if ($applications.Count -ne 1 -or $applications[0].Program -ine $clientExecutable) { throw 'Firewall program identity mismatch; no removal.' }
    return $rules[0]
}
function Write-NewDurableJson {
    param([string]$Path,[object]$Value)
    $jsonBytes = [Text.UTF8Encoding]::new($false).GetBytes(($Value | ConvertTo-Json -Depth 7) + "`n")
    $jsonStream = [IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
    try { $jsonStream.Write($jsonBytes,0,$jsonBytes.Length); $jsonStream.Flush($true) } finally { $jsonStream.Dispose() }
}
function Read-OwnedProcessPath {
    param([object]$ProcessObject)
    try {
        $pathValue = $ProcessObject.Path
        return @{ path=$pathValue; status=$(if ($pathValue) { 'observed' } else { 'unavailable' }) }
    } catch {
        return @{ path=$null; status='unavailable' }
    }
}
function Read-OwnedParentMetadata {
    param([int]$OwnedProcessId)
    try {
        $records = @(Get-CimInstance Win32_Process -Filter "ProcessId=$OwnedProcessId" -ErrorAction Stop)
        if ($records.Count -ne 1 -or $null -eq $records[0].PSObject.Properties['ParentProcessId']) { return @{ parent_process_id=$null; status='unavailable' } }
        return @{ parent_process_id=$records[0].ParentProcessId; status='observed' }
    } catch { return @{ parent_process_id=$null; status='unavailable' } }
}
function Start-OwnedSerialLauncher {
    param([DateTime]$Deadline)
    # No separate launch worker: this same containment owner alone can enter cleanup.
    if ([DateTime]::UtcNow -ge $Deadline -or (Test-Path -LiteralPath (Join-Path $runPath 'stop.request'))) { Write-TrialWindowEvent -State 'ANCHOR_LAUNCH_ADMISSION_CLOSED' -Details @{ process_created=$false }; return }
    if (@(Get-Process -Name NewWorld,NewWorldLauncher -ErrorAction SilentlyContinue).Count -ne 0) { throw 'Preserve preexisting game/launcher.' }
    if (@(Get-Process -Name Steam -ErrorAction SilentlyContinue).Count -eq 0) { throw 'Legitimate Steam client required.' }
    $launcherPath = 'C:\Program Files (x86)\Steam\steamapps\common\New World\NewWorldLauncher.exe'
    if ((Get-FileHash -LiteralPath $launcherPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne '5a9217fafb5656c0b72b516583287ca362c3e1a87e1b5b515ad64a6402b292ec') { throw 'Original vendor launcher changed.' }
    if ((Get-FileHash -LiteralPath $clientExecutable -Algorithm SHA256).Hash.ToLowerInvariant() -cne 'dff94b76032fdd528c936e9f9313dea1736ad5432d32cb068933b8a3d5ed8096') { throw 'Installed candidate changed before launch.' }
    $launchBoundary = [DateTime]::UtcNow.ToString('o')
    Write-NewDurableJson -Path (Join-Path $runPath 'anchor-launch-intent.json') -Value @{ schema=1; timestamp_utc=$launchBoundary; state='OWNED_ANCHOR_LAUNCH_INTENT'; run_directory=$runPath; exclusive_game_and_launcher_absent=$true; containment_owner_process_id=$PID }
    $childEnvironment = @{ SteamAppId='1063730'; SteamGameId='1063730'; SSL_CERT_FILE=$null; SSL_CERT_DIR=$null }
    # The created Process object is retained before any fallible ownership-file write.
    $script:ownedLauncherObject = Start-Process -FilePath $launcherPath -WorkingDirectory (Split-Path -Parent $launcherPath) -Environment $childEnvironment -WindowStyle Hidden -PassThru
    $launchIdentity = [ordered]@{ schema=1; timestamp_utc=$launchBoundary; state='OWNED_ANCHOR_LAUNCHER_CREATED'; run_directory=$runPath; method='Serial containment-owner original installed launcher; certificate-data-only candidate; EAC intact'; original_launcher_process_id=$script:ownedLauncherObject.Id; original_launcher_start_time_utc=$script:ownedLauncherObject.StartTime.ToUniversalTime().ToString('o'); candidate_sha256='dff94b76032fdd528c936e9f9313dea1736ad5432d32cb068933b8a3d5ed8096'; launcher_sha256='5a9217fafb5656c0b72b516583287ca362c3e1a87e1b5b515ad64a6402b292ec'; process_memory_accessed=$false; launcher_environment_scoped=$true; windows_elevated_trial_owner=$true }
    Write-NewDurableJson -Path (Join-Path $runPath 'anchor-launch-manifest.json') -Value $launchIdentity
    Write-TrialWindowEvent -State 'OWNED_ANCHOR_LAUNCHER_CREATED' -Details @{ process_id=$launchIdentity.original_launcher_process_id; start_time_utc=$launchIdentity.original_launcher_start_time_utc; method=$launchIdentity.method }
    $observeDeadline = [DateTime]::UtcNow.AddSeconds(30)
    while ([DateTime]::UtcNow -lt $observeDeadline) {
        $candidates = @(Get-Process -Name NewWorld -ErrorAction SilentlyContinue | Where-Object { $_.StartTime.ToUniversalTime() -ge [DateTimeOffset]::Parse($launchBoundary).UtcDateTime })
        if ($candidates.Count -gt 1) { throw 'Ambiguous fresh games; retain containment.' }
        if ($candidates.Count -eq 1) {
            $candidateProcess = $candidates[0]
            $candidatePathReadback = Read-OwnedProcessPath -ProcessObject $candidateProcess
            if ($candidatePathReadback.path -and $candidatePathReadback.path -ine $clientExecutable) { throw 'Fresh game path conflict.' }
            if ($candidatePathReadback.status -cne 'observed') { Write-TrialWindowEvent -State 'OWNED_GAME_PATH_UNAVAILABLE' -Details @{ process_id=$candidateProcess.Id; attribution_limit='fresh_PID_start_time_not_live_image_path'; eac_cause_proven=$false } }
            $candidateMetadata = Read-OwnedParentMetadata -OwnedProcessId $candidateProcess.Id
            if ($candidateMetadata.status -cne 'observed') { Write-TrialWindowEvent -State 'OWNED_GAME_PARENT_METADATA_UNAVAILABLE' -Details @{ process_id=$candidateProcess.Id; parent_pid_proven=$false; eac_cause_proven=$false } }
            $identity = [ordered]@{ schema=1; timestamp_utc=[DateTime]::UtcNow.ToString('o'); process_id=$candidateProcess.Id; start_time_utc=$candidateProcess.StartTime.ToUniversalTime().ToString('o'); launch_boundary_utc=$launchBoundary; run_directory=$runPath; launch_manifest=(Join-Path $runPath 'anchor-launch-manifest.json'); live_path_verified=[bool]$candidatePathReadback.path; parent_process_id=$candidateMetadata.parent_process_id; direct_parent_pid_matches_launcher=($candidateMetadata.parent_process_id -eq $launchIdentity.original_launcher_process_id); launcher_ancestry_verified=$false; identity_basis='exclusive_fresh_serial_trial_PID_start_time_not_process_memory_or_full_ancestry'; installed_candidate_sha256_after_launch=(Get-FileHash -LiteralPath $clientExecutable -Algorithm SHA256).Hash.ToLowerInvariant() }
            # Publish cleanup identity even when the launcher/update changed the disk image.
            Write-NewDurableJson -Path $ownedClientPath -Value $identity
            Write-TrialWindowEvent -State 'OWNED_ANCHOR_GAME_CORRELATED' -Details @{ process_id=$identity.process_id; start_time_utc=$identity.start_time_utc; installed_candidate_sha256_after_launch=$identity.installed_candidate_sha256_after_launch; direct_parent_pid_matches_launcher=$identity.direct_parent_pid_matches_launcher; ancestry_verified=$false; live_path_verified=$identity.live_path_verified }
            if ($identity.installed_candidate_sha256_after_launch -cne $launchIdentity.candidate_sha256) { throw 'Launcher/update changed candidate; abort attribution.' }
            return
        }
        Start-Sleep -Milliseconds 200
    }
    Write-TrialWindowEvent -State 'OWNED_ANCHOR_GAME_NOT_OBSERVED' -Details @{ bounded_wait_seconds=30; dtls_conclusion='none'; launcher_refusal_not_inferred=$true }
}
function Stop-OwnedAnchorLauncher {
    # Retained object closes the create-before-publish failure gap in this same process.
    if ($null -ne $script:ownedLauncherObject) {
        $ownedLauncher = $script:ownedLauncherObject
        if (-not $ownedLauncher.HasExited) {
            $ownedLauncher.Kill()
            if (-not $ownedLauncher.WaitForExit(10000)) { throw 'Owned launcher remains; retain containment.' }
            Write-TrialWindowEvent -State 'OWNED_ANCHOR_LAUNCHER_STOPPED' -Details @{ process_id=$ownedLauncher.Id; identity_basis='retained_created_Process_object_in_serial_owner' }
        }
    }
}
function Stop-OwnedTrialClient {
    $clients = @(Get-Process -Name 'NewWorld' -ErrorAction SilentlyContinue)
    if ($clients.Count -eq 0) { return }
    if (-not (Test-Path -LiteralPath $ownedClientPath -PathType Leaf)) { throw 'Running game has no recorded owned identity; retain containment.' }
    $identity = Get-Content -LiteralPath $ownedClientPath -Raw | ConvertFrom-Json -DateKind String
    $expectedStart = [DateTimeOffset]::Parse($identity.start_time_utc).UtcDateTime
    $launchBoundary = [DateTimeOffset]::Parse($identity.launch_boundary_utc).UtcDateTime
    $ownedClient = Get-Process -Id $identity.process_id -ErrorAction SilentlyContinue
    if ($null -ne $ownedClient) {
        if ($ownedClient.ProcessName -cne 'NewWorld' -or $ownedClient.StartTime.ToUniversalTime().Ticks -ne $expectedStart.Ticks -or $expectedStart -lt $launchBoundary) { throw 'PID/start-time ownership mismatch; retain containment.' }
        $cleanupPathReadback = Read-OwnedProcessPath -ProcessObject $ownedClient
        if ($cleanupPathReadback.path -and $cleanupPathReadback.path -ine $clientExecutable) { throw 'Live executable path conflict; retain containment.' }
        if ($cleanupPathReadback.status -cne 'observed') { Write-TrialWindowEvent -State 'OWNED_CLEANUP_PATH_UNAVAILABLE' -Details @{ process_id=$ownedClient.Id; pid_start_time_verified=$true; live_image_path_verified=$false } }
        Stop-Process -Id $ownedClient.Id -ErrorAction Stop
        if (-not $ownedClient.WaitForExit(10000)) { throw 'Owned client still running; retain containment.' }
        Write-TrialWindowEvent -State 'OWNED_CLIENT_STOPPED' -Details @{ process_id = $identity.process_id; start_time_utc = $identity.start_time_utc }
    }
    if (@(Get-Process -Name 'NewWorld' -ErrorAction SilentlyContinue).Count -gt 0) { throw 'A different game remains; retain containment.' }
}
if (Test-Path -LiteralPath $eventsPath) { throw 'Fresh trial window event file required.' }
if (@(Get-Process -Name 'NewWorld' -ErrorAction SilentlyContinue).Count -gt 0) { throw 'Preserve an already running client; do not start trial.' }
if ((Get-FileHash -LiteralPath $clientExecutable -Algorithm SHA256).Hash.ToLowerInvariant() -cne $expectedClientHash) { throw 'Client installation identity changed.' }
if (@(Get-NetFirewallProfile | Where-Object { $_.Enabled -ne $true }).Count -gt 0) { throw 'All firewall profiles must already be enabled; do not change them.' }
$listeners = @(Get-NetTCPConnection -LocalPort 443 -State Listen -ErrorAction Stop)
if (@($listeners | Where-Object { $_.LocalAddress -eq '127.0.0.1' -and $_.OwningProcess -eq $IPv4ListenerProcessId }).Count -ne 1 -or @($listeners | Where-Object { $_.LocalAddress -eq '::1' -and $_.OwningProcess -eq $IPv6ListenerProcessId }).Count -ne 1) { throw 'Both owned HTTPS listeners required.' }
$plan = @{ rule_name = $ruleName; group = $ruleGroup; program = $clientExecutable; remote_addresses = $remoteAddresses; seconds = $Seconds }
[IO.File]::WriteAllText((Join-Path $runPath 'firewall-ownership.json'), ($plan | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))
try {
    $null = New-NetFirewallRule -Name $ruleName -DisplayName $ruleName -Group $ruleGroup -Description $runPath -Direction Outbound -Action Block -Enabled True -Profile Any -Program $clientExecutable -Protocol Any -RemoteAddress $remoteAddresses -PolicyStore PersistentStore
    $activeRule = Get-OwnedRule -PolicyStore ActiveStore
    if ($null -eq $activeRule -or [string]$activeRule.Enabled -ne 'True' -or [string]$activeRule.Direction -ne 'Outbound' -or [string]$activeRule.Action -ne 'Block' -or [string]$activeRule.Profile -ne 'Any') { throw 'Effective firewall scope readback failed.' }
    $addressFilter = $activeRule | Get-NetFirewallAddressFilter
    $portFilter = $activeRule | Get-NetFirewallPortFilter
    if ([string]$portFilter.Protocol -ne 'Any' -or @(Compare-Object -ReferenceObject $remoteAddresses -DifferenceObject @($addressFilter.RemoteAddress)).Count -gt 0) { throw 'Effective firewall address/protocol readback failed.' }
    Write-TrialWindowEvent -State 'GAME_OUTBOUND_CONTAINMENT_CONFIGURED' -Details @{ rule_name = $ruleName; program = $clientExecutable; profile = 'Any'; protocol = 'Any'; remote_addresses = @($addressFilter.RemoteAddress); evidence_source = 'ActiveStore_configuration_not_packet_trace'; helper_processes_filtered = $false }
    & $validatorPath -Path $redirectScript -Execute -ArgumentList @('-Action','Apply','-JournalDirectory',$journalPath,'-EndpointProfile',$EndpointProfile) | Out-Null
    $resolverEvidence = @{}
    foreach ($observedEndpointName in $endpointNames) {
        $resolvedAddresses = @([Net.Dns]::GetHostAddresses($observedEndpointName) | ForEach-Object { $_.ToString() })
        if ($resolvedAddresses.Count -eq 0 -or @($resolvedAddresses | Where-Object { $_ -notin @('127.0.0.1','::1') }).Count -gt 0) { throw 'Non-loopback resolver result; do not launch.' }
        $resolverEvidence[$observedEndpointName] = $resolvedAddresses
    }
    Write-TrialWindowEvent -State 'BOOTSTRAP_TRIAL_READY' -Details @{ hostname = 'd2c74t4zimux3r.cloudfront.net'; resolutions = $resolverEvidence; endpoint_profile = $EndpointProfile; seconds = $Seconds; evidence_source = 'operator_resolver_not_client_dns' }
    & $validatorPath -Path $anchorSetter -Execute -ArgumentList @('-Action','Apply','-CandidateJournal',$anchorJournal,'-RunDirectory',$runPath) | Out-Null
    Write-TrialWindowEvent -State 'REP_ANCHOR_TRIAL_READY' -Details @{ candidate_journal_sha256=(Get-FileHash -LiteralPath $anchorJournal -Algorithm SHA256).Hash.ToLowerInvariant(); candidate_image_sha256='dff94b76032fdd528c936e9f9313dea1736ad5432d32cb068933b8a3d5ed8096'; same_verifier_instructions=$true; anchor_policy_substituted=$true; launcher_eac_unchanged=$true }
    $deadline = [DateTime]::UtcNow.AddSeconds($Seconds)
    Start-OwnedSerialLauncher -Deadline $deadline
    while ([DateTime]::UtcNow -lt $deadline -and -not (Test-Path -LiteralPath (Join-Path $runPath 'stop.request'))) { Start-Sleep -Milliseconds 250 }
} catch {
    Write-TrialWindowEvent -State 'BOOTSTRAP_TRIAL_FAILED' -Details @{ exception_type = $_.Exception.GetType().Name; script_line_number = $_.InvocationInfo.ScriptLineNumber; raw_error_or_arguments_saved = $false }
    throw
} finally {
    try {
        Stop-OwnedAnchorLauncher
        Stop-OwnedTrialClient
        & $validatorPath -Path $anchorSetter -Execute -ArgumentList @('-Action','Restore','-CandidateJournal',$anchorJournal,'-RunDirectory',$runPath) | Out-Null
        Write-TrialWindowEvent -State 'STOCK_CLIENT_RESTORED_BEFORE_ROUTING_RELEASE' -Details @{ stock_image_sha256='8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e'; stock_signature_valid=$true; game_absent=$true }
        & $validatorPath -Path $redirectScript -Execute -ArgumentList @('-Action','Restore','-JournalDirectory',$journalPath,'-EndpointProfile',$EndpointProfile) | Out-Null
        $ownedRule = Get-OwnedRule
        if ($null -ne $ownedRule) { $ownedRule | Remove-NetFirewallRule -ErrorAction Stop }
        if ($null -ne (Get-OwnedRule) -or $null -ne (Get-OwnedRule -PolicyStore ActiveStore)) { throw 'Owned firewall rule remains after removal.' }
        Write-TrialWindowEvent -State 'BOOTSTRAP_TRIAL_CLOSED' -Details @{ client_absent = $true; hosts_restoration_requested = $true; owned_firewall_rule_absent = $true; trust_cleanup_is_parent_owned = $true }
    } catch {
        Write-TrialWindowEvent -State 'BOOTSTRAP_TRIAL_CLEANUP_BLOCKED' -Details @{ exception_type = $_.Exception.GetType().Name; preserve_remaining_containment = $true }
        throw
    }
}
