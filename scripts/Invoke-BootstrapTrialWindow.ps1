# IPv4/IPv6 ranges and program scope: Microsoft NetSecurity New-NetFirewallRule.
# https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule
# Own live trial only; never called by offline protocol validation.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$RunDirectory,
    [Parameter(Mandatory)][int]$IPv4ListenerProcessId,
    [Parameter(Mandatory)][int]$IPv6ListenerProcessId,
    [ValidateRange(1,600)][int]$Seconds = 300
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$runPath = [IO.Path]::GetFullPath($RunDirectory)
$privatePrefix = (Join-Path $workspaceRoot 'private') + [IO.Path]::DirectorySeparatorChar
if (-not $runPath.StartsWith($privatePrefix, [StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $runPath -PathType Container)) { throw 'Existing ignored private run required.' }
$journalPath = Join-Path $runPath 'hosts-journal'
$eventsPath = Join-Path $runPath 'trial-window.jsonl'
$ownedClientPath = Join-Path $runPath 'owned-client.json'
$clientExecutable = 'C:\Program Files (x86)\Steam\steamapps\common\New World\Bin64\NewWorld.exe'
$expectedClientHash = '8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e'
$validatorPath = 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1'
$redirectScript = Join-Path $PSScriptRoot 'Set-ConnectivityHosts.ps1'
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
        if ($ownedClient.Path -and $ownedClient.Path -ine $clientExecutable) { throw 'Live executable path conflict; retain containment.' }
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
    & $validatorPath -Path $redirectScript -Execute -ArgumentList @('-Action','Apply','-JournalDirectory',$journalPath) | Out-Null
    $resolvedAddresses = @([Net.Dns]::GetHostAddresses('d2c74t4zimux3r.cloudfront.net') | ForEach-Object { $_.ToString() })
    if ($resolvedAddresses.Count -eq 0 -or @($resolvedAddresses | Where-Object { $_ -notin @('127.0.0.1','::1') }).Count -gt 0) { throw 'Non-loopback resolver result; do not launch.' }
    Write-TrialWindowEvent -State 'BOOTSTRAP_TRIAL_READY' -Details @{ hostname = 'd2c74t4zimux3r.cloudfront.net'; addresses = $resolvedAddresses; seconds = $Seconds; evidence_source = 'operator_resolver_not_client_dns' }
    $deadline = [DateTime]::UtcNow.AddSeconds($Seconds)
    while ([DateTime]::UtcNow -lt $deadline -and -not (Test-Path -LiteralPath (Join-Path $runPath 'stop.request'))) { Start-Sleep -Milliseconds 250 }
} catch {
    Write-TrialWindowEvent -State 'BOOTSTRAP_TRIAL_FAILED' -Details @{ exception_type = $_.Exception.GetType().Name }
    throw
} finally {
    try {
        Stop-OwnedTrialClient
        & $validatorPath -Path $redirectScript -Execute -ArgumentList @('-Action','Restore','-JournalDirectory',$journalPath) | Out-Null
        $ownedRule = Get-OwnedRule
        if ($null -ne $ownedRule) { $ownedRule | Remove-NetFirewallRule -ErrorAction Stop }
        if ($null -ne (Get-OwnedRule) -or $null -ne (Get-OwnedRule -PolicyStore ActiveStore)) { throw 'Owned firewall rule remains after removal.' }
        Write-TrialWindowEvent -State 'BOOTSTRAP_TRIAL_CLOSED' -Details @{ client_absent = $true; hosts_restoration_requested = $true; owned_firewall_rule_absent = $true; trust_cleanup_is_parent_owned = $true }
    } catch {
        Write-TrialWindowEvent -State 'BOOTSTRAP_TRIAL_CLEANUP_BLOCKED' -Details @{ exception_type = $_.Exception.GetType().Name; preserve_remaining_containment = $true }
        throw
    }
}
