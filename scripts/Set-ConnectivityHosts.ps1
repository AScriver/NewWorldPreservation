[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Prepare','Apply','Restore')][string]$Action,
    [Parameter(Mandatory)][string]$JournalDirectory,
    [string]$HostsPath = (Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'),
    [ValidateSet('BootstrapOnly','TokenServices')][string]$EndpointProfile = 'BootstrapOnly'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$journalPath = [IO.Path]::GetFullPath($JournalDirectory)
$targetPath = [IO.Path]::GetFullPath($HostsPath)
$systemHostsPath = [IO.Path]::GetFullPath((Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'))
$privatePrefix = (Join-Path $workspaceRoot 'private') + [IO.Path]::DirectorySeparatorChar
$scratchPrefix = (Join-Path $workspaceRoot '.scratch') + [IO.Path]::DirectorySeparatorChar
if (-not ($journalPath.StartsWith($privatePrefix, [StringComparison]::OrdinalIgnoreCase) -or $journalPath.StartsWith($scratchPrefix, [StringComparison]::OrdinalIgnoreCase))) {
    throw 'Journal must be in ignored workspace private/ or .scratch/.'
}
if ($targetPath -ine $systemHostsPath -and -not $targetPath.StartsWith($scratchPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Only the Windows hosts file or an isolated .scratch/ fixture is allowed.'
}
if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) { throw 'Hosts target must already exist.' }
if ((Get-Item -LiteralPath $targetPath).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse-point hosts target refused.' }
$endpointName = 'd2c74t4zimux3r.cloudfront.net' # Observed current-client bootstrap, not an arbitrary host list.
$endpointNames = @($endpointName)
if ($EndpointProfile -eq 'TokenServices') { $endpointNames += @('tokenservice.amazongames.com','prod.newworld.com') } # Observed current public descriptor, not observed contacts yet.
$planPath = Join-Path $journalPath 'plan.json'
$backupPath = Join-Path $journalPath 'before.bin'
$journalEventsPath = Join-Path $journalPath 'events.jsonl'
$utf8Strict = [Text.UTF8Encoding]::new($false, $true)
function Get-ByteHash {
    param([byte[]]$Content)
    $hasher = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash($Content))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose() }
}
function Write-HostsEvent {
    param([string]$State, [hashtable]$Details)
    $record = [ordered]@{ schema = 1; timestamp_utc = [DateTime]::UtcNow.ToString('o'); state = $State; hostname = $endpointName; hostnames = $endpointNames; metadata = $Details }
    $serialized = $record | ConvertTo-Json -Depth 5 -Compress
    [IO.File]::AppendAllText($journalEventsPath, $serialized + "`n", [Text.UTF8Encoding]::new($false))
    $serialized
}
function Read-StreamBytes {
    param([IO.FileStream]$TargetStream)
    $TargetStream.Position = 0
    $memoryStream = [IO.MemoryStream]::new()
    try { $TargetStream.CopyTo($memoryStream); return ,$memoryStream.ToArray() }
    finally { $memoryStream.Dispose() }
}
function Write-StreamBytes {
    param([IO.FileStream]$TargetStream, [byte[]]$Content)
    $TargetStream.Position = 0
    $TargetStream.Write($Content, 0, $Content.Length)
    $TargetStream.SetLength($Content.Length)
    $TargetStream.Flush($true)
}
if ($Action -eq 'Prepare') {
    if (Test-Path -LiteralPath $journalPath) { throw 'Use a fresh journal directory; never overwrite an earlier backup.' }
    $beforeBytes = [IO.File]::ReadAllBytes($targetPath)
    $beforeText = $utf8Strict.GetString($beforeBytes) # Refuse UTF-16/invalid UTF-8 rather than rewrite an unknown encoding.
    if ($beforeText.Contains([char]0)) { throw 'Unsupported hosts encoding.' }
    foreach ($hostsLine in ($beforeText -split "`n")) {
        $activePart = ($hostsLine -split '#', 2)[0].Trim()
        foreach ($observedEndpointName in $endpointNames) {
            if (($activePart -split '\s+') -icontains $observedEndpointName) { throw 'Existing observed-host mapping conflicts with this test; preserve it.' }
        }
    }
    $redirectRunId = [guid]::NewGuid().ToString('N')
    $separator = ''
    if ($beforeText.Length -gt 0 -and -not $beforeText.EndsWith("`n")) { $separator = "`r`n" }
    $blockText = $separator + "# BEGIN NewWorldPreservation $redirectRunId`r`n"
    foreach ($observedEndpointName in $endpointNames) { $blockText += "127.0.0.1 $observedEndpointName`r`n::1 $observedEndpointName`r`n" }
    $blockText += "# END NewWorldPreservation $redirectRunId`r`n"
    $blockBytes = $utf8Strict.GetBytes($blockText)
    $afterBytes = [byte[]]($beforeBytes + $blockBytes)
    $null = New-Item -ItemType Directory -Path $journalPath
    [IO.File]::WriteAllBytes($backupPath, $beforeBytes)
    $plan = [ordered]@{ schema = 1; run_id = $redirectRunId; target = $targetPath; hostname = $endpointName; endpoint_profile = $EndpointProfile; hostnames = $endpointNames; before_sha256 = (Get-ByteHash $beforeBytes); applied_sha256 = (Get-ByteHash $afterBytes); block_base64 = [Convert]::ToBase64String($blockBytes) }
    [IO.File]::WriteAllText($planPath, ($plan | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))
    Write-HostsEvent -State 'HOSTS_REDIRECT_PREPARED' -Details @{ hosts_modified = $false; before_sha256 = $plan.before_sha256; addresses = @('127.0.0.1','::1') }
    return
}
$plan = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
if ($plan.schema -ne 1 -or $plan.target -ine $targetPath -or $plan.hostname -cne $endpointName) { throw 'Journal identity does not match requested target.' }
if ($plan.PSObject.Properties.Name -contains 'endpoint_profile') {
    if ($plan.endpoint_profile -cne $EndpointProfile -or @($plan.hostnames).Count -ne $endpointNames.Count -or (@($plan.hostnames) -join '|') -cne ($endpointNames -join '|')) { throw 'Journal endpoint profile/list mismatch; no mutation.' }
} elseif ($EndpointProfile -ne 'BootstrapOnly') { throw 'Legacy journal cannot expand hostname scope.' }
$beforeBytes = [IO.File]::ReadAllBytes($backupPath)
$blockBytes = [Convert]::FromBase64String($plan.block_base64)
if ((Get-ByteHash $beforeBytes) -cne $plan.before_sha256 -or (Get-ByteHash ([byte[]]($beforeBytes + $blockBytes))) -cne $plan.applied_sha256) { throw 'Backup/plan integrity failure.' }
# Exclusive file sharing serializes a guarded read, write and readback. Preserve existing ACLs.
$targetStream = [IO.FileStream]::new($targetPath, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
try {
    $currentBytes = Read-StreamBytes $targetStream
    $currentHash = Get-ByteHash $currentBytes
    $desiredBytes = $null
    if ($Action -eq 'Apply') {
        if ($currentHash -ceq $plan.applied_sha256) { Write-HostsEvent -State 'HOSTS_REDIRECT_ALREADY_APPLIED' -Details @{}; return }
        if ($currentHash -cne $plan.before_sha256) { throw 'Hosts changed after preparation; refusing to overwrite it.' }
        $desiredBytes = [byte[]]($beforeBytes + $blockBytes)
    } else {
        if ($currentHash -ceq $plan.before_sha256) { Write-HostsEvent -State 'HOSTS_REDIRECT_ALREADY_RESTORED' -Details @{}; return }
        if ($currentHash -ceq $plan.applied_sha256) { $desiredBytes = $beforeBytes }
        else {
            # Preserve concurrent unrelated edits; remove exactly our unique tagged block.
            $currentText = $utf8Strict.GetString($currentBytes)
            $blockText = $utf8Strict.GetString($blockBytes)
            $blockIndex = $currentText.IndexOf($blockText, [StringComparison]::Ordinal)
            if ($blockIndex -lt 0 -or $currentText.IndexOf($blockText, $blockIndex + $blockText.Length, [StringComparison]::Ordinal) -ge 0) { throw 'Our unique block is absent/ambiguous; manual reconciliation required, no overwrite.' }
            $desiredBytes = $utf8Strict.GetBytes($currentText.Remove($blockIndex, $blockText.Length))
        }
    }
    Write-HostsEvent -State ('HOSTS_REDIRECT_' + $Action.ToUpperInvariant() + '_START') -Details @{ before_write_sha256 = $currentHash }
    try {
        Write-StreamBytes -TargetStream $targetStream -Content $desiredBytes
        if ((Get-ByteHash (Read-StreamBytes $targetStream)) -cne (Get-ByteHash $desiredBytes)) { throw 'Hosts readback mismatch.' }
    } catch {
        Write-StreamBytes -TargetStream $targetStream -Content $currentBytes
        throw
    }
    Write-HostsEvent -State ('HOSTS_REDIRECT_' + $Action.ToUpperInvariant() + '_COMPLETE') -Details @{ readback_sha256 = (Get-ByteHash $desiredBytes); original_bytes_restored = ((Get-ByteHash $desiredBytes) -ceq $plan.before_sha256); unrelated_edits_preserved = $true }
} finally { $targetStream.Dispose() }
