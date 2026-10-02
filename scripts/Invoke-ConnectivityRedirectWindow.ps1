[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$JournalDirectory,
    [Parameter(Mandatory)][int]$IPv4ListenerProcessId,
    [Parameter(Mandatory)][int]$IPv6ListenerProcessId,
    [ValidateRange(1,600)][int]$Seconds = 300
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$journalPath = [IO.Path]::GetFullPath($JournalDirectory)
$privatePrefix = (Join-Path $workspaceRoot 'private') + [IO.Path]::DirectorySeparatorChar
$scratchPrefix = (Join-Path $workspaceRoot '.scratch') + [IO.Path]::DirectorySeparatorChar
if (-not ($journalPath.StartsWith($privatePrefix, [StringComparison]::OrdinalIgnoreCase) -or $journalPath.StartsWith($scratchPrefix, [StringComparison]::OrdinalIgnoreCase))) { throw 'Ignored workspace journal required.' }
$stopPath = Join-Path $journalPath 'stop.request'
$failurePath = Join-Path $journalPath 'window-failure.json'
$windowEventsPath = Join-Path $journalPath 'window-events.jsonl'
$validatorPath = 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1'
$redirectScriptPath = Join-Path $PSScriptRoot 'Set-ConnectivityHosts.ps1'
function Write-WindowEvent {
    param([string]$State, [hashtable]$Details)
    $record = [ordered]@{ schema = 1; timestamp_utc = [DateTime]::UtcNow.ToString('o'); state = $State; metadata = $Details }
    [IO.File]::AppendAllText($windowEventsPath, ($record | ConvertTo-Json -Depth 5 -Compress) + "`n", [Text.UTF8Encoding]::new($false))
}
try {
    $listeners = @(Get-NetTCPConnection -LocalPort 443 -State Listen -ErrorAction Stop)
    if (@($listeners | Where-Object { $_.LocalAddress -eq '127.0.0.1' -and $_.OwningProcess -eq $IPv4ListenerProcessId }).Count -ne 1 -or @($listeners | Where-Object { $_.LocalAddress -eq '::1' -and $_.OwningProcess -eq $IPv6ListenerProcessId }).Count -ne 1) {
        throw 'Both expected owned loopback HTTPS listeners must be present before redirect.'
    }
    Write-WindowEvent -State 'REDIRECT_WINDOW_START' -Details @{ seconds = $Seconds; no_client_launch_or_trust_import = $true }
    & $validatorPath -Path $redirectScriptPath -Execute -ArgumentList @('-Action','Apply','-JournalDirectory',$journalPath) | Out-Null
    $resolvedAddresses = @([Net.Dns]::GetHostAddresses('d2c74t4zimux3r.cloudfront.net') | ForEach-Object { $_.ToString() })
    if ($resolvedAddresses.Count -eq 0 -or @($resolvedAddresses | Where-Object { $_ -notin @('127.0.0.1','::1') }).Count -gt 0) { throw 'Operator resolver still returns a non-loopback address; do not launch client.' }
    Write-WindowEvent -State 'ENDPOINT_RESOLUTION' -Details @{ hostname = 'd2c74t4zimux3r.cloudfront.net'; addresses = $resolvedAddresses; evidence_source = 'operator_dotnet_resolver_not_client_dns_trace' }
    $windowDeadline = [DateTime]::UtcNow.AddSeconds($Seconds)
    while ([DateTime]::UtcNow -lt $windowDeadline -and -not (Test-Path -LiteralPath $stopPath)) { Start-Sleep -Milliseconds 250 }
} catch {
    # Safe exception type, not arbitrary source text or hosts contents.
    [IO.File]::WriteAllText($failurePath, (@{ timestamp_utc = [DateTime]::UtcNow.ToString('o'); state = 'REDIRECT_WINDOW_FAILED'; exception_type = $_.Exception.GetType().Name } | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
    throw
} finally {
    & $validatorPath -Path $redirectScriptPath -Execute -ArgumentList @('-Action','Restore','-JournalDirectory',$journalPath) | Out-Null
    Write-WindowEvent -State 'REDIRECT_WINDOW_CLOSED' -Details @{ restoration_requested = $true }
}
